"""
app/db/base_class.py
---------------------
Declarative base class used by all SQLAlchemy ORM models.

Features:
- Automatic snake_case table names.
- Correct English pluralization:
    Category -> categories
    User -> users
    Role -> roles
    MentorAvailabilitySlot -> mentor_availability_slots
- TimestampMixin providing created_at / updated_at columns.
"""

from datetime import datetime
import re

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Base class inherited by every ORM model."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Convert CamelCase class names to snake_case plural table names.

        Examples:
            User -> users
            Role -> roles
            Category -> categories
            Mentor -> mentors
            MentorDocument -> mentor_documents
            MentorAvailabilitySlot -> mentor_availability_slots
        """

        name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

        # Category -> categories
        if name.endswith("y"):
            name = name[:-1] + "ies"

        # Class -> classes, Address -> addresses
        elif name.endswith(("s", "x", "z", "ch", "sh")):
            name = name + "es"

        # User -> users
        else:
            name = name + "s"

        return name


class TimestampMixin:
    """Adds created_at and updated_at timestamps to every model."""

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )