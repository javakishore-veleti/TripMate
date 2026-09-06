import { Injectable, computed, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, map, of, tap } from 'rxjs';

import { AppUser, EMPTY_PREFERENCES, UserPreferences } from '../models/api.models';
import { ApiService } from './api.service';
import { TokenStorage } from './token.storage';

interface AuthResponse {
  success: boolean;
  user?: AppUser;
  access_token?: string;
  token_type?: string;
  message?: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly userState = signal<AppUser | null>(null);
  readonly user = this.userState.asReadonly();
  readonly signedIn = computed(() => this.userState() !== null);

  constructor(
    private readonly api: ApiService,
    private readonly tokens: TokenStorage,
    private readonly router: Router,
  ) {}

  loadSession(): Observable<AppUser | null> {
    return this.api.get<AuthResponse>('/auth/me').pipe(
      tap((response) => this.acceptAuth(response)),
      map((response) => response.user ?? null),
      catchError(() => {
        this.tokens.clear();
        this.userState.set(null);
        return of(null);
      }),
    );
  }

  signup(email: string, password: string, displayName: string): Observable<AuthResponse> {
    return this.api
      .post<AuthResponse>('/auth/signup', {
        email,
        password,
        display_name: displayName,
      })
      .pipe(tap((response) => this.acceptAuth(response)));
  }

  signin(email: string, password: string): Observable<AuthResponse> {
    return this.api
      .post<AuthResponse>('/auth/signin', { email, password })
      .pipe(tap((response) => this.acceptAuth(response)));
  }

  signout(): void {
    this.api.post('/auth/signout').subscribe({
      complete: () => this.clearAndGoHome(),
      error: () => this.clearAndGoHome(),
    });
  }

  deleteAccount(): Observable<{ success: boolean; message?: string }> {
    return this.api.delete<{ success: boolean; message?: string }>('/auth/account').pipe(
      tap(() => {
        this.tokens.clear();
        this.userState.set(null);
      }),
    );
  }

  savePreferences(preferences: UserPreferences): Observable<UserPreferences> {
    return this.api
      .put<{ success: boolean; preferences: UserPreferences }>('/preferences', preferences)
      .pipe(
        map((response) => response.preferences ?? EMPTY_PREFERENCES),
        tap((saved) => {
          const current = this.userState();
          if (current) {
            this.userState.set({ ...current, preferences: saved });
          }
        }),
      );
  }

  private acceptAuth(response: AuthResponse): void {
    if (response.success && response.access_token) {
      this.tokens.write(response.access_token);
    }
    this.userState.set(response.user ?? null);
  }

  private clearAndGoHome(): void {
    this.tokens.clear();
    this.userState.set(null);
    void this.router.navigateByUrl('/');
  }
}
