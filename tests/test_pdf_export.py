"""Unit tests for the PDF report export module."""

import io
import os
import pytest

from exif_extractor import extract_exif
from exif_extractor.pdf_export import generate_pdf_report

SAMPLE_JPG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample.jpg")
CLEAN_PNG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "samples", "clean_export.png")


def test_pdf_export_with_full_exif_and_gps():
    """Verify PDF export on an image with rich EXIF and GPS data."""
    report = extract_exif(SAMPLE_JPG)
    with open(SAMPLE_JPG, "rb") as fh:
        raw_bytes = fh.read()
    
    pdf_bytes = generate_pdf_report(report, image_bytes=raw_bytes)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert b"%%EOF" in pdf_bytes
    assert len(pdf_bytes) > 2000


def test_pdf_export_without_exif():
    """Verify PDF export on a clean PNG image without EXIF."""
    report = extract_exif(CLEAN_PNG)
    with open(CLEAN_PNG, "rb") as fh:
        raw_bytes = fh.read()
    
    pdf_bytes = generate_pdf_report(report, image_bytes=raw_bytes)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1000


def test_pdf_export_without_image_preview():
    """Verify PDF export when raw image bytes are omitted."""
    report = extract_exif(SAMPLE_JPG)
    pdf_bytes = generate_pdf_report(report, image_bytes=None)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 2000
