"""Download remote images into ContentFile (posts, products, etc.)."""

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
