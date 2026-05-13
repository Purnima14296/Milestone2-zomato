from __future__ import annotations

from pydantic import BaseModel, Field


class BudgetRangeIn(BaseModel):
    min: float | None = Field(default=None, ge=0)
    max: float | None = Field(default=None, ge=0)


class PreferencesIn(BaseModel):
    location: str = Field(min_length=1, max_length=200)
    budget: BudgetRangeIn | None = None
    cuisines: list[str] = Field(default_factory=list)
    minimum_rating: float | None = Field(default=None, ge=0, le=5)
    additional_preferences: str | None = Field(default=None, max_length=2000)


class RecommendationRequest(BaseModel):
    preferences: PreferencesIn
    top_k: int = Field(default=5, ge=1, le=20)
    shortlist_top_n: int = Field(default=30, ge=5, le=100)
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_tokens: int = Field(default=900, ge=200, le=8000)


class RecommendationMetadata(BaseModel):
    processing_time_ms: float
    model: str
    top_k: int
    shortlist_size: int
    candidates_after_filtering: int
    pipeline_version: str = "0.1.0"


class RecommendationResponse(BaseModel):
    recommendations: list[dict]
    metadata: RecommendationMetadata
