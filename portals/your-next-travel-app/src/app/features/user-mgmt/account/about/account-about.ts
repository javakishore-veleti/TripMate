import { Component } from '@angular/core';

import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-account-about',
  templateUrl: './account-about.html',
})
export class AccountAbout {
  constructor(readonly auth: AuthService) {}

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
