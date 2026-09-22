"""Streamlit web frontend for the EXIF Metadata Extractor.

Run it with:

    streamlit run app.py

Drop an image on the main page (or in the sidebar), or pick one of the bundled
demo images, and the browser displays comprehensive EXIF metadata:
camera identity, capture settings, timestamps, GPS location with interactive
maps, visual color palette swatches, extended metadata, searchable tag explorer,
and in-memory privacy scrubbing.

Uploaded files are processed purely in-memory (never written to disk as temp files).
"""

from __future__ import annotations

import collections
import hashlib
import io
import json
import math
import mimetypes
import os
import sys
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from PIL import Image, ImageCms, ImageOps, ImageStat, UnidentifiedImageError
from PIL.ExifTags import GPSTAGS, TAGS
import streamlit as st

# Make the package importable no matter how the app is launched.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from exif_extractor.extractor import ExifError, ExifReport, GpsInfo, extract_exif
from exif_extractor.batch import build_batch_summary, build_comparison_dataframe
from exif_extractor.pdf_export import generate_pdf_report
from exif_extractor.extractor import (
    _parse_gps,
    _stringify,
    _tag_name,
)
from exif_extractor.formatter import _human_size
SAMPLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample.jpg")
SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
ACCEPTED_TYPES = ["jpg", "jpeg", "png", "webp", "tiff", "tif", "bmp", "gif"]
DEMO_EXTENSIONS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp", ".gif")

# Precompute reverse tag mappings for the Tag Explorer
TAG_NAME_TO_ID: Dict[str, int] = {v: k for k, v in TAGS.items()}
GPS_NAME_TO_ID: Dict[str, int] = {v: k for k, v in GPSTAGS.items()}


def discover_demo_images() -> Dict[str, str]:
    """Map demo label -> path for the bundled fixtures, if present."""
    demos = {}
    if os.path.exists(SAMPLE_PATH):
        demos["sample.jpg — full EXIF + GPS (Eiffel Tower)"] = SAMPLE_PATH
    if os.path.isdir(SAMPLES_DIR):
        for name in sorted(os.listdir(SAMPLES_DIR)):
            if name.lower().endswith(DEMO_EXTENSIONS):
                demos[name] = os.path.join(SAMPLES_DIR, name)
    return demos


def calculate_aspect_ratio(width: int, height: int) -> str:
    """Return a clean aspect ratio representation (e.g. 16:9, 4:3, 1:1)."""
    if height == 0:
        return "N/A"
    gcd = math.gcd(width, height)
    rw, rh = width // gcd, height // gcd
    if rw <= 32 and rh <= 32:
        return f"{rw}:{rh}"
    ratio = width / height
    if abs(ratio - 16 / 9) < 0.03:
        return "16:9"
    if abs(ratio - 4 / 3) < 0.03:
        return "4:3"
    if abs(ratio - 3 / 2) < 0.03:
        return "3:2"
    if abs(ratio - 1.0) < 0.01:
        return "1:1"
    return f"{ratio:.2f}:1"


def get_bit_depth(img: Image.Image) -> str:
    """Determine the human-friendly bit depth from a PIL Image."""
    mode_depths = {
        "1": "1-bit (B&W bilevel)",
        "L": "8-bit (Grayscale)",
        "P": "8-bit (Palette mapped)",
        "RGB": "24-bit (8-bit per channel RGB)",
        "RGBA": "32-bit (8-bit per channel RGBA)",
        "CMYK": "32-bit (8-bit per channel CMYK)",
        "YCbCr": "24-bit (YCbCr)",
        "I": "32-bit (Signed integer pixels)",
        "F": "32-bit (Floating point pixels)",
    }
    return mode_depths.get(img.mode, f"{len(img.getbands()) * 8}-bit ({img.mode})")


def decode_flash(val: Any) -> Optional[str]:
    """Decode EXIF Flash integer tag into human-readable description."""
    if val is None:
        return None
    try:
        code = int(val)
        flash_dict = {
            0x0000: "No Flash (did not fire)",
            0x0001: "Flash fired",
            0x0005: "Strobe return light not detected",
            0x0007: "Strobe return light detected",
            0x0009: "Flash fired, compulsory flash mode",
            0x000D: "Flash fired, compulsory mode, return not detected",
            0x000F: "Flash fired, compulsory mode, return detected",
            0x0010: "Flash did not fire, compulsory mode",
            0x0018: "Flash did not fire, auto mode",
            0x0019: "Flash fired, auto mode",
            0x001D: "Flash fired, auto mode, return not detected",
            0x001F: "Flash fired, auto mode, return detected",
            0x0020: "No flash function",
            0x0041: "Flash fired, red-eye reduction",
            0x0045: "Flash fired, red-eye reduction, return not detected",
            0x0047: "Flash fired, red-eye reduction, return detected",
            0x0049: "Flash fired, compulsory mode, red-eye reduction",
            0x004D: "Flash fired, compulsory mode, red-eye reduction, return not detected",
            0x004F: "Flash fired, compulsory mode, red-eye reduction, return detected",
            0x0059: "Flash fired, auto mode, red-eye reduction",
            0x005D: "Flash fired, auto mode, return not detected, red-eye reduction",
            0x005F: "Flash fired, auto mode, return detected, red-eye reduction",
        }
        return flash_dict.get(code, f"Flash status code: {code}")
    except (ValueError, TypeError):
        return str(val)


def decode_white_balance(val: Any) -> Optional[str]:
    """Decode WhiteBalance tag."""
    if val is None:
        return None
    try:
        code = int(val)
        return {0: "Auto white balance", 1: "Manual white balance"}.get(
            code, f"Mode {code}"
        )
    except (ValueError, TypeError):
        return str(val)


def decode_metering_mode(val: Any) -> Optional[str]:
    """Decode MeteringMode tag."""
    if val is None:
        return None
    try:
        code = int(val)
        metering_dict = {
            0: "Unknown",
            1: "Average",
            2: "Center-weighted average",
            3: "Spot",
            4: "Multi-spot",
            5: "Pattern / Multi-segment",
            6: "Partial",
            255: "Other",
        }
        return metering_dict.get(code, f"Mode {code}")
    except (ValueError, TypeError):
        return str(val)


def decode_exposure_program(val: Any) -> Optional[str]:
    """Decode ExposureProgram tag."""
    if val is None:
        return None
    try:
        code = int(val)
        prog_dict = {
            0: "Not defined",
            1: "Manual",
            2: "Normal / Program AE",
            3: "Aperture priority (AE)",
            4: "Shutter priority (AE)",
            5: "Creative program (depth of field)",
            6: "Action program (high shutter speed)",
            7: "Portrait mode",
            8: "Landscape mode",
        }
        return prog_dict.get(code, f"Program {code}")
    except (ValueError, TypeError):
        return str(val)


def classify_tag_group(tag_name: str) -> str:
    """Classify an EXIF tag into an intuitive logical category."""
    if tag_name.startswith("GPS") or tag_name in ("GPSInfo", "GPSLatitude", "GPSLongitude", "GPSAltitude"):
        return "📍 GPS & Geolocation"
    if tag_name in (
        "Make", "Model", "LensModel", "LensMake", "LensSpecification",
        "Software", "Artist", "Copyright", "HostComputer", "BodySerialNumber",
        "CameraOwnerName", "LensSerialNumber"
    ):
        return "📷 Device & Author"
    if tag_name in (
        "ExposureTime", "FNumber", "ISOSpeedRatings", "FocalLength",
        "FocalLengthIn35mmFilm", "Flash", "WhiteBalance", "MeteringMode",
        "ExposureProgram", "ExposureBiasValue", "MaxApertureValue",
        "LightSource", "DigitalZoomRatio", "SceneCaptureType", "ExposureMode"
    ):
        return "🎚️ Capture & Optics"
    if tag_name in (
        "DateTime", "DateTimeOriginal", "DateTimeDigitized",
        "SubsecTime", "SubsecTimeOriginal", "SubsecTimeDigitized",
        "OffsetTime", "OffsetTimeOriginal", "OffsetTimeDigitized"
    ):
        return "🕐 Timestamps"
    if tag_name in (
        "ExifImageWidth", "ExifImageHeight", "Orientation", "XResolution",
        "YResolution", "ResolutionUnit", "ColorSpace", "BitsPerSample", "Compression"
    ):
        return "📐 Geometry & Format"
    return "🗂️ Extended Metadata"


def extract_dominant_colors(
    img: Image.Image, num_colors: int = 6
) -> List[Dict[str, Any]]:
    """Compute dominant colors and percentages using Pillow MEDIANCUT quantization."""
    try:
        small = img.convert("RGB").resize((100, 100))
        palette_img = small.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
        palette = palette_img.getpalette()[: num_colors * 3]
        colors = [tuple(palette[i : i + 3]) for i in range(0, len(palette), 3)]
        counts = collections.Counter(palette_img.tobytes())
        total = sum(counts.values()) or 1

        results = []
        for idx, (r, g, b) in enumerate(colors):
            cnt = counts.get(idx, 0)
            pct = (cnt / total) * 100
            hex_code = f"#{r:02x}{g:02x}{b:02x}"
            # Perceived luminance for high-contrast text color
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            text_color = "#000000" if lum > 140 else "#ffffff"
            results.append(
                {
                    "hex": hex_code,
                    "rgb": f"RGB({r}, {g}, {b})",
                    "pct": pct,
                    "text_color": text_color,
                }
            )
        return results
    except Exception:
        return []


def create_scrubbed_image(pil_img: Image.Image) -> Tuple[bytes, str, str]:
    """Strip all EXIF, GPS, and metadata in-memory using Pillow.

    Returns:
        Tuple of (clean_bytes, filename_extension, mime_type)
    """
    # Exif transpose first so orientation is visually preserved before tag removal
    transposed = ImageOps.exif_transpose(pil_img)
    clean_img = Image.new(transposed.mode, transposed.size)
    clean_img.paste(transposed)

    raw_format = getattr(pil_img, "format", None) or "JPEG"
    fmt = raw_format if raw_format in ("JPEG", "PNG", "WEBP", "TIFF", "BMP", "GIF") else "JPEG"

    # JPEG does not support alpha / palette modes cleanly
    if fmt == "JPEG" and clean_img.mode in ("RGBA", "P", "LA"):
        clean_img = clean_img.convert("RGB")

    buf = io.BytesIO()
    if fmt == "JPEG":
        clean_img.save(buf, format="JPEG", quality=95)
        ext = ".jpg"
        mime = "image/jpeg"
    elif fmt == "PNG":
        clean_img.save(buf, format="PNG", optimize=True)
        ext = ".png"
        mime = "image/png"
    elif fmt == "WEBP":
        clean_img.save(buf, format="WEBP", quality=95)
        ext = ".webp"
        mime = "image/webp"
    else:
        clean_img.save(buf, format=fmt)
        ext = f".{fmt.lower()}"
        mime = f"image/{fmt.lower()}"

    return buf.getvalue(), ext, mime


def section_table(pairs: List[Tuple[str, Optional[str]]], empty_message: str) -> None:
    """Render a two-column Field/Value table, or a caption when all empty."""
    rows = [(label, str(value)) for label, value in pairs if value not in (None, "")]
    if not rows:
        st.caption(empty_message)
        return
    st.table(pd.DataFrame(rows, columns=["Field", "Value"]).set_index("Field"))


# ------------------------------------------------------------------ Page Config --
st.set_page_config(
    page_title="EXIF Metadata Extractor & Privacy Inspector",
    page_icon="🕵️",
    layout="wide",
)

# Initialize Session State
if "loaded_file_bytes" not in st.session_state:
    st.session_state["loaded_file_bytes"] = None
if "loaded_file_name" not in st.session_state:
    st.session_state["loaded_file_name"] = None
if "loaded_batch_files" not in st.session_state:
    st.session_state["loaded_batch_files"] = None
if "last_sidebar_uploader_id" not in st.session_state:
    st.session_state["last_sidebar_uploader_id"] = None

# ------------------------------------------------------------------ Sidebar UI --
st.sidebar.title("🕵️ EXIF Extractor")
st.sidebar.caption("OSINT / privacy tool — see what photos silently share.")

sidebar_uploaded = st.sidebar.file_uploader(
    "Upload image(s)",
    type=ACCEPTED_TYPES,
    accept_multiple_files=True,
    key="sidebar_uploader",
    help="Accepts JPG, JPEG, PNG, WEBP, TIFF, BMP, GIF. Select one or multiple images.",
)

demos = discover_demo_images()
demo_choice = None
if demos:
    demo_choice = st.sidebar.selectbox("…or pick a demo image", list(demos.keys()))

# The sidebar demo button is kept as the FIRST button for test harness stability
load_sample = st.sidebar.button("Load demo image", disabled=not demos, width="stretch")

has_loaded = (
    st.session_state["loaded_file_bytes"] is not None
    or st.session_state["loaded_batch_files"] is not None
)

if has_loaded:
    if st.sidebar.button("🔄 Analyze Another Image", key="sidebar_reset_btn", width="stretch"):
        st.session_state["loaded_file_bytes"] = None
        st.session_state["loaded_file_name"] = None
        st.session_state["loaded_batch_files"] = None
        st.rerun()

st.sidebar.divider()
st.sidebar.info("Only inspect images you own or have permission to analyze.")

# ------------------------------------------------------------ Input Resolution --
# 1. Check sidebar file uploader
if sidebar_uploaded:
    if isinstance(sidebar_uploaded, list):
        if len(sidebar_uploaded) == 1:
            u = sidebar_uploaded[0]
            sidebar_file_id = f"{u.name}_{u.size}"
            if st.session_state["last_sidebar_uploader_id"] != sidebar_file_id:
                st.session_state["last_sidebar_uploader_id"] = sidebar_file_id
                st.session_state["loaded_file_bytes"] = u.getvalue()
                st.session_state["loaded_file_name"] = u.name
                st.session_state["loaded_batch_files"] = None
        elif len(sidebar_uploaded) > 1:
            batch_id = "_".join(f"{u.name}_{u.size}" for u in sidebar_uploaded)
            if st.session_state["last_sidebar_uploader_id"] != batch_id:
                st.session_state["last_sidebar_uploader_id"] = batch_id
                st.session_state["loaded_batch_files"] = [(u.name, u.getvalue()) for u in sidebar_uploaded]
                st.session_state["loaded_file_bytes"] = None
                st.session_state["loaded_file_name"] = None
    else:
        u = sidebar_uploaded
        sidebar_file_id = f"{u.name}_{u.size}"
        if st.session_state["last_sidebar_uploader_id"] != sidebar_file_id:
            st.session_state["last_sidebar_uploader_id"] = sidebar_file_id
            st.session_state["loaded_file_bytes"] = u.getvalue()
            st.session_state["loaded_file_name"] = u.name
            st.session_state["loaded_batch_files"] = None

# 2. Check sidebar demo button
if load_sample and demo_choice and demo_choice in demos:
    demo_path = demos[demo_choice]
    with open(demo_path, "rb") as fh:
        st.session_state["loaded_file_bytes"] = fh.read()
    st.session_state["loaded_file_name"] = os.path.basename(demo_path)
    st.session_state["loaded_batch_files"] = None

file_bytes = st.session_state.get("loaded_file_bytes")
file_name = st.session_state.get("loaded_file_name")
batch_files = st.session_state.get("loaded_batch_files")

# ----------------------------------------------------------- Landing Page UI --
# Rendered prominently on the main page whenever no image is loaded
if file_bytes is None and not batch_files:
    st.title("🕵️ EXIF Metadata Extractor & Privacy Inspector")
    st.markdown(
        """
        Cameras and smartphones quietly embed **metadata (EXIF)** into every photograph you take:
        your specific camera model, serial numbers, exact timestamps, exposure configuration, and
        most dangerously — **precise GPS coordinates** revealing where you were standing.

        **Drop one or more images below** or select a quick test fixture to audit what information travels
        silently with your files.
        """
    )

    # Prominent Styled Drag-and-Drop Uploader on Main Page
    main_uploaded = st.file_uploader(
        "📁 Drag and drop image(s) here, or browse files",
        type=ACCEPTED_TYPES,
        accept_multiple_files=True,
        key="main_page_uploader",
        help="Supports JPG, JPEG, PNG, WEBP, TIFF, BMP, GIF. Select single or multiple images for batch comparison.",
    )

    st.markdown("##### ⚡ Quick Test Fixtures (Click to analyze instantly):")
    chip_col1, chip_col2, chip_col3, chip_col4 = st.columns(4)

    chip_clicked_path = None
    with chip_col1:
        if st.button("🗼 Sample (Eiffel Tower)", key="chip_eiffel", width="stretch"):
            chip_clicked_path = SAMPLE_PATH
    with chip_col2:
        if st.button("🗽 iPhone NYC", key="chip_nyc", width="stretch"):
            chip_clicked_path = os.path.join(SAMPLES_DIR, "iphone_nyc.jpg")
    with chip_col3:
        if st.button("🦘 Pixel Sydney", key="chip_sydney", width="stretch"):
            chip_clicked_path = os.path.join(SAMPLES_DIR, "pixel_sydney.jpg")
    with chip_col4:
        if st.button("🛡️ Clean PNG", key="chip_clean", width="stretch"):
            chip_clicked_path = os.path.join(SAMPLES_DIR, "clean_export.png")

    # Handle main uploader or chips
    if main_uploaded:
        if isinstance(main_uploaded, list):
            if len(main_uploaded) == 1:
                st.session_state["loaded_file_bytes"] = main_uploaded[0].getvalue()
                st.session_state["loaded_file_name"] = main_uploaded[0].name
                st.session_state["loaded_batch_files"] = None
                st.rerun()
            elif len(main_uploaded) > 1:
                st.session_state["loaded_batch_files"] = [(u.name, u.getvalue()) for u in main_uploaded]
                st.session_state["loaded_file_bytes"] = None
                st.session_state["loaded_file_name"] = None
                st.rerun()
        else:
            st.session_state["loaded_file_bytes"] = main_uploaded.getvalue()
            st.session_state["loaded_file_name"] = main_uploaded.name
            st.session_state["loaded_batch_files"] = None
            st.rerun()

    if chip_clicked_path and os.path.exists(chip_clicked_path):
        with open(chip_clicked_path, "rb") as fh:
            st.session_state["loaded_file_bytes"] = fh.read()
        st.session_state["loaded_file_name"] = os.path.basename(chip_clicked_path)
        st.session_state["loaded_batch_files"] = None
        st.rerun()

    st.markdown("---")
    feat1, feat2, feat3, feat4 = st.columns(4)
    with feat1:
        st.subheader("📷 Camera Specs")
        st.caption("Identify camera make, model, lens profile, software versions, and serials.")
    with feat2:
        st.subheader("🎚 Capture Settings")
        st.caption("Inspect aperture, shutter speed, ISO, focal length, flash, and metering.")
    with feat3:
        st.subheader("📍 GPS Geolocation")
        st.caption("Pinpoint coordinates on interactive maps and open direct map routes.")
    with feat4:
        st.subheader("🛡️ Privacy Scrubbing")
        st.caption("Strip all metadata in-memory with one click and download clean photos.")

    st.stop()

# ------------------------------------------------------------- Batch View --
if batch_files and len(batch_files) > 1:
    st.title(f"📦 Batch Analysis ({len(batch_files)} Images)")
    reports = []
    for b_name, b_bytes in batch_files:
        try:
            reports.append(extract_exif(b_bytes, file_name=b_name))
        except Exception:
            pass

    if reports:
        b_summary = build_batch_summary(reports)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Images", b_summary["total_count"])
        m2.metric("With GPS (High Risk)", f"{b_summary['with_gps_count']} 🚨")
        m3.metric("With EXIF", b_summary["with_exif_count"])
        m4.metric("Total File Size", _human_size(b_summary["total_file_size"]))

        st.markdown("#### 📊 Image Comparison Matrix")
        comp_df = build_comparison_dataframe(reports)
        st.dataframe(comp_df, width="stretch", hide_index=True)

        # Batch map if any GPS points
        map_points = [
            {"latitude": r.gps.latitude, "longitude": r.gps.longitude, "file": getattr(r, "file_path", "image")}
            for r in reports
            if getattr(r, "has_gps", False) and getattr(r, "gps", None) is not None
        ]
        if map_points:
            st.markdown("#### 🗺️ Geographic Distribution")
            st.map(pd.DataFrame(map_points))

        st.download_button(
            "⬇️ Download Batch Comparison (CSV)",
            data=comp_df.to_csv(index=False),
            file_name="batch_comparison.csv",
            mime="text/csv",
        )

        st.markdown("---")
        st.subheader("🔍 Deep-Dive Inspection (Inspect Individual File)")
        file_options = [r.file_path for r in reports]
        selected_file_name = st.selectbox("Select image to view complete 7-tab forensic breakdown:", file_options)
        selected_idx = file_options.index(selected_file_name)
        file_name, file_bytes = batch_files[selected_idx]
    else:
        st.error("No valid images could be parsed in this batch.")
        st.stop()

# ------------------------------------------------ Single File Processing --
if file_bytes is not None:
    try:
        report = extract_exif(file_bytes, file_name=file_name)
    except ExifError as exc:
        st.error(f"Could not read image: {exc}")
        if st.button("Try another image"):
            st.session_state["loaded_file_bytes"] = None
            st.session_state["loaded_file_name"] = None
            st.session_state["loaded_batch_files"] = None
            st.rerun()
        st.stop()

    # Open PIL image for visual inspection and rotation correction
    try:
        pil_image = Image.open(io.BytesIO(file_bytes))
        # Exif transpose so mobile photos taken in portrait mode are not rotated sideways
        transposed_preview = ImageOps.exif_transpose(pil_image)
    except Exception as exc:
        st.error(f"Could not decode image bytes: {exc}")
        st.stop()

    # Safe attribute access guarding against any ExifReport version
    all_tags = getattr(report, "all_tags", {}) or {}
    has_gps = bool(getattr(report, "has_gps", False) or getattr(report, "gps", None))
    has_exif = bool(getattr(report, "has_exif", False) or all_tags)
    img_format = getattr(report, "image_format", pil_image.format or "UNKNOWN")
    file_size_val = getattr(report, "file_size", len(file_bytes))
    img_w, img_h = pil_image.size
    megapixels = (img_w * img_h) / 1_000_000
    mp_str = f"{megapixels:.2f} MP" if megapixels >= 0.1 else f"{megapixels:.3f} MP"
    aspect_ratio_str = calculate_aspect_ratio(img_w, img_h)
    color_mode = pil_image.mode
    has_alpha = "Yes" if color_mode in ("RGBA", "LA", "PA") or ("transparency" in pil_image.info) else "No"
    bit_depth_str = get_bit_depth(pil_image)

    # --------------------------------------------------- Header & Privacy Banner --
    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.title(f"🕵️ {file_name}")
    with header_col2:
        if st.button("🔄 Analyze New Image", key="btn_reset_top", width="stretch"):
            st.session_state["loaded_file_bytes"] = None
            st.session_state["loaded_file_name"] = None
            st.rerun()

    st.markdown(
        f"**Format:** `{img_format}` &nbsp;|&nbsp; "
        f"**File Size:** `{_human_size(file_size_val)}` ({file_size_val:,} bytes)"
    )

    # Privacy Risk Badge
    if has_gps:
        st.error("🚨 **HIGH PRIVACY RISK — Leaks precise GPS location**")
        st.markdown(
            """
            * **Precise Coordinates Embedded:** This photo contains latitude and longitude coordinates pointing to where it was taken.
            * **Physical Safety Hazard:** Sharing this file directly can expose your home, workplace, school, or travel itinerary.
            * **Recommendation:** Use the **Export & Clean** tab below to scrub all geolocation metadata before sharing!
            """
        )
    elif has_exif or any(
        [
            getattr(report, "camera_make", None),
            getattr(report, "camera_model", None),
            getattr(report, "datetime_original", None),
            getattr(report, "software", None),
        ]
    ):
        st.warning("⚠️ **MEDIUM PRIVACY RISK — Contains device & capture metadata**")
        st.markdown(
            """
            * **Device Fingerprinting:** Reveals hardware make, model, lens info, and operating software.
            * **Timeline Exposure:** Contains precise timestamps of when the picture was captured.
            * **Location Safe:** No GPS coordinates were detected in this image.
            * **Recommendation:** If you require total anonymity, scrub metadata in the **Export & Clean** tab.
            """
        )
    else:
        st.success("✅ **LOW PRIVACY RISK — Safe to share**")
        st.markdown(
            """
            * **No Location Data:** Zero GPS coordinates or altitude values are present.
            * **Clean Metadata:** Device identifiers, serial numbers, and capture timestamps were stripped or never recorded.
            * **Safe for Publishing:** This photo is safe to share without silently leaking personal information.
            """
        )

    # Metric Columns
    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
    metric_col1.metric("Dimensions", f"{img_w} × {img_h} px")
    metric_col2.metric("Megapixels", mp_str)
    metric_col3.metric("Aspect Ratio", aspect_ratio_str)
    metric_col4.metric("Color Mode", color_mode)
    metric_col5.metric("Alpha Channel", has_alpha)

    # Preview and Headline Summary
    preview_col, summary_col = st.columns([2, 3])
    with preview_col:
        st.image(
            transposed_preview,
            caption=f"Preview: {file_name} ({img_w} × {img_h})",
            width="stretch",
        )
    with summary_col:
        st.subheader("📊 Headline Summary")
        summary_pairs = [
            ("Camera Make", getattr(report, "camera_make", None)),
            ("Camera Model", getattr(report, "camera_model", None)),
            ("Lens Model", getattr(report, "lens_model", None)),
            ("Software", getattr(report, "software", None)),
            ("Date Taken", getattr(report, "datetime_original", None)),
            ("Shutter Speed", f"{getattr(report, 'exposure_time', '')} s" if getattr(report, "exposure_time", None) else None),
            ("Aperture", f"f/{getattr(report, 'f_number', '')}" if getattr(report, "f_number", None) else None),
            ("ISO", getattr(report, "iso", None)),
            ("GPS Data", "Embedded (Coordinates present)" if has_gps else "None (No location)"),
            ("EXIF Tags", str(len(all_tags))),
        ]
        section_table(summary_pairs, "No headline metadata present.")

    # --------------------------------------------------------------------- Tabs --
    tab_overview, tab_camera, tab_gps, tab_visual, tab_extended, tab_tags, tab_export = st.tabs(
        [
            "📋 Overview & Specs",
            "📷 Camera & Capture",
            "📍 GPS & Location",
            "🎨 Visual & Colors",
            "🗂️ Extended Metadata",
            "🔍 Tag Explorer",
            "💾 Export & Clean",
        ]
    )

    # ------------------------------------------------ Tab 1: Overview & Specs --
    with tab_overview:
        st.subheader("📋 File Properties & Specifications")
        mime_type = mimetypes.guess_type(file_name)[0] or f"image/{img_format.lower()}"
        dpi_val = pil_image.info.get("dpi")
        if isinstance(dpi_val, tuple):
            dpi_str = f"{round(dpi_val[0])} × {round(dpi_val[1])} DPI"
        elif dpi_val:
            dpi_str = f"{dpi_val} DPI"
        elif all_tags.get("XResolution"):
            dpi_str = f"{all_tags.get('XResolution')} × {all_tags.get('YResolution', all_tags.get('XResolution'))} DPI"
        else:
            dpi_str = "72 × 72 (Standard screen)"

        n_frames = getattr(pil_image, "n_frames", 1)
        frame_str = f"{n_frames} {'(Animated)' if n_frames > 1 else '(Static single frame)'}"

        specs_pairs = [
            ("File Name", file_name),
            ("File Size", f"{_human_size(file_size_val)} ({file_size_val:,} bytes)"),
            ("MIME Type", mime_type),
            ("Image Format", img_format),
            ("Dimensions", f"{img_w} × {img_h} pixels"),
            ("Megapixels", mp_str),
            ("Aspect Ratio", aspect_ratio_str),
            ("Color Mode", color_mode),
            ("Bit Depth", bit_depth_str),
            ("Resolution / DPI", dpi_str),
            ("Frame Count", frame_str),
        ]
        section_table(specs_pairs, "No specifications available.")

        st.markdown("#### 🔐 Cryptographic Checksums (File Integrity)")
        hash_c1, hash_c2 = st.columns(2)
        with hash_c1:
            st.text_input("MD5 Hash", hashlib.md5(file_bytes).hexdigest(), disabled=True)
        with hash_c2:
            st.text_input("SHA-256 Hash", hashlib.sha256(file_bytes).hexdigest(), disabled=True)

    # ------------------------------------------------ Tab 2: Camera & Capture --
    with tab_camera:
        st.subheader("📷 Camera & Hardware")
        cam_hardware = [
            ("Make", getattr(report, "camera_make", None) or all_tags.get("Make")),
            ("Model", getattr(report, "camera_model", None) or all_tags.get("Model")),
            ("Lens", getattr(report, "lens_model", None) or all_tags.get("LensModel")),
            ("Software", getattr(report, "software", None) or all_tags.get("Software")),
        ]
        section_table(cam_hardware, "No camera or software tags present.")

        st.subheader("🎚️ Optics & Exposure Settings")
        shutter_val = getattr(report, "exposure_time", None) or all_tags.get("ExposureTime")
        aperture_val = getattr(report, "f_number", None) or all_tags.get("FNumber")
        iso_val = getattr(report, "iso", None) or all_tags.get("ISOSpeedRatings")
        focal_val = getattr(report, "focal_length", None) or all_tags.get("FocalLength")
        focal_35 = all_tags.get("FocalLengthIn35mmFilm")
        flash_val = decode_flash(all_tags.get("Flash"))
        wb_val = decode_white_balance(all_tags.get("WhiteBalance"))
        metering_val = decode_metering_mode(all_tags.get("MeteringMode"))
        prog_val = decode_exposure_program(all_tags.get("ExposureProgram"))

        cam_exposure = [
            ("Shutter Speed", f"{shutter_val} s" if shutter_val else None),
            ("Aperture", f"f/{aperture_val}" if aperture_val else None),
            ("ISO Speed", str(iso_val) if iso_val else None),
            ("Focal Length", f"{focal_val} mm" if focal_val else None),
            ("35mm Equivalent", f"{focal_35} mm" if focal_35 else None),
            ("Flash Status", flash_val),
            ("White Balance", wb_val),
            ("Metering Mode", metering_val),
            ("Exposure Program", prog_val),
        ]
        section_table(cam_exposure, "No exposure setting tags present.")

        st.subheader("🕐 Capture Timestamps")
        cam_timestamps = [
            ("Taken (Original)", getattr(report, "datetime_original", None) or all_tags.get("DateTimeOriginal")),
            ("Digitized", getattr(report, "datetime_digitized", None) or all_tags.get("DateTimeDigitized")),
            ("Modified", all_tags.get("DateTime")),
        ]
        section_table(cam_timestamps, "No datetime tags present.")

    # ------------------------------------------------ Tab 3: GPS & Location --
    with tab_gps:
        st.subheader("📍 Geolocation & Coordinates")
        if has_gps and getattr(report, "gps", None) is not None:
            gps: GpsInfo = report.gps
            lat = getattr(gps, "latitude", 0.0)
            lon = getattr(gps, "longitude", 0.0)
            dms_val = getattr(gps, "dms_string", "")
            alt_val = all_tags.get("GPSAltitude")

            # Decimal degree metric cards (used by automated smoke tests)
            lat_col, lon_col = st.columns(2)
            lat_col.metric("Latitude", f"{lat:.6f}°")
            lon_col.metric("Longitude", f"{lon:.6f}°")

            st.markdown(f"**DMS Coordinates:** `{dms_val}`")
            if alt_val:
                st.markdown(f"**Altitude:** `{alt_val} meters`")
            else:
                st.markdown("**Altitude:** Not recorded in GPS IFD")

            st.markdown("#### 🗺️ Interactive Satellite & Map View")
            map_data = pd.DataFrame([{"lat": lat, "lon": lon}])
            st.map(map_data, latitude="lat", longitude="lon", zoom=14)

            st.markdown("#### 🌐 OpenStreetMap Embedded View")
            osm_embed_url = (
                f"https://www.openstreetmap.org/export/embed.html"
                f"?bbox={lon-0.01:.6f}%2C{lat-0.01:.6f}%2C{lon+0.01:.6f}%2C{lat+0.01:.6f}"
                f"&layer=mapnik&marker={lat:.6f}%2C{lon:.6f}"
            )
            st.iframe(osm_embed_url, height=360)

            st.markdown("#### 🚀 External Map Navigation")
            gmaps_url = f"https://www.google.com/maps?q={lat:.6f},{lon:.6f}"
            apple_url = f"https://maps.apple.com/?q={lat:.6f},{lon:.6f}"
            osm_url = f"https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lon:.6f}#map=16/{lat:.6f}/{lon:.6f}"

            act1, act2, act3 = st.columns(3)
            act1.link_button("🌐 Open in Google Maps", gmaps_url, width="stretch")
            act2.link_button("🍎 Open in Apple Maps", apple_url, width="stretch")
            act3.link_button("🗺️ Open in OpenStreetMap", osm_url, width="stretch")
        else:
            st.success("✅ **No GPS location data found embedded in this image.**")
            st.caption("Coordinates, altitude, and location timestamps are completely absent.")

    # ------------------------------------------------ Tab 4: Visual & Colors --
    with tab_visual:
        st.subheader("🎨 Dominant Color Palette")
        st.caption("Quantized dominant color swatches computed directly from image pixels.")
        swatches = extract_dominant_colors(pil_image, num_colors=6)
        if swatches:
            swatches_html = '<div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 25px;">'
            for sw in swatches:
                swatches_html += (
                    f'<div style="flex: 1 1 120px; min-width: 110px; max-width: 170px; '
                    f'background-color: {sw["hex"]}; color: {sw["text_color"]}; '
                    f'padding: 14px 10px; border-radius: 8px; border: 1px solid rgba(0,0,0,0.15); '
                    f'box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center;">'
                    f'<div style="font-family: monospace; font-size: 1.05em; font-weight: 700;">{sw["hex"].upper()}</div>'
                    f'<div style="font-size: 0.8em; margin-top: 2px;">{sw["rgb"]}</div>'
                    f'<div style="font-size: 0.85em; font-weight: 600; margin-top: 5px;">{sw["pct"]:.1f}%</div>'
                    f'</div>'
                )
            swatches_html += "</div>"
            st.markdown(swatches_html, unsafe_allow_html=True)
        else:
            st.caption("Could not extract color palette.")

        st.subheader("💡 Tonal & Brightness Analysis")
        try:
            stat = ImageStat.Stat(pil_image.convert("L"))
            mean_brightness = stat.mean[0]
            rms_contrast = stat.rms[0]
            median_tone = stat.median[0]

            if mean_brightness < 80:
                tone_badge = "Low Key / Dark Exposure"
                tone_desc = "Predominantly shadow tones; typical of night, indoor moody, or underexposed shots."
            elif mean_brightness > 175:
                tone_badge = "High Key / Bright Exposure"
                tone_desc = "Predominantly bright tones; typical of outdoor sun, snow, or high exposure."
            else:
                tone_badge = "Balanced Exposure"
                tone_desc = "Evenly distributed midtones across the tonal range."

            b_c1, b_c2, b_c3, b_c4 = st.columns(4)
            b_c1.metric("Mean Brightness", f"{mean_brightness:.1f} / 255")
            b_c2.metric("Brightness %", f"{mean_brightness / 2.55:.1f}%")
            b_c3.metric("RMS Contrast", f"{rms_contrast:.1f}")
            b_c4.metric("Median Tone", f"{median_tone} / 255")

            st.info(f"**Exposure Character:** {tone_badge} — {tone_desc}")
        except Exception as exc:
            st.caption(f"Brightness analysis unavailable: {exc}")

    # ------------------------------------------------ Tab 5: Extended Metadata --
    with tab_extended:
        st.subheader("🗂️ PNG Chunks, AI Prompts & ICC Profiles")

        # 1. Check for PNG text chunks or AI prompts (Stable Diffusion, Midjourney, etc.)
        text_chunks: Dict[str, str] = {}
        if hasattr(pil_image, "text") and pil_image.text:
            text_chunks.update(pil_image.text)
        for k, v in pil_image.info.items():
            if isinstance(v, str) and k not in ("exif", "icc_profile", "photoshop"):
                text_chunks[k] = v

        ai_keywords = ("parameters", "prompt", "workflow", "sd-metadata", "generation_data")
        has_ai_prompt = any(k.lower() in ai_keywords for k in text_chunks)

        if has_ai_prompt:
            st.warning("🤖 **AI Generation Metadata Detected in Image Chunks!**")

        if text_chunks:
            st.markdown("##### Embedded Text Chunks / Parameters")
            for chunk_key, chunk_val in text_chunks.items():
                with st.expander(f"Chunk: {chunk_key}", expanded=chunk_key.lower() in ai_keywords):
                    st.code(chunk_val, language="text")
        else:
            st.caption("No embedded text chunks or AI generation prompts found.")

        # 2. ICC Color Profile
        st.markdown("##### 🎨 ICC Color Profile")
        icc_data = pil_image.info.get("icc_profile")
        if icc_data:
            profile_name = "Embedded Profile"
            try:
                profile_name = ImageCms.getProfileDescription(io.BytesIO(icc_data)).strip()
            except Exception:
                pass
            st.markdown(f"**Profile Description:** `{profile_name}`")
            st.markdown(f"**Profile Raw Size:** `{len(icc_data):,} bytes`")
        else:
            st.caption("No embedded ICC profile found (sRGB standard color space assumed).")

        # 3. Raw Info Dictionary
        st.markdown("##### 📦 Raw Image Container Metadata")
        raw_info_summary = {}
        for k, v in pil_image.info.items():
            if isinstance(v, bytes):
                raw_info_summary[k] = f"<binary blob: {len(v)} bytes>"
            else:
                raw_info_summary[k] = v
        if raw_info_summary:
            st.json(raw_info_summary)
        else:
            st.caption("No additional container metadata present.")

    # ------------------------------------------------ Tab 6: Tag Explorer --
    with tab_tags:
        st.subheader("🔍 Complete Tag Explorer")
        if all_tags:
            tag_rows = []
            for tag_name, tag_val in all_tags.items():
                raw_id = TAG_NAME_TO_ID.get(tag_name, GPS_NAME_TO_ID.get(tag_name))
                id_repr = f"0x{raw_id:04X} ({raw_id})" if isinstance(raw_id, int) else "—"
                group_label = classify_tag_group(tag_name)
                tag_rows.append(
                    {
                        "Tag Name": str(tag_name),
                        "Tag ID": id_repr,
                        "Group": group_label,
                        "Value": str(tag_val),
                    }
                )

            df_all_tags = pd.DataFrame(tag_rows)

            col_search, col_grp = st.columns([3, 1])
            with col_search:
                search_query = st.text_input(
                    "Search tags",
                    placeholder="Type tag name, ID, or value to filter...",
                    key="tag_search_field",
                )
            with col_grp:
                all_groups = ["All Groups"] + sorted(list(set(df_all_tags["Group"])))
                group_filter = st.selectbox("Filter Group", all_groups, key="tag_group_select")

            filtered_df = df_all_tags.copy()
            if group_filter != "All Groups":
                filtered_df = filtered_df[filtered_df["Group"] == group_filter]
            if search_query:
                query_lower = search_query.lower()
                mask = (
                    filtered_df["Tag Name"].str.lower().str.contains(query_lower)
                    | filtered_df["Tag ID"].str.lower().str.contains(query_lower)
                    | filtered_df["Value"].str.lower().str.contains(query_lower)
                )
                filtered_df = filtered_df[mask]

            st.dataframe(filtered_df, width="stretch", hide_index=True)
            st.caption(f"Showing {len(filtered_df)} of {len(df_all_tags)} total tags.")
        else:
            st.caption("No EXIF tags present in this image.")

    # ------------------------------------------------ Tab 7: Export & Clean --
    with tab_export:
        st.subheader("💾 Export Reports & Privacy Cleaning")
        base_file_name = os.path.splitext(file_name)[0]

        st.markdown("#### 1. Export Metadata Reports")
        export_col1, export_col2, export_col3 = st.columns(3)
        with export_col1:
            try:
                report_dict = asdict(report)
            except Exception:
                report_dict = {
                    "file_path": getattr(report, "file_path", file_name),
                    "file_size": file_size_val,
                    "image_format": img_format,
                    "image_size": [img_w, img_h],
                    "all_tags": all_tags,
                }
            json_dump = json.dumps(report_dict, indent=2, default=str)
            st.download_button(
                "⬇️ Download JSON Report",
                data=json_dump,
                file_name=f"{base_file_name}_exif.json",
                mime="application/json",
                width="stretch",
            )

        with export_col2:
            if all_tags:
                csv_dump = df_all_tags.to_csv(index=False)
            else:
                csv_dump = "Tag Name,Tag ID,Group,Value\n"
            st.download_button(
                "⬇️ Download CSV Tags",
                data=csv_dump,
                file_name=f"{base_file_name}_tags.csv",
                mime="text/csv",
                width="stretch",
            )

        with export_col3:
            try:
                pdf_bytes = generate_pdf_report(report, image_bytes=file_bytes)
                st.download_button(
                    "📄 Download Forensic PDF",
                    data=pdf_bytes,
                    file_name=f"{base_file_name}_forensic_report.pdf",
                    mime="application/pdf",
                    width="stretch",
                    help="Download a clean, multi-page PDF forensic report with checksums, settings, and maps.",
                )
            except Exception as pdf_err:
                st.caption(f"PDF export unavailable: {pdf_err}")

        st.markdown("---")
        st.markdown("#### 2. Scrub & Download Safe Clean Image")
        st.markdown(
            """
            Strip all embedded EXIF records, GPS coordinates, camera serial numbers, and device history.
            Processing is executed **strictly in-memory** and your photo is correctly oriented before
            metadata tags are removed.
            """
        )

        clean_bytes, clean_ext, clean_mime = create_scrubbed_image(pil_image)
        clean_out_name = f"clean_{base_file_name}{clean_ext}"

        st.download_button(
            "🛡️ Download Cleaned Image (Scrub Metadata)",
            data=clean_bytes,
            file_name=clean_out_name,
            mime=clean_mime,
            type="primary",
            width="stretch",
            help="Download this image with 100% of EXIF, GPS, and personal metadata removed.",
        )

        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Original Size", _human_size(len(file_bytes)))
        sc2.metric("Cleaned Size", _human_size(len(clean_bytes)))
        sc3.metric("Metadata Tags Removed", len(all_tags))
