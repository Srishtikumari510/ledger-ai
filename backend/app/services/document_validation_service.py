"""Validate uploaded files before OCR/extraction."""
import io
from PyPDF2 import PdfReader
from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.core.logging import logger
from app.schemas.extraction import FileValidation


SUPPORTED_MIME = {"application/pdf", "image/jpeg", "image/jpg", "image/png"}


def _detect_extension_mime(filename: str) -> str | None:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "application/pdf"
    if lower.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if lower.endswith(".png"):
        return "image/png"
    return None


def validate_document(file_bytes: bytes, filename: str, content_type: str | None) -> FileValidation:
    logger.info("Validation start | file=%s | content_type=%s | size=%d",
                filename, content_type, len(file_bytes))

    detected_mime = _detect_extension_mime(filename) or content_type or ""

    if detected_mime not in SUPPORTED_MIME:
        logger.warning("Unsupported file type | file=%s | mime=%s", filename, detected_mime)
        return FileValidation(
            file_type=detected_mime or "unknown",
            is_supported=False,
            is_readable=False,
            page_count=0,
            status="FAILED",
            error_code="UNSUPPORTED_FILE_TYPE",
            error_message="Only PDF / JPG / PNG documents are supported.",
        )

    if not file_bytes or len(file_bytes) == 0:
        return FileValidation(
            file_type=detected_mime, is_supported=True, is_readable=False,
            page_count=0, status="FAILED",
            error_code="EMPTY_FILE", error_message="Uploaded file is empty.",
        )

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        return FileValidation(
            file_type=detected_mime, is_supported=True, is_readable=True,
            page_count=0, status="FAILED",
            error_code="FILE_TOO_LARGE",
            error_message=f"File exceeds {settings.MAX_FILE_SIZE_MB} MB limit.",
        )

    if detected_mime == "application/pdf":
        return _validate_pdf(file_bytes, detected_mime)
    return _validate_image(file_bytes, detected_mime)


def _validate_pdf(file_bytes: bytes, mime: str) -> FileValidation:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as e:
        logger.exception("Corrupted PDF | error=%s", e)
        return FileValidation(
            file_type=mime, is_supported=True, is_readable=False, page_count=0,
            status="FAILED", error_code="CORRUPTED_FILE",
            error_message="PDF is corrupted or unreadable.",
        )

    try:
        page_count = len(reader.pages)
    except Exception as e:
        logger.exception("Failed counting PDF pages | error=%s", e)
        return FileValidation(
            file_type=mime, is_supported=True, is_readable=False, page_count=0,
            status="FAILED", error_code="CORRUPTED_FILE",
            error_message="PDF pages could not be read.",
        )

    if page_count == 0:
        return FileValidation(
            file_type=mime, is_supported=True, is_readable=False, page_count=0,
            status="FAILED", error_code="EMPTY_PDF",
            error_message="PDF contains no pages.",
        )

    if page_count > settings.MAX_PAGES:
        return FileValidation(
            file_type=mime, is_supported=True, is_readable=True, page_count=page_count,
            status="FAILED", error_code="PAGE_LIMIT_EXCEEDED",
            error_message=f"Document has {page_count} pages; max {settings.MAX_PAGES} allowed.",
        )

    logger.info("PDF validation PASS | pages=%d", page_count)
    return FileValidation(
        file_type=mime, is_supported=True, is_readable=True,
        page_count=page_count, status="PASS",
    )


def _validate_image(file_bytes: bytes, mime: str) -> FileValidation:
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
        with Image.open(io.BytesIO(file_bytes)) as img:
            _ = img.size
    except (UnidentifiedImageError, Exception) as e:
        logger.exception("Corrupted image | error=%s", e)
        return FileValidation(
            file_type=mime, is_supported=True, is_readable=False, page_count=0,
            status="FAILED", error_code="CORRUPTED_FILE",
            error_message="Image file is corrupted or unreadable.",
        )

    logger.info("Image validation PASS | mime=%s", mime)
    return FileValidation(
        file_type=mime, is_supported=True, is_readable=True,
        page_count=1, status="PASS",
    )
