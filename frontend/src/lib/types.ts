export type BudgetRangeIn = {
  min?: number | null;
  max?: number | null;
};

export type PreferencesIn = {
  location: string;
  budget?: BudgetRangeIn | null;
  cuisines: string[];
  minimum_rating?: number | null;
  additional_preferences?: string | null;
};

export type LocationsResponse = {
  locations: string[];
  count: number;
};

export type RecommendationRequest = {
  preferences: PreferencesIn;
  top_k?: number;
  shortlist_top_n?: number;
  temperature?: number;
  max_tokens?: number;
};

export type RecommendationMetadata = {
  processing_time_ms: number;
  model: string;
  top_k: number;
  shortlist_size: number;
  candidates_after_filtering: number;
  pipeline_version: string;
};

export type RecommendationItem = {
  rank: number;
  restaurant_name: string;
  reason: string;
  source: string;
  city?: string;
  cuisines?: unknown;
  rating?: number;
  cost_estimate?: number;
};

export type RecommendationResponse = {
  recommendations: RecommendationItem[];
  metadata: RecommendationMetadata;
};
