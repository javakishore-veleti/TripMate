import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { AreaEvent, InterestPlace, TravelRequestRecord } from '../../../core/models/api.models';
import { ModelHintCopy, isModelConfigMessage, modelHintFor, needsModelHint } from '../../../core/models/model-hint';
import { AuthService } from '../../../core/services/auth.service';
import { TravelService } from '../../../core/services/travel.service';
import { photoForPlace, tripStory } from '../dashboard/trip-story';
import { calendarKey, tripDates } from '../dashboard/trip-when';

const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const HAPPEN_PAGE_SIZE = 5;

export interface CalendarDay {
  key: string;
  day: number;
  inMonth: boolean;
  isToday: boolean;
  eventCount: number;
  tripCount: number;
}

@Component({
  selector: 'app-trip-journal',
  imports: [RouterLink],
  templateUrl: './journal.html',
})
export class TripJournal implements OnInit {
  readonly weekdays = WEEKDAYS;
  records = signal<TravelRequestRecord[]>([]);
  loading = signal(true);
  asking = signal(false);
  askError = signal('');
  events = signal<AreaEvent[]>([]);
  classifyNote = signal('');
  skillNames = signal<string[]>([]);
  happenPage = signal(0);
  view = signal(new Date(new Date().getFullYear(), new Date().getMonth(), 1));
  placesSource = signal('');
  watchedPlaces = signal<string[]>([]);
  cached = signal(false);
  modelHint = signal<ModelHintCopy | null>(null);

  trips = computed(() => this.records().map((record) => ({ record, story: tripStory(record) })));
  places = computed<InterestPlace[]>(() => this.auth.user()?.preferences?.places ?? []);
  radius = computed(() => this.auth.user()?.preferences?.event_radius_miles || 200);
  monthLabel = computed(() =>
    this.view().toLocaleDateString(undefined, { month: 'long', year: 'numeric' }),
  );
  eventDays = computed(() => {
    const marks = new Map<string, number>();
    for (const event of this.events()) {
      for (const key of this.keysForEvent(event)) {
        marks.set(key, (marks.get(key) || 0) + 1);
      }
    }
    return marks;
  });
  tripDays = computed(() => {
    const marks = new Map<string, number>();
    const year = this.view().getFullYear();
    const month = this.view().getMonth();
    for (const item of this.trips()) {
      for (const date of tripDates(item.record)) {
        if (date.getFullYear() === year && date.getMonth() === month) {
          const key = calendarKey(date);
          marks.set(key, (marks.get(key) || 0) + 1);
        }
      }
    }
    return marks;
  });
  days = computed<CalendarDay[]>(() => this.buildDays());
  happenPageCount = computed(() => Math.max(1, Math.ceil(this.events().length / HAPPEN_PAGE_SIZE)));
  selectedEvents = computed(() => {
    const start = this.happenPage() * HAPPEN_PAGE_SIZE;
    return this.events().slice(start, start + HAPPEN_PAGE_SIZE);
  });
  canHappenPrev = computed(() => this.happenPage() > 0);
  canHappenNext = computed(() => this.happenPage() < this.happenPageCount() - 1);
  usingDefaults = computed(() => this.placesSource() === 'system_default');
  placeNotice = computed(() =>
    this.usingDefaults()
      ? `Showing built-in default places: ${this.watchedPlaces().join(' · ')}.`
      : '',
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
    this.loadHappenings();
  }

  shiftMonth(delta: number): void {
    const current = this.view();
    this.view.set(new Date(current.getFullYear(), current.getMonth() + delta, 1));
    this.happenPage.set(0);
    this.loadHappenings();
  }

  shiftHappenings(delta: number): void {
    const next = this.happenPage() + delta;
    if (next < 0 || next >= this.happenPageCount()) {
      return;
    }
    this.happenPage.set(next);
  }

  photoFor(event: AreaEvent): string {
    return photoForPlace(event.city || event.near, event.country);
  }

  eventWhere(event: AreaEvent): string {
    return [event.city, event.region, event.country].filter((part) => part).join(', ') || event.near;
  }

  private customerNote(raw: string): string {
    const text = raw.replace(/\s+/g, ' ').trim();
    if (
      !text ||
      /one short sentence|what to look for|return json|look for this month/i.test(text)
    ) {
      return 'Go find a spark near your cities.';
    }
    return text;
  }

  planEvent(event: AreaEvent): void {
    const where = this.eventWhere(event);
    const prompt = `Plan a trip around ${event.name}${where ? ` in ${where}` : ''}. ${event.blurb} Keep it within about ${this.radius()} miles of ${event.near || 'my saved places'}.`;
    sessionStorage.setItem('ynt.planPrompt', prompt);
    void this.router.navigateByUrl('/plan');
  }

  private loadHappenings(): void {
    this.asking.set(true);
    this.askError.set('');
    this.modelHint.set(null);
    const view = this.view();
    this.travel
      .journalHappenings({
        year: view.getFullYear(),
        month: view.getMonth() + 1,
      })
      .subscribe({
        next: (response) => {
          this.asking.set(false);
          this.events.set(response.events ?? []);
          this.happenPage.set(0);
          this.classifyNote.set(this.customerNote(response.classify_note || ''));
          this.skillNames.set(response.skill_names ?? []);
          this.placesSource.set(response.places_source || '');
          this.watchedPlaces.set(response.places ?? []);
          this.cached.set(Boolean(response.cached));
          if (needsModelHint(response)) {
            this.modelHint.set(modelHintFor('journal'));
            return;
          }
          if (!response.success) {
            this.askError.set(response.message || 'Could not load what is happening.');
          }
        },
        error: (err: HttpErrorResponse) => {
          this.asking.set(false);
          this.events.set([]);
          const message = err.error?.message || '';
          if (isModelConfigMessage(message)) {
            this.modelHint.set(modelHintFor('journal'));
            return;
          }
          this.askError.set(message || 'Could not load what is happening.');
        },
      });
  }

  private buildDays(): CalendarDay[] {
    const view = this.view();
    const year = view.getFullYear();
    const month = view.getMonth();
    const first = new Date(year, month, 1);
    const start = new Date(first);
    start.setDate(first.getDate() - first.getDay());
    const todayKey = this.keyFor(new Date());
    const eventMarks = this.eventDays();
    const tripMarks = this.tripDays();
    const cells: CalendarDay[] = [];
    for (let i = 0; i < 42; i += 1) {
      const date = new Date(start);
      date.setDate(start.getDate() + i);
      const key = this.keyFor(date);
      cells.push({
        key,
        day: date.getDate(),
        inMonth: date.getMonth() === month,
        isToday: key === todayKey,
        eventCount: eventMarks.get(key) || 0,
        tripCount: tripMarks.get(key) || 0,
      });
    }
    return cells;
  }

  private keyFor(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private keysForEvent(event: AreaEvent): string[] {
    if (event.day && /^\d{4}-\d{2}-\d{2}$/.test(event.day)) {
      return [event.day];
    }
    const view = this.view();
    const year = view.getFullYear();
    const month = view.getMonth();
    const matches = [...(event.when || '').matchAll(/\b(\d{1,2})\b/g)];
    const keys = new Set<string>();
    for (const match of matches) {
      const day = Number(match[1]);
      if (day >= 1 && day <= 31) {
        const date = new Date(year, month, day);
        if (date.getMonth() === month) {
          keys.add(this.keyFor(date));
        }
      }
    }
    return [...keys];
  }
}
