import { HttpErrorResponse } from '@angular/common/http';
import { Component, EventEmitter, Input, Output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { TravelService } from '../../../core/services/travel.service';

export const DELETE_TRAVEL_PLAN_PHRASE = 'delete this travel plan';

@Component({
  selector: 'app-delete-plan',
  imports: [FormsModule],
  templateUrl: './delete-plan.html',
})
export class DeletePlan {
  @Input({ required: true }) threadId = '';
  @Output() deleted = new EventEmitter<void>();

  readonly phrase = DELETE_TRAVEL_PLAN_PHRASE;
  step = signal(0);
  typed = '';
  deleting = signal(false);
  error = signal('');

  constructor(private readonly travel: TravelService) {}

  canDelete(): boolean {
    return this.typed.trim().toLowerCase() === this.phrase;
  }

  askAgain(): void {
    this.error.set('');
    this.typed = '';
    this.step.set(1);
  }

  cancel(): void {
    this.step.set(0);
    this.typed = '';
    this.error.set('');
  }

  confirm(): void {
    if (!this.threadId || !this.canDelete()) {
      return;
    }
    this.deleting.set(true);
    this.error.set('');
    this.travel.deleteRequest(this.threadId, this.typed.trim()).subscribe({
      next: () => {
        this.deleting.set(false);
        this.deleted.emit();
      },
      error: (err: HttpErrorResponse) => {
        this.deleting.set(false);
        this.error.set(err.error?.message || 'Could not delete this travel plan.');
      },
    });
  }
}
