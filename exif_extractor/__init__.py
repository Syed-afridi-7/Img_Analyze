"""EXIF Metadata Extractor - an OSINT tool that reveals what cameras hide in photos."""

from .extractor import ExifError, ExifReport, GpsInfo, extract_exif
from .gps import (
    apple_maps_link,
    dms_to_decimal,
    google_maps_link,
    openstreetmap_link,
)
from .batch import (
    build_batch_summary,
    build_comparison_dataframe,
)
from .pdf_export import generate_pdf_report

__version__ = "1.2.0"

__all__ = [
    "ExifError",
    "ExifReport",
    "GpsInfo",
    "extract_exif",
    "dms_to_decimal",
    "google_maps_link",
    "openstreetmap_link",
    "apple_maps_link",
    "build_batch_summary",
    "build_comparison_dataframe",
    "generate_pdf_report",
]
