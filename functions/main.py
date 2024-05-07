# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Welcome to Cloud Functions for Firebase for Python!
# Deploy with `firebase deploy`

# The Cloud Functions for Firebase SDK to create Cloud Functions and set up triggers.
import os
import re
from firebase_functions import firestore_fn, https_fn, options

# The Firebase Admin SDK to access Cloud Firestore.
from firebase_admin import initialize_app, firestore

import markdown
from flask import jsonify
import google.ai.generativelanguage as glm
import google.generativeai as genai
from bs4 import BeautifulSoup

from google.oauth2 import service_account

app = initialize_app()

# Used to securely store your API key
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')

# Select your Gemini API endpoint.
SERVICE_ACCOUNT_FILE_NAME = 'service_account_key.json'
AQA_MODEL = "models/aqa"
PRODUCT_NAME = "Angular"
ANSWER_STYLE = "VERBOSE"  # or ABSTRACTIVE, EXTRACTIVE
CORPUS_NAME = "corpora/angular-dev" # TODO: change this to your DocsAgent Corpus Name!
LOG_LEVEL = "VERBOSE"

@https_fn.on_request(cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
def generate_aqa_answer(req: https_fn.Request) -> https_fn.Response:
    # Grab the text parameter.
    prompt = req.args.get("text")
    if prompt is None:
        return https_fn.Response("No text parameter provided", status=400)

    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE_NAME)
    scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language.retriever'])
    
    generative_service_client = glm.GenerativeServiceClient(credentials=scoped_credentials)

    # Prepare parameters for the AQA model
    content = glm.Content(parts=[glm.Part(text=prompt)])
    retriever_config = glm.SemanticRetrieverConfig(
        source=CORPUS_NAME, query=content
    )

    # Create a request to the AQA model
    req = glm.GenerateAnswerRequest(
        model=AQA_MODEL,
        contents=[content],
        semantic_retriever=retriever_config,
        answer_style=ANSWER_STYLE,
    )

    try:
        aqa_response = generative_service_client.generate_answer(req)
        answer = aqa_response.answer.content.parts[0].text
        print(aqa_response)
    except:
        print('Generate AQA answer - in the exception')

    try:
        answer = convert_to_html(answer)
        print(answer)
    except:
        print('Make HTML - in the exception')

    try:
        resource_url = get_url(aqa_response.answer.grounding_attributions[0].source_id.semantic_retriever_chunk.chunk)
    except:
        print('Resouce URL attempt - in the exception')

    questions = get_genai_follow_up_questions(prompt, aqa_response.answer.grounding_attributions)

    if (aqa_response.answerable_probability < .1):
        answer = "Sorry, that question isn't answered on Angular.dev. Please try again!"
        resource_url = ''

    return jsonify({
        'answer': answer,
        'probability': aqa_response.answerable_probability,
        'url': resource_url,
        'questions': questions
    })

def get_url(chunk_resource_name: str) -> str:
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE_NAME)
    scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language.retriever'])
    retriever_service_client = glm.RetrieverServiceClient(credentials=scoped_credentials)

    url = "Reference URL"
    try:
        # Get the metadata from the first attributed passages for the source
        get_chunk_response = retriever_service_client.get_chunk(
            name=chunk_resource_name
        )
        metadata = get_chunk_response.custom_metadata
        for m in metadata:
            if m.key == "url":
                url = m.string_value
    except:
        url = "URL unknown"

    url = url.replace('/overview', '')
    url = url.replace('/reference', '')
    url = url.replace('/best-practices', '')
    url = url.replace('/introduction/what-is-angular', '/overview')
    url = url.replace('_', '-')

    return url

def convert_to_html(answer):
    prompt = "Read the answer below. Convert the answer into valid HTML, with no markdown wrapper. The title should be an <h4>."
    response = call_genai_generate_content(prompt + answer)

    return response

def get_genai_follow_up_questions(prompt, grounding_attributions):
    context = "Given a developer just asked " + prompt
    for item in grounding_attributions:
        context = add_custom_instruction_to_context(
            context, item.content.parts[0].text
        )
    new_condition = "Read the context below and answer the user's question at the end."
    new_context_with_instruction = add_custom_instruction_to_context(
        new_condition, context
    )
    new_question = (
        "What are 3 questions developers might ask after reading the context above?"
    )
    new_response = markdown.markdown(
        ask_model_with_context(
            new_context_with_instruction, new_question
        )
    )
    related_questions = parse_related_questions_response_to_list(new_response)

    return related_questions

# Add custom instruction as a prefix to the context
def add_custom_instruction_to_context(condition, context):
    new_context = ""
    new_context += condition + "\n\n" + context
    return new_context

# Use this method for talking to a PaLM text model
def ask_model_with_context(context, question):
    new_prompt = f"{context}\n\nQuestion: {question}"

    response = call_genai_generate_content(new_prompt)

    return response

# Parse a response containing a list of related questions from the language model
# and convert it into an HTML-based list.
def parse_related_questions_response_to_list(response):
    soup = BeautifulSoup(response, "html.parser")
    questions = []
    for item in soup.find_all("li"):
        # In case there are code tags, remove the tag and just replace with plain text
        if item.find("code"):
            text = item.find("code").text
            # item.code.replace_with(text)
            questions += [text]
        # In case there are <p> tags within the <li> strip <p>
        if item.find("p"):
            text = item.find("p").text
            # link = soup.new_tag(
            #     "a",
            #     # href=url_for("chatui.question", ask=urllib.parse.quote_plus(text)),
            # )
            # link.string = text
            # item.string = ""
            # item.append(link)
            questions += [text]
        if item.string is not None:
            # link = soup.new_tag(
            #     "a",
            #     # href=url_for(
            #     #     "chatui.question", ask=urllib.parse.quote_plus(item.string)
            #     # ),
            # )
            # link.string = item.string
            # item.string = ""
            # item.append(link)
            questions += [item.string]
    return questions

# Print the prompt on the terminal for debugging
def print_the_prompt(prompt):
    print("#########################################")
    print("#              PROMPT                   #")
    print("#########################################")
    print(prompt)
    print("#########################################")
    print("#           END OF PROMPT               #")
    print("#########################################")
    print("\n")

@https_fn.on_request(cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
def generate_genai_answer(req: https_fn.Request) -> https_fn.Response:
    # Grab the text parameter.
    prompt = req.args.get("text")
    if prompt is None:
        return https_fn.Response("No text parameter provided", status=400)

    response = call_genai_generate_content(prompt)

    return jsonify({
        'answer': response
    })

@https_fn.on_request(cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
def hello(req: https_fn.Request) -> https_fn.Response:
    return https_fn.Response("Hello world!")
    return jsonify({
        'answer': 'hello'
    })

def call_genai_generate_content(prompt) -> str:
    # Print the prompt for debugging if the log level is VERBOSE.
    if LOG_LEVEL == "VERBOSE":
        print_the_prompt(prompt)

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
    except:
        print("Failed to call the model!")
    if response.text is None:
        print("Block reason: " + str(response.filters))
        print("Safety feedback: " + str(response.safety_feedback))

    return response.text
