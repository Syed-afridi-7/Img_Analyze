"""Generate a varied set of demo images for testing/demoing the extractor.

Each fixture exercises a different real-world EXIF scenario:

    samples/pixel_sydney.jpg    phone photo, GPS S/E hemisphere (Sydney)
    samples/iphone_nyc.jpg      phone photo, GPS N/W hemisphere (New York)
    samples/galaxy_rio.jpg      phone photo, GPS S/W hemisphere (Rio) — both coords negative
    samples/dslr_landscape.jpg  dedicated camera, full settings, NO GPS
    samples/clean_export.png    metadata-free export (what platforms strip to)

Together with the root sample.jpg (N/E, Eiffel Tower) this covers all four
GPS quadrants, the no-GPS branch, and the no-EXIF branch.

Uses piexif (dev-only dependency) because it correctly serializes nested
EXIF/GPS sub-IFDs. Usage:

    python tests/make_samples.py [output_dir]
"""

import os
import sys

import piexif
from PIL import Image


def make_gradient(size, top, bottom):
    """Vertical two-color gradient so each fixture is visually distinct."""
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def build_exif(spec):
    """Serialize a fixture spec into EXIF bytes via piexif."""
    zeroth = {
        piexif.ImageIFD.Make: spec["make"].encode("ascii"),
        piexif.ImageIFD.Model: spec["model"].encode("ascii"),
        piexif.ImageIFD.Software: spec["software"].encode("ascii"),
        piexif.ImageIFD.Orientation: 1,
    }
    exif_ifd = {
        piexif.ExifIFD.DateTimeOriginal: spec["taken"],
        piexif.ExifIFD.DateTimeDigitized: spec["taken"],
        piexif.ExifIFD.FNumber: spec["f_number"],
        piexif.ExifIFD.ExposureTime: spec["exposure"],
        piexif.ExifIFD.ISOSpeedRatings: spec["iso"],
        piexif.ExifIFD.FocalLength: spec["focal_length"],
        piexif.ExifIFD.PixelXDimension: spec["size"][0],
        piexif.ExifIFD.PixelYDimension: spec["size"][1],
    }
    if spec.get("lens"):
        exif_ifd[piexif.ExifIFD.LensModel] = spec["lens"].encode("ascii")

    exif_dict = {"0th": zeroth, "Exif": exif_ifd}

    # GPS: (ref, [(deg), (min), (sec)]) per axis; S/W make values negative.
    gps = spec.get("gps")
    if gps:
        lat, lon = gps
        exif_dict["GPS"] = {
            piexif.GPSIFD.GPSLatitudeRef: lat[0].encode("ascii"),
            piexif.GPSIFD.GPSLatitude: lat[1],
            piexif.GPSIFD.GPSLongitudeRef: lon[0].encode("ascii"),
            piexif.GPSIFD.GPSLongitude: lon[1],
        }
    return piexif.dump(exif_dict)


# DMS rationals are (numerator, denominator) pairs per degrees/minutes/seconds.
SPECS = [
    {
        # Sydney Opera House: 33° 51' 24.48" S, 151° 12' 55.08" E
        "filename": "pixel_sydney.jpg",
        "size": (800, 600),
        "gradient": ((27, 108, 168), (2, 44, 67)),  # teal -> navy
        "make": "Google",
        "model": "Pixel 8",
        "software": "Android 14",
        "taken": "2024:11:02 07:41:13",
        "f_number": (168, 100),   # f/1.68
        "exposure": (1, 120),
        "iso": 50,
        "focal_length": (681, 100),  # 6.81 mm
        "gps": (
            ("S", [(33, 1), (51, 1), (2448, 100)]),
            ("E", [(151, 1), (12, 1), (5508, 100)]),
        ),
    },
    {
        # Times Square, New York: 40° 45' 28.8" N, 73° 59' 7.8" W
        "filename": "iphone_nyc.jpg",
        "size": (1024, 768),
        "gradient": ((61, 52, 139), (122, 72, 170)),  # indigo -> plum
        "make": "Apple",
        "model": "iPhone 15 Pro",
        "software": "iOS 18.2",
        "taken": "2025:01:15 18:22:47",
        "f_number": (178, 100),   # f/1.78
        "exposure": (1, 60),
        "iso": 125,
        "focal_length": (24, 1),  # 24 mm equivalent
        "gps": (
            ("N", [(40, 1), (45, 1), (2880, 100)]),
            ("W", [(73, 1), (59, 1), (780, 100)]),
        ),
    },
    {
        # Christ the Redeemer, Rio: 22° 57' 6.84" S, 43° 12' 37.8" W
        "filename": "galaxy_rio.jpg",
        "size": (900, 600),
        "gradient": ((242, 166, 90), (60, 28, 79)),  # sunset orange -> purple
        "make": "samsung",
        "model": "SM-S921B",  # Galaxy S24
        "software": "One UI 6.1",
        "taken": "2025:03:09 06:58:31",
        "f_number": (18, 10),    # f/1.8
        "exposure": (1, 500),
        "iso": 40,
        "focal_length": (24, 1),
        "gps": (
            ("S", [(22, 1), (57, 1), (684, 100)]),
            ("W", [(43, 1), (12, 1), (3780, 100)]),
        ),
    },
    {
        # Dedicated camera: geotagging off — exercises the "no GPS" branch.
        "filename": "dslr_landscape.jpg",
        "size": (1200, 800),
        "gradient": ((126, 200, 227), (45, 106, 79)),  # sky -> forest
        "make": "Canon",
        "model": "Canon EOS R6",
        "software": "Firmware 1.8.1",
        "lens": "RF24-105mm F4L IS USM",
        "taken": "2023:08:20 09:12:05",
        "f_number": (80, 10),    # f/8.0
        "exposure": (1, 250),
        "iso": 100,
        "focal_length": (45, 1),
        "gps": None,
    },
]

CLEAN_SPEC = {
    # Metadata-free PNG — what a stripped platform export looks like.
    "filename": "clean_export.png",
    "size": (400, 300),
    "gradient": ((205, 205, 210), (120, 120, 128)),
}


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base, "samples")
    os.makedirs(out_dir, exist_ok=True)

    for spec in SPECS:
        out_path = os.path.join(out_dir, spec["filename"])
        img = make_gradient(spec["size"], *spec["gradient"])
        img.save(out_path, "JPEG", exif=build_exif(spec), quality=90)
        print(f"Wrote {out_path} ({os.path.getsize(out_path)} bytes)")

    out_path = os.path.join(out_dir, CLEAN_SPEC["filename"])
    img = make_gradient(CLEAN_SPEC["size"], *CLEAN_SPEC["gradient"])
    img.save(out_path, "PNG")  # no exif= → no metadata block
    print(f"Wrote {out_path} ({os.path.getsize(out_path)} bytes)")


if __name__ == "__main__":
    main()
