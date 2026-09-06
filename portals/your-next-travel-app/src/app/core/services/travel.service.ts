import { HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import {
  AccountDeskResponse,
  AreaEventsResponse,
  DefaultPlacesResponse,
  JournalHappeningsResponse,
  LlmCatalog,
  PacksLensResponse,
  PlanDeskResponse,
  TravelRequestRecord,
  TravelResponse,
} from '../models/api.models';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class TravelService {
  constructor(private readonly api: ApiService) {}

  areaEvents(horizon: string): Observable<AreaEventsResponse> {
    return this.api.post<AreaEventsResponse>('/area-events', { horizon });
  }

  defaultPlaces(): Observable<DefaultPlacesResponse> {
    return this.api.get<DefaultPlacesResponse>('/places/defaults');
  }

  planDesk(): Observable<PlanDeskResponse> {
    return this.api.post<PlanDeskResponse>('/plan/desk', {});
  }

  packsLens(): Observable<PacksLensResponse> {
    return this.api.post<PacksLensResponse>('/preference-skills/lens', {});
  }

  accountDesk(): Observable<AccountDeskResponse> {
    return this.api.post<AccountDeskResponse>('/account/desk', {});
  }

  journalHappenings(payload: {
    expand?: boolean;
    year?: number;
    month?: number;
  } = {}): Observable<JournalHappeningsResponse> {
    return this.api.post<JournalHappeningsResponse>('/journal/happenings', payload);
  }

  catalog(baseUrl = ''): Observable<LlmCatalog> {
    let params = new HttpParams();
    if (baseUrl.trim()) {
      params = params.set('base_url', baseUrl.trim());
    }
    return this.api.get<LlmCatalog>('/llm/catalog', params);
  }

  plan(payload: Record<string, unknown>): Observable<TravelResponse> {
    return this.api.post<TravelResponse>('/travel/planner', payload);
  }

  savePlan(threadId: string): Observable<{ success: boolean; message?: string; request?: TravelRequestRecord }> {
    return this.api.post('/travel/requests/save', { thread_id: threadId });
  }

  plannerTrace(threadId: string, cursor = 0): Observable<{ lines: string[]; cursor: number; done: boolean }> {
    return this.api.get(`/travel/planner/${threadId}/trace`, new HttpParams().set('cursor', String(cursor)));
  }

  cancelPlan(threadId: string): Observable<{ success: boolean; cancelled?: boolean }> {
    return this.api.post(`/travel/planner/${threadId}/cancel`, {});
  }

  approve(payload: Record<string, unknown>): Observable<TravelResponse> {
    return this.api.post<TravelResponse>('/travel/approve', payload);
  }

  listRequests(): Observable<TravelRequestRecord[]> {
    return this.api
      .get<{ requests: TravelRequestRecord[] }>('/travel/requests')
      .pipe(map((response) => response.requests ?? []));
  }

  getRequest(threadId: string): Observable<TravelRequestRecord> {
    return this.api
      .get<{ request: TravelRequestRecord }>(`/travel/requests/${threadId}`)
      .pipe(map((response) => response.request));
  }

  deleteRequest(threadId: string, confirmation: string): Observable<{ success: boolean; message?: string }> {
    return this.api.delete<{ success: boolean; message?: string }>(
      `/travel/requests/${threadId}`,
      { confirmation },
    );
  }
}
