"""GPS coordinate helpers.

Cameras store GPS as sexagesimal (degrees/minutes/seconds) rationals in EXIF
tags. These helpers convert that to decimal degrees and build a map link so a
location can be opened directly in a browser.
"""

from __future__ import annotations

from typing import Sequence, Tuple, Union


def _clean_ref(ref: Union[str, bytes, bytearray]) -> str:
    """Normalize a hemisphere ref like 'N', 'S', b'N' to a clean uppercase string."""
    if isinstance(ref, (bytes, bytearray)):
        return ref.decode("ascii", errors="replace").strip("\x00 ").upper()
    return str(ref).strip("\x00 ").upper()


def _as_float(value) -> float:
    """Convert an EXIF rational (e.g. IFDRational or tuple) to a float."""
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        if value.denominator != 0:
            return float(value.numerator) / float(value.denominator)
        return float(value.numerator)
    if isinstance(value, (tuple, list)) and len(value) == 2 and value[1] != 0:
        return float(value[0]) / float(value[1])
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def dms_to_decimal(
    degrees: Sequence,
    minutes: Sequence,
    seconds: Sequence,
    ref: Union[str, bytes],
) -> float:
    """Convert DMS coordinates + a N/S/E/W reference into decimal degrees.

    Args:
        degrees/minutes/seconds: Each a rational, tuple, or number as stored
            in the GPSLatitude/GPSLongitude EXIF tags.
        ref: One of ``N``, ``S``, ``E``, ``W`` (case-insensitive, str or bytes).

    Returns:
        Signed decimal degrees. South and West are negative.
    """
    decimal = _as_float(degrees) + _as_float(minutes) / 60.0 + _as_float(seconds) / 3600.0
    clean_ref = _clean_ref(ref)
    if clean_ref in ("S", "W"):
        decimal = -decimal
    return decimal


def google_maps_link(latitude: float, longitude: float) -> str:
    """Return a Google Maps URL that drops a pin at the given coordinates."""
    # Round to 6 decimals (~11 cm precision) to avoid float noise like
    # 2.2944999999999998 in the URL.
    return f"https://www.google.com/maps?q={latitude:.6f},{longitude:.6f}"


def openstreetmap_link(latitude: float, longitude: float) -> str:
    """Return an OpenStreetMap URL with a pin at the given coordinates."""
    lat = round(float(latitude), 6)
    lon = round(float(longitude), 6)
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}"


def apple_maps_link(latitude: float, longitude: float) -> str:
    """Return an Apple Maps URL that drops a pin at the given coordinates."""
    lat = round(float(latitude), 6)
    lon = round(float(longitude), 6)
    return f"https://maps.apple.com/?q={lat},{lon}"


def format_dms(
    degrees: Sequence,
    minutes: Sequence,
    seconds: Sequence,
    ref: Union[str, bytes],
) -> str:
    """Human-readable DMS string, e.g. ``48° 51' 24.07" N``."""
    clean_ref = _clean_ref(ref)
    return (
        f"{_as_float(degrees):.0f}° "
        f"{_as_float(minutes):.0f}' "
        f'{_as_float(seconds):.2f}" {clean_ref}'
    )


def decimal_pair(
    lat_dms: Tuple[Sequence, Sequence, Sequence, str],
    lon_dms: Tuple[Sequence, Sequence, Sequence, str],
) -> Tuple[float, float]:
    """Convenience wrapper turning (lat DMS tuple, lon DMS tuple) -> (lat, lon)."""
    lat = dms_to_decimal(*lat_dms)
    lon = dms_to_decimal(*lon_dms)
    return lat, lon
