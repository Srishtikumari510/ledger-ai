"""Pydantic schemas for extraction and validation results."""
from typing import Any, Optional
from pydantic import BaseModel, Field


class FileValidation(BaseModel):
    file_type: str
    is_supported: bool
    is_readable: bool
    page_count: int = 0
    status: str = Field(..., description="PASS or FAILED")
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class Evidence(BaseModel):
    source_text: Optional[str] = None
    page_number: Optional[int] = None


class ExtractedField(BaseModel):
    value: Any = None
    confidence: Optional[float] = None
    page_number: Optional[int] = None
    evidence: Optional[Evidence] = None


class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    extra: Optional[dict[str, Any]] = None


class ValidationCheck(BaseModel):
    name: str
    formula: str
    operands: dict[str, Any] = {}
    calculated_value: Optional[float] = None
    reported_value: Optional[float] = None
    variance: Optional[float] = None
    status: str = Field(..., description="PASS | FAILED | NOT_APPLICABLE")
    message: Optional[str] = None


class ValidationResult(BaseModel):
    checks: list[ValidationCheck] = []
    overall_status: str = "NOT_APPLICABLE"
    issues: list[str] = []


class ProcessingMetadata(BaseModel):
    ocr_used: bool = False
    llm_used: bool = False
    processed_at: str
    processing_time_ms: int
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
