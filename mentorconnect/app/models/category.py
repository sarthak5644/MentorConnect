"""
app/models/category.py
-----------------------
Taxonomy tables used to classify mentor expertise and let students filter/search.

categories -> broad domain, e.g. "Technology", "Business", "Design"
fields     -> specific sub-topic under a category, e.g. "Machine Learning" under "Technology"

Mentors are linked to fields via the `mentor_fields` association table (many-to-many),
since a mentor can have expertise in multiple fields, and a field can have many mentors.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin

# Many-to-many association: mentors <-> fields (expertise)
mentor_fields = Table(
    "mentor_fields",
    Base.metadata,
    Column("mentor_id", Integer, ForeignKey("mentors.id", ondelete="CASCADE"), primary_key=True),
    Column("field_id", Integer, ForeignKey("fields.id", ondelete="CASCADE"), primary_key=True),
)


class Category(Base, TimestampMixin):
    """Top-level domain category, e.g. Technology, Business, Healthcare."""
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    fields = relationship("Field", back_populates="category", cascade="all, delete-orphan")


class Field(Base, TimestampMixin):
    """Specific subject/skill under a category, e.g. 'Machine Learning' under 'Technology'."""
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    category = relationship("Category", back_populates="fields")
    mentors = relationship("Mentor", secondary=mentor_fields, back_populates="expertise_fields")
