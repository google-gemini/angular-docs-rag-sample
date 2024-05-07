/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {Component, inject} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {RouterOutlet} from '@angular/router';
import {MarkdownModule} from 'ngx-markdown';
import {GenerativeLanguageService} from '../gen-ai.service';
import {BubbleComponent, ChatBubble} from './bubble/bubble.component';
import {MatProgressBarModule} from '@angular/material/progress-bar';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [RouterOutlet, FormsModule, MarkdownModule, BubbleComponent, MatProgressBarModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss',
})
export class ChatComponent {
  protected question = '';
  protected prompt = '';
  protected loading = false;

  protected followUpQuestions = [
    'What are Angular signals?',
    'What is control flow?',
    'How do I bind to a template?',
    'Adding a new route with the Router',
    'What is Angular?',
  ];
  protected conversation: ChatBubble[] = [{type: 'answer', text: 'Hi there! How can I help?'}];

  private generativeLanguage = inject(GenerativeLanguageService);

  async getAnswer(prompt?: string) {
    this.prompt = prompt ?? this.question;
    this.addDialog(this.prompt);
    this.question = '';
    this.loading = true;

    await (
      await this.generativeLanguage.getAQAAnswer(this.prompt)
    ).subscribe(async (res) => {
      if (res.questions) this.followUpQuestions = res.questions;
      this.addDialog(res.answer, res.url, false);
    });
  }

  addDialog(text: string, url?: string, isQuestion: boolean = true) {
    this.loading = false;
    this.conversation.push({
      text: text,
      type: isQuestion ? 'question' : 'answer',
    });
  }
}
