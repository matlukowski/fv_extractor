"""Unit tests for Image Processor module (RED phase - tests first)"""
import pytest
import base64
from io import BytesIO
from PIL import Image
from src.processors.image_processor import (
    prepare_image_for_api,
    UnsupportedFormatError,
    CorruptedFileError
)


class TestPrepareImageFromJPEG:
    """Test JPEG image processing"""

    def test_prepare_image_from_jpeg(self, sample_jpeg_buffer):
        """Should process JPEG and return list with base64 string"""
        result = prepare_image_for_api(sample_jpeg_buffer)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], str)

        # Verify it's valid base64
        decoded = base64.b64decode(result[0])
        assert len(decoded) > 0

    def test_prepare_image_jpeg_creates_valid_image(self, sample_jpeg_buffer):
        """Should create base64 that can be decoded back to valid image"""
        result = prepare_image_for_api(sample_jpeg_buffer)

        # Decode base64 and load as image
        decoded = base64.b64decode(result[0])
        img = Image.open(BytesIO(decoded))

        assert img.format == 'JPEG'
        assert img.size[0] > 0
        assert img.size[1] > 0


class TestPrepareImageFromPNG:
    """Test PNG image processing"""

    def test_prepare_image_from_png(self, sample_png_buffer):
        """Should process PNG and return list with base64 string"""
        result = prepare_image_for_api(sample_png_buffer)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], str)

    def test_prepare_image_png_converts_to_jpeg(self, sample_png_buffer):
        """Should convert PNG to JPEG format"""
        result = prepare_image_for_api(sample_png_buffer)

        # Decode and verify format is JPEG
        decoded = base64.b64decode(result[0])
        img = Image.open(BytesIO(decoded))

        assert img.format == 'JPEG'


class TestImageResizing:
    """Test image resizing functionality"""

    def test_image_resizing_when_too_large(self, sample_large_image_buffer):
        """Should resize image when largest dimension > max_size"""
        result = prepare_image_for_api(sample_large_image_buffer, max_size=2000)

        # Decode and check size
        decoded = base64.b64decode(result[0])
        img = Image.open(BytesIO(decoded))

        # Largest dimension should be <= 2000
        assert max(img.size) <= 2000

    def test_image_resizing_preserves_aspect_ratio(self, sample_large_image_buffer):
        """Should preserve aspect ratio when resizing"""
        # Original is 4000x3000 (4:3 ratio)
        result = prepare_image_for_api(sample_large_image_buffer, max_size=2000)

        decoded = base64.b64decode(result[0])
        img = Image.open(BytesIO(decoded))

        # Should maintain 4:3 aspect ratio (within rounding)
        aspect_ratio = img.size[0] / img.size[1]
        expected_ratio = 4000 / 3000
        assert abs(aspect_ratio - expected_ratio) < 0.01

    def test_image_not_resized_when_small(self, sample_small_image_buffer):
        """Should not resize image if already smaller than max_size"""
        result = prepare_image_for_api(sample_small_image_buffer, max_size=2000)

        decoded = base64.b64decode(result[0])
        img = Image.open(BytesIO(decoded))

        # Should be close to original size (500x400)
        # Allow some tolerance for JPEG compression
        assert img.size[0] <= 500
        assert img.size[1] <= 400


class TestImageQuality:
    """Test JPEG quality compression"""

    def test_image_quality_compression(self, sample_jpeg_buffer):
        """Should apply specified JPEG quality"""
        result = prepare_image_for_api(sample_jpeg_buffer, jpeg_quality=85)

        # Just verify it produces valid output
        decoded = base64.b64decode(result[0])
        img = Image.open(BytesIO(decoded))
        assert img.format == 'JPEG'

    def test_image_quality_affects_size(self, sample_jpeg_buffer):
        """Lower quality should produce smaller file size"""
        result_high = prepare_image_for_api(sample_jpeg_buffer, jpeg_quality=95)
        result_low = prepare_image_for_api(sample_jpeg_buffer, jpeg_quality=50)

        size_high = len(base64.b64decode(result_high[0]))
        size_low = len(base64.b64decode(result_low[0]))

        # Lower quality should produce smaller file
        assert size_low < size_high


class TestBase64Encoding:
    """Test base64 encoding format"""

    def test_base64_encoding_format(self, sample_jpeg_buffer):
        """Should return valid base64 string"""
        result = prepare_image_for_api(sample_jpeg_buffer)

        # Should be able to decode without errors
        try:
            decoded = base64.b64decode(result[0])
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Base64 decoding failed: {e}")

    def test_base64_is_string(self, sample_jpeg_buffer):
        """Should return string, not bytes"""
        result = prepare_image_for_api(sample_jpeg_buffer)

        assert isinstance(result[0], str)


class TestErrorHandling:
    """Test error handling for invalid inputs"""

    def test_corrupted_file_raises_error(self, corrupted_buffer):
        """Should raise CorruptedFileError for corrupted files"""
        with pytest.raises(CorruptedFileError):
            prepare_image_for_api(corrupted_buffer)

    def test_unsupported_format_raises_error(self, text_file_buffer):
        """Should raise UnsupportedFormatError for non-image files"""
        with pytest.raises(UnsupportedFormatError):
            prepare_image_for_api(text_file_buffer)

    def test_empty_buffer_raises_error(self):
        """Should raise error for empty buffer"""
        empty_buffer = BytesIO(b'')

        with pytest.raises((CorruptedFileError, UnsupportedFormatError, ValueError)):
            prepare_image_for_api(empty_buffer)


class TestPDFProcessing:
    """Test PDF file processing"""

    @pytest.mark.skip(reason="PDF support requires pdf2image and poppler - will implement later")
    def test_prepare_image_from_single_page_pdf(self):
        """Should convert single-page PDF to image"""
        # Will implement when pdf2image is properly set up
        pass

    @pytest.mark.skip(reason="PDF support requires pdf2image and poppler")
    def test_prepare_image_from_multipage_pdf(self):
        """Should handle multi-page PDFs (extract first page or all pages)"""
        # Will implement when pdf2image is properly set up
        pass

    @pytest.mark.skip(reason="PDF support requires pdf2image and poppler")
    def test_password_protected_pdf_raises_error(self):
        """Should raise clear error for password-protected PDFs"""
        # Will implement when pdf2image is properly set up
        pass


class TestEdgeCases:
    """Test edge cases"""

    def test_very_small_image(self):
        """Should handle very small images (e.g., 10x10)"""
        img = Image.new('RGB', (10, 10), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)

        result = prepare_image_for_api(buffer)

        assert len(result) == 1
        assert isinstance(result[0], str)

    def test_square_image(self):
        """Should handle square images correctly"""
        img = Image.new('RGB', (1000, 1000), color='green')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)

        result = prepare_image_for_api(buffer)

        decoded = base64.b64decode(result[0])
        result_img = Image.open(BytesIO(decoded))

        # Should maintain square aspect ratio
        assert abs(result_img.size[0] - result_img.size[1]) < 2

    def test_grayscale_image(self):
        """Should handle grayscale images"""
        img = Image.new('L', (800, 600), color=128)
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)

        result = prepare_image_for_api(buffer)

        assert len(result) == 1
        # Should convert to RGB JPEG
        decoded = base64.b64decode(result[0])
        result_img = Image.open(BytesIO(decoded))
        assert result_img.mode in ['RGB', 'L']  # Either is acceptable
