# Project Document — EXIF Metadata Extractor (OSINT Tool)

| Field            | Value                                          |
| ---------------- | ---------------------------------------------- |
| **Project name** | EXIF Metadata Extractor                        |
| **Category**     | Open Source Intelligence (OSINT) / Privacy     |
| **Version**      | 1.1.0 (v1.0.0 CLI · v1.1.0 web frontend)      |
| **Status**       | Complete — built, tested, verified             |
| **Date**         | 2026-08-14                                     |
| **Platform**     | Windows / macOS / Linux (developed on Windows) |
| **Language**     | Python 3.9+ (verified on 3.14.6)               |
| **License**      | MIT                                            |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Motivation](#2-problem-statement--motivation)
3. [Goals & Objectives](#3-goals--objectives)
4. [Scope](#4-scope)
5. [Technology Stack](#5-technology-stack)
6. [System Architecture](#6-system-architecture)
7. [Repository Layout](#7-repository-layout)
8. [Module Specifications](#8-module-specifications)
9. [Data Model](#9-data-model)
10. [EXIF Technical Primer](#10-exif-technical-primer)
11. [GPS Coordinate Handling](#11-gps-coordinate-handling)
12. [CLI Reference](#12-cli-reference)
13. [Library API Reference](#13-library-api-reference)
14. [Output Specification](#14-output-specification)
15. [Error Handling](#15-error-handling)
16. [Installation & Quick Start](#16-installation--quick-start)
17. [Testing & Verification](#17-testing--verification)
18. [Development Log](#18-development-log)
19. [Known Limitations](#19-known-limitations)
20. [Security, Privacy & Ethics](#20-security-privacy--ethics)
21. [Roadmap / Future Enhancements](#21-roadmap--future-enhancements)
22. [Glossary](#22-glossary)
23. [Appendix A — Verified Sample Output](#appendix-a--verified-sample-output)

---

## 1. Executive Summary

The EXIF Metadata Extractor is a command-line OSINT and privacy-awareness
tool that reads the hidden **EXIF metadata** embedded in image files
(`.jpg`, `.jpeg`, `.png`, `.tiff`, `.webp`) and presents it in a clean,
sectioned terminal report.

Modern cameras and smartphones automatically write metadata into every photo
they produce: the device make and model, firmware, the exact date and time
the shutter fired, camera settings, and — critically — **GPS coordinates**
pinpointing where the photo was taken. Most users are unaware this data
exists, let alone that it travels with the file when shared directly.

This tool makes that data visible. Given an image, it extracts and displays:

- **Camera identity** — make, model, lens, software/firmware
- **Timestamps** — when the photo was taken and digitized
- **Capture settings** — aperture, exposure, ISO, focal length
- **Location** — GPS latitude/longitude in decimal degrees and DMS, plus a
  direct **Google Maps pin link**

It also emphasizes the privacy dimension: a single unedited photo can reveal
what phone you own, when you were somewhere, and exactly where you were
standing. The tool lets users audit their own images before sharing them.

The implementation is a small, dependency-light Python package (only Pillow)
that works both as a CLI and as an importable library, with JSON output for
machine consumption.

---

## 2. Problem Statement & Motivation

### The problem

When a digital camera or phone captures a JPEG, it embeds an EXIF
(Exchangeable Image File Format) block into the file header. This block
routinely contains personally identifying information:

| Data            | Privacy impact                                            |
| --------------- | --------------------------------------------------------- |
| Camera model    | Reveals device ownership and spending habits              |
| Date/time taken | Reveals when the subject was at a location (patterns)     |
| GPS coordinates | Reveals **exact physical location** — home, workplace     |
| Software field  | Reveals editing tools, sometimes OS or app versions       |
| Serial numbers  | Can uniquely identify a specific device (not extracted)   |

Most social platforms strip EXIF on upload (protecting users by default),
but images shared directly — email attachments, cloud-drive links, messaging
apps with "send as file," forum posts, dating apps — often retain it. Users
have no easy way to see what they are leaking.

### Motivation

1. **Education** — demonstrate concretely how much data hides in an ordinary
   photo, making the abstract privacy risk tangible.
2. **Self-audit** — give users a fast way to check whether their images are
   clean before publishing them.
3. **OSINT training** — provide a simple, readable, well-documented example
   of a classic OSINT technique (metadata analysis) suitable for security
   courses and CTF-style exercises.

---

## 3. Goals & Objectives

### Functional goals

| #    | Goal                                                                 | Status |
| ---- | -------------------------------------------------------------------- | ------ |
| G1   | Parse image files and extract EXIF metadata                         | ✅ Done |
| G2   | Surface camera/phone make and model                                  | ✅ Done |
| G3   | Extract exact date/time the photo was taken                          | ✅ Done |
| G4   | Parse GPS coordinates (latitude/longitude) from DMS rationals        | ✅ Done |
| G5   | Generate a direct Google Maps link to the capture location           | ✅ Done |
| G6   | Format output cleanly in the terminal (sections, alignment)          | ✅ Done |
| G7   | Support batch processing of multiple images                          | ✅ Done |
| G8   | Provide machine-readable JSON output                                 | ✅ Done |
| G9   | Degrade gracefully on images with no/partial EXIF                    | ✅ Done |

### Non-functional goals

| #    | Goal                                                        | Status |
| ---- | ----------------------------------------------------------- | ------ |
| N1   | Minimal dependencies (Pillow only for the tool itself)      | ✅ Done |
| N2   | Cross-platform (Windows ANSI handling included)             | ✅ Done |
| N3   | Clean architecture: extraction / parsing / rendering split  | ✅ Done |
| N4   | Importable as a library, not just a CLI                     | ✅ Done |
| N5   | Clear error messages with proper exit codes                 | ✅ Done |

### Learning objectives (educational project)

- Working with binary file formats (TIFF/EXIF IFD structure)
- Rational number encoding and DMS→decimal coordinate conversion
- Pillow's EXIF APIs and their quirks (sub-IFDs, IFDRational)
- Terminal UI formatting with ANSI escape codes
- argparse CLI design and JSON serialization

---

## 4. Scope

### In scope (v1.0.0)

- Reading EXIF from JPEG/JPEG-encoded files, and TIFF/WebP where Pillow
  exposes it
- IFD0 tags, Exif sub-IFD tags (flattened by Pillow), GPS sub-IFD
- Headline OSINT fields + full raw tag dump
- Decimal + DMS coordinate rendering, Google Maps link generation
- Single-file and batch CLI operation, JSON export
- Windows ANSI color enabling

### Out of scope (v1.0.0)

- **Removing/stripping EXIF** (documented as roadmap item)
- Writing or editing EXIF (the test fixture generator does this, the tool
  itself is read-only)
- MakerNotes decoding (manufacturer-proprietary sub-IFDs)
- HEIC/HEIF input (requires `pillow-heif` extra)
- Video container metadata (MOV/MP4)
- GUI or web interface
- Reverse geocoding coordinates to street addresses (would require a
  network API; tool is fully offline)

---

## 5. Technology Stack

| Component          | Choice                              | Why                                                        |
| ------------------ | ----------------------------------- | ---------------------------------------------------------- |
| Language           | Python 3.9+                         | Spec requirement; ubiquitous for security tooling          |
| Image/EXIF library | **Pillow 12.3.0**                   | Spec suggestion; mature, pure-metadata access              |
| CLI framework      | `argparse` (stdlib)                 | Zero extra dependencies, standard                          |
| Data structures    | `dataclasses` (stdlib)              | Clean typed reports, free `asdict()` JSON serialization    |
| Color output       | ANSI escapes + `ctypes` (Win VT)    | No dependency; auto-detects TTY                            |
| Test fixture gen   | **piexif 1.1.3** (dev-only)         | Correctly serializes nested EXIF/GPS sub-IFDs              |
| Web frontend (opt.)| **Streamlit 1.61.1**                | Browser UI over the same package; optional extra           |
| Runtime deps       | 1 (Pillow) CLI / +1 (Streamlit) web | Install friction near zero                                 |

### Verified environment

```
OS:        Windows 10 (10.0.26200), Git Bash shell
Python:    3.14.6
Pillow:    12.3.0
piexif:    1.1.3 (dev only)
Streamlit: 1.61.1 (web frontend, optional)
```

---

## 6. System Architecture

### 6.1 High-level data flow

```
                        ┌─────────────────────────────────┐
   user                 │           cli.py                │
   ─── IMAGE paths ──▶  │  argparse → _process_one()      │
                        └───────┬───────────────┬─────────┘
                                │               │
                     text mode  │               │  --json mode
                                ▼               ▼
                ┌───────────────────────┐  ┌──────────────────────┐
                │  extractor.py         │  │ json.dumps(          │
                │  extract_exif(path)   │  │   asdict(report))    │
                │                       │  └──────────────────────┘
                │  Pillow Image.open    │
                │  img._getexif()       │
                │        │              │
                │        ├── TAGS       │  (IFD0 + Exif sub-IFD names)
                │        └── GPSTAGS ───┼──▶ _parse_gps()
                │                       │         │
                │  _stringify /         │         ▼
                │  _rational_str        │  ┌──────────────────────┐
                └───────────┬───────────┘  │ gps.py               │
                            │              │  dms_to_decimal()    │
                            ▼              │  format_dms()        │
                ┌───────────────────────┐  │  google_maps_link()  │
                │  formatter.py         │  └──────────────────────┘
                │  render_report()      │
                │  print_report()       │
                └───────────┬───────────┘
                            ▼
                       stdout (ANSI / plain)
```

### 6.2 Design principles

1. **Separation of concerns** — four modules, one job each:
   `extractor` (I/O + parsing), `gps` (pure math), `formatter`
   (presentation), `cli` (argument handling). `gps.py` has no dependencies
   on Pillow and is trivially unit-testable.
2. **Structured report object** — extraction returns a typed
   `ExifReport` dataclass, not a printout. Renderers (terminal, JSON) are
   interchangeable consumers.
3. **Headline vs. dump** — the report distinguishes curated OSINT-relevant
   fields from the raw tag dictionary; the CLI exposes the dump only with
   `--all`.
4. **Graceful absence** — EXIF is optional data. Every field may be `None`
   and every section renders an explicit "not present" note rather than
   crashing or silently omitting context.
5. **Pure functions for math** — `dms_to_decimal` and `google_maps_link`
   are side-effect-free and independently reusable.

### 6.3 Key technical decisions

| Decision | Rationale |
| -------- | --------- |
| `img._getexif()` over `img.getexif()` | `_getexif()` returns a plain dict with the Exif sub-IFD already flattened (DateTimeOriginal, FNumber, etc. at top level) and GPSInfo as a nested dict — simplest shape to consume. Trade-off documented in [Limitations](#19-known-limitations). |
| GPS tags named via `GPSTAGS`, not `TAGS` | The GPS sub-IFD uses its own tag-id namespace; `TAGS` only covers IFD0. Confirmed by the GPS-null bug during development (see [Development Log](#18-development-log)). |
| Rationals rendered as decimals | `IFDRational.__str__` yields `28/10`; users expect `f/2.8`. Exception: shutter speeds keep fraction form (`1/250`) as that is photographic convention. |
| 6-decimal coordinate rounding in links | Avoids float artifacts like `2.2944999999999998` in URLs; 1e-6° ≈ 11 cm, far beyond GPS accuracy. |
| ctypes VT enabling on Windows | Windows 10+ supports ANSI only after enabling `ENABLE_VIRTUAL_TERMINAL_PROCESSING`; falls back to plain text if the call fails. |
| piexif for fixture generation only | Pillow 12.3.0's `Image.Exif` cannot reliably serialize nested GPS sub-IFDs (see Development Log #2). piexif is correct for *writing*; the tool itself never writes EXIF, so it stays a dev dependency. |

---

## 7. Repository Layout

```
E:\logan\
├── PROJECT_DOCUMENT.md          ← this document
├── README.md                    ← user-facing quick documentation
├── requirements.txt             ← runtime deps (Pillow)
├── sample.jpg                   ← generated demo image with EXIF + GPS
├── samples\                     ← generated demo set (5 scenarios)
│   ├── pixel_sydney.jpg         ← GPS S/E hemisphere fixture
│   ├── iphone_nyc.jpg           ← GPS N/W hemisphere fixture
│   ├── galaxy_rio.jpg           ← GPS S/W fixture (both coords negative)
│   ├── dslr_landscape.jpg       ← camera + lens, no GPS
│   └── clean_export.png         ← metadata-free export
├── app.py                       ← Streamlit web frontend
├── .streamlit\
│   └── config.toml              ← dark theme + telemetry off
├── exif_extractor\              ← the package
│   ├── __init__.py              ← public exports, __version__
│   ├── __main__.py              ← enables `python -m exif_extractor`
│   ├── cli.py                   ← argparse CLI, batch loop, exit codes
│   ├── extractor.py             ← core: open image, parse EXIF, build ExifReport
│   ├── formatter.py             ← terminal rendering, color detection
│   └── gps.py                   ← DMS↔decimal math, Maps link builder
└── tests\
    ├── make_sample.py           ← generates sample.jpg (needs piexif)
    ├── make_samples.py          ← generates the samples/ demo set
    └── test_streamlit_app.py    ← headless AppTest smoke tests for app.py
```

Line counts (approx.): `extractor.py` ~200, `formatter.py` ~190,
`cli.py` ~110, `gps.py` ~70, `app.py` ~230 — deliberately small enough to
read in one sitting.

---

## 8. Module Specifications

### 8.1 `exif_extractor/__init__.py`

Public package surface:

```python
from exif_extractor import ExifReport, extract_exif,      # extraction
                           dms_to_decimal, google_maps_link  # gps helpers
__version__ = "1.0.0"
```

### 8.2 `exif_extractor/gps.py` — coordinate math (no Pillow imports)

| Function | Signature | Description |
| -------- | --------- | ----------- |
| `_as_float` | `(value) -> float` | Converts an EXIF rational — `(num, den)` tuple or number — to float; guards zero denominators. |
| `dms_to_decimal` | `(degrees, minutes, seconds, ref: str) -> float` | DMS + N/S/E/W reference → signed decimal degrees. S/W negate the result. |
| `google_maps_link` | `(lat: float, lon: float) -> str` | `https://www.google.com/maps?q={lat:.6f},{lon:.6f}` — 6-decimal rounding kills float noise. |
| `format_dms` | `(d, m, s, ref) -> str` | `48° 51' 30.24" N` human-readable form. |
| `decimal_pair` | `(lat_dms, lon_dms) -> (float, float)` | Convenience wrapper converting both axes at once. |

### 8.3 `exif_extractor/extractor.py` — core extraction

**Constants**

- `_HEADLINE_TAGS` — set of tag names treated as OSINT-relevant (Make,
  Model, LensModel, Software, DateTimeOriginal, DateTimeDigitized, GPSInfo,
  ExifImageWidth/Height, Orientation, FNumber, ExposureTime,
  ISOSpeedRatings, FocalLength).

**Classes**

- `ExifError(Exception)` — file missing / unreadable / not an image.
- `GpsInfo` dataclass — `latitude: float`, `longitude: float`,
  `dms_string: str`, `maps_link: str`.
- `ExifReport` dataclass — full fields listed in [§9 Data Model](#9-data-model);
  properties `has_exif`, `has_gps`.

**Functions**

| Function | Description |
| -------- | ----------- |
| `_tag_name(tag_id: int) -> str` | IFD0 tag id → name via `PIL.ExifTags.TAGS`, fallback `Tag_{id}`. |
| `_stringify(value) -> str` | Renders any EXIF value for the dump: IFDRational via `_rational_str`, bytes decoded as ASCII (NUL-stripped), tuples joined. |
| `_rational_str(value) -> str` | Rational → clean number. `den ∈ {0,1}` → integer; `1/N` kept as fraction (shutter convention); otherwise decimal via `:g` (`2.8`, `50`). |
| `_parse_gps(gps_ifd: dict) -> GpsInfo \| None` | Names GPS ids via `GPSTAGS`; requires all four of GPSLatitude/Ref + GPSLongitude/Ref; unpacks `(d, m, s)` rational tuples; converts via `dms_to_decimal`; tolerant of `TypeError/ValueError/IndexError/ZeroDivisionError`. |
| `extract_exif(file_path: str) -> ExifReport` | **Main entry point.** Validates path, sizes file, opens via Pillow, pulls `_getexif()`, builds `all_tags` (GPSInfo replaced by placeholder note), populates headline fields, parses GPS. Raises `ExifError` on any I/O or format failure. |
| `parse_datetime(value) -> datetime \| None` | Parses `"%Y:%m:%d %H:%M:%S"` EXIF timestamps; utility for consumers. |
| `headline_tag_names() -> list[str]` | Sorted `_HEADLINE_TAGS` (introspection helper). |

**Processing order in `extract_exif`:**

1. `os.path.isfile` check → `ExifError` if missing
2. `os.path.getsize`
3. `Image.open` (context-managed) → format, `(width, height)`
4. `img._getexif()` → `None` for EXIF-less files (e.g. plain PNG)
5. Build `all_tags` dict (GPSInfo → placeholder string)
6. Populate headline scalars via `.get()`
7. Locate GPSInfo entry → `_parse_gps` → `report.gps`

### 8.4 `exif_extractor/formatter.py` — presentation

| Function | Description |
| -------- | ----------- |
| `_supports_color(stream)` | TTY check; on win32 delegates to `_enable_windows_ansi()`. |
| `_enable_windows_ansi()` | `ctypes` → `kernel32.GetStdHandle(-11)` + `SetConsoleMode(\| 0x0004)` (ENABLE_VIRTUAL_TERMINAL_PROCESSING). Returns `False` on any failure → plain text. |
| `_human_size(bytes)` | `14.2 KB` / `2.4 MB` style rendering. |
| `_row(label, value, color)` | Two-column row: 14-char dim label, bold value. |
| `_section(title, color)` | Cyan heading + 48-char dim rule. |
| `render_report(report, *, show_all_tags=False, color=None, stream=sys.stdout) -> str` | Builds the full report string (see [§14](#14-output-specification)). `color=None` auto-detects. |
| `print_report(report, *, show_all_tags=False, color=None)` | Prints `render_report` to stdout. |

Color palette: header rule **magenta**, title/report values **bold**, section
heads **cyan**, labels/dim text **dim**, Maps link arrow **green**, warnings
**yellow**.

### 8.5 `exif_extractor/cli.py` — command line

| Element | Description |
| ------- | ----------- |
| `SUPPORTED_EXT` | Informational set of extensions (`.jpg .jpeg .png .tiff .tif .webp .heic`). *Not enforced* — any file Pillow can open is accepted; see [Limitations](#19-known-limitations). |
| `_report_to_dict(report)` | `dataclasses.asdict` → JSON-ready dict. |
| `build_parser()` | argparse setup: `IMAGE...` (nargs `+`), `-a/--all`, `-j/--json` (`dest="as_json"`), `--no-color`. Description + epilog carry the responsible-use notice. |
| `_process_one(path, *, show_all, as_json, no_color) -> int` | One image → report or error. Text errors go to **stderr** with `✗`; JSON errors are emitted as `{"file":…, "error":…}` objects. Returns 0/1. |
| `main(argv=None) -> int` | Batch loop; `--json` implies color-off; separates multi-file text reports with a `═`×50 divider; aggregates exit code (`0` only if every file succeeded). |

### 8.6 `exif_extractor/__main__.py`

Three lines — imports `cli.main`, `sys.exit(main())`. Enables
`python -m exif_extractor`.

### 8.7 `app.py` — Streamlit web frontend (optional, v1.1.0)

Browser UI over the same package. Run with `python -m streamlit run app.py`
(Windows-safe: the bare `streamlit` shim requires Python's `Scripts`
directory on PATH).

| Element             | Description                                                                                                     |
| ------------------- | --------------------------------------------------------------------------------------------------------------- |
| Sidebar             | File uploader (`.jpg .jpeg .png .tiff .tif .webp`), "Load sample image" button (enabled when `sample.jpg` exists), responsible-use notice. |
| Landing state       | Explainer + three feature cards (Camera / Settings / Location); `st.stop()` until an input exists.               |
| Input handling      | Upload bytes (or sample) parked in a `tempfile.NamedTemporaryFile` with the original extension → `extract_exif(path)` → temp file deleted. Nothing leaves the machine. |
| Header              | Filename + privacy banner: **warning** (GPS present) / **success** (no GPS) / **info** (no EXIF).                |
| Overview            | Preview column (`st.image`) + Format / Dimensions / File size / EXIF-tag-count metrics.                          |
| Tabs                | **Report** — Camera, Capture settings, Date/time tables + GPS metrics, DMS string, Maps link, embedded Google Maps iframe (`st.iframe`, zoom 15). **All tags** — sortable dataframe. **JSON** — code view + `st.download_button`. |
| `section_table()`   | Local helper: Field/Value table, or a caption when every value is absent.                                        |
| Reuse               | Imports `extract_exif`, `ExifError`, and `_human_size` from the package — zero duplicated extraction logic.       |
| Demo picker         | `discover_demo_images()` scans `sample.jpg` + `samples/`; sidebar selectbox + "Load demo image" button render only when fixtures exist. |
| Config              | `.streamlit/config.toml`: dark theme with magenta accent; `gatherUsageStats = false` (privacy tool shouldn't phone home). |

### 8.8 `tests/make_sample.py` — fixture generator

- `make_gradient((640, 480))` — synthetic RGB gradient (so the file isn't
  blank; JPEG compression has real content to chew on).
- `build_exif_dict()` — piexif-format dict with:
  - **IFD0:** `Make="AcmeCam"`, `Model="X-200"`, `Software="firmware 4.2.1"`,
    `Orientation=1`
  - **Exif IFD:** `DateTimeOriginal="2024:05:17 14:30:00"`,
    `DateTimeDigitized="…:01"`, `FNumber=(28,10)` (f/2.8),
    `ExposureTime=(1,250)`, `ISOSpeedRatings=100`, `FocalLength=(50,1)`,
    pixel dimensions 640×480
  - **GPS IFD (Eiffel Tower):** `GPSLatitudeRef=b"N"`,
    `GPSLatitude=[(48,1),(51,1),(3024,100)]`, `GPSLongitudeRef=b"E"`,
    `GPSLongitude=[(2,1),(17,1),(4020,100)]`
    → 48° 51' 30.24" N, 2° 17' 40.20" E → 48.8584, 2.2945
- Saves `sample.jpg` (JPEG, quality 90, ~14.2 KB).

### 8.9 `tests/make_samples.py` — demo fixture set generator

Parameterized generator (piexif, dev-only) producing five fixtures into
`samples/`, each with a distinct gradient so files are visually
distinguishable. Together with `sample.jpg` the set covers **all four GPS
quadrants**, the no-GPS branch, and the no-EXIF branch:

| Fixture                | Device / notes                         | GPS (decimal)                  |
| ---------------------- | -------------------------------------- | ------------------------------ |
| `pixel_sydney.jpg`     | Google Pixel 8, Android 14             | −33.8568, 151.2153 (S/E)       |
| `iphone_nyc.jpg`       | Apple iPhone 15 Pro, iOS 18.2          | 40.7580, −73.9855 (N/W)        |
| `galaxy_rio.jpg`       | Samsung SM-S921B, One UI 6.1           | −22.9519, −43.2105 (S/W)       |
| `dslr_landscape.jpg`   | Canon EOS R6 + LensModel, **no GPS**   | —                              |
| `clean_export.png`     | saved without `exif=` → no metadata    | —                              |

Specs live in the `SPECS` list (make/model/software/timestamps/capture
settings/DMS rationals per image); DMS values are hand-derived and
round-trip exactly through `dms_to_decimal`.

---

## 9. Data Model

### 9.1 `ExifReport` (dataclass)

| Field               | Type                     | Source tag(s)              | Notes                          |
| ------------------- | ------------------------ | -------------------------- | ------------------------------ |
| `file_path`         | `str`                    | —                          | As passed by caller            |
| `file_size`         | `int`                    | `os.path.getsize`          | Bytes                          |
| `image_format`      | `str`                    | `img.format`               | `"JPEG"`, `"PNG"`, …           |
| `image_size`        | `tuple[int, int]`        | `img.size`                 | (width, height)                |
| `camera_make`       | `str \| None`            | Make (271)                 |                                |
| `camera_model`      | `str \| None`            | Model (272)                |                                |
| `lens_model`        | `str \| None`            | LensModel (42036)          | Common on mirrorless/phones    |
| `software`          | `str \| None`            | Software (305)             | Firmware or editor             |
| `datetime_original` | `str \| None`            | DateTimeOriginal (36867)   | `YYYY:MM:DD HH:MM:SS`          |
| `datetime_digitized`| `str \| None`            | DateTimeDigitized (36868)  |                                |
| `f_number`          | `str \| None`            | FNumber (33437)            | Rendered `2.8`                |
| `exposure_time`     | `str \| None`            | ExposureTime (33434)       | Rendered `1/250`              |
| `iso`               | `str \| None`            | ISOSpeedRatings (34855)    |                                |
| `focal_length`      | `str \| None`            | FocalLength (37386)        | Rendered `50` (mm appended by formatter) |
| `orientation`       | `str \| None`            | Orientation (274)          | Raw value; `1` = normal        |
| `gps`               | `GpsInfo \| None`        | GPSInfo (34853) sub-IFD    | `None` when absent/incomplete  |
| `all_tags`          | `dict[str, str]`         | every parsed tag           | GPSInfo stored as placeholder note |

Properties: `has_exif` → `bool(all_tags)`; `has_gps` → `gps is not None`.

### 9.2 `GpsInfo` (dataclass)

| Field        | Type     | Example                                            |
| ------------ | -------- | -------------------------------------------------- |
| `latitude`   | `float`  | `48.8584`                                          |
| `longitude`  | `float`  | `2.2945`                                           |
| `dms_string` | `str`    | `48° 51' 30.24" N, 2° 17' 40.20" E`                |
| `maps_link`  | `str`    | `https://www.google.com/maps?q=48.858400,2.294500` |

---

## 10. EXIF Technical Primer

### 10.1 Where EXIF lives

In JPEG, EXIF occupies an **APP1 marker segment** immediately after the SOI,
beginning with `Exif\x00\x00` followed by a TIFF header. In TIFF, the tags
are native IFDs. In PNG, an `eXIf` chunk may carry the same TIFF structure
(rare in the wild; most PNGs from editors have none).

### 10.2 IFD structure

EXIF organizes tags into **Image File Directories**:

| IFD          | Contains                                        | Pillow access                |
| ------------ | ----------------------------------------------- | ---------------------------- |
| IFD0         | Camera identity, orientation, software          | `_getexif()` top level       |
| Exif sub-IFD | Timestamps, capture settings                    | Flattened into `_getexif()`  |
| GPS sub-IFD  | Coordinates, altitude, speed, satellites        | `GPSInfo` dict (id→value)    |
| Interop      | Rarely used                                     | Not surfaced                 |
| IFD1         | Embedded thumbnail                              | Not surfaced                 |

### 10.3 Tag reference (tags this tool surfaces)

| Tag                | ID (dec / hex)   | IFD   | Type          | Rendered as        |
| ------------------ | ---------------- | ----- | ------------- | ------------------ |
| Make               | 271 / 0x010F     | IFD0  | ASCII         | `AcmeCam`          |
| Model              | 272 / 0x0110     | IFD0  | ASCII         | `X-200`            |
| Software           | 305 / 0x0131     | IFD0  | ASCII         | `firmware 4.2.1`   |
| Orientation        | 274 / 0x0112     | IFD0  | SHORT         | `1`                |
| ExposureTime       | 33434 / 0x829A   | Exif  | RATIONAL      | `1/250`            |
| FNumber            | 33437 / 0x829D   | Exif  | RATIONAL      | `2.8`              |
| ISOSpeedRatings    | 34855 / 0x8827   | Exif  | SHORT         | `100`              |
| ExifImageWidth     | 40962 / 0xA002   | Exif  | LONG          | `640`              |
| ExifImageHeight    | 40963 / 0xA003   | Exif  | LONG          | `480`              |
| FocalLength        | 37386 / 0x920A   | Exif  | RATIONAL      | `50`               |
| DateTimeOriginal   | 36867 / 0x9003   | Exif  | ASCII         | `2024:05:17 14:30:00` |
| DateTimeDigitized  | 36868 / 0x9004   | Exif  | ASCII         | `2024:05:17 14:30:01` |
| LensModel          | 42036 / 0xA434   | Exif  | ASCII         | (when present)     |
| GPSInfo            | 34853 / 0x8825   | IFD0  | SubIFD ptr    | parsed → `GpsInfo` |

### 10.4 RATIONAL encoding

EXIF stores fractions as two 32-bit unsigned integers. Pillow exposes them
as `IFDRational` objects (`numerator`, `denominator`). The tool's
`_rational_str` policy:

- denominator 0 or 1 → integer
- numerator 1 (shutter speeds) → keep `1/N` fraction
- otherwise → decimal (`:g`) — `28/10` → `2.8`

---

## 11. GPS Coordinate Handling

### 11.1 Storage format

The GPS sub-IFD stores each axis as three RATIONALs (degrees, minutes,
seconds) plus an ASCII reference:

```
GPSLatitudeRef  (1)  = "N" | "S"
GPSLatitude     (2)  = [ (48,1), (51,1), (3024,100) ]
GPSLongitudeRef (3)  = "E" | "W"
GPSLongitude    (4)  = [ (2,1), (17,1), (4020,100) ]
```

### 11.2 Conversion

```
decimal = degrees + minutes/60 + seconds/3600
if ref in ("S", "W"): decimal = -decimal
```

Example: `48 + 51/60 + 30.24/3600 = 48.8584` (N) and
`2 + 17/60 + 40.20/3600 = 2.2945` (E) — the Eiffel Tower.

### 11.3 Link precision

Google Maps URLs are formatted to 6 decimal places
(`48.858400,2.294500`). One millionth of a degree ≈ **11 cm** at the
equator — finer than consumer GPS accuracy (~3–5 m), while eliminating
binary-float artifacts such as `2.2944999999999998`.

### 11.4 Robustness

`_parse_gps` requires all four coordinate tags; anything else returns
`None` (rendered as "No GPS data embedded"). Conversion failures
(`TypeError`, `ValueError`, `IndexError`, `ZeroDivisionError`) also degrade
to `None` rather than aborting the report.

---

## 12. CLI Reference

### 12.1 Synopsis

```
python -m exif_extractor IMAGE [IMAGE ...] [-a | --all] [-j | --json] [--no-color]
```

### 12.2 Options

| Flag           | Effect                                                            |
| -------------- | ----------------------------------------------------------------- |
| `IMAGE ...`    | One or more image paths (required, at least one)                  |
| `-a, --all`    | Append the complete EXIF tag dump after the structured report     |
| `-j, --json`   | Emit one JSON object per image (implies color-off)                |
| `--no-color`   | Force plain text (auto when piped/redirected or non-TTY)          |
| `-h, --help`   | Usage text with responsible-use epilog                            |

### 12.3 Exit codes

| Code | Meaning                                                    |
| ---- | ---------------------------------------------------------- |
| `0`  | Every requested file was processed successfully            |
| `1`  | At least one file failed (missing, unreadable, not image)  |

Failures do not abort the batch — remaining files are still processed, and
the code aggregates via `exit_code = exit_code or rc`.

### 12.4 Examples

```bash
python -m exif_extractor photo.jpg                 # basic report
python -m exif_extractor photo.jpg --all           # + full tag dump
python -m exif_extractor a.jpg b.png c.jpg         # batch
python -m exif_extractor photo.jpg --json          # machine-readable
python -m exif_extractor photo.jpg --no-color > r.txt   # clean redirect
```

---

## 13. Library API Reference

```python
from exif_extractor import (
    extract_exif,        # file -> ExifReport
    ExifReport,          # report dataclass
    dms_to_decimal,      # DMS rationals + ref -> signed decimal degrees
    google_maps_link,    # lat/lon -> URL string
)

# --- Extract ---
report = extract_exif("photo.jpg")

# --- Headline fields (None when absent) ---
report.camera_make          # "Apple"
report.camera_model         # "iPhone 14 Pro"
report.lens_model
report.software
report.datetime_original    # "2024:05:17 14:30:00"
report.f_number             # "2.8"
report.image_size           # (4032, 3024)
report.file_size            # bytes

# --- GPS ---
report.has_gps              # bool
if report.has_gps:
    report.gps.latitude     # 48.8584
    report.gps.longitude    # 2.2945
    report.gps.dms_string   # "48° 51' 30.24\" N, ..."
    report.gps.maps_link    # https://www.google.com/maps?q=...

# --- Full dump ---
report.all_tags             # {"Make": "Apple", ...}
report.has_exif             # bool

# --- Rendering (independent of CLI) ---
from exif_extractor.formatter import render_report, print_report
text = render_report(report, show_all_tags=True, color=False)
print_report(report)

# --- Errors ---
from exif_extractor.extractor import ExifError
try:
    extract_exif("missing.jpg")
except ExifError as e:
    print(e)                # "File not found: missing.jpg"

# --- Pure GPS helpers ---
dms_to_decimal((48,1), (51,1), (3024,100), "N")   # 48.8584
google_maps_link(48.8584, 2.2945)
# https://www.google.com/maps?q=48.858400,2.294500
```

---

## 14. Output Specification

### 14.1 Terminal report sections (in order)

| Section            | Contents                                                        |
| ------------------ | --------------------------------------------------------------- |
| Header             | `═`×50 rule, centered bold title, `═`×50 rule                    |
| `FILE`             | Path, Format, Dimensions (`W × H px`), File size (human units)  |
| `CAMERA`           | Make, Model, Lens, Software — or explicit "not present" note    |
| `CAPTURE SETTINGS` | Aperture (`f/2.8`), Exposure (`1/250 s`), ISO, Focal length — omitted entirely if all absent |
| `DATE / TIME`      | Taken, Digitized — or explicit note                             |
| `GPS / LOCATION`   | Latitude/Longitude (6-dp °), DMS string, green `▸ Google Maps:` link — or explicit note |
| `ALL EXIF TAGS`    | Only with `--all`; 28-char-aligned name/value rows              |

For EXIF-less images the report stops after `FILE` with a yellow notice:
"No EXIF metadata found in this image." plus a hint that a platform or
editor may have stripped it.

### 14.2 Layout constants

- Header/rules: 50 chars; section rules: 48 chars
- Row labels: left-padded to 14 chars (dump labels: 28)
- Multi-file runs: reports separated by a blank line + `═`×50 + blank line

### 14.3 Color behavior

| Environment                  | Behavior                                        |
| ---------------------------- | ----------------------------------------------- |
| TTY on POSIX                 | ANSI colors on                                  |
| TTY on Windows 10+           | VT processing enabled via `ctypes` → colors on  |
| Legacy console / VT failure  | Plain text (auto fallback)                      |
| Piped or redirected          | Plain text (isatty check)                       |
| `--no-color`                 | Plain text, always                              |
| `--json`                     | Always plain (color codes would corrupt JSON)   |

### 14.4 JSON schema (`--json`)

One object per image, matching `asdict(ExifReport)`:

```json
{
  "file_path": "sample.jpg",
  "file_size": 14565,
  "image_format": "JPEG",
  "image_size": [640, 480],
  "camera_make": "AcmeCam",
  "camera_model": "X-200",
  "lens_model": null,
  "software": "firmware 4.2.1",
  "datetime_original": "2024:05:17 14:30:00",
  "datetime_digitized": "2024:05:17 14:30:01",
  "f_number": "2.8",
  "exposure_time": "1/250",
  "iso": "100",
  "focal_length": "50",
  "orientation": "1",
  "gps": {
    "latitude": 48.8584,
    "longitude": 2.2945,
    "dms_string": "48° 51' 30.24\" N, 2° 17' 40.20\" E",
    "maps_link": "https://www.google.com/maps?q=48.858400,2.294500"
  },
  "all_tags": { "Make": "AcmeCam", "Model": "X-200", "...": "..." }
}
```

Error case (JSON mode):

```json
{ "file": "missing.jpg", "error": "File not found: missing.jpg" }
```

---

## 15. Error Handling

| Condition                    | Behavior                                                              |
| ---------------------------- | --------------------------------------------------------------------- |
| Path doesn't exist           | `ExifError("File not found: …")` → `✗ …` on **stderr**, exit 1         |
| Not an image / corrupt       | `ExifError("Could not read image '…': …")` wrapping Pillow's error    |
| Valid image, no EXIF         | Normal report; `FILE` section + explicit "No EXIF metadata" notice    |
| Partial EXIF (no camera)     | CAMERA section shows "No camera/software tags present."               |
| No GPS tags                  | GPS section shows "No GPS data embedded in this image."               |
| Malformed GPS (missing tag / bad rational) | `_parse_gps` → `None`; treated as "no GPS"             |
| Zero-denominator rational    | `_as_float` guards; `_rational_str` falls back to numerator           |
| Batch with mixed results     | Each file reported independently; exit 1 if any failed                |

Design stance: **missing metadata is data, not an error.** The tool states
clearly what is absent; only true I/O failures produce nonzero exits.

---

## 16. Installation & Quick Start

### Prerequisites

- Python 3.9+ (verified on 3.14.6)
- Pillow ≥ 10.0 (verified on 12.3.0)

### Install

```bash
cd E:\logan            # or wherever the project lives
python -m pip install -r requirements.txt
```

### 30-second demo

```bash
python -m exif_extractor sample.jpg
```

The bundled `sample.jpg` (14.2 KB) contains a full EXIF set with Eiffel
Tower GPS coordinates — the report ends with a live Google Maps link.

### Regenerate / customize the sample

```bash
python -m pip install piexif        # dev-only dependency
python tests/make_sample.py         # writes sample.jpg in project root
python tests/make_sample.py C:\some\dir   # or to a custom directory
```

### Try it on real photos

Point it at unedited camera/phone JPEGs. Most contain at least make/model
and timestamps; phone photos often include GPS. Images downloaded from
social platforms will typically show "No EXIF metadata" — the platforms
stripped it.

---

## 17. Testing & Verification

### 17.1 Strategy

The project ships a **self-contained fixture generator** rather than a
binary test image: `tests/make_sample.py` deterministically produces a JPEG
with known tag values, so expected output can be asserted exactly. Manual
verification was performed against this fixture plus adversarial inputs.

### 17.2 Verified test matrix

| #  | Case                                | Command                                      | Expected / Observed result                                            |
| -- | ----------------------------------- | -------------------------------------------- | --------------------------------------------------------------------- |
| 1  | Full EXIF + GPS JPEG                | `python -m exif_extractor sample.jpg`        | All sections; camera AcmeCam X-200; f/2.8; 48.858400°/2.294500°; Maps link ✅ |
| 2  | PNG without EXIF                    | `python -m exif_extractor plain.png`         | FILE section + "No EXIF metadata found in this image." ✅              |
| 3  | Full tag dump                       | `python -m exif_extractor sample.jpg --all`  | 15-entry ALL EXIF TAGS table appended ✅                               |
| 4  | JSON output                         | `python -m exif_extractor sample.jpg --json` | Valid JSON; `gps` object with clean 6-dp link ✅                        |
| 5  | Missing file                        | `python -m exif_extractor nonexistent.jpg`  | `✗ File not found: nonexistent.jpg` on stderr; exit code 1 ✅          |
| 6  | Batch mode                          | multiple paths                              | Reports separated by `═` divider; per-file processing ✅               |
| 7  | `dms_to_decimal` correctness        | `((48,1),(51,1),(3024,100),"N")`            | `48.8584` exactly ✅                                                    |
| 8  | `google_maps_link` float handling   | `(48.8584, 2.2945)`                         | `…q=48.858400,2.294500` (no float noise) ✅                            |
| 9  | Library import surface              | `from exif_extractor import …`              | All four exports usable; `report.gps.maps_link` correct ✅             |
| 10 | Web app landing render              | `AppTest.from_file("app.py").run()`         | No exceptions; explainer + feature cards render ✅                     |
| 11 | Web app sample report               | AppTest → click "Load sample image"         | No exceptions; 6 metrics; 48.8584 / 2.2945 present ✅                  |
| 12 | Web server boot                     | `python -m streamlit run app.py --server.headless` | HTTP 200 on :8501; health endpoint returns `ok` ✅             |
| 13 | Six-fixture batch (all quadrants)   | CLI over `sample.jpg` + `samples/*`         | S/E → −33.8568; N/W → −73.9855; S/W → both negative; no-GPS + no-EXIF branches render ✅ |
| 14 | Web demo picker + S-hemisphere load | AppTest → select `pixel_sydney`, click Load | 6 options listed; −33.8568 / 151.2153 metrics render ✅        |

### 17.3 GPS fixture ground truth

Encoded DMS → expected decimal (both verified through the full pipeline):

| Axis | DMS rationals                  | Decimal        |
| ---- | ------------------------------ | -------------- |
| Lat  | 48° 51' 30.24" N               | `48.8584`      |
| Lon  | 2° 17' 40.20" E                | `2.2945`       |

Cross-check: these are the Eiffel Tower's published coordinates
(48.8584, 2.2945).

### 17.4 Suggested automated tests (roadmap)

- ✅ *Shipped:* headless web-app smoke tests — `tests/test_streamlit_app.py`
  (Streamlit AppTest; run with `python tests/test_streamlit_app.py`)
- `pytest` suite asserting `ExifReport` fields against fixture constants
- Property test: `dms_to_decimal` with S/W refs equals negated N/E result
- Snapshot test of `render_report(..., color=False)`
- CLI integration test via `main([...])` return codes and capsys

---

## 18. Development Log

Honest record of issues hit while building v1.0.0 and their resolutions.

### #1 — Pillow cannot write nested GPS sub-IFD via `Image.Exif`

- **Symptom:** `exif.tobytes()` raised
  `TypeError: write_undefined() takes 2 positional arguments but 4 were given`,
  then `TypeError: bad operand type for abs(): 'tuple'` in
  `_limit_rational` when the GPS dict was assigned via
  `exif[Base.GPSInfo] = {...}`.
- **Root cause:** `Image.Exif.__setitem__` stores everything in `_data`;
  `tobytes()` only lifts sub-IFD dicts held in the internal `_ifds` map,
  which has no public setter. GPS DMS tuples therefore reached the writer
  mistyped.
- **Resolution:** fixture generation moved to **piexif**, which serializes
  nested IFDs correctly. The tool itself remains read-only and
  Pillow-only.

### #2 — GPS not detected (returned `None`)

- **Symptom:** full report rendered, but GPS section said "No GPS data".
- **Root cause:** `_parse_gps` named GPS tag ids with `PIL.ExifTags.TAGS`
  (the IFD0 namespace). Id 2 is `ExposureTime` there, not `GPSLatitude`;
  the required-key check silently failed.
- **Fix:** use `PIL.ExifTags.GPSTAGS` for the GPS IFD. Verified with a
  probe: `get_ifd(GPSInfo)` returns `{1:'N', 2:(48.0,51.0,30.24), …}`.

### #3 — Aperture displayed as `f/28/10`

- **Symptom:** `Aperture  f/28/10` instead of `f/2.8`.
- **Root cause:** `_stringify` rendered `IFDRational` as
  `f"{num}/{den}"`.
- **Fix:** new `_rational_str` policy — integers when denominator ≤ 1,
  `1/N` fractions for shutter speeds, `:g` decimals otherwise → `2.8`,
  `50`, `1/250`.

### #4 — Float noise in Maps URL

- **Symptom:** `…maps?q=48.8584,2.2944999999999998`.
- **Fix:** format both coordinates to 6 decimals in `google_maps_link`
  (≈11 cm precision — beyond GPS accuracy, kills the artifact).

### #5 — ANSI colors never rendered on Windows

- **Symptom:** raw `[35m…` sequences in captured output.
- **Root cause:** original `_supports_color` hard-disabled color on
  `win32`.
- **Fix:** `_enable_windows_ansi()` uses `ctypes` to set
  `ENABLE_VIRTUAL_TERMINAL_PROCESSING` on the console handle; failure
  falls back to plain text. `--no-color` remains a manual override.

### #6 — Environment/tooling notes

- First `pip install piexif` hit a different environment (silent no-op);
  `python -m pip install piexif` installed 1.1.3 correctly.
- A dead placeholder branch and a stray walrus expression were removed
  during cleanup before final verification.

### #7 — Web frontend added (v1.1.0)

- Built `app.py` on Streamlit 1.61.1, reusing `extract_exif` via a local
  temp file (the extractor is path-based; uploads never persist on disk
  beyond parsing and never leave the machine).
- Caught during smoke testing: `st.components.v1.iframe` had passed its
  announced removal date (2026-06-01) and warned on every run; migrated to
  the modern `st.iframe` — warning cleared, tests re-run green.
- Streamlit usage telemetry disabled (`browser.gatherUsageStats = false`)
  in `.streamlit/config.toml` — a privacy tool shouldn't phone home.
- Verified with Streamlit's AppTest harness (landing + sample flows, GPS
  metric assertions) and a headless server boot (HTTP 200, health `ok`).

---

## 19. Known Limitations

| #  | Limitation                                          | Detail / Mitigation                                                          |
| -- | --------------------------------------------------- | ---------------------------------------------------------------------------- |
| L1 | **Uses Pillow private API `img._getexif()`**        | Underscore-prefixed; could change in future Pillow. Migration path: `img.getexif()` + `exif.get_ifd(ExifTags.IFD.GPSInfo)` (roadmap R2). |
| L2 | **PNG EXIF support is weak**                        | Plain PNGs typically carry no EXIF; Pillow's `_getexif` doesn't read PNG `eXIf` chunks on all versions. Report will say "No EXIF metadata" — accurate for the common case. |
| L3 | **HEIC/HEIF unsupported**                           | Vanilla Pillow can't decode; `pillow-heif` extra would add it (roadmap R3).  |
| L4 | **GPS extras not surfaced**                         | Altitude, GPS timestamp, speed, satellites are in the sub-IFD but not parsed — only lat/lon (roadmap R4). |
| L5 | **MakerNotes not decoded**                          | Manufacturer-proprietary blobs (lens serials etc.) remain opaque in the dump. |
| L6 | **Embedded thumbnail not inspected**                | IFD1 thumbnail can itself carry metadata or differ from the main image.      |
| L7 | **`SUPPORTED_EXT` not enforced**                    | Declared in `cli.py` but informational; any Pillow-readable file is accepted. Arguably a feature (e.g. MPO/JPEG variants). |
| L8 | **No directory recursion / globbing**               | Explicit paths only (roadmap R5).                                            |
| L9 | **No EXIF removal**                                 | Read-only by design; stripping is the natural companion feature (roadmap R1). |
| L10| **Legacy consoles may show raw escapes**            | If VT enabling fails and the shell is still a TTY, codes can leak; `--no-color` is the escape hatch. |
| L11| **No automated test suite**                         | Verified manually (see §17); pytest suite is roadmap R6.                     |
| L12| **Orientation shown as raw number**                 | `1` rather than "normal", `6` rather than "rotated 90° CW". Cosmetic.        |
| L13| **Web uploads go through a temp file**              | `extract_exif` is path-based; uploads park in `tempfile` and are deleted after parsing. Local-only; nothing is uploaded anywhere. |
| L14| **Web uploader mirrors CLI format support**         | HEIC etc. rejected at the uploader (`ACCEPTED_TYPES`), consistent with Pillow limits (L3). |

---

## 20. Security, Privacy & Ethics

### Responsible-use stance

This is a **defensive/educational** tool. Its stated purpose is to expose
metadata risk so users can protect themselves.

**Appropriate use**

- Auditing your own images before sharing them publicly
- Privacy training, security courses, CTF challenges
- Verifying that a "cleaned" export actually had metadata removed
- Journalists/researchers examining files they legitimately possess

**Inappropriate use**

- Stalking, harassing, or deanonymizing individuals
- Processing images you have no right to inspect
- Building profiles of people's locations or routines

The CLI's `--help` epilog carries this notice explicitly.

### Threat-model notes (why EXIF matters)

- **Location disclosure:** GPS tags are the highest-impact leak — a single
  photo can reveal a home address, workplace, or school.
- **Temporal patterns:** DateTimeOriginal across many photos reconstructs
  routines and absences.
- **Device fingerprinting:** Make/Model/Software narrow identification;
  serial-number-bearing MakerNotes can uniquely identify a camera (not
  parsed by this tool, but present in the raw dump territory).
- **Platform behavior:** Major social networks strip EXIF on upload; the
  risk concentrates in direct/file transfers — which is exactly the case
  this tool lets users check.

### Operational safety of the tool itself

- **Fully offline (CLI)** — no network calls; the Google Maps link is a
  formatted string only (opening it is the user's choice)
- **Web frontend** — parsing is local (temp file, deleted after use); the
  embedded map iframe loads Google Maps in the browser only when GPS is
  displayed, and only the coordinates — never the image — are sent
- **Read-only** — never modifies input files
- **No telemetry** — no usage reporting of any kind
- **No exif writing** — cannot be used to forge metadata

### Removing EXIF before sharing (user guidance)

```bash
exiftool -all= photo.jpg          # ExifTool
mogrify -strip photo.jpg          # ImageMagick
```

Or use the OS "remove location" share option (iOS/Android share sheets),
or re-export through an editor that discards metadata.

---

## 21. Roadmap / Future Enhancements

| #   | Enhancement                                 | Value                                                 |
| --- | ------------------------------------------- | ----------------------------------------------------- |
| R1  | `--strip [OUT]` — write a metadata-free copy | Completes the privacy workflow: detect → remove       |
| R2  | Migrate to public API (`getexif()` + `get_ifd`) | Removes the `_getexif()` private-API dependency (L1) |
| R3  | HEIC/HEIF via `pillow-heif`                 | iPhone default format                                 |
| R4  | GPS altitude, timestamp, speed, satellites  | Richer location context                               |
| R5  | Directory recursion + glob patterns         | Audit whole libraries at once                         |
| R6  | pytest suite with fixture assertions        | CI-ready regression safety                            |
| R7  | `--csv` batch export                        | Spreadsheet-friendly audits                           |
| R8  | `--open` — launch the Maps link             | Convenience                                           |
| R9  | Map provider choice (OSM / Bing)            | Avoid Google dependency for link targets              |
| R10 | Orientation → human words                   | Cosmetic polish (L12)                                 |
| R11 | MakerNotes decoding (Canon/Nikon/Sony)      | Deeper device fingerprinting                          |
| R12 | `--ascii` fallback (no Unicode box chars)   | Legacy-console friendliness                           |

---

## 22. Glossary

| Term              | Definition                                                                |
| ----------------- | ------------------------------------------------------------------------- |
| **EXIF**          | Exchangeable Image File Format — metadata standard embedded in photos     |
| **IFD**           | Image File Directory — a tagged block within EXIF/TIFF                   |
| **Sub-IFD**       | An IFD referenced from another (e.g. GPS IFD via the GPSInfo tag)        |
| **RATIONAL**      | EXIF numeric type: two 32-bit ints forming a fraction                     |
| **IFDRational**   | Pillow's Python object exposing `numerator` / `denominator`              |
| **DMS**           | Degrees / Minutes / Seconds coordinate notation                          |
| **Decimal degrees** | Latitude/longitude as signed floats (S/W negative)                     |
| **OSINT**         | Open Source Intelligence — analysis of publicly available data            |
| **APP1**          | JPEG application segment where EXIF resides                               |
| **MakerNotes**    | Manufacturer-proprietary metadata blob inside EXIF                       |
| **Metadata stripping** | Removing EXIF before publication (exiftool, mogrify, OS share sheet) |
| **VT processing** | Windows console mode enabling ANSI escape interpretation                 |

---

## Appendix A — Verified Sample Output

Actual `python -m exif_extractor sample.jpg --all --no-color` output from
the final build (colors stripped for documentation):

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

ALL EXIF TAGS
────────────────────────────────────────────────
  DateTimeDigitized           2024:05:17 14:30:01
  DateTimeOriginal            2024:05:17 14:30:00
  ExifImageHeight             480
  ExifImageWidth              640
  ExifOffset                  115
  ExposureTime                1/250
  FNumber                     2.8
  FocalLength                 50
  GPSInfo                     <GPS data — parsed separately>
  ISOSpeedRatings             100
  Make                        AcmeCam
  Model                       X-200
  Orientation                 1
  Software                    firmware 4.2.1
```

EXIF-less image case:

```
══════════════════════════════════════════════════
               EXIF METADATA REPORT
══════════════════════════════════════════════════

FILE
────────────────────────────────────────────────
  Path          plain.png
  Format        PNG
  Dimensions    100 × 100 px
  File size     286 B

EXIF
────────────────────────────────────────────────
  No EXIF metadata found in this image.
  (It may have been stripped by a platform or editor.)
```

Error case (stderr, exit 1):

```
✗ File not found: nonexistent.jpg
```

---

*End of document — EXIF Metadata Extractor v1.0.0*
