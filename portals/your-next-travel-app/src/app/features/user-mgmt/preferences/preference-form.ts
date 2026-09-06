import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { EMPTY_SKILL_SECTIONS, PreferenceSkillSections } from '../../../core/models/api.models';
import { PreferenceSkillsService } from '../../../core/services/preference-skills.service';

@Component({
  selector: 'app-preference-form',
  imports: [FormsModule, RouterLink],
  templateUrl: './preference-form.html',
})
export class PreferenceForm implements OnInit {
  readonly sections: { key: keyof PreferenceSkillSections; title: string; hint: string }[] = [
    { key: 'who', title: 'Who this is for', hint: 'Solo, couple, kids, mixed ages…' },
    { key: 'home', title: 'Home base', hint: 'City and country you usually leave from.' },
    { key: 'budget', title: 'Budget', hint: 'Typical spend and currency.' },
    { key: 'pace', title: 'Pace and style', hint: 'Relaxed, packed, mid-range, luxury…' },
    { key: 'interests', title: 'Interests', hint: 'Food, museums, hiking, beaches…' },
    { key: 'avoid', title: 'Avoid', hint: 'Things this pack should skip.' },
    { key: 'notes', title: 'Notes', hint: 'Anything else the planner should honor.' },
  ];

  id = '';
  name = '';
  description = '';
  form: PreferenceSkillSections = { ...EMPTY_SKILL_SECTIONS };
  openKey = signal<keyof PreferenceSkillSections>('who');
  error = signal('');
  saving = signal(false);

  constructor(
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly skillsApi: PreferenceSkillsService,
  ) {}

  ngOnInit(): void {
    this.id = this.route.snapshot.paramMap.get('id') || '';
    if (!this.id) {
      return;
    }
    this.skillsApi.get(this.id).subscribe({
      next: (skill) => {
        this.name = skill.name;
        this.description = skill.description;
        this.form = { ...EMPTY_SKILL_SECTIONS, ...skill.sections };
      },
      error: () => this.error.set('Preference not found.'),
    });
  }

  isOpen(key: keyof PreferenceSkillSections): boolean {
    return this.openKey() === key;
  }

  toggle(key: keyof PreferenceSkillSections): void {
    this.openKey.set(this.openKey() === key ? 'who' : key);
  }

  submit(): void {
    this.error.set('');
    if (!this.name.trim()) {
      this.error.set('Give this preference a name.');
      return;
    }
    this.saving.set(true);
    const payload = {
      name: this.name.trim(),
      description: this.description.trim(),
      sections: this.form,
    };
    const request = this.id
      ? this.skillsApi.update(this.id, payload)
      : this.skillsApi.create(payload);
    request.subscribe({
      next: () => {
        this.saving.set(false);
        void this.router.navigateByUrl('/preferences');
      },
      error: (err: HttpErrorResponse) => {
        this.saving.set(false);
        this.error.set(err.error?.message || 'Could not save the preference file.');
      },
    });
  }
}
