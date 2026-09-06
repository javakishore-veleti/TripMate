import { Component } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';
import { BrandBar } from '../brand-bar/brand-bar';

@Component({
  selector: 'app-shell',
  imports: [RouterOutlet, RouterLink, BrandBar],
  templateUrl: './shell.html',
})
export class Shell {
  readonly year = new Date().getFullYear();

  constructor(readonly auth: AuthService) {}
}
