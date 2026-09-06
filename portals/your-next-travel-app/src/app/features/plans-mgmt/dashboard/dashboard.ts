import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { AreaEvent, InterestPlace, TravelRequestRecord } from '../../../core/models/api.models';
import { ModelHintCopy, isModelConfigMessage, modelHintFor, needsModelHint } from '../../../core/models/model-hint';
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
  placesSource = signal('');
  watchedPlaces = signal<string[]>([]);
  cached = signal(false);
  modelHint = signal<ModelHintCopy | null>(null);

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

  usingDefaults = computed(() => this.placesSource() === 'system_default');
  placeNotice = computed(() =>
    this.usingDefaults()
      ? `Showing built-in default places: ${(this.watchedPlaces().length ? this.watchedPlaces() : this.places().map((place) => [place.city, place.country].filter(Boolean).join(', '))).join(' · ')}.`
      : '',
  );

  ngOnInit(): void {
    this.travel.listRequests().subscribe({
      next: (records) => {
        this.records.set(records);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
    this.askEvents();
  }

  togglePlanning(): void {
    this.planningOpen.set(!this.planningOpen());
  }

  setHorizon(value: Horizon): void {
    this.horizon.set(value);
    this.askEvents();
  }

  askEvents(): void {
    this.asking.set(true);
    this.askError.set('');
    this.modelHint.set(null);
    this.travel.areaEvents(this.horizon()).subscribe({
      next: (response) => {
        this.asking.set(false);
        this.events.set(response.events ?? []);
        this.windowNote.set(response.window || '');
        this.placesSource.set(response.places_source || '');
        this.watchedPlaces.set(response.places ?? []);
        this.cached.set(Boolean(response.cached));
        if (needsModelHint(response)) {
          this.modelHint.set(modelHintFor('dashboard'));
          return;
        }
        if (!response.success) {
          this.askError.set(response.message || 'Could not load events around your places.');
        }
      },
      error: (err: HttpErrorResponse) => {
        this.asking.set(false);
        this.events.set([]);
        const message = err.error?.message || '';
        if (isModelConfigMessage(message)) {
          this.modelHint.set(modelHintFor('dashboard'));
          return;
        }
        this.askError.set(message || 'Could not load events around your places.');
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
