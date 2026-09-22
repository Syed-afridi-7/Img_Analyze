"""Terminal rendering for :class:`ExifReport` objects.

Produces a clean, sectioned, colorized readout. ANSI colors are used on TTYs
and stripped automatically when output is piped or redirected.
"""

from __future__ import annotations

import shutil
import sys
from typing import List, Optional

from .extractor import ExifReport

# ANSI color helpers. _supports_color() decides whether to actually emit them.
_ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
}


def _supports_color(stream=sys.stdout) -> bool:
    if not (hasattr(stream, "isatty") and stream.isatty()):
        return False
    if sys.platform == "win32":
        # Enable ANSI VT processing on Windows 10+ terminals.
        return _enable_windows_ansi()
    return True


def _enable_windows_ansi() -> bool:
    """Try to enable ANSI escape processing on Windows. Returns success."""
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        # STD_OUTPUT_HANDLE = -11; ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        if not kernel32.SetConsoleMode(handle, mode.value | 0x0004):
            return False
        return True
    except Exception:
        return False


def _c(name: str, text: str, enabled: bool) -> str:
    if not enabled or name == "reset":
        return text
    return f"{_ANSI[name]}{text}{_ANSI['reset']}"


def _human_size(num_bytes: int) -> str:
    """Render a byte count as e.g. ``2.4 MB``."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024.0 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def _row(label: str, value: str, color: bool) -> str:
    """A two-column row: dim label, bold value."""
    return f"  {_c('dim', f'{label:<14}', color)}{_c('bold', value, color)}"


def _section(title: str, color: bool) -> str:
    bar = "─" * 48
    return f"\n{_c('cyan', title, color)}\n{_c('dim', bar, color)}"


def render_report(
    report: ExifReport,
    *,
    show_all_tags: bool = False,
    color: Optional[bool] = None,
    stream=sys.stdout,
) -> str:
    """Render an :class:`ExifReport` as a string suitable for printing.

    Args:
        report: The parsed EXIF report.
        show_all_tags: Also append the full tag dump.
        color: Override color detection; None auto-detects from ``stream``.
        stream: Used only to detect TTY for auto color.
    """
    if color is None:
        color = _supports_color(stream)

    lines: List[str] = []

    # Header.
    lines.append(
        _c("magenta", "═" * 50, color)
    )
    title = "EXIF METADATA REPORT"
    lines.append(_c("bold", title.center(50), color))
    lines.append(_c("magenta", "═" * 50, color))

    # File section.
    lines.append(_section("FILE", color))
    lines.append(_row("Path", report.file_path, color))
    lines.append(_row("Format", report.image_format, color))
    lines.append(
        _row(
            "Dimensions",
            f"{report.image_size[0]} × {report.image_size[1]} px",
            color,
        )
    )
    lines.append(_row("File size", _human_size(report.file_size), color))

    if not report.has_exif:
        lines.append(
            _section("EXIF", color)
        )
        msg = "No EXIF metadata found in this image."
        lines.append(f"  {_c('yellow', msg, color)}")
        lines.append(
            f"  {_c('dim', '(It may have been stripped by a platform or editor.)', color)}"
        )
        lines.append("")
        return "\n".join(lines)

    # Camera section.
    lines.append(_section("CAMERA", color))
    shown = False
    if report.camera_make:
        lines.append(_row("Make", str(report.camera_make), color))
        shown = True
    if report.camera_model:
        lines.append(_row("Model", str(report.camera_model), color))
        shown = True
    if report.lens_model:
        lines.append(_row("Lens", str(report.lens_model), color))
        shown = True
    if report.software:
        lines.append(_row("Software", str(report.software), color))
        shown = True
    if not shown:
        lines.append(f"  {_c('dim', 'No camera/software tags present.', color)}")

    # Capture settings.
    any_settings = any(
        [report.f_number, report.exposure_time, report.iso, report.focal_length]
    )
    if any_settings:
        lines.append(_section("CAPTURE SETTINGS", color))
        if report.f_number:
            lines.append(_row("Aperture", f"f/{report.f_number}", color))
        if report.exposure_time:
            lines.append(_row("Exposure", f"{report.exposure_time} s", color))
        if report.iso:
            lines.append(_row("ISO", str(report.iso), color))
        if report.focal_length:
            lines.append(_row("Focal length", f"{report.focal_length} mm", color))

    # Date/time section — this is a key privacy leak.
    lines.append(_section("DATE / TIME", color))
    if report.datetime_original:
        lines.append(_row("Taken", str(report.datetime_original), color))
    if report.datetime_digitized:
        lines.append(_row("Digitized", str(report.datetime_digitized), color))
    if not report.datetime_original and not report.datetime_digitized:
        lines.append(f"  {_c('dim', 'No datetime tags present.', color)}")

    # GPS section — the headline OSINT leak.
    lines.append(_section("GPS / LOCATION", color))
    if report.has_gps:
        gps = report.gps
        lines.append(_row("Latitude", f"{gps.latitude:.6f}°", color))
        lines.append(_row("Longitude", f"{gps.longitude:.6f}°", color))
        lines.append(_row("DMS", gps.dms_string, color))
        lines.append("")
        link_line = f"  {_c('green', '▸ Google Maps: ', color)}{gps.maps_link}"
        lines.append(link_line)
    else:
        lines.append(f"  {_c('dim', 'No GPS data embedded in this image.', color)}")

    # Optional full dump.
    if show_all_tags and report.all_tags:
        lines.append(_section("ALL EXIF TAGS", color))
        for name in sorted(report.all_tags):
            value = report.all_tags[name]
            lines.append(f"  {_c('dim', f'{name:<28}', color)}{value}")

    lines.append("")
    return "\n".join(lines)


def print_report(
    report: ExifReport,
    *,
    show_all_tags: bool = False,
    color: Optional[bool] = None,
) -> None:
    """Print a report to stdout, auto-detecting color."""
    text = render_report(
        report, show_all_tags=show_all_tags, color=color, stream=sys.stdout
    )
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "ascii"
        print(text.encode(encoding, errors="replace").decode(encoding))
