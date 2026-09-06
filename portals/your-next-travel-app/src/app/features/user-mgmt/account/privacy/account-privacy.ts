import { HttpErrorResponse } from '@angular/common/http';
import { Component, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-account-privacy',
  imports: [RouterLink],
  templateUrl: './account-privacy.html',
})
export class AccountPrivacy {
  error = signal('');
  deleting = signal(false);

  constructor(
    private readonly auth: AuthService,
    private readonly router: Router,
  ) {}

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
