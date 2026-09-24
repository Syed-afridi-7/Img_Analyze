# EXIF Metadata Extractor (OSINT Tool)

A privacy-awareness / OSINT tool that reads hidden **EXIF metadata** from
image files (`.jpg`, `.jpeg`, `.png`, `.tiff`) and shows what cameras and
phones quietly embed in every photo — the device that took it, the exact date
and time, and the **GPS coordinates** of where it was taken, with a one-click
Google Maps link.

> 🛡️ **Why this exists:** Most people don't realize a single photo posted
> online can reveal their phone model, when they were somewhere, and exactly
> where on Earth they were standing. This tool makes that data visible so you
> understand the privacy cost — and confirms whether your own images are clean
> before you share them.

## Features

- 📷 **Camera identification** — make, model, lens, firmware/software.
- 🕐 **Date & time** — when the photo was actually taken (not the file timestamp).
- 🎚️ **Capture settings** — aperture, exposure, ISO, focal length.
- 📍 **GPS location** — latitude/longitude in decimal degrees + DMS, with a
  direct **Google Maps** pin link.
- 🧾 **Full tag dump** — every EXIF tag the image contains.
- 🗂️ **Batch mode** — pass multiple files at once.
- 🤖 **JSON output** — for piping into other tools.
- 🎨 **Color terminal output** (auto-enabled, with `--no-color` override).

## Requirements

- Python 3.9+
- [Pillow](https://python-pillow.org) (`pip install Pillow`)

Only Pillow is needed to run the tool. `piexif` is an optional extra used only
by the test fixture generator (`tests/make_sample.py`).

## Installation

```bash
git clone <your-repo-url>
cd exif-extractor
pip install -r requirements.txt
```

## Usage

```bash
# Basic scan of one image
python -m exif_extractor photo.jpg

# Include every EXIF tag (full dump)
python -m exif_extractor photo.jpg --all

# Scan several files at once
python -m exif_extractor img1.jpg img2.png img3.jpg

# Machine-readable output
python -m exif_extractor photo.jpg --json

# Disable color (or pipe to a file)
python -m exif_extractor photo.jpg --no-color > report.txt
```

### Command-line options

| Flag          | Description                                              |
| ------------- | -------------------------------------------------------- |
| `IMAGE ...`   | One or more image files to inspect.                      |
| `-a, --all`   | Also print the complete EXIF tag dump.                   |
| `-j, --json`  | Output results as JSON instead of a formatted report.    |
| `--no-color`  | Disable ANSI color (auto-off when output is piped).      |

## Example output

```
══════════════════════════════════════════════════
               EXIF METADATA REPORT
══════════════════════════════════════════════════

FILE
────────────────────────────────────────────────
  Path          sample.jpg
  Format        JPEG
  Dimensions    640 × 480 px
  File size     14.2 KB

CAMERA
────────────────────────────────────────────────
  Make          AcmeCam
  Model         X-200
  Software      firmware 4.2.1

CAPTURE SETTINGS
────────────────────────────────────────────────
  Aperture      f/2.8
  Exposure      1/250 s
  ISO           100
  Focal length  50 mm

DATE / TIME
────────────────────────────────────────────────
  Taken         2024:05:17 14:30:00
  Digitized     2024:05:17 14:30:01

GPS / LOCATION
────────────────────────────────────────────────
  Latitude      48.858400°
  Longitude     2.294500°
  DMS           48° 51' 30.24" N, 2° 17' 40.20" E

  ▸ Google Maps: https://www.google.com/maps?q=48.858400,2.294500
```

## Trying it out

Demo images are included — one at the project root plus a set in `samples/`
covering the common EXIF scenarios:

| File                          | Scenario                                              |
| ----------------------------- | ----------------------------------------------------- |
| `sample.jpg`                  | Full EXIF + GPS, N/E quadrant (Eiffel Tower)           |
| `samples/pixel_sydney.jpg`    | Phone photo, **S**outhern latitude (Sydney)            |
| `samples/iphone_nyc.jpg`      | Phone photo, **W**estern longitude (New York)          |
| `samples/galaxy_rio.jpg`      | Phone photo, both coordinates negative (Rio)           |
| `samples/dslr_landscape.jpg`  | Dedicated camera + lens, **no GPS** (geotagging off)   |
| `samples/clean_export.png`    | Metadata-free export — what platforms strip to         |

Generate (or regenerate) them with:

```bash
pip install piexif            # only needed for the generators
python tests/make_sample.py   # writes sample.jpg
python tests/make_samples.py  # writes the samples/ set
python -m exif_extractor sample.jpg samples/*.jpg
```

In the web frontend, the sidebar's **demo image picker** lists all of them.
Or point the tool at any of your own photos — most unedited phone pictures
contain at least the camera model and timestamp, and many contain GPS.

## Web frontend (Streamlit)

The same tool in the browser — upload an image and get the report with an
embedded map of the GPS location.

```bash
python -m pip install streamlit
python -m streamlit run app.py
```

Then open http://localhost:8501. Features:

- Drag-and-drop upload (`.jpg`/`.jpeg`/`.png`/`.tiff`/`.webp`) or a
  **demo-image picker** with six bundled fixtures (all GPS quadrants,
  no-GPS camera, stripped export)
- Image preview plus format / dimensions / file size / tag-count metrics
- Tabbed views: formatted **Report**, full **All tags** table, downloadable
  **JSON**
- GPS coordinates with an embedded Google Maps view pinned to the capture
  spot, plus the direct Maps link
- Privacy banner that warns when an image leaks its location
- Dark theme; Streamlit usage telemetry disabled (`.streamlit/config.toml`)

Everything runs locally — uploads are parsed through a local temp file and
never leave the machine. (The embedded map loads Google Maps in your
browser, but only when GPS data is present.)

> **Windows note:** prefer `python -m streamlit run app.py`. The bare
> `streamlit` command only works if Python's `Scripts` directory (e.g.
> `C:\Users\<you>\AppData\Local\Python\pythoncore-3.14-64\Scripts`) is on
> your PATH; `python -m …` always works.

## How it works

1. The image is opened with Pillow (`Image.open`).
2. `img._getexif()` returns the EXIF tag dictionary (IFD0 + flattened Exif
   sub-IFD). Tag ids are mapped to readable names via `PIL.ExifTags.TAGS`.
3. The GPS sub-IFD (`GPSInfo`) is keyed by GPS tag ids and named via
   `PIL.ExifTags.GPSTAGS`. Latitude/longitude are stored as
   degrees/minutes/seconds rationals, which are converted to signed decimal
   degrees (South/West become negative).
4. The decimal coordinates are dropped into a Google Maps query URL.
5. Results are formatted into sections (File / Camera / Settings / Date /
   GPS) and printed, or serialized to JSON.

### Project layout

```
exif_extractor/
  __init__.py     # package exports
  __main__.py     # enables `python -m exif_extractor`
  cli.py          # argparse CLI
  extractor.py    # core: open image, parse EXIF, build ExifReport
  formatter.py    # terminal rendering (color, sections, sizes)
  gps.py          # DMS→decimal conversion + Google Maps link
app.py            # Streamlit web frontend (streamlit run app.py)
.streamlit/
  config.toml     # dark theme, telemetry off
samples/                  # generated demo image set
tests/
  make_sample.py        # generates a sample.jpg with EXIF + GPS
  make_samples.py       # generates the samples/ demo set
  test_streamlit_app.py # headless smoke tests for the web app
requirements.txt
README.md
PROJECT_DOCUMENT.md
```

## Using the library directly

The package is also importable as a library:

```python
from exif_extractor import extract_exif

report = extract_exif("photo.jpg")

print(report.camera_model)     # "iPhone 14 Pro"
print(report.datetime_original)  # "2024:05:17 14:30:00"
if report.has_gps:
    print(report.gps.latitude)
    print(report.gps.maps_link)  # open this in a browser
```

## Privacy note & responsible use

- ✅ Use this on **your own** images or images you have permission to inspect.
- ✅ Use it to verify your photos are clean before posting them publicly.
- ❌ Do **not** use it to stalk or deanonymize others.
- Many platforms (Twitter/X, Instagram, Facebook, WhatsApp) automatically
  strip EXIF on upload — which protects privacy but is exactly why people are
  surprised when a *directly shared* original still leaks location data.

**To remove EXIF from your own photos before sharing**, re-export or use
tools like `exiftool -all= photo.jpg`, ImageMagick (`mogrify -strip`), or the
"remove location" option in your phone's share sheet.

## Academic Dissertation & Technical Report

An ultra-detailed, publication-grade academic dissertation (~47,000+ words, 80+ pages equivalent) is available in the [`docs/`](docs/) directory:

- 📄 **Master Thesis:** [`docs/DISSERTATION.md`](docs/DISSERTATION.md)
- 📂 **Modular Chapter Files:** [`docs/dissertation/`](docs/dissertation/)
  - `00_front_matter.md` — Title page, evaluation rubrics, IEEE abstract, figure & table indices.
  - `01_introduction.md` — Evolution of EXIF 2.32, photography vs. privacy paradox, threat modeling, research objectives.
  - `02_literature_review.md` — Forensic tool comparison, JFIF/TIFF/PNG container specs, FRE 901 crypto, geodesy & colorimetry math.
  - `03_system_architecture.md` — End-to-end pipeline, DFD Levels 0–2, UML diagrams, zero-disk in-memory sandbox proofs.
  - `04_implementation.md` — Deep code walkthrough (stream hashing, bitmasks, rational tuples, AI chunk detection, lossless scrubbing).
  - `05_batch_processing.md` — Ingestion mechanics, cross-image risk scoring, multi-point geospatial mapping, comparative CSV export.
  - `06_testing_validation.md` — 48 automated test suite breakdown, Case Studies A–D, latency and RAM benchmarks.
  - `07_limitations.md` — Unsigned EXIF spoofing, C2PA, social media CDN stripping, RAW containers, and pixel-level leakage.
  - `08_conclusion.md` — Contributions, multi-disciplinary impact in OSINT/DFIR, and future AI/YOLO roadmap.
  - `09_appendices_code.md` — EXIF/GPS tag dictionary (0x010E to 0xA434), PNG chunk reference, and core source code listings.
  - `10_references.md` — 53 publication-grade IEEE/ACM citations.

## License

MIT — see source headers. Built as an educational OSINT/privacy project.

