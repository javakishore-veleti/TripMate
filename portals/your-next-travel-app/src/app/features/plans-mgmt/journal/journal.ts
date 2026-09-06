import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { AreaEvent, InterestPlace, TravelRequestRecord } from '../../../core/models/api.models';
import { AuthService } from '../../../core/services/auth.service';
import { TravelService } from '../../../core/services/travel.service';
import { photoForPlace, tripStory } from '../dashboard/trip-story';

const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

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
  expanding = signal(false);
  askError = signal('');
  events = signal<AreaEvent[]>([]);
  pack = signal('');
  food = signal('');
  ideas = signal('');
  classifyNote = signal('');
  skillNames = signal<string[]>([]);
  expanded = signal(false);
  view = signal(new Date(new Date().getFullYear(), new Date().getMonth(), 1));

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
      const raw = item.record.updated_at || item.record.created_at;
      if (!raw) {
        continue;
      }
      const date = new Date(raw);
      if (date.getFullYear() === year && date.getMonth() === month) {
        const key = this.keyFor(date);
        marks.set(key, (marks.get(key) || 0) + 1);
      }
    }
    return marks;
  });
  days = computed<CalendarDay[]>(() => this.buildDays());
  selectedEvents = computed(() => this.events().slice(0, this.expanded() ? 12 : 5));

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
    this.loadHappenings(false);
  }

  shiftMonth(delta: number): void {
    const current = this.view();
    this.view.set(new Date(current.getFullYear(), current.getMonth() + delta, 1));
    this.expanded.set(false);
    this.pack.set('');
    this.food.set('');
    this.ideas.set('');
    this.loadHappenings(false);
  }

  seeMore(): void {
    this.loadHappenings(true);
  }

  photoFor(event: AreaEvent): string {
    return photoForPlace(event.city || event.near, event.country);
  }

  eventWhere(event: AreaEvent): string {
    return [event.city, event.region, event.country].filter((part) => part).join(', ') || event.near;
  }

  planEvent(event: AreaEvent): void {
    const where = this.eventWhere(event);
    const prompt = `Plan a trip around ${event.name}${where ? ` in ${where}` : ''}. ${event.blurb} Keep it within about ${this.radius()} miles of ${event.near || 'my saved places'}.`;
    sessionStorage.setItem('ynt.planPrompt', prompt);
    void this.router.navigateByUrl('/plan');
  }

  private loadHappenings(expand: boolean): void {
    if (!this.places().length) {
      this.askError.set('Add cities on your account first.');
      this.events.set([]);
      return;
    }
    if (expand) {
      this.expanding.set(true);
    } else {
      this.asking.set(true);
    }
    this.askError.set('');
    const view = this.view();
    this.travel
      .journalHappenings({
        expand,
        year: view.getFullYear(),
        month: view.getMonth() + 1,
      })
      .subscribe({
        next: (response) => {
          this.asking.set(false);
          this.expanding.set(false);
          this.events.set(response.events ?? []);
          this.classifyNote.set(response.classify_note || '');
          this.skillNames.set(response.skill_names ?? []);
          this.pack.set(response.pack || '');
          this.food.set(response.food || '');
          this.ideas.set(response.ideas || '');
          this.expanded.set(Boolean(response.expanded));
          if (!response.success) {
            this.askError.set(response.message || 'Could not load what is happening.');
          }
        },
        error: (err: HttpErrorResponse) => {
          this.asking.set(false);
          this.expanding.set(false);
          this.events.set([]);
          this.askError.set(err.error?.message || 'Could not load what is happening.');
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
