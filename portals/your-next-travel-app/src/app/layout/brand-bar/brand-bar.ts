import { Component, OnInit } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-brand-bar',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './brand-bar.html',
})
export class BrandBar implements OnInit {
  constructor(readonly auth: AuthService) {}

  ngOnInit(): void {
    if (!this.auth.signedIn()) {
      this.auth.loadSession().subscribe();
    }
  }

  signout(): void {
    this.auth.signout();
  }
}
