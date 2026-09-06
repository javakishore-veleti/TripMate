import { Routes } from '@angular/router';

import { authGuard } from '../../core/guards/auth.guard';
import { Dashboard } from './dashboard/dashboard';
import { TripJournal } from './journal/journal';
import { Plan } from './plan/plan';
import { RequestDetail } from './request-detail/request-detail';

export const PLANS_MGMT_ROUTES: Routes = [
  { path: 'dashboard', canActivate: [authGuard], component: Dashboard },
  { path: 'trip-journal', canActivate: [authGuard], component: TripJournal },
  { path: 'plan', canActivate: [authGuard], component: Plan },
  { path: 'requests/:threadId', canActivate: [authGuard], component: RequestDetail },
];
