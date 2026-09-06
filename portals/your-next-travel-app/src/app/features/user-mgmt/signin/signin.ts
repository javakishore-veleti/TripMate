import { HttpErrorResponse } from '@angular/common/http';
import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-signin',
  imports: [FormsModule, RouterLink],
  templateUrl: './signin.html',
})
export class Signin {
  email = '';
  password = '';
  error = signal('');

  constructor(
    private readonly auth: AuthService,
    private readonly router: Router,
  ) {}

  submit(): void {
    this.error.set('');
    this.auth.signin(this.email, this.password).subscribe({
      next: (response) => {
        if (!response.success) {
          this.error.set(response.message || 'Could not sign in.');
          return;
        }
        void this.router.navigateByUrl('/dashboard');
      },
      error: (err: HttpErrorResponse) => {
        this.error.set(err.error?.message || 'Could not sign in.');
      },
    });
  }
}
