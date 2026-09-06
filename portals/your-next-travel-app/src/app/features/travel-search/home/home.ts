import { Component, OnInit, computed, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { PreferenceSkillSummary } from '../../../core/models/api.models';
import { AuthService } from '../../../core/services/auth.service';
import { PreferenceSkillsService } from '../../../core/services/preference-skills.service';
import { DESTINATION_GROUPS, Destination } from '../destinations';

@Component({
  selector: 'app-home',
  imports: [RouterLink],
  templateUrl: './home.html',
})
export class Home implements OnInit {
  readonly groups = DESTINATION_GROUPS;
  openId = signal(this.groups[0]?.id ?? '');
  selected = signal<Destination | null>(null);
  packs = signal<PreferenceSkillSummary[]>([]);

  placeCount = computed(() =>
    this.groups.reduce((total, group) => total + group.places.length, 0),
  );

  firstName = computed(() => {
    const raw = this.auth.user()?.display_name || this.auth.user()?.email || '';
    return raw.split(/\s|@/)[0] || 'there';
  });

  constructor(
    readonly auth: AuthService,
    private readonly router: Router,
    private readonly skills: PreferenceSkillsService,
  ) {}

  ngOnInit(): void {
    if (!this.auth.signedIn()) {
      return;
    }
    this.skills.list().subscribe({
      next: (result) => this.packs.set(result.skills.filter((item) => item.selected).slice(0, 5)),
    });
  }

  isOpen(id: string): boolean {
    return this.openId() === id;
  }

  toggle(id: string): void {
    this.openId.set(this.openId() === id ? '' : id);
  }

  choose(place: Destination): void {
    this.selected.set(place);
  }

  planSelected(): void {
    const place = this.selected();
    if (!place) {
      return;
    }
    const prompt = `Plan a complete trip to ${place.name}, ${place.country}. Keep it practical and fun for mixed ages.`;
    sessionStorage.setItem('ynt.planPrompt', prompt);
    if (this.auth.signedIn()) {
      void this.router.navigateByUrl('/plan');
      return;
    }
    void this.router.navigateByUrl('/signin');
  }
}
