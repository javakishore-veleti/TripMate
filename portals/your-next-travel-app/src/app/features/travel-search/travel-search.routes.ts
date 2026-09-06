import { Routes } from '@angular/router';

import { Home } from './home/home';

export const TRAVEL_SEARCH_ROUTES: Routes = [
  { path: '', pathMatch: 'full', component: Home },
];
