import { HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { AreaEventsResponse, LlmCatalog, TravelRequestRecord, TravelResponse } from '../models/api.models';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class TravelService {
  constructor(private readonly api: ApiService) {}

  areaEvents(horizon: string): Observable<AreaEventsResponse> {
    return this.api.post<AreaEventsResponse>('/area-events', { horizon });
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
