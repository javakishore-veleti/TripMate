import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

import { TokenStorage } from '../services/token.storage';

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const tokens = inject(TokenStorage);
  const router = inject(Router);
  const token = tokens.read();
  const headers = token ? req.headers.set('Authorization', `Bearer ${token}`) : req.headers;
  const request = req.clone({
    headers,
    withCredentials: true,
  });
  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      const authCall = request.url.includes('/api/v1/auth/');
      if (error.status === 401 && !authCall) {
        tokens.clear();
        void router.navigateByUrl('/signin');
      }
      return throwError(() => error);
    }),
  );
};
