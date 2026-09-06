import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { AccountDeskResponse } from '../../../../core/models/api.models';
import { ModelHintCopy, isModelConfigMessage, modelHintFor, needsModelHint } from '../../../../core/models/model-hint';
import { AuthService } from '../../../../core/services/auth.service';
import { TravelService } from '../../../../core/services/travel.service';

@Component({
  selector: 'app-account-about',
  imports: [RouterLink],
  templateUrl: './account-about.html',
})
export class AccountAbout implements OnInit {
  desk = signal<AccountDeskResponse | null>(null);
  modelHint = signal<ModelHintCopy | null>(null);

  constructor(
    readonly auth: AuthService,
    private readonly travel: TravelService,
  ) {}

  ngOnInit(): void {
    this.travel.accountDesk().subscribe({
      next: (response) => {
        this.desk.set(response);
        if (needsModelHint(response)) {
          this.modelHint.set(modelHintFor('account'));
        }
      },
      error: (err: HttpErrorResponse) => {
        if (isModelConfigMessage(err.error?.message)) {
          this.modelHint.set(modelHintFor('account'));
        }
      },
    });
  }

  email(): string {
    return this.auth.user()?.email || '';
  }

  latestSignin(): string {
    const raw = this.auth.user()?.last_signin_at;
    if (!raw) {
      return 'Not recorded yet';
    }
    const when = new Date(raw);
    if (Number.isNaN(when.getTime())) {
      return raw;
    }
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(when);
  }
}
