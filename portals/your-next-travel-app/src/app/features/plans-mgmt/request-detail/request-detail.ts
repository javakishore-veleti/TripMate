import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import {
  TravelRequestRecord,
  TravelResult,
  specialistLabel,
  tripAccepted,
  tripNotes,
  tripSpecialists,
} from '../../../core/models/api.models';
import { TravelService } from '../../../core/services/travel.service';
import { ApprovalPanel } from '../../approvals-mgmt/approval-panel/approval-panel';
import { DeletePlan } from '../delete-plan/delete-plan';
import { renderMarkdown, travelAnswer } from '../plan/markdown';

@Component({
  selector: 'app-request-detail',
  imports: [FormsModule, ApprovalPanel, DeletePlan],
  templateUrl: './request-detail.html',
})
export class RequestDetail implements OnInit {
  record = signal<TravelRequestRecord | null>(null);
  answerHtml = signal('');
  feedback = '';
  loading = signal(false);
  error = signal('');
  awaitingApproval = signal(false);

  constructor(
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly travel: TravelService,
  ) {}

  ngOnInit(): void {
    const threadId = this.route.snapshot.paramMap.get('threadId') || '';
    this.travel.getRequest(threadId).subscribe({
      next: (record) => this.show(record),
      error: () => this.error.set('Request not found.'),
    });
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

  specialistName(name: string): string {
    return specialistLabel(name);
  }

  tokenLine(): string {
    const usage = this.record()?.usage;
    if (!usage) {
      return '';
    }
    const cost = usage.cost_usd != null ? ` · $${Number(usage.cost_usd).toFixed(4)}` : '';
    return `${usage.llm_calls ?? 0} LLM calls · ${usage.input_tokens ?? 0} in / ${usage.output_tokens ?? 0} out${cost}`;
  }

  submitApproval(approved: boolean): void {
    const record = this.record();
    if (!record) {
      return;
    }
    if (!approved && !this.feedback.trim()) {
      this.error.set('Enter revision feedback before requesting changes.');
      return;
    }
    this.loading.set(true);
    this.travel
      .approve({
        thread_id: record.thread_id,
        approved,
        feedback: this.feedback.trim(),
        agentic_adapter: record.agentic_adapter,
        llm_provider: record.llm_provider,
        llm_model: record.llm_model,
        llm_base_url: record.result?.llm_base_url || '',
      })
      .subscribe({
        next: (response) => {
          this.loading.set(false);
          if (!response.success) {
            this.error.set(response.message || 'Could not resume the plan.');
            return;
          }
          this.show({
            ...record,
            status: response.result?.requires_approval ? 'awaiting_approval' : 'completed',
            result: response.result || record.result,
            hitl: {
              ...record.hitl,
              approved,
              feedback: this.feedback,
              requires_approval: Boolean(response.result?.requires_approval),
            },
          });
        },
        error: (err: HttpErrorResponse) => {
          this.loading.set(false);
          this.error.set(err.error?.message || 'Could not resume the plan.');
        },
      });
  }

  afterDeleted(): void {
    void this.router.navigateByUrl('/trip-journal');
  }

  copy(): void {
    const record = this.record();
    const text = travelAnswer(record?.result, record?.prompt) || record?.prompt || '';
    if (text) {
      void navigator.clipboard.writeText(text);
    }
  }

  private show(record: TravelRequestRecord): void {
    this.record.set(record);
    const result: TravelResult = record.result || {};
    this.answerHtml.set(renderMarkdown(travelAnswer(result, record.prompt)));
    this.awaitingApproval.set(record.status === 'awaiting_approval' || Boolean(result.requires_approval));
  }
}
