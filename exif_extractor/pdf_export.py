"""PDF forensic report generation for ExifReport using fpdf2."""

from __future__ import annotations

import datetime
import io
import os
from typing import Optional

from fpdf import FPDF
from PIL import Image

from .extractor import ExifReport


def _clean_text(text: object) -> str:
    """Clean text for standard PDF core fonts (latin-1 compatible)."""
    if text is None:
        return "N/A"
    s = str(text)
    # Replace common unicode symbols with ASCII equivalents
    replacements = {
        "\u00b0": " deg",
        "\u2014": " - ",
        "\u2013": " - ",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u00d7": "x",
        "\u2022": "*",
        "\u26a0": "[!]",
        "\u2705": "[OK]",
        "\U0001f6a8": "[ALERT]",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    # Filter to latin-1
    return s.encode("latin-1", errors="replace").decode("latin-1")


class ForensicReportPDF(FPDF):
    """Custom PDF layout for forensic image metadata reports."""

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 41, 59)
        self.cell(0, 8, "FORENSIC IMAGE METADATA REPORT", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 116, 139)
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.cell(0, 5, f"Automated OSINT & Metadata Extraction  |  Generated: {now_str}", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(3)
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        page_str = f"Page {self.page_no()}/{{nb}}"
        self.cell(0, 10, f"EXIF Metadata Extractor  -  Confidential Forensic Report  |  {page_str}", align="C")

    def chapter_title(self, title: str):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(241, 245, 249)
        self.set_text_color(15, 23, 42)
        self.cell(0, 7, f"  {_clean_text(title)}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def key_value_row(self, key: str, value: object, key_width: float = 55):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(71, 85, 105)
        self.cell(key_width, 6, _clean_text(key), border=0)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(15, 23, 42)
        val_str = _clean_text(value)
        self.multi_cell(0, 6, val_str, new_x="LMARGIN", new_y="NEXT")


def generate_pdf_report(report: ExifReport, image_bytes: Optional[bytes] = None) -> bytes:
    """Generate a clean, professional forensic PDF report for an ExifReport.

    Args:
        report: The ExifReport instance to document.
        image_bytes: Optional raw image bytes to embed a small preview.

    Returns:
        bytes: Raw PDF document bytes ready for download or writing.
    """
    pdf = ForensicReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # --- File Overview & Privacy Risk Box ---
    risk = getattr(report, "privacy_risk", "LOW")
    reasons = getattr(report, "privacy_reasons", [])

    if risk == "HIGH":
        pdf.set_fill_color(254, 242, 242)
        pdf.set_draw_color(239, 68, 68)
        text_r, text_g, text_b = 185, 28, 28
    elif risk == "MEDIUM":
        pdf.set_fill_color(254, 243, 199)
        pdf.set_draw_color(245, 158, 11)
        text_r, text_g, text_b = 180, 83, 9
    else:
        pdf.set_fill_color(240, 253, 244)
        pdf.set_draw_color(34, 197, 94)
        text_r, text_g, text_b = 21, 128, 61

    pdf.set_line_width(0.4)
    start_y = pdf.get_y()
    box_height = 20 + (len(reasons) * 5 if reasons else 0)
    pdf.rect(pdf.l_margin, start_y, pdf.w - pdf.l_margin - pdf.r_margin, box_height, style="FD")
    pdf.set_xy(pdf.l_margin + 4, start_y + 3)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(text_r, text_g, text_b)
    pdf.cell(0, 6, f"PRIVACY ASSESSMENT: {risk} RISK", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(30, 41, 59)
    if reasons:
        for r in reasons:
            pdf.cell(pdf.l_margin + 4)
            pdf.cell(0, 5, f"- {_clean_text(r)}", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(pdf.l_margin + 4)
        pdf.cell(0, 5, "No sensitive location or camera identifying data detected in this image.", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(start_y + box_height + 4)

    # Embed optional small preview if image is valid
    if image_bytes:
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                # Convert to RGB if needed (JPEG embed is fast and standard)
                rgb_img = img.convert("RGB")
                buf = io.BytesIO()
                rgb_img.thumbnail((300, 300))
                rgb_img.save(buf, format="JPEG", quality=85)
                buf.seek(0)
                img_width = 45
                pdf.image(buf, x=pdf.w - pdf.r_margin - img_width, y=pdf.get_y(), w=img_width)
        except Exception:
            pass

    # --- Section 1: File & Cryptographic Verification ---
    pdf.chapter_title("1. File Identification & Cryptographic Verification")
    file_name = getattr(report, "file_name", None) or os.path.basename(report.file_path or "image")
    pdf.key_value_row("Target File Name", file_name)
    pdf.key_value_row("File Size", f"{report.file_size:,} bytes")
    pdf.key_value_row("Image Format", report.image_format)
    pdf.key_value_row("Dimensions", f"{report.image_size[0]} x {report.image_size[1]} pixels")
    mp = getattr(report, "megapixels", None)
    if mp:
        pdf.key_value_row("Megapixels", f"{mp:.2f} MP")
    ar = getattr(report, "aspect_ratio_str", None)
    if ar:
        pdf.key_value_row("Aspect Ratio", ar)
    cm = getattr(report, "color_mode", None)
    if cm:
        cd = getattr(report, "color_depth", "")
        pdf.key_value_row("Color Mode / Depth", f"{cm} ({cd})" if cd else cm)
    ha = getattr(report, "has_alpha", None)
    if ha is not None:
        pdf.key_value_row("Alpha Channel", "Present (Transparency)" if ha else "None")
    dpi = getattr(report, "dpi", None)
    if dpi:
        pdf.key_value_row("Pixel Density (DPI)", f"{dpi[0]:.0f} x {dpi[1]:.0f} DPI")

    # Hashes
    md5 = getattr(report, "file_hash_md5", None)
    if md5:
        pdf.key_value_row("MD5 Checksum", md5)
    sha1 = getattr(report, "file_hash_sha1", None)
    if sha1:
        pdf.key_value_row("SHA-1 Checksum", sha1)
    sha256 = getattr(report, "file_hash_sha256", None)
    if sha256:
        pdf.key_value_row("SHA-256 Checksum", sha256)

    pdf.ln(3)

    # --- Section 2: Camera & Capture Telemetry ---
    pdf.chapter_title("2. Camera & Optical Settings")
    if report.has_exif:
        pdf.key_value_row("Camera Make", report.camera_make or "Unknown")
        pdf.key_value_row("Camera Model", report.camera_model or "Unknown")
        pdf.key_value_row("Lens Model", report.lens_model or "Unknown")
        pdf.key_value_row("Software / Firmware", report.software or "Unknown")
        pdf.key_value_row("Date/Time Taken", report.datetime_original or "Not recorded")
        pdf.key_value_row("Date/Time Digitized", report.datetime_digitized or "Not recorded")

        # Capture settings
        f_num = f"f/{report.f_number}" if report.f_number else "N/A"
        pdf.key_value_row("Aperture", f_num)
        exp = f"{report.exposure_time} s" if report.exposure_time else "N/A"
        pdf.key_value_row("Exposure Time", exp)
        pdf.key_value_row("ISO Speed", report.iso or "N/A")
        focal = f"{report.focal_length} mm" if report.focal_length else "N/A"
        focal_35 = getattr(report, "focal_length_35mm", None)
        if focal_35:
            focal += f" (35mm equivalent: {focal_35} mm)"
        pdf.key_value_row("Focal Length", focal)

        prog = getattr(report, "exposure_program_name", None)
        if prog:
            pdf.key_value_row("Exposure Program", prog)
        meter = getattr(report, "metering_mode_name", None)
        if meter:
            pdf.key_value_row("Metering Mode", meter)
        flash = getattr(report, "flash_description", None)
        if flash:
            pdf.key_value_row("Flash Mode", flash)
        wb = getattr(report, "white_balance_name", None)
        if wb:
            pdf.key_value_row("White Balance", wb)
        orient = getattr(report, "orientation_description", None) or report.orientation
        if orient:
            pdf.key_value_row("Orientation", orient)
    else:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 6, "No camera or optical EXIF metadata was found in this file.", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)

    # --- Section 3: Geolocation & GPS Intelligence ---
    pdf.chapter_title("3. Geolocation & GPS Intelligence")
    if report.has_gps and report.gps:
        gps = report.gps
        pdf.key_value_row("Latitude", f"{gps.latitude:.6f} deg")
        pdf.key_value_row("Longitude", f"{gps.longitude:.6f} deg")
        pdf.key_value_row("Coordinates (DMS)", gps.dms_string)
        alt = getattr(gps, "altitude", None)
        if alt is not None:
            alt_ref = getattr(gps, "altitude_ref", 0)
            ref_str = "below sea level" if alt_ref == 1 else "above sea level"
            pdf.key_value_row("Altitude", f"{alt:.1f} m ({alt * 3.28084:.1f} ft) {ref_str}")
        pdf.key_value_row("Google Maps Link", gps.maps_link)
        osm = getattr(gps, "openstreetmap_link", None)
        if osm:
            pdf.key_value_row("OpenStreetMap Link", osm)
        apple = getattr(gps, "apple_maps_link", None)
        if apple:
            pdf.key_value_row("Apple Maps Link", apple)
    else:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 6, "No embedded GPS location coordinates found in this image.", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)

    # --- Section 4: Visual & Dominant Colors ---
    colors = getattr(report, "dominant_colors", [])
    if colors:
        pdf.chapter_title("4. Visual & Color Analysis")
        bright = getattr(report, "brightness", None)
        if bright is not None:
            pdf.key_value_row("Perceived Brightness", f"{bright:.1f} / 255.0")
        color_str = ", ".join(f"{c['hex']} ({c['percentage']:.1f}%)" for c in colors if isinstance(c, dict) and "hex" in c)
        if color_str:
            pdf.key_value_row("Top Dominant Colors", color_str)
        pdf.ln(3)

    # --- Section 5: Extended Non-EXIF Metadata ---
    png_chunks = getattr(report, "png_chunks", {})
    icc = getattr(report, "icc_profile", None)
    if png_chunks or icc:
        pdf.chapter_title("5. Extended Container & Metadata Chunks")
        if icc:
            pdf.key_value_row("ICC Color Profile", icc)
        if png_chunks:
            for k, v in png_chunks.items():
                pdf.key_value_row(f"Chunk [{k}]", v)
        pdf.ln(3)

    # --- Section 6: Complete Tag Dump ---
    if report.all_tags:
        pdf.chapter_title(f"6. Complete EXIF Tag Dump ({len(report.all_tags)} Tags)")
        pdf.set_font("Courier", "B", 8)
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(203, 213, 225)
        pdf.cell(60, 6, " Tag Name", border=1, fill=True)
        pdf.cell(0, 6, " Value", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Courier", "", 7.5)
        for tag, val in sorted(report.all_tags.items(), key=lambda x: str(x[0])):
            t_str = _clean_text(str(tag))[:35]
            v_str = _clean_text(str(val))[:80]
            pdf.cell(60, 5, f" {t_str}", border=1)
            pdf.cell(0, 5, f" {v_str}", border=1, new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())
