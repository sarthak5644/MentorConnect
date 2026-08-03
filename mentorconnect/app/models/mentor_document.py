"""
app/models/mentor_document.py
------------------------------
Documents uploaded by mentors for identity/credential verification
(e.g. ID proof, degree certificates, experience letters). Reviewed by Super Admin
before a mentor's `approval_status` can move to APPROVED.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin
from app.models.enums import DocumentStatus


class MentorDocument(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)

    document_type = Column(String(100), nullable=False)   # e.g. "ID_PROOF", "DEGREE_CERTIFICATE"
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)        # stored relative path on disk/S3 key
    file_size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)

    status = Column(SAEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False, index=True)
    reviewed_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String(500), nullable=True)

    mentor = relationship("Mentor", back_populates="documents")

    def __repr__(self) -> str:
        return f"<MentorDocument id={self.id} mentor_id={self.mentor_id} type={self.document_type}>"
