import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-approval-panel',
  imports: [FormsModule],
  templateUrl: './approval-panel.html',
})
export class ApprovalPanel {
  @Input() message = '';
  @Input() loading = false;
  @Input() feedback = '';
  @Output() feedbackChange = new EventEmitter<string>();
  @Output() decided = new EventEmitter<boolean>();

  onFeedback(value: string): void {
    this.feedback = value;
    this.feedbackChange.emit(value);
  }

  submit(approved: boolean): void {
    this.decided.emit(approved);
  }
}
