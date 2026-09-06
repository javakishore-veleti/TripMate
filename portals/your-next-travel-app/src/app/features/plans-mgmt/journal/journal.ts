import { Component, OnInit, computed, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { TravelRequestRecord } from '../../../core/models/api.models';
import { TravelService } from '../../../core/services/travel.service';
import { tripStory } from '../dashboard/trip-story';

@Component({
  selector: 'app-trip-journal',
  imports: [RouterLink],
  templateUrl: './journal.html',
})
export class TripJournal implements OnInit {
  records = signal<TravelRequestRecord[]>([]);
  loading = signal(true);
  open = signal(true);

  trips = computed(() => this.records().map((record) => ({ record, story: tripStory(record) })));

  constructor(private readonly travel: TravelService) {}

  ngOnInit(): void {
    this.travel.listRequests().subscribe({
      next: (records) => {
        this.records.set(records);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  toggle(): void {
    this.open.set(!this.open());
  }
}
