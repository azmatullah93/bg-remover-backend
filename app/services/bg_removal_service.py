import io
from typing import Iterator

from PIL import Image
from rembg import remove

from app.core.config import config
from app.utils.file_utils import validate_image, InvalidImageError

CHUNK_SIZE = 64 * 1024  # 64 KB

# Privacy: Uploaded images exist only in memory during processing. No disk storage.


def remove_background(content: bytes, session) -> bytes:
    validate_image(content, config.max_upload_size_bytes)

    input_image = Image.open(io.BytesIO(content))
    output_image = remove(
        input_image,
        session=session,
        alpha_matting=False,
        post_process_mask=True,
    )

    buffer = io.BytesIO()
    output_image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


def remove_background_stream(content: bytes, session) -> Iterator[bytes]:
    png_bytes = remove_background(content, session)
    offset = 0
    while offset < len(png_bytes):
        chunk = png_bytes[offset : offset + CHUNK_SIZE]
        offset += len(chunk)
        yield chunk
