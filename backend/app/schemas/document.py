"""Pydantic schemas for API request/response."""
from typing import Any, Optional
from pydantic import BaseModel
from app.schemas.extraction import FileValidation, ValidationResult, ProcessingMetadata


class DocumentResponse(BaseModel):
    document_name: str
    document_type: str
    processing_status: str
    overall_confidence: Optional[float] = None
    file_validation: FileValidation
    extracted_data: dict[str, Any] = {}
    validation: ValidationResult
    processing_metadata: ProcessingMetadata


class DocumentListItem(BaseModel):
    document_name: str
    document_type: str
    processing_status: str
    overall_confidence: Optional[float] = None
    processed_at: str


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
