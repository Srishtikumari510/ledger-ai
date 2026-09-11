"""Text extraction from PDFs and images. Native-first, smart OCR fallback."""
import io
import re
import shutil
from pathlib import Path
from typing import NamedTuple

import pdfplumber
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes

from app.core.logging import logger


class PageText(NamedTuple):
    page_number: int
    text: str


def _configure_tesseract() -> None:
    """Find Tesseract on this system (works on Windows dev + Linux prod)."""
    if shutil.which("tesseract"):
        return
    common_paths = [
        # Windows dev
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        str(Path.home() / "AppData/Local/Tesseract-OCR/tesseract.exe"),
        # Linux production (Docker / Render)
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
        # macOS
        "/opt/homebrew/bin/tesseract",
        "/usr/local/bin/tesseract",
    ]
    for p in common_paths:
        if Path(p).exists():
            pytesseract.pytesseract.tesseract_cmd = p
            logger.info("Tesseract configured at %s", p)
            return
    logger.warning("Tesseract not found on PATH. Image OCR may fail.")


_configure_tesseract()


def _tesseract_available() -> bool:
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def _is_meaningful_text(text: str) -> bool:
    """
    Decide whether extracted text is actually useful.

    Returns True if text has enough alphabetic words to be worth using
    without OCR. Returns False if the text looks like junk / watermark /
    hidden metadata, in which case OCR should be forced.
    """
    if not text or len(text.strip()) < 50:
        return False

    # Count alphabetic words of >= 3 chars
    words = re.findall(r"[A-Za-z]{3,}", text)
    if len(words) < 15:
        return False

    # Letter ratio (letters / total non-space characters)
    stripped = re.sub(r"\s", "", text)
    if not stripped:
        return False
    letters = sum(c.isalpha() for c in stripped)
    if letters / len(stripped) < 0.35:
        return False

    return True


def _ocr_image_object(img: Image.Image) -> str:
    """Run Tesseract on a PIL Image."""
    try:
        return pytesseract.image_to_string(img)
    except Exception as e:
        logger.exception("Tesseract failed on image | error=%s", e)
        return ""


def _resolve_poppler_path() -> str | None:
    """Find Poppler on this system (works on Windows dev + Linux prod)."""
    from app.core.config import settings

    # 1. Prefer explicit env var
    if settings.POPPLER_PATH and Path(settings.POPPLER_PATH).exists():
        return settings.POPPLER_PATH

    # 2. Try common Linux/macOS locations
    for p in ("/usr/bin", "/usr/local/bin", "/opt/homebrew/bin", "/opt/local/bin"):
        if Path(p).exists() and (Path(p) / "pdftoppm").exists():
            return p

    # 3. Try Windows winget location
    win_candidates = list(
        Path.home().glob(
            "AppData/Local/Microsoft/WinGet/Packages/*Poppler*/**/Library/bin"
        )
    )
    for p in win_candidates:
        if (p / "pdftoppm.exe").exists():
            return str(p)

    # 4. Rely on PATH (return None → pdf2image will search PATH itself)
    return None


def _ocr_pdf(file_bytes: bytes) -> tuple[list[PageText], bool]:
    """Convert PDF pages to images and OCR each page."""
    if not _tesseract_available():
        logger.error("OCR requested but Tesseract is not installed.")
        return [], True

    try:
        kwargs = {"dpi": 300}
        poppler = _resolve_poppler_path()
        if poppler:
            kwargs["poppler_path"] = poppler
            logger.info("Using Poppler at %s", poppler)
        else:
            logger.info("Using Poppler from PATH (no explicit poppler_path set).")

        images = convert_from_bytes(file_bytes, **kwargs)
    except Exception as e:
        logger.exception("PDF-to-image conversion failed (is Poppler installed?) | error=%s", e)
        return [], True

    pages: list[PageText] = []
    for i, img in enumerate(images, start=1):
        text = _ocr_image_object(img)
        logger.info("OCR page %d | chars=%d", i, len(text))
        pages.append(PageText(page_number=i, text=text))

    logger.info("OCR complete | pages=%d", len(pages))
    return pages, True


def extract_text_from_pdf(file_bytes: bytes) -> tuple[list[PageText], bool]:
    """
    Extract text from PDF.
    Uses native text if meaningful; otherwise forces OCR.
    """
    native_pages: list[PageText] = []

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                native_pages.append(PageText(page_number=i, text=text))
    except Exception as e:
        logger.exception("pdfplumber failed | error=%s", e)
        native_pages = []

    combined = "\n".join(p.text for p in native_pages)
    logger.info(
        "Native extraction | pages=%d | total_chars=%d | meaningful=%s",
        len(native_pages), len(combined), _is_meaningful_text(combined),
    )

    if _is_meaningful_text(combined):
        return native_pages, False

    # Fallback: OCR
    logger.info("Native text insufficient - falling back to OCR.")
    ocr_pages, ocr_used = _ocr_pdf(file_bytes)

    # If OCR returned content, prefer it. Otherwise fall back to native (may help).
    if any(p.text.strip() for p in ocr_pages):
        return ocr_pages, ocr_used

    logger.warning("OCR yielded no text. Returning native text (if any).")
    return native_pages, True


def extract_text_from_image(file_bytes: bytes) -> tuple[list[PageText], bool]:
    """OCR a JPG/PNG image."""
    if not _tesseract_available():
        logger.error("OCR requested but Tesseract is not installed.")
        return [PageText(page_number=1, text="")], True

    try:
        img = Image.open(io.BytesIO(file_bytes))
        text = _ocr_image_object(img)
    except Exception as e:
        logger.exception("Image OCR failed | error=%s", e)
        text = ""

    return [PageText(page_number=1, text=text)], True


def extract_text(file_bytes: bytes, filename: str, content_type: str) -> tuple[list[PageText], bool]:
    """Unified entry point."""
    lower = filename.lower()
    if lower.endswith(".pdf") or content_type == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    return extract_text_from_image(file_bytes)