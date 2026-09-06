import { Routes } from '@angular/router';

import { Shell } from './layout/shell/shell';

export const routes: Routes = [
  {
    path: '',
    component: Shell,
    children: [
      {
        path: '',
        loadChildren: () =>
          import('./features/travel-search/travel-search.routes').then((m) => m.TRAVEL_SEARCH_ROUTES),
      },
      {
        path: '',
        loadChildren: () =>
          import('./features/user-mgmt/user-mgmt.routes').then((m) => m.USER_MGMT_ROUTES),
      },
      {
        path: '',
        loadChildren: () =>
          import('./features/plans-mgmt/plans-mgmt.routes').then((m) => m.PLANS_MGMT_ROUTES),
      },
      {
        path: '',
        loadChildren: () =>
          import('./features/approvals-mgmt/approvals-mgmt.routes').then((m) => m.APPROVALS_MGMT_ROUTES),
      },
      {
        path: '',
        loadChildren: () => import('./features/privacy/privacy.routes').then((m) => m.PRIVACY_ROUTES),
      },
    ],
  },
];
