"""
app/repositories/mentor_document_repository.py
---------------------------------------------------
Data access methods for mentor verification documents.
"""

from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mentor_document import MentorDocument
from app.repositories.base import BaseRepository


class MentorDocumentRepository(BaseRepository[MentorDocument]):
    def __init__(self, db: Session):
        super().__init__(MentorDocument, db)

    def list_by_mentor(self, mentor_id: int) -> List[MentorDocument]:
        stmt = select(MentorDocument).where(MentorDocument.mentor_id == mentor_id)
        return list(self.db.execute(stmt).scalars().all())
