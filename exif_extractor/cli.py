"""Command-line interface for the EXIF Metadata Extractor.

Usage examples::

    python -m exif_extractor photo.jpg
    python -m exif_extractor photo.jpg --all
    python -m exif_extractor img1.jpg img2.png --json
    python -m exif_extractor photo.jpg --no-color
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from typing import List

from .extractor import ExifError, ExifReport, extract_exif
from .formatter import print_report, render_report

SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp", ".heic"}


def _report_to_dict(report: ExifReport) -> dict:
    """Serialize a report to a JSON-friendly dict."""
    data = asdict(report)
    return data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exif_extractor",
        description=(
            "OSINT tool: extract hidden EXIF metadata (camera, date/time, GPS) "
            "from images like .jpg and .png, and reveal where a photo was taken."
        ),
        epilog=(
            "Only use this on images you own or have permission to inspect. "
            "The goal is to show how much personal data photos leak."
        ),
    )
    parser.add_argument(
        "images",
        metavar="IMAGE",
        nargs="+",
        help="One or more image files (.jpg, .jpeg, .png, .tiff).",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Also print every EXIF tag found (full dump).",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        dest="as_json",
        help="Output results as JSON instead of a formatted report.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color even on a terminal.",
    )
    return parser


def _process_one(
    file_path: str, *, show_all: bool, as_json: bool, no_color: bool
) -> int:
    """Process a single image. Returns process exit code (0 ok, 1 error)."""
    try:
        report = extract_exif(file_path)
    except ExifError as exc:
        if as_json:
            print(json.dumps({"file": file_path, "error": str(exc)}, indent=2))
        else:
            print(f"✗ {exc}", file=sys.stderr)
        return 1

    if as_json:
        print(json.dumps(_report_to_dict(report), indent=2, default=str))
    else:
        print_report(report, show_all_tags=show_all, color=not no_color)
    return 0


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.as_json and not args.no_color:
        # JSON should always be plain — color codes would corrupt it.
        args.no_color = True

    exit_code = 0
    for i, file_path in enumerate(args.images):
        if len(args.images) > 1 and not args.as_json and i > 0:
            print("\n" + "═" * 50 + "\n")
        rc = _process_one(
            file_path,
            show_all=args.all,
            as_json=args.as_json,
            no_color=args.no_color,
        )
        exit_code = exit_code or rc
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
