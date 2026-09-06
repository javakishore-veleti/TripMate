import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map } from 'rxjs';

import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.signedIn()) {
    return true;
  }
  return auth.loadSession().pipe(map((user) => (user ? true : router.parseUrl('/signin'))));
};

export const guestGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.signedIn()) {
    return router.parseUrl('/dashboard');
  }
    return auth.loadSession().pipe(map((user) => (user ? router.parseUrl('/dashboard') : true)));
};
