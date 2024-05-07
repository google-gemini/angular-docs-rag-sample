import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
@Injectable({
  providedIn: 'root'
})
export class GenerativeLanguageService {
  private generateAqaURL = 'http://127.0.0.1:5001/chatbot-demo-7e376/us-central1/generate_aqa_answer'
  
  constructor(private http: HttpClient) { }

  async getAQAAnswer(prompt: string): Promise<Observable<AQAResponse>> {
    return this.http.get<AQAResponse>(`${this.generateAqaURL}?text=${prompt}`)
  }
}
export interface AQAResponse {
  answer: string;
  probability: Number;
  url: string,
  questions?: string[]
}

export interface GeminiResponse {
  answer: string;
  questions?: string[]
}
