"""
app/utils/sanitizer.py
-------------------------
Input sanitization helpers to defend against XSS and HTML injection in
user-supplied free-text fields (bios, chat messages, complaint descriptions, etc).
Pydantic validators catch obviously malicious patterns at the schema layer;
this module performs the actual HTML-escaping before text is persisted/rendered,
providing defense in depth (belt-and-suspenders, not a replacement for the
frontend also escaping output).
"""

import html
import re
from typing import Optional

# Strip any raw HTML tags entirely (we don't support rich text anywhere in this API)
_TAG_RE = re.compile(r"<[^>]*>")
# Collapse excessive whitespace/newlines that could be used to mangle layouts
_MULTI_NEWLINE_RE = re.compile(r"\n{4,}")


def sanitize_text(value: Optional[str]) -> Optional[str]:
    """
    Defensive sanitizer for any free-text user input:
    1. Strip HTML tags completely.
    2. HTML-escape any remaining special characters (&, <, >, quotes).
    3. Normalize excessive whitespace.
    """
    if value is None:
        return None

    value = _TAG_RE.sub("", value)
    value = html.escape(value, quote=True)
    value = _MULTI_NEWLINE_RE.sub("\n\n\n", value)
    return value.strip()


def sanitize_filename(filename: str) -> str:
    """
    Strip directory traversal sequences and unsafe characters from an uploaded
    filename before using it to build a path on disk.
    """
    filename = filename.replace("\\", "/").split("/")[-1]  # drop any path component
    filename = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    # Prevent hidden files / leading dots that could create unexpected paths
    filename = filename.lstrip(".")
    return filename or "file"
