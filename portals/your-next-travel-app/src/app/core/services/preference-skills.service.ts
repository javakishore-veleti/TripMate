import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { PreferenceSkill, PreferenceSkillSummary } from '../models/api.models';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class PreferenceSkillsService {
  constructor(private readonly api: ApiService) {}

  list(): Observable<{ skills: PreferenceSkillSummary[]; maxSelected: number }> {
    return this.api
      .get<{ skills: PreferenceSkillSummary[]; max_selected: number }>('/preference-skills')
      .pipe(map((response) => ({ skills: response.skills ?? [], maxSelected: response.max_selected ?? 5 })));
  }

  get(id: string): Observable<PreferenceSkill> {
    return this.api
      .get<{ skill: PreferenceSkill }>(`/preference-skills/${id}`)
      .pipe(map((response) => response.skill));
  }

  create(payload: Partial<PreferenceSkill>): Observable<PreferenceSkill> {
    return this.api
      .post<{ skill: PreferenceSkill }>('/preference-skills', payload)
      .pipe(map((response) => response.skill));
  }

  update(id: string, payload: Partial<PreferenceSkill>): Observable<PreferenceSkill> {
    return this.api
      .put<{ skill: PreferenceSkill }>(`/preference-skills/${id}`, payload)
      .pipe(map((response) => response.skill));
  }

  remove(id: string): Observable<void> {
    return this.api.delete<void>(`/preference-skills/${id}`);
  }

  select(ids: string[]): Observable<string[]> {
    return this.api
      .put<{ ids: string[] }>('/preference-skills-selection', { ids })
      .pipe(map((response) => response.ids ?? []));
  }
}
