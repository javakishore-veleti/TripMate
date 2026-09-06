import { Routes } from '@angular/router';

import { authGuard, guestGuard } from '../../core/guards/auth.guard';
import { Account } from './account/account';
import { AccountAbout } from './account/about/account-about';
import { AccountBriefModels } from './account/brief-models/account-brief-models';
import { AccountPlaces } from './account/places/account-places';
import { AccountPrivacy } from './account/privacy/account-privacy';
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
  {
    path: 'account',
    canActivate: [authGuard],
    component: Account,
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'about' },
      { path: 'about', component: AccountAbout },
      { path: 'places', component: AccountPlaces },
      { path: 'models', component: AccountBriefModels },
      { path: 'privacy', component: AccountPrivacy },
    ],
  },
];
