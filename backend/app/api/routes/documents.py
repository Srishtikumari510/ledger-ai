"""REST API routes for document processing."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.repositories import document_repository as repo
from app.schemas.document import DocumentListItem, DocumentResponse
from app.services.document_service import ProcessingError, process_document


router = APIRouter(prefix="/api/v1", tags=["documents"])


@router.get("/health")
def health():
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@router.post("/documents/process", response_model=DocumentResponse)
async def process(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db),
):
    logger.info("POST /documents/process | file=%s | type=%s", file.filename, document_type)
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail={"code": "UPLOAD_READ_ERROR", "message": str(e)})

    try:
        result = process_document(
            db=db,
            file_bytes=file_bytes,
            filename=file.filename or "unnamed",
            content_type=file.content_type or "",
            document_type=document_type,
        )
    except ProcessingError as e:
        code_to_status = {
            "UNSUPPORTED_FILE_TYPE": 400,
            "UNSUPPORTED_DOCUMENT_TYPE": 400,
            "EMPTY_FILE": 400,
            "CORRUPTED_FILE": 400,
            "PAGE_LIMIT_EXCEEDED": 400,
            "FILE_TOO_LARGE": 413,
            "NO_TEXT_EXTRACTED": 422,
            "EXTRACTION_FAILED": 500,
            "VALIDATION_FAILED": 400,
        }
        status = code_to_status.get(e.code, 500)
        raise HTTPException(status_code=status, detail={"code": e.code, "message": e.message})
    except Exception as e:
        logger.exception("Unexpected processing error | error=%s", e)
        raise HTTPException(
            status_code=500,
            detail={"code": "INTERNAL_ERROR", "message": "Unexpected error during processing."},
        )

    return result


@router.get("/documents", response_model=list[DocumentListItem])
def list_all(db: Session = Depends(get_db)):
    return repo.list_documents(db)


@router.get("/documents/{document_name}", response_model=DocumentResponse)
def get_by_name(document_name: str, db: Session = Depends(get_db)):
    result = repo.get_latest_by_name(db, document_name)
    if not result:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": f"No processed document named '{document_name}'."},
        )
    return result
