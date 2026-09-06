import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnDestroy, OnInit, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Subscription, interval, startWith, switchMap } from 'rxjs';

import { Router, RouterLink } from '@angular/router';

import {
  LlmCatalog,
  LlmProviderOption,
  PlanDeskResponse,
  TravelResult,
  specialistLabel,
  tripAccepted,
  tripNotes,
  tripSpecialists,
} from '../../../core/models/api.models';
import { ModelHintCopy, isModelConfigMessage, modelHintFor, needsModelHint } from '../../../core/models/model-hint';
import { TravelService } from '../../../core/services/travel.service';
import { ApprovalPanel } from '../../approvals-mgmt/approval-panel/approval-panel';
import { DeletePlan } from '../delete-plan/delete-plan';
import { renderMarkdown, travelAnswer } from './markdown';

function clipLine(text: string, limit: number): string {
  const cleaned = text.replace(/\s+/g, ' ').trim();
  if (cleaned.length <= limit) {
    return cleaned;
  }
  const cut = cleaned.slice(0, limit - 1);
  const at = cut.lastIndexOf(' ');
  return `${cut.slice(0, at > 40 ? at : undefined)}…`;
}

@Component({
  selector: 'app-plan',
  imports: [FormsModule, RouterLink, ApprovalPanel, DeletePlan],
  templateUrl: './plan.html',
})
export class Plan implements OnInit, OnDestroy {
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
  saved = signal(false);
  saving = signal(false);
  cancelling = signal(false);
  prompt = '';
  desk = signal<PlanDeskResponse | null>(null);
  deskError = signal('');
  modelHint = signal<ModelHintCopy | null>(null);
  traceOpen = signal(false);
  traceLines = signal<string[]>([]);
  private traceSub: Subscription | null = null;

  traceText = computed(() => this.traceLines().join('\n'));
  usingDefaults = computed(() => this.desk()?.places_source === 'system_default');
  deskPlaces = computed(() => this.desk()?.places ?? []);
  deskNote = computed(() => clipLine(this.desk()?.note || '', 140));
  deskLeftover = computed(() => clipLine(this.desk()?.leftover || '', 80));

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
    this.travel.planDesk().subscribe({
      next: (response) => {
        this.desk.set(response);
        if (needsModelHint(response)) {
          this.modelHint.set(modelHintFor('plan'));
        }
      },
      error: (err: HttpErrorResponse) => {
        if (isModelConfigMessage(err.error?.message)) {
          this.modelHint.set(modelHintFor('plan'));
          return;
        }
        this.deskError.set(err.error?.message || 'Could not load the plan desk.');
      },
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

  ngOnDestroy(): void {
    this.stopTrace();
  }

  setPrompt(text: string): void {
    this.message = text;
  }

  toggleTrace(): void {
    this.traceOpen.set(!this.traceOpen());
  }

  private ensureThreadId(): string {
    if (!this.threadId) {
      const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
      this.threadId = `${stamp}-${Math.random().toString(36).slice(2, 12)}`;
    }
    return this.threadId;
  }

  private startTrace(): void {
    this.stopTrace();
    this.traceLines.set(['Started. Watching the pipeline…']);
    this.traceOpen.set(true);
    const threadId = this.ensureThreadId();
    let cursor = 0;
    this.traceSub = interval(400)
      .pipe(
        startWith(0),
        switchMap(() => this.travel.plannerTrace(threadId, cursor)),
      )
      .subscribe({
        next: (snapshot) => {
          if (snapshot.lines?.length) {
            this.traceLines.update((lines) => [...lines, ...snapshot.lines]);
          }
          cursor = snapshot.cursor ?? cursor;
          if (snapshot.done) {
            this.stopTrace();
          }
        },
      });
  }

  private stopTrace(): void {
    this.traceSub?.unsubscribe();
    this.traceSub = null;
  }

  specialists(result: TravelResult): string[] {
    return tripSpecialists(result);
  }

  accepted(result: TravelResult): boolean {
    return tripAccepted(result);
  }

  notes(result: TravelResult): string {
    return tripNotes(result);
  }

  agentLabel(name: string): string {
    return specialistLabel(name);
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
    this.startTrace();
    this.travel
      .plan({
        message: this.message.trim(),
        thread_id: this.ensureThreadId(),
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
    this.startTrace();
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

  cancelRun(): void {
    if (!this.threadId || this.cancelling()) {
      return;
    }
    this.cancelling.set(true);
    this.travel.cancelPlan(this.threadId).subscribe({
      error: () => this.cancelling.set(false),
    });
  }

  savePlan(): void {
    if (!this.threadId || this.saved() || this.saving()) {
      return;
    }
    this.saving.set(true);
    this.error.set('');
    this.travel.savePlan(this.threadId).subscribe({
      next: (response) => {
        this.saving.set(false);
        if (!response.success) {
          this.error.set(response.message || 'Could not save this plan.');
          return;
        }
        this.saved.set(true);
      },
      error: (err: HttpErrorResponse) => {
        this.saving.set(false);
        this.error.set(err.error?.message || err.message || 'Could not save this plan.');
      },
    });
  }

  private applyResponse(response: { success: boolean; message?: string; thread_id?: string; result?: TravelResult }, fallbackPrompt: string): void {
    this.loading.set(false);
    this.cancelling.set(false);
    if (!response.success) {
      if (isModelConfigMessage(response.message)) {
        this.modelHint.set(modelHintFor('plan'));
        this.error.set('');
        return;
      }
      this.error.set(response.message || 'Something went wrong.');
      return;
    }
    this.threadId = response.thread_id || this.threadId;
    const result = response.result || {};
    this.saved.set(false);
    if (result.cancelled) {
      this.result.set(null);
      this.answerHtml.set('');
      this.awaitingApproval.set(false);
      this.prompt = result.prompt || fallbackPrompt;
      return;
    }
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
    this.cancelling.set(false);
    this.stopTrace();
    if (isModelConfigMessage(err.error?.message || err.message)) {
      this.modelHint.set(modelHintFor('plan'));
      this.error.set('');
      return;
    }
    this.error.set(err.error?.message || err.message || 'Request failed.');
  }
}
