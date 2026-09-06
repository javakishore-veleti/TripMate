import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import {
  EMPTY_PLACE,
  EMPTY_PREFERENCES,
  InterestPlace,
  LlmCatalog,
  LlmProviderOption,
} from '../../../core/models/api.models';
import { AuthService } from '../../../core/services/auth.service';
import { TravelService } from '../../../core/services/travel.service';

@Component({
  selector: 'app-account',
  imports: [FormsModule, RouterLink],
  templateUrl: './account.html',
})
export class Account implements OnInit {
  readonly slots = [0, 1, 2, 3, 4];
  places: InterestPlace[] = this.slots.map(() => ({ ...EMPTY_PLACE }));
  radius = 200;
  providerId = 'ollama';
  modelId = '';
  ollamaUrl = 'http://127.0.0.1:11434';
  catalog = signal<LlmCatalog | null>(null);
  modelOpen = signal(true);
  error = signal('');
  saved = signal('');
  saving = signal(false);
  deleting = signal(false);

  constructor(
    readonly auth: AuthService,
    private readonly router: Router,
    private readonly travel: TravelService,
  ) {}

  ngOnInit(): void {
    const prefs = this.auth.user()?.preferences ?? EMPTY_PREFERENCES;
    this.radius = prefs.event_radius_miles || 200;
    this.places = this.slots.map((index) => ({
      ...EMPTY_PLACE,
      ...(prefs.places?.[index] ?? {}),
    }));
    this.providerId = prefs.llm_provider || 'ollama';
    this.modelId = prefs.llm_model || '';
    this.ollamaUrl = prefs.llm_base_url || 'http://127.0.0.1:11434';
    this.travel.catalog(this.ollamaUrl).subscribe((catalog) => {
      this.catalog.set(catalog);
      this.providerId = prefs.llm_provider || catalog.default_provider || 'ollama';
      this.ollamaUrl = prefs.llm_base_url || catalog.ollama_base_url || this.ollamaUrl;
      this.modelId =
        prefs.llm_model ||
        (this.providerId === 'ollama' ? catalog.default_ollama_model : catalog.default_model) ||
        this.models()[0]?.id ||
        '';
      if (!this.models().some((item) => item.id === this.modelId)) {
        this.modelId = this.models()[0]?.id || '';
      }
    });
  }

  providers(): LlmProviderOption[] {
    return this.catalog()?.providers ?? [];
  }

  models() {
    return this.providers().find((item) => item.id === this.providerId)?.models ?? [];
  }

  isOllama(): boolean {
    return this.providerId === 'ollama';
  }

  onProviderChange(): void {
    const models = this.models();
    this.modelId = models[0]?.id || '';
    if (this.isOllama()) {
      this.ollamaUrl = this.catalog()?.ollama_base_url || this.ollamaUrl;
    }
  }

  onOllamaUrlChange(): void {
    if (!this.isOllama()) {
      return;
    }
    this.travel.catalog(this.ollamaUrl).subscribe((catalog) => {
      this.catalog.set(catalog);
      if (!this.models().some((item) => item.id === this.modelId)) {
        this.modelId = this.models()[0]?.id || catalog.default_ollama_model || '';
      }
    });
  }

  toggleModel(): void {
    this.modelOpen.set(!this.modelOpen());
  }

  saveProfile(): void {
    this.error.set('');
    this.saved.set('');
    this.saving.set(true);
    const current = this.auth.user()?.preferences ?? EMPTY_PREFERENCES;
    this.auth
      .savePreferences({
        ...EMPTY_PREFERENCES,
        ...current,
        places: this.places,
        event_radius_miles: Number(this.radius) || 200,
        llm_provider: this.providerId,
        llm_model: this.modelId,
        llm_base_url: this.isOllama() ? this.ollamaUrl : '',
      })
      .subscribe({
        next: (prefs) => {
          this.saving.set(false);
          this.radius = prefs.event_radius_miles || 200;
          this.places = this.slots.map((index) => ({
            ...EMPTY_PLACE,
            ...(prefs.places?.[index] ?? {}),
          }));
          this.providerId = prefs.llm_provider || 'ollama';
          this.modelId = prefs.llm_model || '';
          this.ollamaUrl = prefs.llm_base_url || this.ollamaUrl;
          this.saved.set('Saved. The dashboard will use these places and this model.');
        },
        error: (err: HttpErrorResponse) => {
          this.saving.set(false);
          this.error.set(err.error?.message || 'Could not save your account.');
        },
      });
  }

  deleteAccount(): void {
    if (
      !window.confirm(
        'Delete this account and every saved trip? This cannot be undone.',
      )
    ) {
      return;
    }
    this.error.set('');
    this.deleting.set(true);
    this.auth.deleteAccount().subscribe({
      next: () => {
        this.deleting.set(false);
        void this.router.navigateByUrl('/');
      },
      error: (err: HttpErrorResponse) => {
        this.deleting.set(false);
        this.error.set(err.error?.message || 'Could not delete the account.');
      },
    });
  }
}
