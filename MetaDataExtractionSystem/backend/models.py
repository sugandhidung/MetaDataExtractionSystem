"""
Pydantic models for request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ExtractionResult(BaseModel):
    """Schema for extracted document metadata."""
    agreement_value: Optional[str] = Field(None, description="Monetary value of the agreement")
    agreement_start_date: Optional[str] = Field(None, description="Start date (DD.MM.YYYY)")
    agreement_end_date: Optional[str] = Field(None, description="End date (DD.MM.YYYY)")
    renewal_notice_days: Optional[str] = Field(None, description="Days for renewal notice")
    party_one: Optional[str] = Field(None, description="First party (landlord/owner)")
    party_two: Optional[str] = Field(None, description="Second party (tenant)")


class ExtractionResponse(BaseModel):
    """Full API response for extraction."""
    filename: str
    status: str
    error_message: Optional[str] = None
    extracted_text_preview: Optional[str] = None
    metadata: ExtractionResult
    confidence: Optional[str] = None
    provider: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str
    provider: Optional[str] = None


class BatchExtractionRequest(BaseModel):
    """Request for batch extraction from the data folder."""
    folder: str = Field("test", description="Folder to process: 'train' or 'test'")


class EvaluationResult(BaseModel):
    """Per-field recall evaluation result."""
    field: str
    true_count: int
    false_count: int
    total: int
    recall: float


class EvaluationResponse(BaseModel):
    """Full evaluation response."""
    per_field_recall: list[EvaluationResult]
    overall_recall: float
    details: list[dict]
