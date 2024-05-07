import { Component, ElementRef, inject, viewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterOutlet } from '@angular/router';
import { MarkdownModule } from 'ngx-markdown';
import { GenerativeLanguageService } from '../gen-ai.service';
import { GenAIService } from '../generative-ai.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    RouterOutlet, 
    FormsModule, 
    MarkdownModule,
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent {
  conversation = viewChild.required<ElementRef>('start');

  question: string = ''
  prompt: string = ''

  followUpQuestions: string[] = ['What are Angular signals?', 'What is control flow?', 'How do I bind to a template?', 'Adding a new route with the Router', 'What is Angular?']

  private genAI = inject(GenAIService);
  private generativeLanguage = inject(GenerativeLanguageService);

  async getAnswer(prompt?: string) {
    this.prompt = prompt ?? this.question;
    this.addDialog(this.prompt)
    this.question = '';

    // this.genAI.fetchAnswer(this.prompt).then((answer) => {
    //   console.log(answer);
    //   this.addDialog(answer, '', false)
    // })

    await (await this.generativeLanguage.getAQAAnswer(this.prompt)).subscribe(async res => {
      // console.log(res);
      
      if (res.questions) this.followUpQuestions = res.questions
      this.addDialog(res.answer, res.url, false)
    });

  }   

  addDialog(text: string, url?: string, isQuestion: boolean = true) {
    const tempDiv = document.createElement("div");
    
    if (isQuestion) {
      tempDiv.className = "question border";
      tempDiv.style.cssText = `
      place-self: end;
      background: color-mix(in srgb, var(--vivid-pink) 15%, transparent);
      border: 1px solid black;
      padding-inline: 1.75rem;
      border-radius: 1rem;
      text-align: right;
      `
      tempDiv.innerHTML = `<p>${text}</p>`;
    } else {
      tempDiv.className = "answer border";
      tempDiv.style.cssText = `
      width: -webkit-fill-available;
      background: color-mix(in srgb, var(--electric-violet) 15%, transparent);
      border: 1px solid black;
      padding-inline: 1.75rem;
      padding-block: 1.375rem;
      border-radius: 1rem;
      `

      let urlElement = ''
      if (url && url != '') {
        urlElement = `<p>To verify this information, please check out: <a href="${url}" target="_blank">${url}</a></p>`
      }

      tempDiv.innerHTML = `
      ${text}
      ${urlElement}
      `;
    }
    this.conversation().nativeElement.insertAdjacentElement('afterend', tempDiv);  
  }
}
