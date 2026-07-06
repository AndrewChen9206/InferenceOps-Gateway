from enum import StrEnum

from pydantic import BaseModel, Field


class TaskType(StrEnum):
    OCR_CLEANUP = "ocr_cleanup"
    DOCUMENT_SUMMARY = "document_summary"
    TABLE_EXTRACTION = "table_extraction"
    FIELD_CLASSIFICATION = "field_classification"
    COMPLEX_REASONING = "complex_reasoning"


class RoutingPolicy(StrEnum):
    PREMIUM_ONLY = "premium_only"
    CHEAP_ONLY = "cheap_only"
    CACHE_FIRST = "cache_first"
    COST_AWARE = "cost_aware"


class InferRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    task_type: TaskType
    prompt: str = Field(..., min_length=1)
    policy: RoutingPolicy = RoutingPolicy.COST_AWARE
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=256, ge=1, le=4096)
    cache: bool = True


class InferResponse(BaseModel):
    request_id: str
    user_id: str
    task_type: TaskType
    selected_model: str
    output: str
    cache_hit: bool
    fallback_used: bool
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost_usd: float
    latency_ms: int
    policy: RoutingPolicy
