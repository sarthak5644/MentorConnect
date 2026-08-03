"""
app/services/file_upload_service.py
---------------------------------------
Orchestrates secure file uploads: validates the file (via utils/file_validator),
persists it to disk, and returns the relative path to store in the database.
Used for mentor profile images, mentor verification documents, and chat attachments.
"""

from typing import Tuple
from fastapi import UploadFile

from app.core.config import settings
from app.utils.file_validator import validate_and_read_upload, save_upload_to_disk


class FileUploadService:
    @staticmethod
    async def upload_profile_image(file: UploadFile) -> str:
        """Validates and stores a profile image. Returns the relative path."""
        contents, filename, _ext = await validate_and_read_upload(
            file, allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS, max_size_mb=5
        )
        return save_upload_to_disk(contents, "profiles", filename)

    @staticmethod
    async def upload_mentor_document(file: UploadFile) -> Tuple[str, str, int]:
        """
        Validates and stores a mentor verification document.
        Returns (relative_path, mime_extension, size_bytes).
        """
        contents, filename, ext = await validate_and_read_upload(
            file, allowed_extensions=settings.ALLOWED_DOCUMENT_EXTENSIONS, max_size_mb=settings.MAX_UPLOAD_SIZE_MB
        )
        relative_path = save_upload_to_disk(contents, "documents", filename)
        return relative_path, ext, len(contents)

    @staticmethod
    async def upload_chat_attachment(file: UploadFile) -> Tuple[str, int]:
        """Validates and stores a chat image/file attachment. Returns (relative_path, size_bytes)."""
        allowed = list(set(settings.ALLOWED_IMAGE_EXTENSIONS + settings.ALLOWED_DOCUMENT_EXTENSIONS))
        contents, filename, _ext = await validate_and_read_upload(
            file, allowed_extensions=allowed, max_size_mb=settings.MAX_UPLOAD_SIZE_MB
        )
        relative_path = save_upload_to_disk(contents, "chat", filename)
        return relative_path, len(contents)
