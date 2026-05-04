"""Download remote images into ContentFile (posts, products, etc.)."""

import base64
import binascii
import mimetypes
import uuid
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError

MAX_IMAGE_BYTES = 5 * 1024 * 1024


def unsafe_image_host(hostname: str) -> bool:
    if not hostname:
        return True
    h = hostname.lower()
    if h in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        return True
    if h.endswith(".local") or h.endswith(".internal"):
        return True
    if h.startswith("192.168.") or h.startswith("10."):
        return True
    if h.startswith("172."):
        parts = h.split(".")
        if len(parts) >= 2:
            try:
                second = int(parts[1])
                if 16 <= second <= 31:
                    return True
            except ValueError:
                pass
    return False


def download_url_to_content_file(url: str) -> ContentFile:
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise ValidationError("Image URL must use http or https.")
    if unsafe_image_host(parsed.hostname or ""):
        raise ValidationError("Image URL host is not allowed.")

    req = Request(url.strip(), headers={"User-Agent": "Petso-Server/1.0"})
    with urlopen(req, timeout=25) as resp:
        ctype = resp.headers.get("Content-Type", "application/octet-stream")
        ctype = ctype.split(";")[0].strip()
        data = resp.read(MAX_IMAGE_BYTES + 1)

    if len(data) > MAX_IMAGE_BYTES:
        raise ValidationError("Image exceeds maximum size (5 MB).")

    ext = mimetypes.guess_extension(ctype) or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"):
        ext = ".jpg"
    name = f"{uuid.uuid4().hex}{ext}"
    return ContentFile(data, name=name)


def base64_to_content_file(raw: str) -> ContentFile:
    """
    Decode a data URL or raw base64 string into a ContentFile (images only).
    Use when clients cannot send multipart reliably (e.g. some proxies / Postman setups).
    """
    s = (raw or "").strip()
    if not s:
        raise ValidationError("image_base64 is empty.")

    mime = None
    lower = s.lower()
    b64_marker = ";base64,"
    idx = lower.find(b64_marker)
    if lower.startswith("data:") and idx != -1:
        head = s[:idx]
        rest = s[idx + len(b64_marker) :]
        if not rest:
            raise ValidationError("Invalid data URL (missing base64 payload).")
        mime_part = head[5:].strip()
        mime = mime_part.split(";")[0].strip() or None
        s = rest.strip()
    try:
        data = base64.b64decode(s, validate=False)
    except binascii.Error as exc:
        raise ValidationError("Invalid base64 image data.") from exc

    if len(data) > MAX_IMAGE_BYTES:
        raise ValidationError("Image exceeds maximum size (5 MB).")
    if len(data) < 24:
        raise ValidationError("Image data is too small.")

    ext = ".png"
    if mime:
        guessed = mimetypes.guess_extension(mime.split(";")[0].strip())
        if guessed in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"):
            ext = guessed
    else:
        if data.startswith(b"\xff\xd8\xff"):
            ext = ".jpg"
        elif data.startswith(b"\x89PNG\r\n\x1a\n"):
            ext = ".png"
        elif data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
            ext = ".gif"
        elif data.startswith(b"RIFF") and len(data) > 12 and data[8:12] == b"WEBP":
            ext = ".webp"

    name = f"{uuid.uuid4().hex}{ext}"
    return ContentFile(data, name=name)
