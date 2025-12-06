"""Pytest configuration and fixtures"""
import pytest
from io import BytesIO
from PIL import Image


@pytest.fixture
def sample_jpeg_buffer():
    """Create a simple JPEG image in memory for testing"""
    img = Image.new('RGB', (800, 600), color='white')
    # Add some content to make it realistic
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "Sample Invoice", fill='black')

    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer


@pytest.fixture
def sample_png_buffer():
    """Create a simple PNG image in memory for testing"""
    img = Image.new('RGB', (800, 600), color='lightblue')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "Sample PNG Invoice", fill='black')

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


@pytest.fixture
def sample_large_image_buffer():
    """Create a large image for resize testing (4000x3000)"""
    img = Image.new('RGB', (4000, 3000), color='blue')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.text((100, 100), "Large Image", fill='white')

    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer


@pytest.fixture
def sample_small_image_buffer():
    """Create a small image that doesn't need resizing"""
    img = Image.new('RGB', (500, 400), color='green')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "Small Image", fill='white')

    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer


@pytest.fixture
def corrupted_buffer():
    """Create a corrupted file buffer for error testing

    Simulates corrupted binary data that looks like it might be an image
    but is actually garbage bytes.
    """
    # Binary data with invalid UTF-8 sequences
    # Mix of high-value bytes that can't be decoded as UTF-8
    buffer = BytesIO(b'\x80\x81\x82\x83\x84\xff\xfe\xfd\xfc' * 10)
    buffer.seek(0)
    return buffer


@pytest.fixture
def text_file_buffer():
    """Create a text file buffer (unsupported format)"""
    buffer = BytesIO(b'This is a text file, not an image')
    buffer.seek(0)
    return buffer
