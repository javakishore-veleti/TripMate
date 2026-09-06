import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Router } from '@angular/router';

import { LlmCatalog, LlmProviderOption, TravelResult } from '../../../core/models/api.models';
import { TravelService } from '../../../core/services/travel.service';
import { ApprovalPanel } from '../../approvals-mgmt/approval-panel/approval-panel';
import { DeletePlan } from '../delete-plan/delete-plan';
import { renderMarkdown, travelAnswer } from './markdown';

const AGENT_LABELS: Record<string, string> = {
  flight_agent: 'Flights',
  hotel_agent: 'Stays',
  weather_agent: 'Weather',
  budget_agent: 'Budget',
  itinerary_agent: 'Days',
};

@Component({
  selector: 'app-plan',
  imports: [FormsModule, ApprovalPanel, DeletePlan],
  templateUrl: './plan.html',
})
export class Plan implements OnInit {
  catalog = signal<LlmCatalog | null>(null);
  providerId = 'ollama';
  modelId = '';
  adapter = 'langgraph';
  ollamaUrl = 'http://127.0.0.1:11434';
  message = '';
  feedback = '';
  threadId: string | null = null;
  loading = signal(false);
  error = signal('');
  result = signal<TravelResult | null>(null);
  answerHtml = signal('');
  awaitingApproval = signal(false);
  prompt = '';

  constructor(
    private readonly travel: TravelService,
    private readonly router: Router,
  ) {}

  ngOnInit(): void {
    const savedPrompt = sessionStorage.getItem('ynt.planPrompt');
    if (savedPrompt) {
      this.message = savedPrompt;
      sessionStorage.removeItem('ynt.planPrompt');
    }
    this.travel.catalog().subscribe((catalog) => {
      this.catalog.set(catalog);
      this.providerId = catalog.default_provider;
      this.modelId = catalog.default_model;
      this.ollamaUrl = catalog.ollama_base_url || this.ollamaUrl;
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
      const models = catalog.providers.find((item) => item.id === 'ollama')?.models ?? [];
      if (models.length && !models.some((item) => item.id === this.modelId)) {
        this.modelId = models[0].id;
      }
    });
  }

  setPrompt(text: string): void {
    this.message = text;
  }

  agentLabel(name: string): string {
    return AGENT_LABELS[name] || name;
  }

  llmPayload(): Record<string, string> {
    return {
      agentic_adapter: this.adapter,
      llm_provider: this.providerId,
      llm_model: this.modelId,
      llm_base_url: this.isOllama() ? this.ollamaUrl : '',
    };
  }

  send(): void {
    this.error.set('');
    if (this.awaitingApproval()) {
      this.error.set('Approve or revise the current draft before starting another plan.');
      return;
    }
    if (!this.message.trim()) {
      this.error.set('Enter a travel request first.');
      return;
    }
    this.loading.set(true);
    this.travel
      .plan({
        message: this.message.trim(),
        thread_id: this.threadId,
        ...this.llmPayload(),
      })
      .subscribe({
        next: (response) => this.applyResponse(response, this.message.trim()),
        error: (err: HttpErrorResponse) => this.fail(err),
      });
  }

  submitApproval(approved: boolean): void {
    this.error.set('');
    if (!this.threadId || !this.awaitingApproval()) {
      this.error.set('There is no draft waiting for approval.');
      return;
    }
    if (!approved && !this.feedback.trim()) {
      this.error.set('Enter revision feedback before requesting changes.');
      return;
    }
    this.loading.set(true);
    this.travel
      .approve({
        thread_id: this.threadId,
        approved,
        feedback: this.feedback.trim(),
        ...this.llmPayload(),
      })
      .subscribe({
        next: (response) => this.applyResponse(response, this.prompt),
        error: (err: HttpErrorResponse) => this.fail(err),
      });
  }

  afterDeleted(): void {
    void this.router.navigateByUrl('/trip-journal');
  }

  copy(): void {
    const text = travelAnswer(this.result() ?? undefined, this.prompt) || this.prompt;
    if (text) {
      void navigator.clipboard.writeText(text);
    }
  }

  private applyResponse(response: { success: boolean; message?: string; thread_id?: string; result?: TravelResult }, fallbackPrompt: string): void {
    this.loading.set(false);
    if (!response.success) {
      this.error.set(response.message || 'Something went wrong.');
      return;
    }
    this.threadId = response.thread_id || this.threadId;
    const result = response.result || {};
    this.result.set(result);
    this.prompt = result.prompt || fallbackPrompt;
    this.answerHtml.set(renderMarkdown(travelAnswer(result, this.prompt)));
    this.awaitingApproval.set(Boolean(result.requires_approval));
    if (!result.requires_approval) {
      this.feedback = '';
    }
  }

  private fail(err: HttpErrorResponse): void {
    this.loading.set(false);
    this.error.set(err.error?.message || err.message || 'Request failed.');
  }
}
