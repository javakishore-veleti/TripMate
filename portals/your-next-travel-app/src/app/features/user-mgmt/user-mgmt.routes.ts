import { Routes } from '@angular/router';

import { authGuard, guestGuard } from '../../core/guards/auth.guard';
import { Account } from './account/account';
import { PreferenceForm } from './preferences/preference-form';
import { Preferences } from './preferences/preferences';
import { Signin } from './signin/signin';
import { Signup } from './signup/signup';

export const USER_MGMT_ROUTES: Routes = [
  { path: 'signin', canActivate: [guestGuard], component: Signin },
  { path: 'signup', canActivate: [guestGuard], component: Signup },
  { path: 'preferences/new', canActivate: [authGuard], component: PreferenceForm },
  { path: 'preferences/:id', canActivate: [authGuard], component: PreferenceForm },
  { path: 'preferences', canActivate: [authGuard], component: Preferences },
  { path: 'account', canActivate: [authGuard], component: Account },
];
