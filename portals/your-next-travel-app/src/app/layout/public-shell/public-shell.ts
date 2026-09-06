import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { BrandBar } from '../brand-bar/brand-bar';

@Component({
  selector: 'app-public-shell',
  imports: [BrandBar, RouterOutlet],
  template: `
    <div class="site">
      <app-brand-bar />
      <main class="app-container">
        <router-outlet />
      </main>
      <footer>Your Next Travel · Explore first. Sign in when you are ready to plan.</footer>
    </div>
  `,
})
export class PublicShell {}
