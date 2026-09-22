"""Core EXIF extraction logic.

Opens an image, pulls its EXIF tags via Pillow, and groups the interesting
ones into a structured :class:`ExifReport`. The report separates the
"OSINT-relevant" fields (camera, datetime, GPS, software) from the raw tag
dump so callers can present either or both.
"""

from __future__ import annotations

import hashlib
import io
import math
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from PIL import Image, ImageStat, UnidentifiedImageError
from PIL.ExifTags import GPSTAGS, IFD, TAGS

from .gps import (
    _as_float,
    apple_maps_link,
    dms_to_decimal,
    format_dms,
    google_maps_link,
    openstreetmap_link,
)

# EXIF tag names we treat as "headline" fields — the ones most revealing of
# personal data. Anything else goes into the full dump.
_HEADLINE_TAGS = {
    "Make",
    "Model",
    "LensModel",
    "Software",
    "DateTimeOriginal",
    "DateTimeDigitized",
    "GPSInfo",
    "ExifImageWidth",
    "ExifImageHeight",
    "Orientation",
    "FNumber",
    "ExposureTime",
    "ISOSpeedRatings",
    "FocalLength",
}

# Tag names that can identify hardware serial numbers
_SERIAL_TAGS = {
    "BodySerialNumber",
    "CameraSerialNumber",
    "SerialNumber",
    "LensSerialNumber",
}

# Common tag mappings in case they are missing from Pillow TAGS
_ADDITIONAL_TAGS = {
    34850: "ExposureProgram",
    37383: "MeteringMode",
    37384: "LightSource",
    37385: "Flash",
    41987: "WhiteBalance",
    41989: "FocalLengthIn35mmFilm",
    42033: "BodySerialNumber",
    42034: "LensSpecification",
    42035: "LensMake",
    42036: "LensModel",
    42037: "LensSerialNumber",
}

EXPOSURE_PROGRAM_MAP = {
    0: "Not defined",
    1: "Manual",
    2: "Normal program",
    3: "Aperture priority",
    4: "Shutter priority",
    5: "Creative program (depth of field)",
    6: "Action program (fast shutter speed)",
    7: "Portrait mode",
    8: "Landscape mode",
}

METERING_MODE_MAP = {
    0: "Unknown",
    1: "Average",
    2: "Center-weighted average",
    3: "Spot",
    4: "Multi-spot",
    5: "Multi-segment / Pattern",
    6: "Partial",
    255: "Other",
}

WHITE_BALANCE_MAP = {
    0: "Auto",
    1: "Manual",
}

LIGHT_SOURCE_MAP = {
    0: "Unknown",
    1: "Daylight",
    2: "Fluorescent",
    3: "Tungsten",
    4: "Flash",
    9: "Fine weather",
    10: "Cloudy weather",
    11: "Shade",
    12: "Daylight fluorescent",
    13: "Day white fluorescent",
    14: "Cool white fluorescent",
    15: "White fluorescent",
    17: "Standard light A",
    18: "Standard light B",
    19: "Standard light C",
    20: "D55",
    21: "D65",
    22: "D75",
    23: "D50",
    24: "ISO studio tungsten",
    255: "Other light source",
}

ORIENTATION_MAP = {
    1: "Horizontal (normal)",
    2: "Mirror horizontal",
    3: "Rotate 180°",
    4: "Mirror vertical",
    5: "Mirror horizontal and rotate 270° CW",
    6: "Rotate 90° CW",
    7: "Mirror horizontal and rotate 90° CW",
    8: "Rotate 270° CW",
}


def decode_flash(val: int) -> str:
    """Decode EXIF Flash bitmask/enum into descriptive text."""
    if val is None:
        return ""
    flash_table = {
        0x0000: "Flash did not fire",
        0x0001: "Flash fired",
        0x0005: "Flash fired, strobe return light not detected",
        0x0007: "Flash fired, strobe return light detected",
        0x0008: "Flash did not fire, compulsory mode",
        0x0009: "Flash fired, compulsory mode",
        0x000D: "Flash fired, compulsory mode, return light not detected",
        0x000F: "Flash fired, compulsory mode, return light detected",
        0x0010: "Flash did not fire, compulsory flash mode",
        0x0014: "Flash did not fire, auto mode",
        0x0018: "Flash did not fire, auto mode",
        0x0019: "Flash fired, auto mode",
        0x001D: "Flash fired, auto mode, return light not detected",
        0x001F: "Flash fired, auto mode, return light detected",
        0x0020: "No flash function",
        0x0041: "Flash fired, red-eye reduction mode",
        0x0045: "Flash fired, red-eye reduction mode, return light not detected",
        0x0047: "Flash fired, red-eye reduction mode, return light detected",
        0x0049: "Flash fired, compulsory mode, red-eye reduction mode",
        0x004D: "Flash fired, compulsory mode, red-eye reduction mode, return light not detected",
        0x004F: "Flash fired, compulsory mode, red-eye reduction mode, return light detected",
        0x0050: "Flash did not fire, auto mode, red-eye reduction mode",
        0x0058: "Flash did not fire, auto mode, red-eye reduction mode",
        0x0059: "Flash fired, auto mode, red-eye reduction mode",
        0x005D: "Flash fired, auto mode, return light not detected, red-eye reduction mode",
        0x005F: "Flash fired, auto mode, return light detected, red-eye reduction mode",
    }
    if val in flash_table:
        return flash_table[val]
    fired = bool(val & 0x01)
    parts = ["Flash fired" if fired else "Flash did not fire"]
    return_light = (val >> 1) & 0x03
    if return_light == 2:
        parts.append("return light not detected")
    elif return_light == 3:
        parts.append("return light detected")
    mode = (val >> 3) & 0x03
    if mode == 1:
        parts.append("compulsory mode")
    elif mode == 2:
        parts.append("suppressed mode")
    elif mode == 3:
        parts.append("auto mode")
    if (val >> 5) & 0x01:
        parts.append("no flash function")
    if (val >> 6) & 0x01:
        parts.append("red-eye reduction")
    return ", ".join(parts)


def calculate_aspect_ratio(width: int, height: int) -> str:
    """Calculate simplified or standard aspect ratio string."""
    if width <= 0 or height <= 0:
        return "Unknown"
    g = math.gcd(width, height)
    sw, sh = width // g, height // g
    if sw <= 30 and sh <= 30:
        return f"{sw}:{sh}"
    ratio = width / height
    common_ratios = [
        (1, 1),
        (4, 3), (3, 4),
        (3, 2), (2, 3),
        (16, 9), (9, 16),
        (16, 10), (10, 16),
        (5, 4), (4, 5),
        (5, 3), (3, 5),
        (21, 9), (9, 21),
    ]
    for rw, rh in common_ratios:
        if abs(ratio - (rw / rh)) < 0.015:
            return f"{rw}:{rh}"
    return f"{sw}:{sh}"


def get_color_depth(mode: str) -> str:
    """Return descriptive color depth string for an image mode."""
    depth_map = {
        "1": "1-bit monochrome (1-bit total)",
        "L": "8 bits per channel (8-bit total)",
        "P": "8 bits per pixel, palette-mapped (8-bit total)",
        "RGB": "8 bits per channel (24-bit total)",
        "RGBA": "8 bits per channel (32-bit total)",
        "RGBX": "8 bits per channel (32-bit total)",
        "CMYK": "8 bits per channel (32-bit total)",
        "YCbCr": "8 bits per channel (24-bit total)",
        "LAB": "8 bits per channel (24-bit total)",
        "HSV": "8 bits per channel (24-bit total)",
        "LA": "8 bits per channel (16-bit total)",
        "PA": "8 bits per channel (16-bit total)",
        "I": "32-bit signed integer (32-bit total)",
        "F": "32-bit floating point (32-bit total)",
        "I;16": "16 bits per channel (16-bit total)",
    }
    return depth_map.get(mode, f"{mode} mode")


def extract_dominant_colors(img: Image.Image, num_colors: int = 5) -> List[Dict[str, object]]:
    """Extract top dominant colors using Pillow quantization."""
    try:
        thumb = img.convert("RGB")
        thumb.thumbnail((100, 100))
        quantized = thumb.quantize(colors=num_colors)
        colors = quantized.getcolors(maxcolors=10000)
        if not colors:
            return []
        palette = quantized.getpalette() or []
        colors.sort(key=lambda x: x[0], reverse=True)
        total_pixels = sum(c[0] for c in colors) or 1
        result = []
        for count, idx in colors[:num_colors]:
            start = idx * 3
            if start + 2 < len(palette):
                r = int(palette[start])
                g = int(palette[start + 1])
                b = int(palette[start + 2])
            else:
                r, g, b = (0, 0, 0)
            percentage = round((count / total_pixels) * 100.0, 2)
            hex_str = f"#{r:02X}{g:02X}{b:02X}"
            result.append({
                "hex": hex_str,
                "rgb": (r, g, b),
                "percentage": percentage,
            })
        return result
    except Exception:
        return []


def calculate_brightness(img: Image.Image) -> float:
    """Calculate average perceived luminance on a 0-255 scale."""
    try:
        thumb = img.copy()
        thumb.thumbnail((100, 100))
        gray = thumb.convert("L")
        stat = ImageStat.Stat(gray)
        return round(float(stat.mean[0]), 2)
    except Exception:
        return 0.0


def extract_icc_profile_name(icc_bytes: bytes) -> Optional[str]:
    """Extract human-readable profile description/name from ICC profile bytes."""
    if not icc_bytes or not isinstance(icc_bytes, (bytes, bytearray)):
        return None
    try:
        from PIL import ImageCms
        desc = ImageCms.getProfileDescription(io.BytesIO(icc_bytes))
        if desc:
            return desc.strip()
    except Exception:
        pass
    try:
        from PIL import ImageCms
        profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_bytes))
        name = ImageCms.getProfileName(profile)
        if name:
            return name.strip()
    except Exception:
        pass
    try:
        idx = icc_bytes.find(b"desc")
        if idx != -1 and len(icc_bytes) > idx + 12:
            length = int.from_bytes(icc_bytes[idx + 8 : idx + 12], "big")
            if 0 < length < 256 and len(icc_bytes) >= idx + 12 + length:
                return (
                    icc_bytes[idx + 12 : idx + 12 + length]
                    .decode("ascii", errors="ignore")
                    .rstrip("\x00")
                    .strip()
                )
    except Exception:
        pass
    return f"ICC Profile ({len(icc_bytes)} bytes)"


def assess_privacy_risk(
    has_gps: bool,
    camera_make: Optional[str],
    camera_model: Optional[str],
    datetime_original: Optional[str],
    all_tags: Dict[str, object],
) -> Tuple[str, List[str]]:
    """Assess privacy risk and produce explanation reasons."""
    reasons: List[str] = []
    found_serials = [
        tag for tag in _SERIAL_TAGS
        if tag in all_tags and all_tags[tag]
    ]

    if has_gps or found_serials:
        if has_gps:
            reasons.append("Embedded GPS location data reveals exact geographic coordinates")
        if found_serials:
            reasons.append(
                f"Device serial number found ({', '.join(found_serials)}), uniquely identifying hardware"
            )
        if camera_model:
            reasons.append(f"Camera model '{camera_model}' reveals device model")
        if datetime_original:
            reasons.append(f"Original capture timestamp '{datetime_original}' reveals when photo was taken")
        return "HIGH", reasons

    if camera_model or datetime_original:
        if camera_model:
            reasons.append(f"Camera model '{camera_model}' reveals device model")
        elif camera_make:
            reasons.append(f"Camera make '{camera_make}' reveals manufacturer")
        if datetime_original:
            reasons.append(f"Original capture timestamp '{datetime_original}' reveals when photo was taken")
        return "MEDIUM", reasons

    reasons.append("No GPS coordinates, device serial numbers, or identifying tags found")
    return "LOW", reasons


@dataclass
class GpsInfo:
    """Parsed GPS data from an image."""

    latitude: float
    longitude: float
    dms_string: str
    maps_link: str
    altitude: Optional[float] = None
    altitude_ref: Optional[int] = None
    openstreetmap_link: Optional[str] = None
    apple_maps_link: Optional[str] = None


@dataclass
class ExifReport:
    """Structured result of inspecting one image."""

    file_path: str
    file_size: int
    image_format: str
    image_size: Tuple[int, int]  # width, height in pixels

    # Headline fields (None when absent in the image).
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    software: Optional[str] = None
    datetime_original: Optional[str] = None
    datetime_digitized: Optional[str] = None
    f_number: Optional[str] = None
    exposure_time: Optional[str] = None
    iso: Optional[str] = None
    focal_length: Optional[str] = None
    orientation: Optional[str] = None
    gps: Optional[GpsInfo] = None

    # Every tag we found, name -> raw value, for the full dump.
    all_tags: Dict[str, object] = field(default_factory=dict)

    # Cryptographic hashes
    md5: Optional[str] = None
    sha1: Optional[str] = None
    sha256: Optional[str] = None

    # Image geometry & structure
    megapixels: Optional[float] = None
    aspect_ratio_str: Optional[str] = None
    color_mode: Optional[str] = None
    color_depth: Optional[str] = None
    has_alpha: bool = False
    dpi: Optional[Tuple[float, float]] = None
    is_animated: bool = False
    frame_count: int = 1

    # Visual & color palette
    dominant_colors: List[Dict[str, object]] = field(default_factory=list)
    brightness: Optional[float] = None

    # Extended non-EXIF metadata
    png_chunks: Dict[str, str] = field(default_factory=dict)
    icc_profile: Optional[str] = None
    raw_info: Dict[str, str] = field(default_factory=dict)

    # Decoded EXIF enum & setting fields
    exposure_program_name: Optional[str] = None
    metering_mode_name: Optional[str] = None
    flash_description: Optional[str] = None
    white_balance_name: Optional[str] = None
    light_source_name: Optional[str] = None
    orientation_description: Optional[str] = None
    focal_length_35mm: Optional[int] = None

    # GPS helpers
    altitude: Optional[float] = None
    altitude_ref: Optional[int] = None
    openstreetmap_link: Optional[str] = None
    apple_maps_link: Optional[str] = None

    # Privacy risk assessment
    privacy_risk: str = "LOW"
    privacy_reasons: List[str] = field(default_factory=list)

    @property
    def has_exif(self) -> bool:
        return bool(self.all_tags)

    @property
    def has_gps(self) -> bool:
        return self.gps is not None


class ExifError(Exception):
    """Raised when a file cannot be read or parsed as an image."""


def _tag_name(tag_id: int) -> str:
    """Map an EXIF tag id to its human-readable name, falling back to the id."""
    if tag_id in TAGS:
        return TAGS[tag_id]
    if tag_id in _ADDITIONAL_TAGS:
        return _ADDITIONAL_TAGS[tag_id]
    return f"Tag_{tag_id}"


def _stringify(value) -> str:
    """Render an EXIF value for the full dump, keeping it readable."""
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return _rational_str(value)
    if isinstance(value, float):
        if 0 < value < 1:
            inv = 1.0 / value
            if abs(inv - round(inv)) < 0.001:
                return f"1/{int(round(inv))}"
        return f"{value:g}"
    if isinstance(value, (bytes, bytearray)):
        try:
            return value.decode("ascii", errors="replace").rstrip("\x00").strip()
        except Exception:
            return value.hex()
    if isinstance(value, tuple):
        return ", ".join(_stringify(v) for v in value)
    return str(value)


def _rational_str(value) -> str:
    """Render an IFDRational as a clean number: 2.8, not 28/10."""
    try:
        num = value.numerator
        den = value.denominator
    except AttributeError:
        return str(value)
    if den in (0, 1):
        return str(num)
    decimal = num / den
    # Prefer a fraction like "1/250" for small shutter speeds, decimal otherwise.
    if num == 1 and den > 1:
        return f"{num}/{den}"
    return f"{decimal:g}"


def _parse_gps(gps_ifd: Dict[object, object]) -> Optional[GpsInfo]:
    """Convert a GPSInfo IFD into a :class:`GpsInfo`, or None if incomplete."""
    gps = {}
    for tag_key, value in gps_ifd.items():
        if isinstance(tag_key, int):
            tag_name = GPSTAGS.get(tag_key, f"GPS_{tag_key}")
        else:
            tag_name = str(tag_key)
        gps[tag_name] = value

    needs = ("GPSLatitude", "GPSLatitudeRef", "GPSLongitude", "GPSLongitudeRef")
    if not all(k in gps for k in needs):
        return None

    try:
        lat_d, lat_m, lat_s = gps["GPSLatitude"]
        lon_d, lon_m, lon_s = gps["GPSLongitude"]
        latitude = dms_to_decimal(lat_d, lat_m, lat_s, gps["GPSLatitudeRef"])
        longitude = dms_to_decimal(lon_d, lon_m, lon_s, gps["GPSLongitudeRef"])
    except (TypeError, ValueError, IndexError, ZeroDivisionError):
        return None

    dms_string = (
        f"{format_dms(lat_d, lat_m, lat_s, gps['GPSLatitudeRef'])}, "
        f"{format_dms(lon_d, lon_m, lon_s, gps['GPSLongitudeRef'])}"
    )

    altitude = None
    if "GPSAltitude" in gps and gps["GPSAltitude"] is not None:
        try:
            altitude = round(_as_float(gps["GPSAltitude"]), 2)
        except (TypeError, ValueError, ZeroDivisionError):
            altitude = None

    altitude_ref = None
    if "GPSAltitudeRef" in gps and gps["GPSAltitudeRef"] is not None:
        ref_val = gps["GPSAltitudeRef"]
        if isinstance(ref_val, (bytes, bytearray)):
            altitude_ref = int(ref_val[0]) if ref_val else 0
        else:
            try:
                altitude_ref = int(ref_val)
            except (TypeError, ValueError):
                altitude_ref = None

    osm_link = openstreetmap_link(latitude, longitude)
    apple_link = apple_maps_link(latitude, longitude)

    return GpsInfo(
        latitude=latitude,
        longitude=longitude,
        dms_string=dms_string,
        maps_link=google_maps_link(latitude, longitude),
        altitude=altitude,
        altitude_ref=altitude_ref,
        openstreetmap_link=osm_link,
        apple_maps_link=apple_link,
    )


def extract_exif(
    source: Union[str, os.PathLike, bytes, io.BytesIO] = None,
    file_name: Optional[str] = None,
    *,
    file_path: Optional[Union[str, os.PathLike]] = None,
) -> ExifReport:
    """Read an image source and return a structured EXIF report.

    Args:
        source: File path, PathLike, raw bytes, or BytesIO stream.
        file_name: Optional filename for display when source is bytes/BytesIO,
            or to override the reported filename.
        file_path: Backward-compatibility keyword argument for file path.

    Raises:
        ExifError: If the source does not exist, cannot be read, or is not a valid image.
    """
    if source is None and file_path is not None:
        source = file_path

    if source is None:
        raise ExifError("No image source provided.")

    reported_path = file_name
    if isinstance(source, (str, os.PathLike)):
        path_str = str(source)
        if not os.path.isfile(path_str):
            raise ExifError(f"File not found: {path_str}")
        reported_path = file_name or path_str
        try:
            with open(path_str, "rb") as f:
                raw_bytes = f.read()
        except OSError as exc:
            raise ExifError(f"Could not read image '{path_str}': {exc}") from exc
    elif isinstance(source, (bytes, bytearray)):
        raw_bytes = bytes(source)
        reported_path = file_name or "<in-memory>"
    elif isinstance(source, io.IOBase) or hasattr(source, "read"):
        if hasattr(source, "getvalue"):
            raw_bytes = source.getvalue()
        else:
            pos = source.tell() if hasattr(source, "tell") else None
            raw_bytes = source.read()
            if pos is not None and hasattr(source, "seek"):
                source.seek(pos)
        reported_path = file_name or "<in-memory>"
    else:
        raise ExifError(f"Unsupported source type: {type(source)}")

    file_size = len(raw_bytes)
    if file_size == 0:
        raise ExifError(f"Empty image data: {reported_path}")

    # Compute cryptographic hashes
    md5_hex = hashlib.md5(raw_bytes).hexdigest()
    sha1_hex = hashlib.sha1(raw_bytes).hexdigest()
    sha256_hex = hashlib.sha256(raw_bytes).hexdigest()

    try:
        with Image.open(io.BytesIO(raw_bytes)) as img:
            image_format = img.format or "UNKNOWN"
            image_size = img.size  # (width, height)
            color_mode = img.mode
            color_depth = get_color_depth(color_mode)
            has_alpha = bool(
                color_mode in ("RGBA", "LA", "PA", "RGBa", "La")
                or "transparency" in img.info
                or ("A" in color_mode and color_mode != "LAB")
            )
            is_animated = bool(getattr(img, "is_animated", False))
            frame_count = int(getattr(img, "n_frames", 1))

            # Visual analysis
            dominant_colors = extract_dominant_colors(img, num_colors=5)
            brightness = calculate_brightness(img)

            # Extended non-EXIF metadata
            png_chunks: Dict[str, str] = {}
            if image_format.upper() == "PNG":
                if hasattr(img, "text") and isinstance(img.text, dict):
                    for k, v in img.text.items():
                        if isinstance(v, (str, int, float, bool)):
                            png_chunks[str(k)] = str(v)
                        elif isinstance(v, (bytes, bytearray)):
                            try:
                                png_chunks[str(k)] = v.decode("utf-8", errors="replace").strip()
                            except Exception:
                                pass

                for k, v in img.info.items():
                    if k in (
                        "exif",
                        "icc_profile",
                        "photoshop",
                        "dpi",
                        "transparency",
                        "gamma",
                        "interlace",
                        "aspect",
                    ):
                        continue
                    if isinstance(v, (str, int, float, bool)):
                        png_chunks[str(k)] = str(v)
                    elif isinstance(v, (bytes, bytearray)):
                        try:
                            png_chunks[str(k)] = v.decode("utf-8", errors="replace").strip()
                        except Exception:
                            pass
            else:
                for k in ("parameters", "prompt", "workflow", "Comment", "comment"):
                    if k in img.info:
                        val = img.info[k]
                        if isinstance(val, (str, int, float, bool)):
                            png_chunks[str(k)] = str(val)
                        elif isinstance(val, (bytes, bytearray)):
                            try:
                                png_chunks[str(k)] = val.decode("utf-8", errors="replace").strip()
                            except Exception:
                                pass

            icc_profile = None
            if "icc_profile" in img.info and img.info["icc_profile"]:
                icc_profile = extract_icc_profile_name(img.info["icc_profile"])

            raw_info = {
                str(k): str(v)
                for k, v in img.info.items()
                if not isinstance(v, (bytes, bytearray))
            }

            # EXIF and IFD extraction
            raw_exif_dict: Dict[int, object] = {}
            gps_raw_dict: Dict[object, object] = {}

            # 1. Modern Pillow getexif()
            exif_obj = None
            try:
                if hasattr(img, "getexif"):
                    exif_obj = img.getexif()
            except Exception:
                exif_obj = None

            if exif_obj and len(exif_obj) > 0:
                for tag_id, value in exif_obj.items():
                    if tag_id == 34853:
                        continue
                    raw_exif_dict[tag_id] = value

                try:
                    if hasattr(IFD, "Exif"):
                        exif_sub = exif_obj.get_ifd(IFD.Exif)
                        for tag_id, value in exif_sub.items():
                            raw_exif_dict[tag_id] = value
                    if hasattr(IFD, "GPSInfo"):
                        gps_sub = exif_obj.get_ifd(IFD.GPSInfo)
                        if gps_sub:
                            gps_raw_dict.update(gps_sub)
                    if hasattr(IFD, "MakerNote"):
                        mn_sub = exif_obj.get_ifd(IFD.MakerNote)
                        for tag_id, value in mn_sub.items():
                            raw_exif_dict[tag_id] = value
                    if hasattr(IFD, "Interop"):
                        interop_sub = exif_obj.get_ifd(IFD.Interop)
                        for tag_id, value in interop_sub.items():
                            raw_exif_dict[tag_id] = value
                except Exception:
                    pass

            # 2. Fallback to legacy img._getexif()
            if not raw_exif_dict and hasattr(img, "_getexif"):
                try:
                    legacy_exif = img._getexif()
                    if legacy_exif:
                        for tag_id, value in legacy_exif.items():
                            if tag_id == 34853 or _tag_name(tag_id) == "GPSInfo":
                                if isinstance(value, dict) and not gps_raw_dict:
                                    gps_raw_dict.update(value)
                            else:
                                raw_exif_dict[tag_id] = value
                except Exception:
                    pass

            # 3. Fallback to piexif
            if (not raw_exif_dict or not gps_raw_dict) and "exif" in img.info:
                try:
                    import piexif
                    p_data = piexif.load(img.info["exif"])
                    if not raw_exif_dict:
                        for ifd_name in ("0th", "Exif", "Interop", "1st"):
                            if ifd_name in p_data and isinstance(p_data[ifd_name], dict):
                                for tag_id, value in p_data[ifd_name].items():
                                    raw_exif_dict[tag_id] = value
                    if not gps_raw_dict and "GPS" in p_data and isinstance(p_data["GPS"], dict):
                        gps_raw_dict.update(p_data["GPS"])
                except Exception:
                    pass

            # DPI extraction from info or EXIF
            dpi = None
            if "dpi" in img.info and isinstance(img.info["dpi"], (tuple, list)) and len(img.info["dpi"]) >= 2:
                try:
                    dpi = (round(float(img.info["dpi"][0]), 2), round(float(img.info["dpi"][1]), 2))
                except (ValueError, TypeError):
                    dpi = None

            if dpi is None:
                x_res = raw_exif_dict.get(282)
                y_res = raw_exif_dict.get(283)
                if x_res is not None and y_res is not None:
                    try:
                        x_f = _as_float(x_res)
                        y_f = _as_float(y_res)
                        if x_f > 0 and y_f > 0:
                            dpi = (round(x_f, 2), round(y_f, 2))
                    except Exception:
                        pass
    except (UnidentifiedImageError, OSError) as exc:
        raise ExifError(f"Could not read image '{reported_path}': {exc}") from exc

    all_tags: Dict[str, object] = {}
    for tag_id, value in raw_exif_dict.items():
        name = _tag_name(tag_id)
        if name == "GPSInfo" or tag_id == 34853:
            continue
        all_tags[name] = _stringify(value)

    if gps_raw_dict:
        all_tags["GPSInfo"] = "<GPS data — parsed separately>"

    width, height = image_size
    megapixels = round((width * height) / 1_000_000.0, 2)
    aspect_ratio_str = calculate_aspect_ratio(width, height)

    report = ExifReport(
        file_path=reported_path,
        file_size=file_size,
        image_format=image_format,
        image_size=image_size,
        all_tags=all_tags,
        md5=md5_hex,
        sha1=sha1_hex,
        sha256=sha256_hex,
        megapixels=megapixels,
        aspect_ratio_str=aspect_ratio_str,
        color_mode=color_mode,
        color_depth=color_depth,
        has_alpha=has_alpha,
        dpi=dpi,
        is_animated=is_animated,
        frame_count=frame_count,
        dominant_colors=dominant_colors,
        brightness=brightness,
        png_chunks=png_chunks,
        icc_profile=icc_profile,
        raw_info=raw_info,
    )

    # Headline fields
    report.camera_make = all_tags.get("Make")
    report.camera_model = all_tags.get("Model")
    report.lens_model = all_tags.get("LensModel")
    report.software = all_tags.get("Software")
    report.datetime_original = all_tags.get("DateTimeOriginal")
    report.datetime_digitized = all_tags.get("DateTimeDigitized")
    report.f_number = all_tags.get("FNumber")
    report.exposure_time = all_tags.get("ExposureTime")
    report.iso = all_tags.get("ISOSpeedRatings")
    report.focal_length = all_tags.get("FocalLength")
    report.orientation = all_tags.get("Orientation")

    # Decoded settings and enum fields
    ep_val = raw_exif_dict.get(34850) or all_tags.get("ExposureProgram")
    if ep_val is not None:
        try:
            report.exposure_program_name = EXPOSURE_PROGRAM_MAP.get(int(ep_val), f"Unknown ({ep_val})")
        except (ValueError, TypeError):
            report.exposure_program_name = str(ep_val)

    mm_val = raw_exif_dict.get(37383) or all_tags.get("MeteringMode")
    if mm_val is not None:
        try:
            report.metering_mode_name = METERING_MODE_MAP.get(int(mm_val), f"Unknown ({mm_val})")
        except (ValueError, TypeError):
            report.metering_mode_name = str(mm_val)

    flash_val = raw_exif_dict.get(37385) or all_tags.get("Flash")
    if flash_val is not None:
        try:
            report.flash_description = decode_flash(int(flash_val))
        except (ValueError, TypeError):
            report.flash_description = str(flash_val)

    wb_val = raw_exif_dict.get(41987) or all_tags.get("WhiteBalance")
    if wb_val is not None:
        try:
            report.white_balance_name = WHITE_BALANCE_MAP.get(int(wb_val), f"Unknown ({wb_val})")
        except (ValueError, TypeError):
            report.white_balance_name = str(wb_val)

    ls_val = raw_exif_dict.get(37384) or all_tags.get("LightSource")
    if ls_val is not None:
        try:
            report.light_source_name = LIGHT_SOURCE_MAP.get(int(ls_val), f"Unknown ({ls_val})")
        except (ValueError, TypeError):
            report.light_source_name = str(ls_val)

    orient_val = raw_exif_dict.get(274) or all_tags.get("Orientation")
    if orient_val is not None:
        try:
            report.orientation_description = ORIENTATION_MAP.get(int(orient_val), f"Unknown ({orient_val})")
        except (ValueError, TypeError):
            report.orientation_description = str(orient_val)

    fl35_val = raw_exif_dict.get(41989) or all_tags.get("FocalLengthIn35mmFilm")
    if fl35_val is not None:
        try:
            report.focal_length_35mm = int(fl35_val)
        except (ValueError, TypeError):
            report.focal_length_35mm = None

    # GPS parsing
    if gps_raw_dict:
        report.gps = _parse_gps(gps_raw_dict)
        if report.gps:
            report.altitude = report.gps.altitude
            report.altitude_ref = report.gps.altitude_ref
            report.openstreetmap_link = report.gps.openstreetmap_link
            report.apple_maps_link = report.gps.apple_maps_link

    # Privacy risk assessment
    risk, reasons = assess_privacy_risk(
        has_gps=report.has_gps,
        camera_make=report.camera_make,
        camera_model=report.camera_model,
        datetime_original=report.datetime_original,
        all_tags=report.all_tags,
    )
    report.privacy_risk = risk
    report.privacy_reasons = reasons

    return report


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse an EXIF datetime string like ``2024:05:17 14:30:00``."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None


def headline_tag_names() -> List[str]:
    """Return the ordered list of headline tag names the report surfaces."""
    return sorted(_HEADLINE_TAGS)
