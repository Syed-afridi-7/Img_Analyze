# EXIF Metadata Extractor & Privacy Inspector — Project Guide

An in-depth analysis of the **EXIF Metadata Extractor & Privacy Inspector** (`Img_Analyze`), outlining its architectural capabilities, supported features, operational usages, and real-world limitations.

---

## 1. Overview

Every time a modern smartphone or digital camera captures a photograph, it writes hidden metadata into the file container known as **EXIF** (Exchangeable Image File Format). This data silently travels with the image when shared as an original file attachment, potentially exposing:
- The exact physical location (GPS coordinates down to street level).
- The device make, model, lens, and hardware serial numbers.
- Exact timestamps (date and time to the second).
- Camera settings and software editing history.

This project is a hybrid **OSINT (Open Source Intelligence)**, **privacy self-auditing**, and **digital forensics** toolkit built with Python and Streamlit. It provides both a modern, interactive web interface and a lightweight CLI to extract, decode, visualize, and sanitize image metadata.

---

## 2. Key Features

### 2.1 File & Security Integrity
- **Cryptographic Hashing:** Computes **MD5**, **SHA-1**, and **SHA-256** checksums directly in-memory to verify image integrity and support forensic chain of custody.
- **Structural Properties:** Calculates exact file sizes, MIME types, image dimensions (width × height), megapixels (MP), aspect ratios (16:9, 4:3, 1:1, etc.), and DPI pixel density.
- **Color Architecture:** Detects color modes (RGB, RGBA, CMYK, Grayscale, Palette), bit depth per channel, total bit depth, alpha channel/transparency presence, and multi-frame animation counts (GIF / animated WebP).

### 2.2 Advanced EXIF & Camera Telemetry
- **Hardware Profile:** Extracts camera manufacturer, model, lens model, firmware version, and hardware serial numbers.
- **Decoded Exposure Settings:** Translates raw numeric tags into human-readable photography terminology:
  - Shutter speed / exposure time (e.g., `1/250 s`).
  - Aperture f-stop (e.g., `f/2.8`).
  - ISO speed rating.
  - Focal length and 35mm equivalent focal length.
  - Flash status (bitmask decoded: fired/not fired, red-eye reduction, return light detected).
  - White balance (Auto / Manual).
  - Metering mode (Center-Weighted, Spot, Multi-Segment / Pattern).
  - Exposure program (Manual, Shutter Priority, Aperture Priority, Normal).
- **Orientation Auto-Correction:** Reads the EXIF orientation tag and transposes the preview image using `ImageOps.exif_transpose` so vertical/portrait photos display right side up.

### 2.3 Geolocation & Mapping Intelligence
- **Dual Coordinate Representation:** Displays exact latitude, longitude, and altitude in decimal degrees and DMS (Degrees, Minutes, Seconds).
- **Interactive Multi-Map Display:**
  - Native interactive map via `st.map` / PyDeck.
  - OpenStreetMap embedded iframe (works reliably without API keys or browser framing blocks).
  - One-click navigation links to Google Maps, Apple Maps, and OpenStreetMap.

### 2.4 Visual & Color Palette Analysis
- **Dominant Color Extraction:** Quantizes image colors to surface the top 6 dominant colors with hex codes, RGB values, and percentage coverage.
- **Tonal Lighting Metrics:** Evaluates mean perceived brightness, median tone, and RMS contrast, classifying the shot (e.g., High Key, Low Key, or Balanced Exposure).

### 2.5 Extended Non-EXIF Metadata & AI Prompt Extraction
- **PNG Text Chunks:** Extracts embedded text chunks (`tEXt`, `zTXt`, `iTXt`), flagging AI generation prompts and parameters from tools like **Stable Diffusion**, **Midjourney**, and **ComfyUI**.
- **ICC Color Profiles:** Reads embedded ICC color profile descriptions (e.g., sRGB, Display P3, Adobe RGB).
- **Raw Container Info:** Dumps underlying container dictionaries (JFIF, TIFF, or WebP headers).

### 2.6 Interactive Tag Explorer
- Searchable and group-filterable data table listing all raw EXIF tags with Hex Tag IDs, category labels, and raw/formatted values.

### 2.7 Multi-Image Batch Analysis & Comparison
- **Multi-File Upload:** Drag-and-drop multiple images simultaneously into the web UI.
- **Batch Comparison Matrix:** Aggregates total image count, total file size, privacy risk breakdown, and side-by-side tabular comparison of camera models, timestamps, GPS, and hashes.
- **Multi-Point Batch Map:** Plots all geolocated photos in a batch together on a single interactive map.
- **Batch CSV Export:** Download combined metadata comparison across all uploaded photos.

### 2.8 Exporting & Privacy Scrubbing
- **Forensic PDF Export:** Generates a formatted, multi-page PDF report using `fpdf2` containing image previews, checksums, camera telemetry, GPS links, and full tag tables.
- **JSON & CSV Export:** Download structured reports for pipeline integration.
- **In-Memory Metadata Scrubber:** Click **"Download Cleaned Image"** to scrub all EXIF, GPS, serial numbers, and container metadata in-memory, producing a safe file ready for sharing.

---

## 3. How to Use the Project

### 3.1 Web Application
1. **Start the App:**
   - Double-click `run-web.bat` or run:
     ```powershell
     python -m streamlit run app.py
     ```
2. **Access the Dashboard:** Open your browser to `http://localhost:8501`.
3. **Analyze Photos:**
   - Drag and drop single or multiple photos into the main dropzone or sidebar.
   - Or click any quick test fixture (`🗼 Eiffel Tower`, `🗽 iPhone NYC`, `🦘 Pixel Sydney`, `🛡️ Clean PNG`).
4. **Review Tabs:**
   - **📋 Overview & Specs:** File hashes, geometry, and technical specs.
   - **📷 Camera & Capture:** Camera model, exposure, and timestamps.
   - **📍 GPS & Location:** Coordinates, altitude, and interactive maps.
   - **🎨 Visual & Colors:** Color swatches and exposure character.
   - **🗂️ Extended Metadata:** AI generation prompts and ICC profiles.
   - **🔍 Tag Explorer:** Search and filter all raw EXIF tags.
   - **💾 Export & Clean:** Download PDF/JSON/CSV reports or download a scrubbed, metadata-free image.

### 3.2 Command-Line Interface (CLI)
For headless servers, terminal scripting, or rapid terminal audits:
- **Analyze an image:**
  ```powershell
  run-cli.bat sample.jpg
  ```
- **Show all raw tags:**
  ```powershell
  run-cli.bat sample.jpg --all
  ```
- **Output JSON for automation:**
  ```powershell
  run-cli.bat sample.jpg --json
  ```
- **Disable terminal ANSI colors:**
  ```powershell
  run-cli.bat sample.jpg --no-color
  ```

---

## 4. Primary Use Cases

1. **Privacy Self-Auditing:**
   - Scrubbing photos before posting them on public forums, classifieds, social networks, or messaging apps.
   - Ensuring family or children's photos do not leak home or school GPS coordinates.
2. **OSINT & Investigative Journalism:**
   - Verifying the authenticity, camera hardware, capture date, and geolocation of submitted media.
   - Checking whether an image has been re-compressed or modified using different software.
3. **Digital Forensics & Incident Response:**
   - Recording cryptographic hashes (MD5, SHA-256) of evidence files.
   - Identifying device serial numbers to link photos to specific physical cameras.
4. **AI Generation Detection:**
   - Discovering embedded prompts and seed parameters inside AI-generated PNG files.
5. **Photography Workflow:**
   - Auditing lens profiles, exposure parameters, and focal lengths across photo collections.

---

## 5. Disadvantages & Limitations

While this tool is comprehensive for image metadata inspection, users should be aware of several technical and contextual limitations:

| Limitation | Technical Reason & Impact |
| :--- | :--- |
| **Social Media Stripping** | Social media platforms (Instagram, Twitter/X, WhatsApp, Facebook, Discord) automatically re-encode and strip EXIF metadata on upload to protect user privacy. Downloaded images from these platforms usually have no EXIF data left to extract. |
| **Tamperability (Unsigned Metadata)** | Standard EXIF blocks are unencrypted, unsigned plain text. Anyone with basic tools (e.g., `exiftool` or Python) can spoof, falsify, or modify timestamps, camera models, or GPS coordinates. EXIF data alone is not proof of authenticity without independent verification. |
| **Still Raster Images Only** | Supports standard raster image formats (`.jpg`, `.jpeg`, `.png`, `.webp`, `.tiff`, `.bmp`, `.gif`). It **does not** support video containers (`.mp4`, `.mov`, `.mkv`), audio files, or proprietary camera RAW formats (`.cr2`, `.nef`, `.arw`, `.dng`) without pre-conversion. |
| **Internet Dependency for Map Tiles** | The core extraction and metadata scrubbing execute 100% locally and offline. However, interactive map tiles (OpenStreetMap, PyDeck basemaps, or Google Maps links) require an internet connection to render geographical map layers. |
| **In-Memory Batch Scale** | Designed for interactive analysis of single images and small-to-medium batches (1 to ~50 images). It loads files into memory and is not architected as a high-throughput distributed pipeline for millions of images. |
| **Quantized Color Approximation** | Dominant color extraction uses Pillow's `MEDIANCUT` quantization on downscaled previews. While fast and representative for UI inspection, it provides an approximation rather than a full spectrophotometric or gamut analysis. |
| **Stripping vs. Deep Forensic Trace Scrubbing** | The built-in privacy scrubber removes all EXIF, GPS, and metadata tags from the image container. However, it does not alter image pixel content (e.g., visible street signs, house numbers, license plates, or reflections still remain visible in the photo itself). |

---

## 6. Summary Matrix

| Metric | Details |
| :--- | :--- |
| **Supported Formats** | JPEG, PNG, WEBP, TIFF, BMP, GIF |
| **Core Dependencies** | `Pillow>=10.0.0`, `fpdf2>=2.8.0`, `streamlit>=1.30.0`, `pandas>=2.0.0` |
| **Network Privacy** | 100% Local processing; zero telemetry; images never leave the local machine |
| **Testing Coverage** | 48 Automated Tests (Unit + Streamlit AppTest Smoke Tests) |
| **Platforms** | Windows, macOS, Linux |
