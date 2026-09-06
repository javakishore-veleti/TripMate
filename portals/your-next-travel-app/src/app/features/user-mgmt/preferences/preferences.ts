import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { PacksLensResponse, PreferenceSkillSummary } from '../../../core/models/api.models';
import { ModelHintCopy, isModelConfigMessage, modelHintFor, needsModelHint } from '../../../core/models/model-hint';
import { PreferenceSkillsService } from '../../../core/services/preference-skills.service';
import { TravelService } from '../../../core/services/travel.service';

@Component({
  selector: 'app-preferences',
  imports: [RouterLink],
  templateUrl: './preferences.html',
})
export class Preferences implements OnInit {
  skills = signal<PreferenceSkillSummary[]>([]);
  maxSelected = 5;
  loading = signal(true);
  error = signal('');
  saved = signal('');
  lens = signal<PacksLensResponse | null>(null);
  modelHint = signal<ModelHintCopy | null>(null);

  constructor(
    private readonly skillsApi: PreferenceSkillsService,
    private readonly travel: TravelService,
  ) {}

  ngOnInit(): void {
    this.reload();
    this.travel.packsLens().subscribe({
      next: (response) => {
        this.lens.set(response);
        if (needsModelHint(response)) {
          this.modelHint.set(modelHintFor('preferences'));
        }
      },
      error: (err: HttpErrorResponse) => {
        if (isModelConfigMessage(err.error?.message)) {
          this.modelHint.set(modelHintFor('preferences'));
        }
      },
    });
  }

  selectedCount(): number {
    return this.skills().filter((item) => item.selected).length;
  }

  toggle(skill: PreferenceSkillSummary): void {
    const next = this.skills().map((item) =>
      item.id === skill.id ? { ...item, selected: !item.selected } : item,
    );
    const selected = next.filter((item) => item.selected).map((item) => item.id);
    if (selected.length > this.maxSelected) {
      this.error.set(`Use at most ${this.maxSelected} preference packs on a search or plan.`);
      return;
    }
    this.error.set('');
    this.skillsApi.select(selected).subscribe({
      next: () => {
        this.skills.set(next);
        this.saved.set('Selection saved. New plans will use these packs.');
      },
      error: (err: HttpErrorResponse) => {
        this.error.set(err.error?.message || 'Could not save the selection.');
      },
    });
  }

  remove(skill: PreferenceSkillSummary): void {
    const label = skill.customized
      ? `Reset “${skill.name}” back to the built-in pack?`
      : `Delete “${skill.name}”? This removes its SKILL.md file.`;
    if (!window.confirm(label)) {
      return;
    }
    this.skillsApi.remove(skill.id).subscribe({
      next: () => this.reload(),
      error: () => this.error.set('Could not delete that preference.'),
    });
  }

  private reload(): void {
    this.loading.set(true);
    this.skillsApi.list().subscribe({
      next: (result) => {
        this.skills.set(result.skills);
        this.maxSelected = result.maxSelected;
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Could not load preferences.');
      },
    });
  }
}
