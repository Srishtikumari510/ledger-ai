"""Orchestrator: validation -> OCR -> extraction -> validation -> persistence."""
import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.repositories import document_repository as repo
from app.schemas.extraction import (
    FileValidation,
    ProcessingMetadata,
    ValidationResult,
)
from app.services import document_validation_service as dvs
from app.services import extraction_service
from app.services import financial_validation_service as fvs
from app.services import ocr_service


class ProcessingError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def process_document(
    db: Session,
    file_bytes: bytes,
    filename: str,
    content_type: str,
    document_type: str,
) -> dict:
    start = time.time()
    logger.info("Processing start | file=%s | type=%s", filename, document_type)

    if document_type not in settings.SUPPORTED_DOCUMENT_TYPES:
        raise ProcessingError(
            "UNSUPPORTED_DOCUMENT_TYPE",
            f"document_type must be one of {settings.SUPPORTED_DOCUMENT_TYPES}",
        )

    # 1. File validation
    fv: FileValidation = dvs.validate_document(file_bytes, filename, content_type)
    if fv.status != "PASS":
        raise ProcessingError(fv.error_code or "VALIDATION_FAILED", fv.error_message or "File validation failed.")

    # 2. OCR / text extraction
    pages, ocr_used = ocr_service.extract_text(file_bytes, filename, content_type)
    if not pages or all(not p.text.strip() for p in pages):
        raise ProcessingError("NO_TEXT_EXTRACTED", "No readable text found in document.")

    # 3. LLM extraction
    try:
        extracted = extraction_service.extract_fields(document_type, pages)
    except Exception as e:
        logger.exception("Extraction failed | error=%s", e)
        raise ProcessingError("EXTRACTION_FAILED", str(e))

    # 4. Financial validation
    validation: ValidationResult = fvs.run_validations(document_type, extracted)

    # 5. Status
    processing_status = "PASS" if validation.overall_status in ("PASS", "NOT_APPLICABLE") else "FAILED"

    elapsed_ms = int((time.time() - start) * 1000)
    meta = ProcessingMetadata(
        ocr_used=ocr_used,
        llm_used=True,
        processed_at=datetime.now(timezone.utc).isoformat(),
        processing_time_ms=elapsed_ms,
        llm_provider=settings.LLM_PROVIDER,
        llm_model=settings.LLM_MODEL,
    )

    # 6. Persist
    payload = {
        "document_name": filename,
        "document_type": document_type,
        "processing_status": processing_status,
        "overall_confidence": None,
        "file_validation": fv.model_dump(),
        "extracted_data": extracted,
        "validation": validation.model_dump(),
        "processing_metadata": meta.model_dump(),
    }
    repo.save_document(db, payload)
    logger.info("Processing complete | status=%s | time_ms=%d", processing_status, elapsed_ms)
    return payload
