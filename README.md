# Angular Docs RAG Sample

Developer sample written in Angular demonstrating how developers might ingest developer docs and make the content accessible to Gemini via RAG (Retrieval Augmented Generation). The ingested content is accessible in the sample through an Angular chatbot.

This project was generated with [Angular CLI](https://github.com/angular/angular1.cli) and uses [DocsAgent](), to impliment RAG (Retrieval Augmented Generation) with Gemini and create a domain-specific expertise chatbot. This sample uses Googles Semantic Revtriever API and Generative Language APIs as well as an AQA (Attributed Questions and Answer) model with Gemini Pro.

For more information on Angular, visit [angular.dev](https://angular.dev/).

## Get the demo running locally!

1. Create a personal fork of the project on Github, then clone the fork on your local machine.
1. Run `npm run install` to install the dependencies required to run the server.
1. [IMPORTANT!!] This demo needs a Gemini API to run. Go to [Google AI Studio](https://aistudio.google.com/app/apikey) to get an API key then add it to the Firebase Function in `angular-docs-rag-sample/functions/.env`. This demo simulates how you might store and protect a private Gemini API key in a real world app.
1. [IMPORTANT!!] This demo relies on a `CORPUS_NAME` from Docs Agent, then authenticates with a `angular-docs-rag-sample/service_account_key.json`. See [DocsAgent Set Up guide](https://github.com/google/generative-ai-docs/tree/main/examples/gemini/python/docs-agent#set-up-docs-agent) to set up your own corpus and authentication.
1. Run `ng run start` to run the server. Since we're using Firebase Functions, you'll need to run our functions and the app in a Firebase Emulator! 
1. Open a browser tab to [http://localhost:4200](http://localhost:4200). The app will automatically reload if you change any of the source files.
