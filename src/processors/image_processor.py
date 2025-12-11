"""Image processor for invoice files (PDF, JPG, PNG)"""
import base64
from io import BytesIO
from typing import List
from PIL import Image
import os
import fitz  # PyMuPDF


class UnsupportedFormatError(Exception):
    """Raised when file format is not supported"""
    pass


class CorruptedFileError(Exception):
    """Raised when file is corrupted or cannot be processed"""
    pass


class PasswordProtectedPDFError(Exception):
    """Raised when PDF is password-protected and requires authentication"""
    pass


def prepare_image_for_api(
    file_buffer: BytesIO,
    max_size: int = 2000,
    jpeg_quality: int = 85,
    password: str | None = None
) -> List[str]:
    """
    Prepare image(s) for AI Vision API by optimizing and encoding to base64.

    Handles JPEG, PNG, and PDF files. Images are:
    - Resized if too large (max dimension = max_size)
    - Converted to JPEG format
    - Compressed with specified quality
    - Encoded to base64 string

    Args:
        file_buffer: File buffer containing image or PDF
        max_size: Maximum dimension size in pixels (default: 2000)
        jpeg_quality: JPEG compression quality 0-100 (default: 85)
        password: Optional password for encrypted PDFs (default: None)

    Returns:
        List of base64-encoded image strings (1 for images, N for PDF pages)

    Raises:
        UnsupportedFormatError: If file format is not supported
        CorruptedFileError: If file is corrupted or cannot be read
        PasswordProtectedPDFError: If PDF is encrypted and password is missing/invalid

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
            # Convert all PDF pages to images
            try:
                pdf_images = _convert_pdf_to_images(file_buffer, dpi=300, password=password)

                # Optimize each page individually
                optimized_images = []
                for img in pdf_images:
                    optimized_b64 = _optimize_image(img, max_size, jpeg_quality)
                    optimized_images.append(optimized_b64)

                return optimized_images

            except (UnsupportedFormatError, CorruptedFileError, PasswordProtectedPDFError):
                raise
            except ImportError:
                raise UnsupportedFormatError(
                    "PDF support requires PyMuPDF library. "
                    "Install with: pip install PyMuPDF"
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
    except PasswordProtectedPDFError:
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


def _convert_pdf_to_images(
    pdf_buffer: BytesIO,
    dpi: int = 300,
    password: str | None = None
) -> List[Image.Image]:
    """
    Convert PDF pages to PIL Images using PyMuPDF.

    Converts ALL pages from PDF to high-quality images for AI processing.

    Args:
        pdf_buffer: BytesIO buffer containing PDF file
        dpi: DPI for rendering (default: 300 for high quality OCR)
        password: Optional password for encrypted PDFs (default: None)

    Returns:
        List of PIL Image objects (RGB mode), one per page

    Raises:
        CorruptedFileError: If PDF is corrupted or cannot be opened
        PasswordProtectedPDFError: If PDF is encrypted and password is missing/invalid
    """
    pdf_buffer.seek(0)

    try:
        # Open PDF from buffer
        pdf_document = fitz.open(stream=pdf_buffer.read(), filetype="pdf")

        # Check if PDF is encrypted/password-protected
        if pdf_document.is_encrypted:
            # Try empty password first (common edge case)
            if pdf_document.authenticate(""):
                # Success with empty password - continue
                pass
            elif password is None:
                # No password provided - need user input
                pdf_document.close()
                raise PasswordProtectedPDFError(
                    "PDF is password-protected. Please provide password."
                )
            else:
                # Try user-provided password
                auth_result = pdf_document.authenticate(password)

                if not auth_result:
                    # Wrong password
                    pdf_document.close()
                    raise PasswordProtectedPDFError(
                        "Invalid password. Please try again."
                    )
                # Password correct - continue processing

        # Check for empty PDF
        page_count = pdf_document.page_count
        if page_count == 0:
            pdf_document.close()
            raise CorruptedFileError("PDF file has no pages")

        # Convert each page to image
        images = []
        zoom = dpi / 72  # PyMuPDF uses 72 DPI as base
        matrix = fitz.Matrix(zoom, zoom)

        for page_num in range(page_count):
            page = pdf_document[page_num]

            # Render page to pixmap
            pix = page.get_pixmap(matrix=matrix)

            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(BytesIO(img_data))

            # Ensure RGB mode
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            images.append(img)

        pdf_document.close()
        return images

    except fitz.FileDataError as e:
        raise CorruptedFileError(f"PDF file is corrupted or invalid: {str(e)}")
    except PasswordProtectedPDFError:
        raise
    except UnsupportedFormatError:
        raise
    except Exception as e:
        raise CorruptedFileError(f"Failed to process PDF: {str(e)}")


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
