export interface AppUser {
  id: string;
  email: string;
  display_name: string;
  last_signin_at?: string | null;
  preferences: UserPreferences;
}

export interface InterestPlace {
  city: string;
  region: string;
  postal_code: string;
  country: string;
}

export interface UserPreferences {
  home_city: string;
  home_country: string;
  typical_budget: string;
  currency: string;
  travel_style: string;
  pace: string;
  interests: string[];
  companions: string;
  avoid: string;
  notes: string;
  places: InterestPlace[];
  event_radius_miles: number;
  llm_provider: string;
  llm_model: string;
  llm_base_url: string;
  llm_jobs: {
    classify: LlmJobChoice;
    reason: LlmJobChoice;
    deep: LlmJobChoice;
  };
}

export interface LlmJobChoice {
  provider: string;
  model: string;
}

export interface AreaEvent {
  name: string;
  kind: string;
  city: string;
  region: string;
  country: string;
  when: string;
  day?: string;
  miles_from: number;
  near: string;
  blurb: string;
}

export interface PipelinePlacesMeta {
  places?: string[];
  places_source?: 'user' | 'system_default' | string;
  cached?: boolean;
  needs_model?: boolean;
}

export interface JournalHappeningsResponse extends PipelinePlacesMeta {
  success: boolean;
  message?: string;
  expanded?: boolean;
  year?: number;
  month?: number;
  window?: string;
  radius_miles?: number;
  skill_names?: string[];
  lens?: string;
  classify_note?: string;
  events?: AreaEvent[];
  pack?: string;
  food?: string;
  ideas?: string;
}

export interface AreaEventsResponse extends PipelinePlacesMeta {
  success: boolean;
  message?: string;
  horizon?: string;
  window?: string;
  radius_miles?: number;
  events?: AreaEvent[];
}

export interface PlanDeskResponse extends PipelinePlacesMeta {
  success: boolean;
  message?: string;
  headline?: string;
  note?: string;
  leftover?: string;
  skill_names?: string[];
}

export interface PacksLensResponse extends PipelinePlacesMeta {
  success: boolean;
  message?: string;
  note?: string;
  skill_names?: string[];
}

export interface AccountDeskResponse extends PipelinePlacesMeta {
  success: boolean;
  message?: string;
  note?: string;
  place_count?: number;
}

export interface DefaultPlacesResponse {
  success: boolean;
  places: InterestPlace[];
  places_source: 'system_default' | string;
}

export interface LlmModelOption {
  id: string;
  label: string;
}

export interface LlmProviderOption {
  id: string;
  label: string;
  models: LlmModelOption[];
  base_url?: string;
  reachable?: boolean;
}

export interface LlmCatalog {
  default_provider: string;
  default_model: string;
  default_ollama_model?: string;
  ollama_base_url?: string;
  providers: LlmProviderOption[];
}

export interface TravelResult {
  thread_id?: string;
  prompt?: string;
  answer?: string;
  itinerary?: string;
  final_response?: string;
  requires_approval?: boolean;
  approval_request?: string;
  selected_specialists?: string[];
  selected_agents?: string[];
  coordinator_notes?: string;
  supervisor_reasoning?: string;
  request_accepted?: boolean;
  request_note?: string;
  guardrail_allowed?: boolean;
  guardrail_reason?: string;
  llm_base_url?: string;
  llm_calls?: number;
  cancelled?: boolean;
  trip_constraints?: Record<string, string | string[] | undefined>;
}

export interface TravelResponse {
  success: boolean;
  thread_id?: string;
  message?: string;
  result?: TravelResult;
}

export interface TravelRequestRecord {
  id: string;
  thread_id: string;
  prompt: string;
  status: string;
  agentic_adapter: string;
  llm_provider: string;
  llm_model: string;
  result: TravelResult;
  hitl: {
    requires_approval?: boolean;
    approved?: boolean;
    feedback?: string;
    approval_request?: string;
  };
  usage: {
    input_tokens?: number;
    output_tokens?: number;
    cost_usd?: number;
    llm_calls?: number;
  };
  created_at?: string;
  updated_at?: string;
}

export interface PreferenceSkillSections {
  who: string;
  home: string;
  budget: string;
  pace: string;
  interests: string;
  avoid: string;
  notes: string;
}

export interface PreferenceSkillSummary {
  id: string;
  name: string;
  description: string;
  selected: boolean;
  builtin?: boolean;
  customized?: boolean;
  updated_at?: string;
}

export interface PreferenceSkill {
  id: string;
  name: string;
  description: string;
  sections: PreferenceSkillSections;
  markdown?: string;
  selected?: boolean;
  builtin?: boolean;
  customized?: boolean;
}

export const EMPTY_SKILL_SECTIONS: PreferenceSkillSections = {
  who: '',
  home: '',
  budget: '',
  pace: '',
  interests: '',
  avoid: '',
  notes: '',
};

export const EMPTY_PLACE: InterestPlace = {
  city: '',
  region: '',
  postal_code: '',
  country: '',
};

export const EMPTY_PREFERENCES: UserPreferences = {
  home_city: '',
  home_country: '',
  typical_budget: '',
  currency: 'USD',
  travel_style: '',
  pace: '',
  interests: [],
  companions: '',
  avoid: '',
  notes: '',
  places: [],
  event_radius_miles: 200,
  llm_provider: 'ollama',
  llm_model: '',
  llm_base_url: '',
  llm_jobs: {
    classify: { provider: 'ollama', model: '' },
    reason: { provider: 'ollama', model: '' },
    deep: { provider: 'ollama', model: '' },
  },
};

export const EMPTY_LLM_JOB: LlmJobChoice = { provider: 'ollama', model: '' };

export const SPECIALIST_LABELS: Record<string, string> = {
  air_research: 'Flights',
  stay_research: 'Stays',
  climate_brief: 'Weather',
  cost_review: 'Budget',
  trip_draft: 'Days',
  flight_agent: 'Flights',
  hotel_agent: 'Stays',
  weather_agent: 'Weather',
  budget_agent: 'Budget',
  itinerary_agent: 'Days',
};

export function tripSpecialists(result?: TravelResult | null): string[] {
  return result?.selected_specialists || result?.selected_agents || [];
}

export function tripAccepted(result?: TravelResult | null): boolean {
  if (result?.request_accepted === false || result?.guardrail_allowed === false) {
    return false;
  }
  return true;
}

export function tripNotes(result?: TravelResult | null): string {
  return result?.coordinator_notes || result?.supervisor_reasoning || '';
}

export function specialistLabel(name: string): string {
  return SPECIALIST_LABELS[name] || name;
}
