import { ApplicationConfig, importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideMarkdown } from 'ngx-markdown';

import { routes } from './app.routes';
import { initializeApp, provideFirebaseApp } from '@angular/fire/app';
import { getFunctions, provideFunctions } from '@angular/fire/functions';
import { USE_EMULATOR } from '@angular/fire/compat/functions'; // comment out to run in the cloud
import { provideHttpClient } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes), 
    provideHttpClient(),
    provideMarkdown(), 
    importProvidersFrom(provideFirebaseApp(
      () => initializeApp(
        {
          "projectId":"chatbot-demo-7e376",
          // "appId":"1:50747532747:web:6dd786ff83aa8e224a024e",
          // "storageBucket":"chatbot-demo-7e376.appspot.com",
          // "apiKey":"AIzaSyDwZPBV3umYu-Vte5ari2AZezshiwnKB5w",
          // "authDomain":"chatbot-demo-7e376.firebaseapp.com",
          // "messagingSenderId":"50747532747","measurementId":"G-VGESDCQQ5B"
          // appId: '',
          // storageBucket: '',
          // apiKey: '',
          // authDomain: '',
          // messagingSenderId: '',
        }
      ))
    ), 
    importProvidersFrom(provideFunctions(() => getFunctions())),
    { provide: USE_EMULATOR, useValue: ['localhost', 5001] } // comment out to run in the cloud
  ]
};
