import re

IMAGE_SIGNATURES = {
    b"\xff\xd8\xff": ["image/jpeg", "image/jpg"],
    b"\x89PNG\r\n\x1a\n": ["image/png"],
    b"RIFF": ["image/webp"],
}

ALLOWED_MIME_TYPES = frozenset({"image/png", "image/jpeg", "image/jpg", "image/webp"})


class InvalidImageError(Exception):
    pass


def sanitize_filename(name: str) -> str:
    safe = re.sub(r"[^\w\-_.]", "_", name)
    return safe[:200] if safe else "image"


def validate_content_type(content_type: str | None) -> None:
    if not content_type:
        raise InvalidImageError("Content-Type is required")
    ct = content_type.split(";")[0].strip().lower()
    if ct not in ALLOWED_MIME_TYPES:
        raise InvalidImageError("Invalid file type. Allowed: PNG, JPEG, WebP")


def validate_image(content: bytes, max_size: int) -> bytes:
    if len(content) > max_size:
        raise InvalidImageError(
            f"File too large. Maximum size is {max_size // (1024 * 1024)} MB"
        )

    if len(content) < 12:
        raise InvalidImageError("File is too small to be a valid image")

    detected = None
    for sig, mime_types in IMAGE_SIGNATURES.items():
        if content.startswith(sig):
            detected = mime_types
            break

    if detected is None:
        if len(content) >= 12 and content[8:12] == b"WEBP":
            detected = ["image/webp"]
        else:
            raise InvalidImageError(
                "Invalid image format. Allowed: JPEG, PNG, WebP"
            )

    return content
