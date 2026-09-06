import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  EMPTY_LLM_JOB,
  EMPTY_PREFERENCES,
  LlmCatalog,
  LlmJobChoice,
  LlmProviderOption,
} from '../../../../core/models/api.models';
import { AuthService } from '../../../../core/services/auth.service';
import { TravelService } from '../../../../core/services/travel.service';

export interface BriefJob {
  id: 'classify' | 'reason' | 'deep';
  title: string;
  blurb: string;
}

@Component({
  selector: 'app-account-brief-models',
  imports: [FormsModule],
  templateUrl: './account-brief-models.html',
})
export class AccountBriefModels implements OnInit {
  readonly briefJobs: BriefJob[] = [
    {
      id: 'classify',
      title: 'What kind of month?',
      blurb: 'Sort festivals, food, outdoors, or family before we look around.',
    },
    {
      id: 'reason',
      title: 'What’s on nearby?',
      blurb: 'Name public events near your cities this week or month.',
    },
    {
      id: 'deep',
      title: 'Think the trip through',
      blurb: 'What to pack, what to eat, and what kind of short trip fits.',
    },
  ];
  providerId = 'ollama';
  modelId = '';
  ollamaUrl = 'http://127.0.0.1:11434';
  jobs: Record<BriefJob['id'], LlmJobChoice> = {
    classify: { ...EMPTY_LLM_JOB },
    reason: { ...EMPTY_LLM_JOB },
    deep: { ...EMPTY_LLM_JOB },
  };
  catalog = signal<LlmCatalog | null>(null);
  error = signal('');
  saved = signal('');
  saving = signal(false);

  constructor(
    private readonly auth: AuthService,
    private readonly travel: TravelService,
  ) {}

  ngOnInit(): void {
    const prefs = this.auth.user()?.preferences ?? EMPTY_PREFERENCES;
    this.providerId = prefs.llm_provider || 'ollama';
    this.modelId = prefs.llm_model || '';
    this.ollamaUrl = prefs.llm_base_url || 'http://127.0.0.1:11434';
    this.jobs = {
      classify: { ...EMPTY_LLM_JOB, ...(prefs.llm_jobs?.classify ?? {}) },
      reason: { ...EMPTY_LLM_JOB, ...(prefs.llm_jobs?.reason ?? {}) },
      deep: { ...EMPTY_LLM_JOB, ...(prefs.llm_jobs?.deep ?? {}) },
    };
    this.travel.catalog(this.ollamaUrl).subscribe((catalog) => {
      this.catalog.set(catalog);
      this.providerId = prefs.llm_provider || catalog.default_provider || 'ollama';
      this.ollamaUrl = prefs.llm_base_url || catalog.ollama_base_url || this.ollamaUrl;
      this.modelId =
        prefs.llm_model ||
        catalog.default_ollama_model ||
        catalog.default_model ||
        this.modelsFor('ollama')[0]?.id ||
        '';
      if (this.providerId === 'ollama' && !this.modelsFor('ollama').some((item) => item.id === this.modelId)) {
        this.modelId = catalog.default_ollama_model || this.modelsFor('ollama')[0]?.id || '';
      }
    });
  }

  providers(): LlmProviderOption[] {
    return this.catalog()?.providers ?? [];
  }

  modelsFor(providerId: string) {
    return this.providers().find((item) => item.id === providerId)?.models ?? [];
  }

  models() {
    return this.modelsFor(this.providerId);
  }

  usesOllama(): boolean {
    return (
      this.providerId === 'ollama' ||
      this.jobs.classify.provider === 'ollama' ||
      this.jobs.reason.provider === 'ollama' ||
      this.jobs.deep.provider === 'ollama'
    );
  }

  onProviderChange(): void {
    const models = this.models();
    this.modelId = models[0]?.id || '';
    if (this.providerId === 'ollama') {
      this.ollamaUrl = this.catalog()?.ollama_base_url || this.ollamaUrl;
    }
  }

  onJobProviderChange(jobId: BriefJob['id']): void {
    const models = this.modelsFor(this.jobs[jobId].provider);
    if (this.jobs[jobId].model && !models.some((item) => item.id === this.jobs[jobId].model)) {
      this.jobs[jobId].model = '';
    }
  }

  onOllamaUrlChange(): void {
    this.travel.catalog(this.ollamaUrl).subscribe((catalog) => {
      this.catalog.set(catalog);
      if (this.providerId === 'ollama' && !this.models().some((item) => item.id === this.modelId)) {
        this.modelId = catalog.default_ollama_model || this.models()[0]?.id || '';
      }
    });
  }

  saveModels(): void {
    this.error.set('');
    this.saved.set('');
    this.saving.set(true);
    const current = this.auth.user()?.preferences ?? EMPTY_PREFERENCES;
    this.auth
      .savePreferences({
        ...EMPTY_PREFERENCES,
        ...current,
        llm_provider: this.providerId || 'ollama',
        llm_model: this.modelId,
        llm_base_url: this.usesOllama() ? this.ollamaUrl : '',
        llm_jobs: {
          classify: { ...this.jobs.classify },
          reason: { ...this.jobs.reason },
          deep: { ...this.jobs.deep },
        },
      })
      .subscribe({
        next: (prefs) => {
          this.saving.set(false);
          this.providerId = prefs.llm_provider || 'ollama';
          this.modelId = prefs.llm_model || '';
          this.ollamaUrl = prefs.llm_base_url || this.ollamaUrl;
          this.jobs = {
            classify: { ...EMPTY_LLM_JOB, ...(prefs.llm_jobs?.classify ?? {}) },
            reason: { ...EMPTY_LLM_JOB, ...(prefs.llm_jobs?.reason ?? {}) },
            deep: { ...EMPTY_LLM_JOB, ...(prefs.llm_jobs?.deep ?? {}) },
          };
          this.saved.set('Models saved. Trip journal and Plan a trip will use them.');
        },
        error: (err: HttpErrorResponse) => {
          this.saving.set(false);
          this.error.set(err.error?.message || 'Could not save models.');
        },
      });
  }
}
