import io

from PIL import Image
from rembg import remove

from app.core.config import config
from app.utils.file_utils import validate_image, InvalidImageError

# Privacy: Uploaded images exist only in memory during processing. No disk storage.


def remove_background(content: bytes, session) -> bytes:
    validate_image(content, config.max_upload_size_bytes)

    input_image = Image.open(io.BytesIO(content))
    try:
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
    finally:
        input_image.close()


# Alias for backwards compatibility
def remove_background_stream(content: bytes, session) -> bytes:
    return remove_background(content, session)
