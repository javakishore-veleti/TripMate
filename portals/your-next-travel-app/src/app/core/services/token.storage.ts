import { Injectable } from '@angular/core';

const TOKEN_KEY = 'ynt.access_token';

@Injectable({ providedIn: 'root' })
export class TokenStorage {
  read(): string | null {
    return sessionStorage.getItem(TOKEN_KEY);
  }

  write(token: string | null | undefined): void {
    if (token) {
      sessionStorage.setItem(TOKEN_KEY, token);
      return;
    }
    sessionStorage.removeItem(TOKEN_KEY);
  }

  clear(): void {
    sessionStorage.removeItem(TOKEN_KEY);
  }
}
