import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { AreaEvent, InterestPlace, TravelRequestRecord } from '../../../core/models/api.models';
import { AuthService } from '../../../core/services/auth.service';
import { TravelService } from '../../../core/services/travel.service';
import { Horizon, horizonLabel } from './season-moments';
import { photoForPlace, tripStory } from './trip-story';

const KIND_LABEL: Record<string, string> = {
  festival: 'Festival',
  culture: 'Culture',
  season: 'In season',
  community: 'Around town',
};

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink],
  templateUrl: './dashboard.html',
})
export class Dashboard implements OnInit {
  records = signal<TravelRequestRecord[]>([]);
  loading = signal(true);
  asking = signal(false);
  askError = signal('');
  events = signal<AreaEvent[]>([]);
  windowNote = signal('');
  horizon = signal<Horizon>('month');
  planningOpen = signal(true);

  trips = computed(() => this.records().map((record) => ({ record, story: tripStory(record) })));
  leftover = computed(() => {
    return (
      this.trips().find((item) => item.record.status === 'awaiting_approval') ??
      this.trips().find((item) => item.record.status !== 'completed') ??
      this.trips()[0] ??
      null
    );
  });

  firstName = computed(() => {
    const raw = this.auth.user()?.display_name || this.auth.user()?.email || '';
    return raw.split(/\s|@/)[0] || 'there';
  });

  places = computed<InterestPlace[]>(() => this.auth.user()?.preferences?.places ?? []);
  radius = computed(() => this.auth.user()?.preferences?.event_radius_miles || 200);
  placeLine = computed(() =>
    this.places()
      .map((place) => [place.city, place.region].filter((part) => part).join(', '))
      .filter((part) => part)
      .join(' · '),
  );
  windowLabel = computed(() => horizonLabel(this.horizon()));
  cards = computed(() =>
    this.events().map((event) => ({
      ...event,
      kindLabel: KIND_LABEL[event.kind] || 'Around town',
      image: photoForPlace(event.city || event.near, event.country),
    })),
  );

  constructor(
    readonly auth: AuthService,
    private readonly travel: TravelService,
    private readonly router: Router,
  ) {}

  ngOnInit(): void {
    this.travel.listRequests().subscribe({
      next: (records) => {
        this.records.set(records);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  togglePlanning(): void {
    this.planningOpen.set(!this.planningOpen());
  }

  setHorizon(value: Horizon): void {
    this.horizon.set(value);
    this.askEvents();
  }

  askEvents(): void {
    if (!this.places().length) {
      this.askError.set('Add cities on your account first.');
      this.events.set([]);
      return;
    }
    this.asking.set(true);
    this.askError.set('');
    this.travel.areaEvents(this.horizon()).subscribe({
      next: (response) => {
        this.asking.set(false);
        this.events.set(response.events ?? []);
        this.windowNote.set(response.window || '');
        if (!response.success) {
          this.askError.set(response.message || 'Could not load events around your places.');
        }
      },
      error: (err: HttpErrorResponse) => {
        this.asking.set(false);
        this.events.set([]);
        this.askError.set(err.error?.message || 'Could not load events around your places.');
      },
    });
  }

  eventWhere(event: AreaEvent): string {
    return [event.city, event.region, event.country].filter((part) => part).join(', ') || event.near;
  }

  planEvent(event: AreaEvent): void {
    const where = [event.city, event.region, event.country].filter((part) => part).join(', ');
    const prompt = `Plan a trip around ${event.name}${where ? ` in ${where}` : ''}. ${event.blurb} Keep it within about ${this.radius()} miles of ${event.near || this.placeLine()}.`;
    sessionStorage.setItem('ynt.planPrompt', prompt);
    void this.router.navigateByUrl('/plan');
  }
}
