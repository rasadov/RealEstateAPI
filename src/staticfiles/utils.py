import os, uuid, io

from PIL import Image
from fastapi import UploadFile

import src.staticfiles.exceptions as exceptions

def generate_unique_filename(filename: str) -> str:
    """Generate a unique filename"""
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{uuid.uuid4().hex}{ext}"
    return unique_filename

def validate_file(
        file: UploadFile,
        max_file_size_mb: int,
        allowed_image_types: set[str]
) -> None:
    """Validate file size and type"""
    # Check file size
    file.file.seek(0, 2)  # Move file pointer to end
    file_size_mb = file.file.tell() / (1024 * 1024)
    file.file.seek(0)  # Reset file pointer to start

    if file_size_mb > max_file_size_mb:
        raise exceptions.FileTooLarge

    if file.content_type not in allowed_image_types:
        raise exceptions.UnsupportedFileType

async def process_image(
        file: UploadFile,
        max_image_size_px: tuple[int, int]
) -> UploadFile:
    """Process image if needed (e.g., resize or convert format)"""
    if file.content_type.startswith("image/"):
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            image.thumbnail(max_image_size_px)
            buffer = io.BytesIO()
            image.save(buffer, format="WEBP", quality=85)
            buffer.seek(0)

            file = UploadFile(
                filename=file.filename.rsplit('.', 1)[0] + ".webp",
                file=buffer
            )
        except Exception:
            raise exceptions.ImageProcessingError
    return file
