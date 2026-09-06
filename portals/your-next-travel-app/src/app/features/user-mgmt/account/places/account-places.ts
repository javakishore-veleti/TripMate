import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { EMPTY_PLACE, EMPTY_PREFERENCES, InterestPlace } from '../../../../core/models/api.models';
import { AuthService } from '../../../../core/services/auth.service';
import { TravelService } from '../../../../core/services/travel.service';

@Component({
  selector: 'app-account-places',
  imports: [FormsModule],
  templateUrl: './account-places.html',
})
export class AccountPlaces implements OnInit {
  readonly slots = [0, 1, 2, 3, 4];
  places: InterestPlace[] = this.slots.map(() => ({ ...EMPTY_PLACE }));
  radius = 200;
  error = signal('');
  saved = signal('');
  saving = signal(false);
  defaultLabels = signal<string[]>([]);

  constructor(
    private readonly auth: AuthService,
    private readonly travel: TravelService,
  ) {}

  usingDefaults(): boolean {
    return !this.places.some((place) => place.city.trim());
  }

  ngOnInit(): void {
    const prefs = this.auth.user()?.preferences ?? EMPTY_PREFERENCES;
    this.radius = prefs.event_radius_miles || 200;
    this.places = this.slots.map((index) => ({
      ...EMPTY_PLACE,
      ...(prefs.places?.[index] ?? {}),
    }));
    if (this.usingDefaults()) {
      this.travel.defaultPlaces().subscribe({
        next: (response) =>
          this.defaultLabels.set(
            (response.places ?? []).map((place) =>
              [place.city, place.region, place.country].filter((part) => part).join(', '),
            ),
          ),
      });
    }
  }

  savePlaces(): void {
    this.error.set('');
    this.saved.set('');
    this.saving.set(true);
    const current = this.auth.user()?.preferences ?? EMPTY_PREFERENCES;
    this.auth
      .savePreferences({
        ...EMPTY_PREFERENCES,
        ...current,
        places: this.places.map((place) => ({
          city: place.city,
          region: place.region,
          country: place.country,
          postal_code: '',
        })),
        event_radius_miles: Number(this.radius) || 200,
      })
      .subscribe({
        next: (prefs) => {
          this.saving.set(false);
          this.radius = prefs.event_radius_miles || 200;
          this.places = this.slots.map((index) => ({
            ...EMPTY_PLACE,
            ...(prefs.places?.[index] ?? {}),
          }));
          this.saved.set('Places saved.');
        },
        error: (err: HttpErrorResponse) => {
          this.saving.set(false);
          this.error.set(err.error?.message || 'Could not save places.');
        },
      });
  }
}
