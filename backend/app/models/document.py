"""SQLAlchemy ORM model for processed documents."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String(255), index=True, nullable=False)
    document_type = Column(String(50), nullable=False)
    processing_status = Column(String(20), nullable=False)

    overall_confidence = Column(Float, nullable=True)

    file_validation = Column(Text, nullable=False)
    extracted_data = Column(Text, nullable=False)
    validation = Column(Text, nullable=False)
    processing_metadata = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Document name={self.document_name} type={self.document_type} status={self.processing_status}>"
