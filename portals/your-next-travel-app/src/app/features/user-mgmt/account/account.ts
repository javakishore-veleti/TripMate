import { Component } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { NgbNav, NgbNavItem, NgbNavLink } from '@ng-bootstrap/ng-bootstrap';
import { filter } from 'rxjs';

@Component({
  selector: 'app-account',
  imports: [RouterLink, RouterLinkActive, RouterOutlet, NgbNav, NgbNavItem, NgbNavLink],
  templateUrl: './account.html',
})
export class Account {
  activeId = 'about';

  constructor(private readonly router: Router) {
    this.activeId = this.tabFromUrl(this.router.url);
    this.router.events
      .pipe(
        filter((event) => event instanceof NavigationEnd),
        takeUntilDestroyed(),
      )
      .subscribe((event) => {
        this.activeId = this.tabFromUrl(event.urlAfterRedirects);
      });
  }

  private tabFromUrl(url: string): string {
    if (url.includes('/account/places')) {
      return 'places';
    }
    if (url.includes('/account/models')) {
      return 'models';
    }
    if (url.includes('/account/privacy')) {
      return 'privacy';
    }
    return 'about';
  }
}
