"""Database access layer for processed documents."""
import json
from typing import Optional

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.document import Document


def save_document(db: Session, payload: dict) -> Document:
    doc = Document(
        document_name=payload["document_name"],
        document_type=payload["document_type"],
        processing_status=payload["processing_status"],
        overall_confidence=payload.get("overall_confidence"),
        file_validation=json.dumps(payload["file_validation"]),
        extracted_data=json.dumps(payload["extracted_data"]),
        validation=json.dumps(payload["validation"]),
        processing_metadata=json.dumps(payload["processing_metadata"]),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    logger.info("Saved document | name=%s | id=%d", doc.document_name, doc.id)
    return doc


def _row_to_dict(doc: Document) -> dict:
    return {
        "document_name": doc.document_name,
        "document_type": doc.document_type,
        "processing_status": doc.processing_status,
        "overall_confidence": doc.overall_confidence,
        "file_validation": json.loads(doc.file_validation),
        "extracted_data": json.loads(doc.extracted_data),
        "validation": json.loads(doc.validation),
        "processing_metadata": json.loads(doc.processing_metadata),
    }


def get_latest_by_name(db: Session, document_name: str) -> Optional[dict]:
    doc = (
        db.query(Document)
        .filter(Document.document_name == document_name)
        .order_by(Document.created_at.desc())
        .first()
    )
    return _row_to_dict(doc) if doc else None


def list_documents(db: Session, limit: int = 100) -> list[dict]:
    docs = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "document_name": d.document_name,
            "document_type": d.document_type,
            "processing_status": d.processing_status,
            "overall_confidence": d.overall_confidence,
            "processed_at": d.created_at.isoformat() + "Z",
        }
        for d in docs
    ]
