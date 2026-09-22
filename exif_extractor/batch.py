"""Batch and multi-image analysis for EXIF reports.

Provides summary aggregation and structured comparison DataFrames across
multiple image inspection results.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import pandas as pd

from .extractor import ExifReport
from .formatter import _human_size


def format_camera_name(report: ExifReport) -> Optional[str]:
    """Format camera make and model cleanly, avoiding duplicate manufacturer names."""
    make = getattr(report, "camera_make", None)
    model = getattr(report, "camera_model", None)
    if make and model:
        make_str = str(make).strip()
        model_str = str(model).strip()
        if make_str.lower() in model_str.lower():
            return model_str
        return f"{make_str} {model_str}"
    if model:
        return str(model).strip()
    if make:
        return str(make).strip()
    return None


def build_batch_summary(reports: List[ExifReport]) -> Dict[str, Any]:
    """Build high-level aggregate summary statistics across a batch of ExifReports.

    Args:
        reports: List of parsed ExifReport instances.

    Returns:
        Dict containing total_count, with_gps_count, with_exif_count,
        total_file_size, unique_cameras, and privacy_breakdown.
    """
    total_count = len(reports)
    with_gps_count = sum(
        1
        for r in reports
        if getattr(r, "has_gps", False) or getattr(r, "gps", None) is not None
    )
    with_exif_count = sum(
        1
        for r in reports
        if getattr(r, "has_exif", False) or bool(getattr(r, "all_tags", None))
    )
    total_file_size = sum(getattr(r, "file_size", 0) for r in reports)

    unique_cameras: List[str] = []
    seen_cameras = set()
    for r in reports:
        cam = format_camera_name(r)
        if cam and cam not in seen_cameras:
            seen_cameras.add(cam)
            unique_cameras.append(cam)

    privacy_breakdown: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in reports:
        risk = getattr(r, "privacy_risk", "LOW") or "LOW"
        risk_str = str(risk).upper()
        if risk_str in privacy_breakdown:
            privacy_breakdown[risk_str] += 1
        else:
            privacy_breakdown[risk_str] = privacy_breakdown.get(risk_str, 0) + 1

    return {
        "total_count": total_count,
        "total_images": total_count,
        "with_gps_count": with_gps_count,
        "with_exif_count": with_exif_count,
        "total_file_size": total_file_size,
        "unique_cameras": unique_cameras,
        "privacy_breakdown": privacy_breakdown,
    }


def build_comparison_dataframe(reports: List[ExifReport]) -> pd.DataFrame:
    """Build a consolidated comparison pandas DataFrame from a list of ExifReports.

    Columns:
        "File Name", "Format", "Dimensions", "MP", "File Size",
        "Camera", "Date Taken", "GPS", "Privacy Risk", "MD5".

    Args:
        reports: List of parsed ExifReport instances.

    Returns:
        pd.DataFrame containing side-by-side comparison data.
    """
    columns = [
        "File Name",
        "Format",
        "Dimensions",
        "MP",
        "File Size",
        "Camera",
        "Date Taken",
        "GPS",
        "Privacy Risk",
        "MD5",
    ]
    if not reports:
        return pd.DataFrame(columns=columns)

    rows = []
    for r in reports:
        file_path = getattr(r, "file_path", None)
        file_name = os.path.basename(file_path) if file_path else "Unknown"

        image_format = getattr(r, "image_format", "UNKNOWN") or "UNKNOWN"

        image_size = getattr(r, "image_size", None)
        if image_size and len(image_size) == 2:
            dimensions = f"{image_size[0]} × {image_size[1]}"
        else:
            dimensions = "—"

        mp = getattr(r, "megapixels", None)
        if mp is not None:
            mp_val = round(float(mp), 2)
        elif image_size and len(image_size) == 2:
            mp_val = round((image_size[0] * image_size[1]) / 1_000_000, 2)
        else:
            mp_val = 0.0

        file_size = getattr(r, "file_size", 0)
        file_size_str = _human_size(file_size) if file_size else "0 B"

        camera = format_camera_name(r) or "—"
        date_taken = getattr(r, "datetime_original", None) or "—"

        gps_info = getattr(r, "gps", None)
        has_gps = getattr(r, "has_gps", False) or gps_info is not None
        if has_gps and gps_info:
            gps_str = f"{gps_info.latitude:.4f}, {gps_info.longitude:.4f}"
        else:
            gps_str = "—"

        privacy_risk = getattr(r, "privacy_risk", "LOW") or "LOW"
        md5_val = getattr(r, "md5", None) or "—"

        rows.append(
            {
                "File Name": file_name,
                "Format": image_format,
                "Dimensions": dimensions,
                "MP": mp_val,
                "File Size": file_size_str,
                "Camera": camera,
                "Date Taken": date_taken,
                "GPS": gps_str,
                "Privacy Risk": privacy_risk,
                "MD5": md5_val,
            }
        )

    return pd.DataFrame(rows, columns=columns)
