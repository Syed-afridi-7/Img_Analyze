"""Unit tests for the batch analysis module."""

import os
import pytest
import pandas as pd

from exif_extractor import (
    extract_exif,
    build_batch_summary,
    build_comparison_dataframe,
)

SAMPLE_JPG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample.jpg")
CLEAN_PNG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "samples", "clean_export.png")
SYDNEY_JPG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "samples", "pixel_sydney.jpg")


def test_batch_summary_empty():
    """Verify batch summary on empty list."""
    summary = build_batch_summary([])
    assert summary["total_count"] == 0
    assert summary["with_gps_count"] == 0
    assert summary["with_exif_count"] == 0
    assert summary["unique_cameras"] == []


def test_batch_summary_multiple_images():
    """Verify aggregate metrics across multiple images."""
    r1 = extract_exif(SAMPLE_JPG)
    r2 = extract_exif(CLEAN_PNG)
    r3 = extract_exif(SYDNEY_JPG)

    summary = build_batch_summary([r1, r2, r3])
    assert summary["total_count"] == 3
    assert summary["with_gps_count"] == 2  # sample and sydney
    assert summary["with_exif_count"] >= 2
    assert summary["total_file_size"] > 0
    assert len(summary["unique_cameras"]) >= 2
    assert "HIGH" in summary["privacy_breakdown"]
    assert "LOW" in summary["privacy_breakdown"]


def test_build_comparison_dataframe():
    """Verify structured DataFrame comparison across images."""
    r1 = extract_exif(SAMPLE_JPG)
    r2 = extract_exif(CLEAN_PNG)

    df = build_comparison_dataframe([r1, r2])
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "File Name" in df.columns
    assert "Format" in df.columns
    assert "Dimensions" in df.columns
    assert "Privacy Risk" in df.columns
    assert "Camera" in df.columns

    # Row 0 (sample.jpg) should have AcmeCam and HIGH risk
    assert "sample.jpg" in df.iloc[0]["File Name"]
    assert df.iloc[0]["Privacy Risk"] == "HIGH"

    # Row 1 (clean_export.png) should be LOW risk
    assert "clean_export.png" in df.iloc[1]["File Name"]
    assert df.iloc[1]["Privacy Risk"] == "LOW"
