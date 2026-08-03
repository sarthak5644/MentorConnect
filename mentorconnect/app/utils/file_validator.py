"""
app/utils/file_validator.py
-------------------------------
Secure file upload helpers: extension whitelisting, size limits, and
magic-byte (file signature) verification so a malicious actor can't simply
rename a .php/.exe file to .jpg and have the server trust the extension alone.
"""

import os
import uuid
from typing import Tuple, List, Optional, Dict

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import FileUploadException
from app.utils.sanitizer import sanitize_filename

# Magic byte signatures for the file types we accept. Checking these bytes
# (not just the extension or client-supplied content-type) prevents
# extension-spoofing attacks where a malicious payload is renamed to .jpg/.png/.pdf.
_MAGIC_SIGNATURES: Dict[str, List[bytes]] = {
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "webp": [b"RIFF"],  # followed by WEBP at offset 8, checked separately below
    "pdf": [b"%PDF-"],
}


def _get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _verify_magic_bytes(header: bytes, extension: str) -> bool:
    """Check the first bytes of the file against known signatures for its claimed extension."""
    signatures = _MAGIC_SIGNATURES.get(extension)
    if not signatures:
        return False
    if extension == "webp":
        # WEBP = RIFF????WEBP - check both the RIFF header and the WEBP marker at offset 8
        return header.startswith(b"RIFF") and header[8:12] == b"WEBP"
    return any(header.startswith(sig) for sig in signatures)


async def validate_and_read_upload(
    file: UploadFile,
    allowed_extensions: List[str],
    max_size_mb: Optional[int] = None,
) -> Tuple[bytes, str, str]:
    """
    Validates an uploaded file's extension, size, and magic bytes.
    Returns (file_bytes, safe_filename, extension) on success.
    Raises FileUploadException on any validation failure.
    """
    if not file.filename:
        raise FileUploadException("No filename provided.")

    safe_name = sanitize_filename(file.filename)
    extension = _get_extension(safe_name)

    if extension not in [e.lower() for e in allowed_extensions]:
        raise FileUploadException(
            f"File type '.{extension}' is not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )

    max_bytes = (max_size_mb or settings.MAX_UPLOAD_SIZE_MB) * 1024 * 1024
    contents = await file.read()

    if len(contents) == 0:
        raise FileUploadException("Uploaded file is empty.")

    if len(contents) > max_bytes:
        raise FileUploadException(
            f"File too large. Maximum allowed size is {max_size_mb or settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    if not _verify_magic_bytes(contents[:16], extension):
        raise FileUploadException(
            "File content does not match its extension. The file may be corrupted or disguised."
        )

    # Generate a random, collision-proof filename - never trust/store the original
    # client-supplied filename directly on disk (prevents path traversal & overwrites).
    unique_filename = f"{uuid.uuid4().hex}.{extension}"

    return contents, unique_filename, extension


def save_upload_to_disk(contents: bytes, subfolder: str, filename: str) -> str:
    """
    Persists validated file bytes to UPLOAD_DIR/subfolder/filename.
    Returns the relative path (suitable for storing in the DB) - never the absolute
    filesystem path, so the app remains portable across environments / storage backends.
    """
    target_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(target_dir, exist_ok=True)

    full_path = os.path.join(target_dir, filename)
    with open(full_path, "wb") as f:
        f.write(contents)

    return os.path.join(subfolder, filename)
