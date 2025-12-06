"""Image processor for invoice files (PDF, JPG, PNG)"""
import base64
from io import BytesIO
from typing import List
from PIL import Image
import os


class UnsupportedFormatError(Exception):
    """Raised when file format is not supported"""
    pass


class CorruptedFileError(Exception):
    """Raised when file is corrupted or cannot be processed"""
    pass


def prepare_image_for_api(
    file_buffer: BytesIO,
    max_size: int = 2000,
    jpeg_quality: int = 85
) -> List[str]:
    """
    Prepare image(s) for AI Vision API by optimizing and encoding to base64.

    Handles JPEG, PNG, and (future) PDF files. Images are:
    - Resized if too large (max dimension = max_size)
    - Converted to JPEG format
    - Compressed with specified quality
    - Encoded to base64 string

    Args:
        file_buffer: File buffer containing image or PDF
        max_size: Maximum dimension size in pixels (default: 2000)
        jpeg_quality: JPEG compression quality 0-100 (default: 85)

    Returns:
        List of base64-encoded image strings (1 for images, N for PDF pages)

    Raises:
        UnsupportedFormatError: If file format is not supported
        CorruptedFileError: If file is corrupted or cannot be read

    Examples:
        >>> with open('invoice.jpg', 'rb') as f:
        ...     buffer = BytesIO(f.read())
        >>> images = prepare_image_for_api(buffer)
        >>> len(images)
        1
    """
    file_buffer.seek(0)

    try:
        # Try to detect format and load image
        file_type = _detect_file_type(file_buffer)

        if file_type == 'pdf':
            # PDF support (future implementation)
            raise UnsupportedFormatError(
                "PDF support requires pdf2image library and poppler. "
                "Currently only JPEG and PNG are supported."
            )
        elif file_type in ['jpeg', 'jpg', 'png']:
            # Load as image
            img = Image.open(file_buffer)
            optimized_b64 = _optimize_image(img, max_size, jpeg_quality)
            return [optimized_b64]
        elif file_type == 'text':
            # Text files are clearly not images
            raise UnsupportedFormatError(
                "Text files are not supported. Supported formats: JPEG, PNG"
            )
        elif file_type == 'unknown':
            # Could be corrupted image file
            raise CorruptedFileError(
                "File appears to be corrupted or is not a valid image format"
            )
        else:
            raise UnsupportedFormatError(
                f"Unsupported file format: {file_type}. "
                f"Supported formats: JPEG, PNG"
            )

    except UnsupportedFormatError:
        raise
    except CorruptedFileError:
        raise
    except Exception as e:
        # Catch-all for PIL errors, file read errors, etc.
        raise CorruptedFileError(
            f"File is corrupted or cannot be processed: {str(e)}"
        )


def _detect_file_type(buffer: BytesIO) -> str:
    """
    Detect file type from buffer magic bytes.

    Args:
        buffer: File buffer

    Returns:
        File type as string ('jpeg', 'png', 'pdf', 'text', 'unknown')
    """
    buffer.seek(0)
    header = buffer.read(16)
    buffer.seek(0)

    if not header:
        raise CorruptedFileError("Empty file")

    # Check magic bytes
    if header.startswith(b'\xff\xd8\xff'):
        return 'jpeg'
    elif header.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    elif header.startswith(b'%PDF'):
        return 'pdf'
    else:
        # Check if it's likely text/ASCII
        try:
            header.decode('utf-8')
            # If it decodes as UTF-8, it's likely a text file
            return 'text'
        except UnicodeDecodeError:
            pass

        # Try to let PIL detect it
        try:
            buffer.seek(0)
            img = Image.open(buffer)
            buffer.seek(0)
            return img.format.lower() if img.format else 'unknown'
        except:
            return 'unknown'


def _optimize_image(
    img: Image.Image,
    max_size: int,
    quality: int
) -> str:
    """
    Optimize image: resize if needed, convert to JPEG, encode to base64.

    Args:
        img: PIL Image object
        max_size: Maximum dimension size
        quality: JPEG quality (0-100)

    Returns:
        Base64-encoded JPEG string
    """
    # Convert to RGB if needed (for PNG with transparency, grayscale, etc.)
    if img.mode not in ('RGB', 'L'):
        # Convert RGBA to RGB with white background
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        else:
            img = img.convert('RGB')

    # Resize if too large
    if max(img.size) > max_size:
        img = _resize_image(img, max_size)

    # Convert to JPEG and encode to base64
    output_buffer = BytesIO()
    img.save(output_buffer, format='JPEG', quality=quality, optimize=True)
    output_buffer.seek(0)

    # Encode to base64
    image_bytes = output_buffer.read()
    base64_string = base64.b64encode(image_bytes).decode('utf-8')

    return base64_string


def _resize_image(img: Image.Image, max_size: int) -> Image.Image:
    """
    Resize image while maintaining aspect ratio.

    Args:
        img: PIL Image object
        max_size: Maximum dimension size

    Returns:
        Resized PIL Image
    """
    width, height = img.size

    # Calculate new dimensions
    if width > height:
        new_width = max_size
        new_height = int((max_size / width) * height)
    else:
        new_height = max_size
        new_width = int((max_size / height) * width)

    # Resize with high-quality algorithm
    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return resized
