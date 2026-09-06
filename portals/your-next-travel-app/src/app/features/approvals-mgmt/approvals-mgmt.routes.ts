import { Routes } from '@angular/router';

import { authGuard } from '../../core/guards/auth.guard';
import { RequestDetail } from '../plans-mgmt/request-detail/request-detail';

export const APPROVALS_MGMT_ROUTES: Routes = [
  { path: 'approvals/:threadId', canActivate: [authGuard], component: RequestDetail },
];
