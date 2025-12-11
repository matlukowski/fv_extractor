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


@pytest.fixture
def sample_pdf_buffer():
    """Create a single-page PDF for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
    except ImportError:
        pytest.skip("reportlab not installed")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 750, "FAKTURA VAT")
    c.drawString(100, 700, "Nr: FV001/2025")
    c.drawString(100, 650, "Data: 2025-01-15")
    c.drawString(100, 600, "Sprzedawca: Test Company")
    c.drawString(100, 550, "NIP: 1234567890")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


@pytest.fixture
def sample_multipage_pdf_buffer():
    """Create a 3-page PDF for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
    except ImportError:
        pytest.skip("reportlab not installed")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Page 1
    c.drawString(100, 750, "FAKTURA - Strona 1/3")
    c.drawString(100, 700, "Nr: FV002/2025")
    c.showPage()

    # Page 2
    c.drawString(100, 750, "Strona 2/3 - Pozycje")
    c.drawString(100, 700, "1. Usługa - 5000 PLN")
    c.showPage()

    # Page 3
    c.drawString(100, 750, "Strona 3/3")
    c.drawString(100, 700, "Suma: 5000 PLN")
    c.showPage()

    c.save()
    buffer.seek(0)
    return buffer


@pytest.fixture
def password_protected_pdf_buffer():
    """Create password-protected PDF for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from PyPDF2 import PdfReader, PdfWriter
    except ImportError:
        pytest.skip("reportlab or PyPDF2 not installed")

    # Create normal PDF
    temp_buffer = BytesIO()
    c = canvas.Canvas(temp_buffer, pagesize=A4)
    c.drawString(100, 750, "Protected Invoice")
    c.save()
    temp_buffer.seek(0)

    # Encrypt it
    reader = PdfReader(temp_buffer)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(user_password="secret123")

    encrypted_buffer = BytesIO()
    writer.write(encrypted_buffer)
    encrypted_buffer.seek(0)
    return encrypted_buffer


@pytest.fixture
def sample_pdf_password():
    """Password for protected PDF fixture"""
    return "secret123"


@pytest.fixture
def sample_pdf_wrong_password():
    """Wrong password for testing authentication failure"""
    return "wrongpassword"
