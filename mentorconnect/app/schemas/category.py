"""
app/schemas/category.py
---------------------------
Schemas for the Category/Field taxonomy used to classify mentor expertise.
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class FieldCreateRequest(BaseModel):
    category_id: int
    name: str = Field(..., min_length=2, max_length=100)


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class FieldOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    name: str
    is_active: bool


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    fields: List[FieldOut] = []
