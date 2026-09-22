"""Comprehensive test suite for EXIF and image metadata extraction.

Tests core extraction logic in exif_extractor:
- extract_exif with file paths, raw bytes, and BytesIO
- cryptographic hashes (md5, sha1, sha256)
- dimensions, megapixels, aspect ratios, color modes, and depth
- clean PNG handling and text chunks
- sample.jpg EXIF tags, GPS links, and decoded settings
- dominant colors extraction and luminance/brightness calculation
- enum decoders (exposure program, metering mode, flash bitmask, white balance,
  light source, orientation, focal length 35mm, altitude)
- privacy risk assessment (HIGH, MEDIUM, LOW)
- backward compatibility with existing data structures and serializers
"""

from __future__ import annotations

import hashlib
import io
import os
import tempfile
from dataclasses import asdict
import json
import pytest
from PIL import Image, ImageCms, PngImagePlugin
import piexif

from exif_extractor import (
    ExifError,
    ExifReport,
    GpsInfo,
    apple_maps_link,
    dms_to_decimal,
    extract_exif,
    google_maps_link,
    openstreetmap_link,
)
from exif_extractor.extractor import (
    calculate_aspect_ratio,
    calculate_brightness,
    decode_flash,
    extract_dominant_colors,
    get_color_depth,
    headline_tag_names,
    parse_datetime,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_JPG = os.path.join(REPO_ROOT, "sample.jpg")
CLEAN_PNG = os.path.join(REPO_ROOT, "samples", "clean_export.png")
DSLR_JPG = os.path.join(REPO_ROOT, "samples", "dslr_landscape.jpg")
SYDNEY_JPG = os.path.join(REPO_ROOT, "samples", "pixel_sydney.jpg")


# -----------------------------------------------------------------------------
# 1. Source Handling: File Path, Raw Bytes, BytesIO, and Error Cases
# -----------------------------------------------------------------------------

def test_extract_from_file_path():
    """Extracting via file path string returns a valid ExifReport."""
    assert os.path.exists(SAMPLE_JPG), "sample.jpg fixture missing"
    report = extract_exif(SAMPLE_JPG)

    assert isinstance(report, ExifReport)
    assert report.file_path == SAMPLE_JPG
    assert report.file_size == os.path.getsize(SAMPLE_JPG)
    assert report.image_format.upper() in ("JPEG", "JPG")
    assert report.image_size == (640, 480)


def test_extract_from_raw_bytes():
    """Extracting via raw bytes works with and without explicit file_name."""
    with open(SAMPLE_JPG, "rb") as f:
        data = f.read()

    # With custom file_name
    report1 = extract_exif(data, file_name="uploaded_photo.jpg")
    assert report1.file_path == "uploaded_photo.jpg"
    assert report1.file_size == len(data)
    assert report1.image_size == (640, 480)
    assert report1.camera_make == "AcmeCam"

    # Without file_name
    report2 = extract_exif(data)
    assert report2.file_path == "<in-memory>"
    assert report2.file_size == len(data)
    assert report2.has_gps is True


def test_extract_from_bytesio():
    """Extracting via BytesIO stream."""
    with open(SAMPLE_JPG, "rb") as f:
        buf = io.BytesIO(f.read())

    report = extract_exif(buf, file_name="streamed.jpg")
    assert report.file_path == "streamed.jpg"
    assert report.image_size == (640, 480)
    assert report.camera_model == "X-200"


def test_extract_backwards_compatible_kwarg():
    """extract_exif(file_path=...) keyword argument still works."""
    report = extract_exif(file_path=SAMPLE_JPG)
    assert report.file_path == SAMPLE_JPG
    assert report.camera_make == "AcmeCam"


def test_extract_invalid_sources():
    """Invalid or missing sources raise ExifError."""
    with pytest.raises(ExifError, match="File not found"):
        extract_exif("this_file_does_not_exist_at_all.jpg")

    with pytest.raises(ExifError, match="Empty image data"):
        extract_exif(b"")

    with pytest.raises(ExifError, match="Could not read image"):
        extract_exif(b"not an image at all garbage bytes")

    with pytest.raises(ExifError, match="No image source provided"):
        extract_exif(None)


# -----------------------------------------------------------------------------
# 2. Cryptographic Hashes
# -----------------------------------------------------------------------------

def test_cryptographic_hashes():
    """MD5, SHA-1, and SHA-256 hashes are computed as lowercase hex strings."""
    with open(SAMPLE_JPG, "rb") as f:
        data = f.read()

    report = extract_exif(data)

    expected_md5 = hashlib.md5(data).hexdigest()
    expected_sha1 = hashlib.sha1(data).hexdigest()
    expected_sha256 = hashlib.sha256(data).hexdigest()

    assert report.md5 == expected_md5
    assert len(report.md5) == 32
    assert report.sha1 == expected_sha1
    assert len(report.sha1) == 40
    assert report.sha256 == expected_sha256
    assert len(report.sha256) == 64


# -----------------------------------------------------------------------------
# 3. Image Geometry, Dimensions, Megapixels, Aspect Ratio, and Modes
# -----------------------------------------------------------------------------

def test_dimensions_and_megapixels():
    """Dimensions and megapixels calculations."""
    report = extract_exif(SAMPLE_JPG)
    assert report.image_size == (640, 480)
    # 640 * 480 = 307,200 -> 0.31 megapixels
    assert report.megapixels == 0.31
    assert report.aspect_ratio_str == "4:3"


@pytest.mark.parametrize(
    "width,height,expected_ratio",
    [
        (1920, 1080, "16:9"),
        (1280, 720, "16:9"),
        (1024, 768, "4:3"),
        (800, 600, "4:3"),
        (1200, 800, "3:2"),
        (900, 600, "3:2"),
        (500, 500, "1:1"),
        (1000, 800, "5:4"),
        (1080, 1920, "9:16"),
    ],
)
def test_aspect_ratio_calculations(width, height, expected_ratio):
    """Aspect ratio string helper identifies standard and simplified ratios."""
    assert calculate_aspect_ratio(width, height) == expected_ratio


def test_color_modes_and_alpha():
    """Verify color modes, descriptive color depth, and alpha channel detection."""
    # RGB image
    rgb_img = Image.new("RGB", (64, 64), (10, 20, 30))
    buf_rgb = io.BytesIO()
    rgb_img.save(buf_rgb, "PNG")
    rep_rgb = extract_exif(buf_rgb.getvalue())
    assert rep_rgb.color_mode == "RGB"
    assert "24-bit" in rep_rgb.color_depth
    assert rep_rgb.has_alpha is False

    # RGBA image
    rgba_img = Image.new("RGBA", (64, 64), (10, 20, 30, 128))
    buf_rgba = io.BytesIO()
    rgba_img.save(buf_rgba, "PNG")
    rep_rgba = extract_exif(buf_rgba.getvalue())
    assert rep_rgba.color_mode == "RGBA"
    assert "32-bit" in rep_rgba.color_depth
    assert rep_rgba.has_alpha is True

    # Grayscale L image
    l_img = Image.new("L", (64, 64), 128)
    buf_l = io.BytesIO()
    l_img.save(buf_l, "PNG")
    rep_l = extract_exif(buf_l.getvalue())
    assert rep_l.color_mode == "L"
    assert "8-bit" in rep_l.color_depth
    assert rep_l.has_alpha is False


def test_animation_and_frames():
    """Animated GIF or multi-frame image properties."""
    frames = [
        Image.new("RGB", (32, 32), (255, 0, 0)),
        Image.new("RGB", (32, 32), (0, 255, 0)),
        Image.new("RGB", (32, 32), (0, 0, 255)),
    ]
    buf = io.BytesIO()
    frames[0].save(buf, "GIF", save_all=True, append_images=frames[1:], loop=0)
    rep = extract_exif(buf.getvalue(), file_name="anim.gif")
    assert rep.is_animated is True
    assert rep.frame_count == 3


def test_dpi_extraction():
    """DPI extraction from img.info and EXIF."""
    img = Image.new("RGB", (100, 100), (200, 200, 200))
    buf = io.BytesIO()
    img.save(buf, "PNG", dpi=(300, 300))
    rep = extract_exif(buf.getvalue())
    assert rep.dpi == (300.0, 300.0)


# -----------------------------------------------------------------------------
# 4. Visual Analysis: Dominant Colors & Brightness
# -----------------------------------------------------------------------------

def test_dominant_colors_solid():
    """A solid pure color image should produce that color as dominant (100%)."""
    img = Image.new("RGB", (100, 100), (255, 0, 0))
    colors = extract_dominant_colors(img, num_colors=5)
    assert len(colors) >= 1
    top = colors[0]
    assert top["hex"] == "#FF0000"
    assert top["rgb"] == (255, 0, 0)
    assert top["percentage"] == 100.0


def test_dominant_colors_structure_on_sample():
    """Dominant colors on sample.jpg has up to 5 colors with correct structure."""
    rep = extract_exif(SAMPLE_JPG)
    assert isinstance(rep.dominant_colors, list)
    assert 1 <= len(rep.dominant_colors) <= 5

    total_pct = 0.0
    for c in rep.dominant_colors:
        assert "hex" in c and c["hex"].startswith("#") and len(c["hex"]) == 7
        assert "rgb" in c and len(c["rgb"]) == 3
        assert all(0 <= val <= 255 for val in c["rgb"])
        assert "percentage" in c and 0.0 < c["percentage"] <= 100.0
        total_pct += c["percentage"]

    # Sum of percentages should be close to 100%
    assert 95.0 <= total_pct <= 105.0


def test_brightness_calculation():
    """Perceived brightness on pure black, pure white, and sample."""
    black_img = Image.new("RGB", (64, 64), (0, 0, 0))
    white_img = Image.new("RGB", (64, 64), (255, 255, 255))

    assert calculate_brightness(black_img) == 0.0
    assert calculate_brightness(white_img) == 255.0

    rep = extract_exif(SAMPLE_JPG)
    assert 0.0 <= rep.brightness <= 255.0
    # sample.jpg is a medium green-blue gradient
    assert 50.0 < rep.brightness < 180.0


# -----------------------------------------------------------------------------
# 5. Extended Non-EXIF Metadata: PNG Chunks, Raw Info, ICC Profile
# -----------------------------------------------------------------------------

def test_png_text_chunks():
    """Extract PNG text chunks (parameters, prompt, comment)."""
    img = Image.new("RGB", (64, 64), (50, 100, 150))
    meta = PngImagePlugin.PngInfo()
    meta.add_text("prompt", "a cybernetic owl in neon rain")
    meta.add_text("parameters", "Steps: 30, Sampler: DPM++ 2M, CFG: 7.0")
    meta.add_text("Comment", "Generated by AI Suite")

    buf = io.BytesIO()
    img.save(buf, "PNG", pnginfo=meta)

    rep = extract_exif(buf.getvalue(), file_name="ai_gen.png")
    assert rep.image_format == "PNG"
    assert "prompt" in rep.png_chunks
    assert rep.png_chunks["prompt"] == "a cybernetic owl in neon rain"
    assert "parameters" in rep.png_chunks
    assert "Steps: 30" in rep.png_chunks["parameters"]
    assert "Comment" in rep.png_chunks


def test_icc_profile_extraction():
    """Extract profile description when ICC profile is embedded."""
    try:
        profile = ImageCms.createProfile("sRGB")
        icc_bytes = ImageCms.ImageCmsProfile(profile).tobytes()
    except Exception:
        pytest.skip("ImageCms profile creation not available in this environment")

    img = Image.new("RGB", (64, 64), (100, 100, 100))
    buf = io.BytesIO()
    img.save(buf, "JPEG", icc_profile=icc_bytes)

    rep = extract_exif(buf.getvalue())
    assert rep.icc_profile is not None
    assert "sRGB" in rep.icc_profile


def test_raw_info_dictionary():
    """Verify raw_info captures non-binary keys from img.info."""
    img = Image.new("RGB", (64, 64))
    buf = io.BytesIO()
    img.save(buf, "JPEG", dpi=(144, 144))

    rep = extract_exif(buf.getvalue())
    assert isinstance(rep.raw_info, dict)
    assert "dpi" in rep.raw_info


# -----------------------------------------------------------------------------
# 6. Sample.jpg EXIF & Decoded Settings
# -----------------------------------------------------------------------------

def test_sample_jpg_exif_tags_and_decoded():
    """Detailed verification of sample.jpg EXIF tags, GPS links, and decoded fields."""
    rep = extract_exif(SAMPLE_JPG)

    # Headline tags
    assert rep.camera_make == "AcmeCam"
    assert rep.camera_model == "X-200"
    assert rep.software == "firmware 4.2.1"
    assert rep.datetime_original == "2024:05:17 14:30:00"
    assert rep.datetime_digitized == "2024:05:17 14:30:01"
    assert rep.f_number == "2.8"
    assert rep.exposure_time == "1/250"
    assert rep.iso == "100"
    assert rep.focal_length == "50"
    assert rep.orientation == "1"

    # Decoded settings
    assert rep.orientation_description == "Horizontal (normal)"

    # GPS checks (Eiffel Tower: 48.8584 N, 2.2945 E)
    assert rep.has_gps is True
    assert rep.gps is not None
    assert round(rep.gps.latitude, 4) == 48.8584
    assert round(rep.gps.longitude, 4) == 2.2945
    assert "48° 51'" in rep.gps.dms_string
    assert "2° 17'" in rep.gps.dms_string

    # Maps links
    assert "google.com/maps" in rep.gps.maps_link
    assert "openstreetmap.org" in rep.gps.openstreetmap_link
    assert "48.8584" in rep.gps.openstreetmap_link
    assert "2.2945" in rep.gps.openstreetmap_link
    assert "maps.apple.com" in rep.gps.apple_maps_link
    assert "48.8584,2.2945" in rep.gps.apple_maps_link

    # Both report and report.gps surface the links
    assert rep.openstreetmap_link == rep.gps.openstreetmap_link
    assert rep.apple_maps_link == rep.gps.apple_maps_link

    # Privacy Risk
    assert rep.privacy_risk == "HIGH"
    assert any("GPS" in reason for reason in rep.privacy_reasons)
    assert any("X-200" in reason for reason in rep.privacy_reasons)


# -----------------------------------------------------------------------------
# 7. Comprehensive Decoded Enum Fields via Synthetic EXIF
# -----------------------------------------------------------------------------

def test_decoded_exif_enums_comprehensive():
    """Test all enum mappings: ExposureProgram, MeteringMode, Flash, WhiteBalance,
    LightSource, Orientation, FocalLengthIn35mm, and Altitude."""
    zeroth = {
        piexif.ImageIFD.Make: b"TestMake",
        piexif.ImageIFD.Model: b"TestModel",
        piexif.ImageIFD.Orientation: 6,  # Rotate 90° CW
    }
    exif_ifd = {
        piexif.ExifIFD.DateTimeOriginal: "2025:06:01 12:00:00",
        piexif.ExifIFD.ExposureProgram: 3,  # Aperture priority
        piexif.ExifIFD.MeteringMode: 2,     # Center-weighted average
        piexif.ExifIFD.Flash: 25,           # Flash fired, auto mode
        piexif.ExifIFD.WhiteBalance: 1,     # Manual
        piexif.ExifIFD.LightSource: 1,      # Daylight
        piexif.ExifIFD.FocalLengthIn35mmFilm: 24,  # 24mm equivalent
    }
    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: b"N",
        piexif.GPSIFD.GPSLatitude: [(40, 1), (0, 1), (0, 1)],
        piexif.GPSIFD.GPSLongitudeRef: b"W",
        piexif.GPSIFD.GPSLongitude: [(74, 1), (0, 1), (0, 1)],
        piexif.GPSIFD.GPSAltitudeRef: 0,  # Above sea level
        piexif.GPSIFD.GPSAltitude: (3505, 10),  # 350.5 meters
    }
    exif_bytes = piexif.dump({"0th": zeroth, "Exif": exif_ifd, "GPS": gps_ifd})

    img = Image.new("RGB", (200, 100), (0, 120, 200))
    buf = io.BytesIO()
    img.save(buf, "JPEG", exif=exif_bytes)

    rep = extract_exif(buf.getvalue())

    assert rep.exposure_program_name == "Aperture priority"
    assert rep.metering_mode_name == "Center-weighted average"
    assert "Flash fired" in rep.flash_description
    assert "auto mode" in rep.flash_description
    assert rep.white_balance_name == "Manual"
    assert rep.light_source_name == "Daylight"
    assert rep.orientation_description == "Rotate 90° CW"
    assert rep.focal_length_35mm == 24

    # Altitude
    assert rep.altitude == 350.5
    assert rep.altitude_ref == 0
    assert rep.gps.altitude == 350.5
    assert rep.gps.altitude_ref == 0


def test_flash_bitmask_decoder():
    """Verify bitmask variations for flash decoding."""
    assert decode_flash(0x0000) == "Flash did not fire"
    assert decode_flash(0x0001) == "Flash fired"
    assert decode_flash(0x0010) == "Flash did not fire, compulsory flash mode"
    assert decode_flash(0x0018) == "Flash did not fire, auto mode"
    assert decode_flash(0x0019) == "Flash fired, auto mode"
    assert "red-eye reduction" in decode_flash(0x0041)


# -----------------------------------------------------------------------------
# 8. Clean PNG Handling & Privacy Risk Ratings
# -----------------------------------------------------------------------------

def test_clean_png_handling():
    """A clean image with no EXIF metadata produces LOW risk and empty tag sets."""
    if os.path.exists(CLEAN_PNG):
        rep = extract_exif(CLEAN_PNG)
    else:
        # Fallback in-memory clean PNG
        img = Image.new("RGB", (400, 300), (200, 200, 210))
        buf = io.BytesIO()
        img.save(buf, "PNG")
        rep = extract_exif(buf.getvalue(), file_name="clean.png")

    assert rep.has_exif is False
    assert rep.has_gps is False
    assert rep.camera_make is None
    assert rep.camera_model is None
    assert rep.datetime_original is None
    assert rep.all_tags == {}
    assert rep.png_chunks == {}
    assert rep.privacy_risk == "LOW"
    assert any("No GPS coordinates" in r for r in rep.privacy_reasons)


def test_privacy_risk_medium():
    """Camera model or datetime original without GPS produces MEDIUM risk."""
    if os.path.exists(DSLR_JPG):
        rep = extract_exif(DSLR_JPG)
        assert rep.has_gps is False
        assert rep.camera_model == "Canon EOS R6"
        assert rep.privacy_risk == "MEDIUM"
        assert any("Canon EOS R6" in r for r in rep.privacy_reasons)
    else:
        # Construct synthetic camera image without GPS
        zeroth = {piexif.ImageIFD.Model: b"Nikon Z6"}
        exif_ifd = {piexif.ExifIFD.DateTimeOriginal: "2024:01:01 10:00:00"}
        exif_bytes = piexif.dump({"0th": zeroth, "Exif": exif_ifd})

        img = Image.new("RGB", (100, 100))
        buf = io.BytesIO()
        img.save(buf, "JPEG", exif=exif_bytes)

        rep = extract_exif(buf.getvalue())
        assert rep.has_gps is False
        assert rep.privacy_risk == "MEDIUM"


def test_privacy_risk_serial_number_high():
    """Device serial number elevates privacy risk to HIGH even without GPS."""
    zeroth = {
        piexif.ImageIFD.Make: b"Sony",
        piexif.ImageIFD.Model: b"A7IV",
    }
    exif_ifd = {
        piexif.ExifIFD.BodySerialNumber: b"SN-99887766",
    }
    exif_bytes = piexif.dump({"0th": zeroth, "Exif": exif_ifd})

    img = Image.new("RGB", (100, 100))
    buf = io.BytesIO()
    img.save(buf, "JPEG", exif=exif_bytes)

    rep = extract_exif(buf.getvalue())
    assert rep.has_gps is False
    assert rep.privacy_risk == "HIGH"
    assert any("serial number" in r.lower() for r in rep.privacy_reasons)


# -----------------------------------------------------------------------------
# 9. GPS Helper Functions in gps.py
# -----------------------------------------------------------------------------

def test_gps_helpers():
    """Test dms_to_decimal, map links, and byte references."""
    # Paris
    lat = dms_to_decimal(48, 51, 30.24, "N")
    lon = dms_to_decimal(2, 17, 40.20, "E")
    assert round(lat, 4) == 48.8584
    assert round(lon, 4) == 2.2945

    # Sydney (Southern & Eastern hemisphere with byte ref)
    lat_s = dms_to_decimal(33, 51, 24.48, b"S")
    lon_e = dms_to_decimal(151, 12, 55.08, b"E")
    assert round(lat_s, 4) == -33.8568
    assert round(lon_e, 4) == 151.2153

    # Link generators
    osm = openstreetmap_link(48.8584, 2.2945)
    assert osm == "https://www.openstreetmap.org/?mlat=48.8584&mlon=2.2945#map=16/48.8584/2.2945"

    apple = apple_maps_link(48.8584, 2.2945)
    assert apple == "https://maps.apple.com/?q=48.8584,2.2945"

    google = google_maps_link(48.8584, 2.2945)
    assert "https://www.google.com/maps?q=48.858400,2.294500" in google


# -----------------------------------------------------------------------------
# 10. Serialization and Backward Compatibility
# -----------------------------------------------------------------------------

def test_json_serialization():
    """ExifReport can be serialized to JSON with asdict without error."""
    rep = extract_exif(SAMPLE_JPG)
    data = asdict(rep)
    json_str = json.dumps(data, default=str)
    assert isinstance(json_str, str)
    decoded = json.loads(json_str)
    assert decoded["camera_make"] == "AcmeCam"
    assert decoded["privacy_risk"] == "HIGH"
    assert "md5" in decoded
    assert "dominant_colors" in decoded


def test_helper_functions():
    """Utility functions like headline_tag_names and parse_datetime."""
    headlines = headline_tag_names()
    assert "Make" in headlines
    assert "Model" in headlines
    assert "GPSInfo" in headlines

    dt = parse_datetime("2024:05:17 14:30:00")
    assert dt is not None
    assert dt.year == 2024 and dt.month == 5 and dt.day == 17

    assert parse_datetime(None) is None
    assert parse_datetime("invalid-date") is None
