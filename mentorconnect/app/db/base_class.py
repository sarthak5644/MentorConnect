"""
app/db/base_class.py
---------------------
Declarative base class that all ORM models inherit from.
Defines common conventions (table naming, common columns via mixin) shared
across the entire schema so we don't repeat ourselves in every model.
"""

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import Column, DateTime


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Auto-generate table name from class name, e.g. MentorDocument -> mentor_documents
        import re
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        if not name.endswith("s"):
            name += "s"
        return name


class TimestampMixin:
    """Mixin adding created_at / updated_at columns to a model."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
