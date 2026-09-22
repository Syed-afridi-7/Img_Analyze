"""Generate a sample .jpg with rich EXIF metadata + GPS, for testing/demoing.

Builds a synthetic image with a green/blue gradient and embeds realistic
camera, datetime, and GPS tags (Eiffel Tower location) so the extractor has
something realistic to read.

Uses ``piexif`` because it correctly serializes nested EXIF/GPS sub-IFDs.
Pillow alone (``Image.Exif``) struggles to write GPS rationals reliably
across versions, so piexif is the dependable choice for *generating* test
data. The extractor itself only needs Pillow.

Usage:
    python tests/make_sample.py [output_dir]
"""

import os
import sys

import piexif
from PIL import Image


def make_gradient(size=(640, 480)):
    """A simple green/blue gradient so the file isn't just blank."""
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(h):
        for x in range(w):
            r = int((x / w) * 80)
            g = int((y / h) * 180) + 40
            b = int(((x + y) / (w + h)) * 200) + 30
            px[x, y] = (r, min(255, g), min(255, b))
    return img


def build_exif_dict():
    """Return a piexif-style exif dict with camera, datetime, and GPS tags."""
    # Eiffel Tower: 48.8584 N, 2.2945 E
    # DMS tuples are rationals: each value is (numerator, denominator).
    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: b"N",
        piexif.GPSIFD.GPSLatitude: [(48, 1), (51, 1), (3024, 100)],
        piexif.GPSIFD.GPSLongitudeRef: b"E",
        piexif.GPSIFD.GPSLongitude: [(2, 1), (17, 1), (4020, 100)],
    }

    exif_ifd = {
        piexif.ExifIFD.DateTimeOriginal: "2024:05:17 14:30:00",
        piexif.ExifIFD.DateTimeDigitized: "2024:05:17 14:30:01",
        piexif.ExifIFD.FNumber: (28, 10),         # f/2.8
        piexif.ExifIFD.ExposureTime: (1, 250),    # 1/250 s
        piexif.ExifIFD.ISOSpeedRatings: 100,
        piexif.ExifIFD.FocalLength: (50, 1),      # 50 mm
        piexif.ExifIFD.PixelXDimension: 640,
        piexif.ExifIFD.PixelYDimension: 480,
    }

    zeroth_ifd = {
        piexif.ImageIFD.Make: b"AcmeCam",
        piexif.ImageIFD.Model: b"X-200",
        piexif.ImageIFD.Software: b"firmware 4.2.1",
        piexif.ImageIFD.Orientation: 1,
    }

    return {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd}


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "sample.jpg")

    img = make_gradient()
    exif_bytes = piexif.dump(build_exif_dict())
    img.save(out_path, "JPEG", exif=exif_bytes, quality=90)
    print(f"Wrote {out_path} ({os.path.getsize(out_path)} bytes)")


if __name__ == "__main__":
    main()
