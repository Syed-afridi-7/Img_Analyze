# CHAPTER 9: Complete System Source Code & Data Dictionaries

---

## 9.1 Comprehensive EXIF & GPS Tag Reference Dictionary

The Exchangeable Image File Format (EXIF) standard (CIPA DC-008 / JEITA CP-3451D) organizes metadata within discrete Image File Directories (IFDs). Each tag is defined by a 16-bit unsigned integer hexadecimal identifier, a standardized tag name, an associated IFD category, an underlying TIFF 6.0 data type, and specific forensic or intelligence significance. 

The following exhaustive reference dictionary details the core primary, photographic telemetry, and geolocation tags implemented and parsed within the `Img_Analyze` engine.

### 9.1.1 Primary Image File Directory (IFD0) Tags

| Tag ID (Hex) | Tag ID (Dec) | Tag Name | IFD Category | Data Type | Forensic & Intelligence Significance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x010E` | 270 | `ImageDescription` | IFD0 | ASCII | Title or caption applied by camera operator or cataloging software. May contain user notes, location hints, or keywords revealing investigative context. |
| `0x010F` | 271 | `Make` | IFD0 | ASCII | Manufacturer of the image recording equipment (e.g., `"Apple"`, `"Canon"`, `"Nikon"`, `"Sony"`). First-tier hardware profiling indicator. |
| `0x0110` | 272 | `Model` | IFD0 | ASCII | Model name or number of the capture hardware (e.g., `"iPhone 15 Pro Max"`, `"ILCE-7RM5"`). Uniquely classifies device tier, sensor capabilities, and release era. |
| `0x0112` | 274 | `Orientation` | IFD0 | SHORT | Visual orientation of image sensor relative to the physical scene (Values 1 through 8). Used by `Img_Analyze` to execute deterministic transposition (`ImageOps.exif_transpose`) prior to analysis and sanitization. |
| `0x011A` | 282 | `XResolution` | IFD0 | RATIONAL | Number of pixels per `ResolutionUnit` in image width dimension. Indicates physical display or print scale intentions. |
| `0x011B` | 283 | `YResolution` | IFD0 | RATIONAL | Number of pixels per `ResolutionUnit` in image height dimension. |
| `0x0128` | 296 | `ResolutionUnit` | IFD0 | SHORT | Unit of measurement for resolution (1 = None, 2 = Inches, 3 = Centimeters). Defaults to inches (DPI) in standard digital workflows. |
| `0x0131` | 305 | `Software` | IFD0 | ASCII | Identifies firmware version (e.g., `"17.4.1"`) or third-party editing software (e.g., `"Adobe Photoshop 25.1"`, `"GIMP 2.10"`). Critical for detecting post-capture tampering, re-compression, or processing pipelines. |
| `0x0132` | 306 | `DateTime` | IFD0 | ASCII | Timestamp indicating when the file container was generated or modified (`YYYY:MM:DD HH:MM:SS`). Comparison against `DateTimeOriginal` reveals editing latency. |
| `0x013B` | 315 | `Artist` | IFD0 | ASCII | Identity of camera owner or photographer configured in hardware preferences. Directly leaks personal identifiable information (PII). |
| `0x8298` | 33432 | `Copyright` | IFD0 | ASCII | Legal copyright notice and owner attribution. Can link anonymous imagery to professional creative studios or corporate entities. |
| `0x8769` | 34665 | `ExifOffset` | IFD0 | LONG | Byte offset pointer from TIFF header start to the SubIFD (EXIF-specific camera telemetry directory). Essential for parsing traversal. |
| `0x8825` | 34853 | `GPSInfo` | IFD0 | LONG | Byte offset pointer from TIFF header start to the dedicated GPS IFD block. Signals presence of GNSS spatial telemetry. |

### 9.1.2 SubIFD (EXIF-Specific Photographic Telemetry) Tags

| Tag ID (Hex) | Tag ID (Dec) | Tag Name | IFD Category | Data Type | Forensic & Intelligence Significance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x829A` | 33434 | `ExposureTime` | SubIFD | RATIONAL | Shutter duration in seconds (e.g., $1/250$ s). Evaluates available ambient light at the scene; crucial for chronolocation validation and shadow analysis. |
| `0x829D` | 33437 | `FNumber` | SubIFD | RATIONAL | Lens aperture diameter ratio ($f$-number, e.g., $f/2.8$). Establishes depth of field; useful for optical lens fingerprinting. |
| `0x8822` | 34850 | `ExposureProgram` | SubIFD | SHORT | Exposure control mode (1 = Manual, 2 = Normal/Auto, 3 = Aperture Priority, 4 = Shutter Priority, etc.). Decoded by `Img_Analyze` via `EXPOSURE_PROGRAM_MAP`. |
| `0x8827` | 34855 | `ISOSpeedRatings` | SubIFD | SHORT | Sensor photographic sensitivity rating. High ISO values ($>3200$) correlate with extreme low-light environments, supporting temporal nighttime corroboration. |
| `0x9000` | 36864 | `ExifVersion` | SubIFD | UNDEFINED | Four-byte ASCII encoding of EXIF specification version supported (e.g., `"0232"` for EXIF 2.32). |
| `0x9003` | 36867 | `DateTimeOriginal` | SubIFD | ASCII | Exact date and time physical shutter actuated (`YYYY:MM:DD HH:MM:SS`). Primary forensic anchor for establishing chronological event sequences. |
| `0x9004` | 36868 | `DateTimeDigitized` | SubIFD | ASCII | Date and time analog image data was converted to digital samples. Identical to `DateTimeOriginal` in digital cameras; diverges in scanned film. |
| `0x9010` | 36880 | `OffsetTime` | SubIFD | ASCII | UTC timezone offset string for `DateTime` (e.g., `"+05:30"`). Resolves geographic longitude ambiguities without active GPS. |
| `0x9011` | 36881 | `OffsetTimeOriginal` | SubIFD | ASCII | UTC timezone offset string for `DateTimeOriginal`. Resolves local capture timezone. |
| `0x9012` | 36882 | `OffsetTimeDigitized` | SubIFD | ASCII | UTC timezone offset string for `DateTimeDigitized`. |
| `0x9201` | 37377 | `ShutterSpeedValue` | SubIFD | SRATIONAL | Shutter speed expressed in APEX (Additive System of Photographic Exposure) logarithmic units: $S_v = -\log_2(\text{ExposureTime})$. |
| `0x9202` | 37378 | `ApertureValue` | SubIFD | RATIONAL | Lens aperture expressed in APEX units: $A_v = 2 \log_2(\text{FNumber})$. |
| `0x9204` | 37380 | `ExposureBiasValue` | SubIFD | SRATIONAL | Exposure compensation offset applied by operator in EV units (e.g., $+0.7$ EV). |
| `0x9207` | 37383 | `MeteringMode` | SubIFD | SHORT | Scene luminance measurement methodology (1 = Average, 2 = Center-Weighted, 3 = Spot, 5 = Multi-Segment/Pattern). Decoded via `METERING_MODE_MAP`. |
| `0x9208` | 37384 | `LightSource` | SubIFD | SHORT | Illuminant type (0 = Unknown, 1 = Daylight, 3 = Tungsten, 4 = Flash, 17 = Standard Light A). Decoded via `LIGHT_SOURCE_MAP`. |
| `0x9209` | 37385 | `Flash` | SubIFD | SHORT | Bitmask recording strobe status (fired/suppressed), return light detection, and red-eye reduction. Decoded via `decode_flash()`. |
| `0x920A` | 37386 | `FocalLength` | SubIFD | RATIONAL | Physical focal length of optical lens assembly in millimeters (e.g., $24.0$ mm). |
| `0x927C` | 37500 | `MakerNote` | SubIFD | UNDEFINED | Vendor-specific proprietary binary payload (Nikon, Canon, Sony). May contain autofocus points, serial numbers, and internal temperature. |
| `0x9286` | 37510 | `UserComment` | SubIFD | UNDEFINED | Extended user comment block. May include 8-byte character code identifier (`ASCII\0\0\0` or `UNICODE\0`). |
| `0x9290` | 37520 | `SubSecTime` | SubIFD | ASCII | Fractional seconds string for `DateTime` (provides sub-millisecond precision). |
| `0x9291` | 37521 | `SubSecTimeOriginal` | SubIFD | ASCII | Fractional seconds string for `DateTimeOriginal`. Essential for micro-sequencing burst mode shots. |
| `0xA001` | 40961 | `ColorSpace` | SubIFD | SHORT | Color space colorimetric profile (1 = sRGB, 65535 = Uncalibrated / Adobe RGB). |
| `0xA002` | 40962 | `ExifImageWidth` | SubIFD | SHORT / LONG | Horizontal pixel count recorded by sensor before cropping. |
| `0xA003` | 40963 | `ExifImageHeight` | SubIFD | SHORT / LONG | Vertical pixel count recorded by sensor before cropping. |
| `0xA403` | 41987 | `WhiteBalance` | SubIFD | SHORT | White balance mode (0 = Auto, 1 = Manual). Decoded via `WHITE_BALANCE_MAP`. |
| `0xA405` | 41989 | `FocalLengthIn35mmFilm` | SubIFD | SHORT | Equivalent 35mm full-frame focal length. Allows standard field-of-view comparisons across disparate sensor formats. |
| `0xA431` | 42033 | `BodySerialNumber` | SubIFD | ASCII | Unique factory-etched serial number of camera body. Incontrovertible hardware fingerprint linking photos to specific physical hardware. |
| `0xA432` | 42034 | `LensSpecification` | SubIFD | 4 RATIONALs | Optical boundaries: minimum focal length, maximum focal length, minimum $f$-number at min focal, and min $f$-number at max focal. |
| `0xA433` | 42035 | `LensMake` | SubIFD | ASCII | Manufacturer of attached lens assembly (e.g., `"Sigma"`, `"Tamron"`). |
| `0xA434` | 42036 | `LensModel` | SubIFD | ASCII | Model name of lens assembly (e.g., `"FE 24-70mm F2.8 GM II"`). Critical for optical profiling. |
| `0xA435` | 42037 | `LensSerialNumber` | SubIFD | ASCII | Unique factory serial number of physical lens assembly. Second hardware fingerprint. |

### 9.1.3 GPS Sub-Directory (GPS IFD) Tags

| Tag ID (Hex) | Tag ID (Dec) | Tag Name | IFD Category | Data Type | Forensic & Intelligence Significance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x0000` | 0 | `GPSVersionID` | GPS IFD | BYTE (4) | Version of GPS IFD header (standard is `2.3.0.0`, encoded as `0x02 0x03 0x00 0x00`). |
| `0x0001` | 1 | `GPSLatitudeRef` | GPS IFD | ASCII | Latitude hemisphere reference: `'N'` indicates Northern Hemisphere ($+$), `'S'` indicates Southern Hemisphere ($-$). |
| `0x0002` | 2 | `GPSLatitude` | GPS IFD | 3 RATIONALs | Sexagesimal latitude expressed as degrees, minutes, and seconds triple: $\{\text{deg}, \text{min}, \text{sec}\}$. |
| `0x0003` | 3 | `GPSLongitudeRef` | GPS IFD | ASCII | Longitude meridian reference: `'E'` indicates Eastern Meridian ($+$), `'W'` indicates Western Meridian ($-$). |
| `0x0004` | 4 | `GPSLongitude` | GPS IFD | 3 RATIONALs | Sexagesimal longitude expressed as degrees, minutes, and seconds triple: $\{\text{deg}, \text{min}, \text{sec}\}$. |
| `0x0005` | 5 | `GPSAltitudeRef` | GPS IFD | BYTE | Altitude datum reference: `0` = Sea level (positive elevation), `1` = Below sea level (negative elevation). |
| `0x0006` | 6 | `GPSAltitude` | GPS IFD | RATIONAL | Distance above or below sea level datum expressed in meters. Reveals vertical floor elevation. |
| `0x0007` | 7 | `GPSTimeStamp` | GPS IFD | 3 RATIONALs | Universal Coordinated Time (UTC) atomic clock time recorded from satellite constellation: $\{\text{hour}, \text{min}, \text{sec}\}$. |
| `0x000B` | 11 | `GPSDOP` | GPS IFD | RATIONAL | Dilution of Precision (DOP). Measure of satellite constellation geometry accuracy. Low values ($<2.0$) indicate exceptional geospatial precision. |
| `0x000D` | 13 | `GPSSpeedRef` | GPS IFD | ASCII | Speed measurement unit: `'K'` = km/h, `'M'` = mph, `'N'` = knots. |
| `0x000E` | 14 | `GPSSpeed` | GPS IFD | RATIONAL | Velocity of GPS receiver during exposure. Reveals vehicular motion or aerial flight. |
| `0x0010` | 16 | `GPSImgDirectionRef`| GPS IFD | ASCII | Direction reference of camera optical axis: `'T'` = True north, `'M'` = Magnetic north. |
| `0x0011` | 17 | `GPSImgDirection` | GPS IFD | RATIONAL | Bearing angle ($0.0^\circ$ to $359.99^\circ$) indicating where camera was pointed during exposure. Critical for sight-line reconstruction. |
| `0x001D` | 29 | `GPSDateStamp` | GPS IFD | ASCII | Date string extracted from GNSS constellation (`YYYY:MM:DD`). Provides independent atomic verification against system clocks. |
| `0x001F` | 31 | `GPSHPositioningError`| GPS IFD | RATIONAL | Horizontal positioning error radius expressed in meters. Quantifies spatial uncertainty circle. |

---

## 9.2 PNG Ancillary Chunk Type Reference & AI Metadata Schemas

The Portable Network Graphics (PNG) specification (ISO/IEC 15948:2004) defines a chunk-based extensible container. While critical chunks (`IHDR`, `PLTE`, `IDAT`, `IEND`) govern raster rendering, *ancillary chunks* encapsulate auxiliary textual and colorimetric metadata.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              PNG 4-BYTE CHUNK STRUCTURE                                │
├──────────────────────┬──────────────────────┬───────────────────┬──────────────────────┤
│ Length (4 Bytes)     │ Chunk Type (4 Bytes) │ Chunk Data (Var)  │ CRC-32 (4 Bytes)     │
│ 32-bit unsigned int  │ 4 ASCII characters   │ Payload bytes     │ Cyclic Redundancy    │
└──────────────────────┴──────────────────────┴───────────────────┴──────────────────────┘
```

### 9.2.1 Textual Ancillary Chunk Architectures

`Img_Analyze` inspects three standardized textual chunks:
1. **`tEXt` (Uncompressed Latin-1 Text Chunk):**
   - **Structure:** Keyword (1–79 bytes, ISO-8859-1 null-terminated) + Text String (Latin-1 encoded).
   - **Usage:** Standard titles, authors, software names, and legacy generation strings.
2. **`zTXt` (Compressed Latin-1 Text Chunk):**
   - **Structure:** Keyword (1–79 bytes, null-terminated) + Compression Method (1 byte, $0 = \text{zlib/deflate}$) + Compressed Text Datastream.
   - **Usage:** Extended parameters, license text, and long descriptions.
3. **`iTXt` (International UTF-8 Text Chunk):**
   - **Structure:** Keyword (1–79 bytes, null-terminated) + Compression Flag (1 byte, 0 or 1) + Compression Method (1 byte) + Language Tag (ASCII, null-terminated) + Translated Keyword (UTF-8, null-terminated) + Text Datastream (UTF-8).
   - **Usage:** Modern international metadata, multi-lingual author signatures, and complex JSON AI prompts.

### 9.2.2 AI Generation Metadata Schemas in PNG Chunks

Generative AI diffusion engines (e.g., Automatic1111 Stable Diffusion WebUI, ComfyUI, Midjourney, NovelAI) utilize PNG textual chunks to serialize model checkpoints, positive prompts, negative prompts, sampling steps, and random seeds. `Img_Analyze` automatically extracts and displays these schemas:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                     TYPICAL GENERATIVE AI PNG CHUNK ALLOCATIONS                        │
├───────────────────┬───────────────────┬────────────────────────────────────────────────┤
│ Engine / Platform │ Chunk Identifier  │ Keyword & Structural Syntax                    │
├───────────────────┼───────────────────┼────────────────────────────────────────────────┤
│ Automatic1111     │ `tEXt` or `iTXt`  │ Keyword: `parameters`                          │
│ Stable Diffusion  │                   │ Value: Raw text block containing:              │
│                   │                   │   - Positive Prompt Text                       │
│                   │                   │   - Negative Prompt (`Negative prompt: ...`)   │
│                   │                   │   - Hyperparameters (`Steps: 30, Sampler:      │
│                   │                   │     DPM++ 2M Karras, CFG scale: 7, Seed:       │
│                   │                   │     3829104829, Size: 512x768, Model: v1-5`)   │
├───────────────────┼───────────────────┼────────────────────────────────────────────────┤
│ ComfyUI           │ `tEXt` or `iTXt`  │ Keyword: `prompt`                              │
│ Node Graph Engine │                   │ Value: Serialized JSON graph representing      │
│                   │                   │ node IDs, inputs, connections, and latent seed │
│                   │                   │ Keyword: `workflow`                            │
│                   │                   │ Value: Full visual layout coordinates in JSON  │
├───────────────────┼───────────────────┼────────────────────────────────────────────────┤
│ Fooocus / Forge   │ `tEXt`            │ Keyword: `Comment` or `Description`            │
│                   │                   │ Value: JSON or YAML encoded prompt dictionary  │
├───────────────────┼───────────────────┼────────────────────────────────────────────────┤
│ NovelAI           │ `tEXt`            │ Keyword: `Comment`                             │
│                   │                   │ Value: JSON string with `prompt`, `uc` (undes) │
└───────────────────┴───────────────────┴────────────────────────────────────────────────┘
```

---

## 9.3 Core Algorithmic Source Code Listings

The following production source code listings illustrate the core algorithms of `Img_Analyze`. Each listing is preceded by architectural rationale and followed by a rigorous technical annotation.

### 9.3.1 Algorithmic Listing 1: Core EXIF Extraction Pipeline (`exif_extractor/extractor.py`)

The primary extraction engine executes in-memory binary inspection, hashes byte arrays across multiple cryptographic algorithms simultaneously, extracts EXIF IFD structures via Pillow, normalizes sexagesimal GPS tags, decodes photographic enums, and evaluates privacy risk levels.

```python
def extract_exif(
    source: Union[str, os.PathLike, bytes, io.BytesIO] = None,
    file_name: Optional[str] = None,
    *,
    file_path: Optional[Union[str, os.PathLike]] = None,
) -> ExifReport:
    """Read an image source and return a structured EXIF report.

    Args:
        source: File path, PathLike, raw bytes, or BytesIO stream.
        file_name: Optional filename for display when source is bytes/BytesIO.
        file_path: Backward-compatibility keyword argument for file path.

    Raises:
        ExifError: If the source cannot be read or is not a valid image.
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
            current_pos = source.tell() if hasattr(source, "tell") else 0
            raw_bytes = source.read()
            if hasattr(source, "seek"):
                source.seek(current_pos)
        reported_path = file_name or "<in-memory>"
    else:
        raise ExifError(f"Unsupported source type: {type(source).__name__}")

    file_size = len(raw_bytes)
    if file_size == 0:
        raise ExifError("Image source is empty (0 bytes).")

    # Cryptographic hashes calculated directly in memory
    md5_hex = hashlib.md5(raw_bytes).hexdigest()
    sha1_hex = hashlib.sha1(raw_bytes).hexdigest()
    sha256_hex = hashlib.sha256(raw_bytes).hexdigest()

    # Image format, dimensions, geometry and palette
    try:
        img = Image.open(io.BytesIO(raw_bytes))
    except (UnidentifiedImageError, OSError) as exc:
        raise ExifError(f"Cannot identify image file: {exc}") from exc

    image_format = (img.format or os.path.splitext(reported_path)[1].lstrip(".").upper() or "UNKNOWN")
    width, height = img.size
    megapixels = round((width * height) / 1_000_000.0, 2)
    aspect_ratio_str = calculate_aspect_ratio(width, height)
    color_mode = img.mode
    color_depth = get_color_depth(color_mode)
    has_alpha = ("A" in color_mode or "transparency" in img.info)
    dpi = img.info.get("dpi")
    if dpi and isinstance(dpi, tuple):
        dpi = (round(float(dpi[0]), 1), round(float(dpi[1]), 1))
    else:
        dpi = None

    is_animated = bool(getattr(img, "is_animated", False))
    frame_count = int(getattr(img, "n_frames", 1))

    # Visual and color palette analysis
    dominant_colors = extract_dominant_colors(img, num_colors=6)
    brightness = calculate_brightness(img)

    # Extended non-EXIF metadata (PNG text chunks, ICC profiles, raw container info)
    png_chunks = {}
    if hasattr(img, "text") and isinstance(img.text, dict):
        for k, v in img.text.items():
            png_chunks[str(k)] = str(v)

    icc_bytes = img.info.get("icc_profile")
    icc_profile = extract_icc_profile_name(icc_bytes) if icc_bytes else None

    raw_info = {}
    for k, v in img.info.items():
        if k in ("exif", "icc_profile", "photoshop"):
            continue
        try:
            s_val = str(v)
            if len(s_val) > 200:
                s_val = s_val[:197] + "..."
            raw_info[str(k)] = s_val
        except Exception:
            pass

    # EXIF extraction
    all_tags: Dict[str, object] = {}
    raw_exif_dict: Dict[int, object] = {}
    gps_raw_dict: Dict[int, object] = {}

    try:
        exif_data = img.getexif()
    except Exception:
        exif_data = None

    if exif_data:
        for tag_id, value in exif_data.items():
            raw_exif_dict[tag_id] = value
            name = _tag_name(tag_id)
            all_tags[name] = _stringify(value)

        # Traverse SubIFDs
        for ifd_id in (IFD.Exif, IFD.GPSInfo, IFD.Makernote):
            try:
                sub_ifd = exif_data.get_ifd(ifd_id)
            except Exception:
                sub_ifd = None
            if not sub_ifd:
                continue

            if ifd_id == IFD.GPSInfo:
                for gid, gval in sub_ifd.items():
                    gps_raw_dict[gid] = gval
                    gname = GPSTAGS.get(gid, f"GPS_{gid}")
                    all_tags[gname] = _stringify(gval)
            else:
                for sid, sval in sub_ifd.items():
                    raw_exif_dict[sid] = sval
                    sname = _tag_name(sid)
                    all_tags[sname] = _stringify(sval)

    # Initialize structured report
    report = ExifReport(
        file_path=reported_path,
        file_size=file_size,
        image_format=image_format,
        image_size=(width, height),
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

    # GPS parsing and Privacy Risk evaluation
    if gps_raw_dict:
        report.gps = _parse_gps(gps_raw_dict)
        if report.gps:
            report.altitude = report.gps.altitude
            report.altitude_ref = report.gps.altitude_ref
            report.openstreetmap_link = report.gps.openstreetmap_link
            report.apple_maps_link = report.gps.apple_maps_link

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
```

#### Annotation of Algorithmic Listing 1
- **Lines 17–44 (Input Ingestion & Memory Buffer Management):** The function dynamically accepts file paths, raw bytes, or file-like streams. If given a seekable stream, it calculates current byte positions and restores stream pointers, ensuring idempotent execution.
- **Lines 49–53 (Forensic Hashing):** MD5, SHA-1, and SHA-256 digests are computed directly over `raw_bytes` before image decoding. This eliminates side effects and records baseline cryptographic signatures for judicial chain of custody.
- **Lines 55–74 (Geometric and Colorimetric Profiling):** Pillow opens a `BytesIO` stream. Image width, height, megapixels, GCD-reduced aspect ratios, color depth mappings, and DPI dimensions are derived without persisting decoded bitmaps to disk.
- **Lines 80–99 (Extended Non-EXIF Analysis):** PNG text chunk mappings (`img.text`) are inspected to capture generative AI parameters. The ICC profile is extracted and resolved to human-readable color profiles (e.g., sRGB, Display P3).
- **Lines 105–136 (Recursive IFD Traversal):** The primary IFD is extracted via `img.getexif()`. SubIFDs (`IFD.Exif`, `IFD.GPSInfo`, `IFD.Makernote`) are recursively inspected. Integer tag IDs are mapped to canonical names using `_tag_name()` and `GPSTAGS`.
- **Lines 174–188 (GPS Parsing & Risk Classification):** Raw GPS dictionaries are passed to `_parse_gps()`. The privacy engine flags `HIGH` risk if GNSS coordinates or hardware serial numbers are present.

---

### 9.3.2 Algorithmic Listing 2: Geodetic Coordinate Normalization (`exif_extractor/gps.py`)

Converts sexagesimal rational triples (Degrees, Minutes, Seconds) and hemisphere directional indicators into signed WGS84 decimal degrees, formatting active navigational URLs for Google Maps, OpenStreetMap, and Apple Maps.

```python
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
        ref: One of 'N', 'S', 'E', 'W' (case-insensitive, str or bytes).

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
    # Round to 6 decimals (~11 cm precision) to avoid float noise in the URL
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
```

#### Annotation of Algorithmic Listing 2
- **Mathematical Formula:** The sexagesimal to decimal conversion evaluates:
  $$\text{Decimal Degrees} = \text{Degrees} + \frac{\text{Minutes}}{60} + \frac{\text{Seconds}}{3600}$$
- **Sign Resolution:** Hemisphere references `'S'` (South) and `'W'` (West) invert the scalar into a signed floating-point number, adhering to the WGS84 ellipsoid coordinate frame.
- **Precision Truncation:** Decimal coordinates are formatted to 6 decimal places ($10^{-6}$ degrees), corresponding to approximately $11.1$ cm of ground resolution at the equator. This suppresses IEEE 754 floating-point inaccuracies (e.g., `2.2944999999999998`) in generated mapping links.

---

### 9.3.3 Algorithmic Listing 3: In-Memory Metadata Cleansing (`app.py`)

The sanitization engine erases EXIF, GPS, serial numbers, and container markers entirely within volatile RAM, transposing image pixels beforehand to ensure visual preservation.

```python
def create_scrubbed_image(pil_img: Image.Image) -> Tuple[bytes, str, str]:
    """Strip all EXIF, GPS, and metadata in-memory using Pillow.

    Returns:
        Tuple of (clean_bytes, filename_extension, mime_type)
    """
    # Exif transpose first so orientation is visually preserved before tag removal
    transposed = ImageOps.exif_transpose(pil_img)
    clean_img = Image.new(transposed.mode, transposed.size)
    clean_img.paste(transposed)

    raw_format = getattr(pil_img, "format", None) or "JPEG"
    fmt = raw_format if raw_format in ("JPEG", "PNG", "WEBP", "TIFF", "BMP", "GIF") else "JPEG"

    # JPEG does not support alpha / palette modes cleanly
    if fmt == "JPEG" and clean_img.mode in ("RGBA", "P", "LA"):
        clean_img = clean_img.convert("RGB")

    buf = io.BytesIO()
    if fmt == "JPEG":
        clean_img.save(buf, format="JPEG", quality=95)
        ext = ".jpg"
        mime = "image/jpeg"
    elif fmt == "PNG":
        clean_img.save(buf, format="PNG", optimize=True)
        ext = ".png"
        mime = "image/png"
    elif fmt == "WEBP":
        clean_img.save(buf, format="WEBP", quality=95)
        ext = ".webp"
        mime = "image/webp"
    elif fmt == "TIFF":
        clean_img.save(buf, format="TIFF")
        ext = ".tiff"
        mime = "image/tiff"
    elif fmt == "BMP":
        clean_img.save(buf, format="BMP")
        ext = ".bmp"
        mime = "image/bmp"
    elif fmt == "GIF":
        clean_img.save(buf, format="GIF")
        ext = ".gif"
        mime = "image/gif"
    else:
        clean_img.save(buf, format="JPEG", quality=95)
        ext = ".jpg"
        mime = "image/jpeg"

    buf.seek(0)
    return buf.getvalue(), ext, mime
```

#### Annotation of Algorithmic Listing 3
- **Visual Integrity Preservation:** In digital cameras, the physical sensor matrix is often oriented horizontally, relying on the EXIF `Orientation` tag (`0x0112`) to instruct downstream decoders to rotate the image. If EXIF is naively stripped without transposition, vertical/portrait images flip sideways. `ImageOps.exif_transpose(pil_img)` physically re-indexes the pixel array before metadata stripping occurs.
- **Sterile Object Instantiation:** `Image.new()` allocates a completely blank canvas in RAM. Pasting the transposed raster onto this sterile canvas guarantees that no residual `info`, `app`, or `exif` object pointers are retained.
- **Format Normalization & Quality Factor:** Mode conflicts (e.g., saving an RGBA alpha image as JPEG) are handled via `convert("RGB")`. JPEGs are written at 95% quality, balancing visual fidelity against artifact introduction.

---

### 9.3.4 Algorithmic Listing 4: Multi-Image Batch Aggregation (`exif_extractor/batch.py`)

Aggregates forensic telemetry across multi-image corpora, computing privacy risk distributions, unique hardware counts, and side-by-side comparative Pandas DataFrames.

```python
def build_batch_summary(reports: List[ExifReport]) -> Dict[str, Any]:
    """Build high-level aggregate summary statistics across a batch of ExifReports.

    Args:
        reports: List of parsed ExifReport instances.

    Returns:
        Dict containing total_count, with_gps_count, with_exif_count,
        total_file_size, unique_cameras, and privacy_breakdown.
    """
    total_count = len(reports)
    with_gps_count = sum(
        1
        for r in reports
        if getattr(r, "has_gps", False) or getattr(r, "gps", None) is not None
    )
    with_exif_count = sum(
        1
        for r in reports
        if getattr(r, "has_exif", False) or bool(getattr(r, "all_tags", None))
    )
    total_file_size = sum(getattr(r, "file_size", 0) for r in reports)

    unique_cameras: List[str] = []
    seen_cameras = set()
    for r in reports:
        cam = format_camera_name(r)
        if cam and cam not in seen_cameras:
            seen_cameras.add(cam)
            unique_cameras.append(cam)

    privacy_breakdown: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in reports:
        risk = getattr(r, "privacy_risk", "LOW") or "LOW"
        risk_str = str(risk).upper()
        if risk_str in privacy_breakdown:
            privacy_breakdown[risk_str] += 1
        else:
            privacy_breakdown[risk_str] = privacy_breakdown.get(risk_str, 0) + 1

    return {
        "total_count": total_count,
        "total_images": total_count,
        "with_gps_count": with_gps_count,
        "with_exif_count": with_exif_count,
        "total_file_size": total_file_size,
        "unique_cameras": unique_cameras,
        "privacy_breakdown": privacy_breakdown,
    }


def build_comparison_dataframe(reports: List[ExifReport]) -> pd.DataFrame:
    """Build a consolidated comparison pandas DataFrame from a list of ExifReports.

    Columns:
        'File Name', 'Format', 'Dimensions', 'MP', 'File Size',
        'Camera', 'Date Taken', 'GPS', 'Privacy Risk', 'MD5'.
    """
    columns = [
        "File Name",
        "Format",
        "Dimensions",
        "MP",
        "File Size",
        "Camera",
        "Date Taken",
        "GPS",
        "Privacy Risk",
        "MD5",
    ]
    rows = []
    for r in reports:
        fname = os.path.basename(r.file_path) if r.file_path else "unknown"
        w, h = getattr(r, "image_size", (0, 0))
        dim_str = f"{w} x {h}" if (w and h) else "N/A"
        mp_val = getattr(r, "megapixels", None)
        mp_str = f"{mp_val:.2f} MP" if mp_val is not None else "N/A"
        size_str = _human_size(getattr(r, "file_size", 0))
        camera_str = format_camera_name(r) or "N/A"
        date_str = getattr(r, "datetime_original", None) or "N/A"

        gps_obj = getattr(r, "gps", None)
        if gps_obj and getattr(gps_obj, "latitude", None) is not None:
            gps_str = f"{gps_obj.latitude:.4f}, {gps_obj.longitude:.4f}"
        else:
            gps_str = "None"

        risk_val = getattr(r, "privacy_risk", "LOW") or "LOW"
        md5_val = getattr(r, "md5", None) or "N/A"

        rows.append({
            "File Name": fname,
            "Format": getattr(r, "image_format", "N/A"),
            "Dimensions": dim_str,
            "MP": mp_str,
            "File Size": size_str,
            "Camera": camera_str,
            "Date Taken": date_str,
            "GPS": gps_str,
            "Privacy Risk": risk_val,
            "MD5": md5_val,
        })

    return pd.DataFrame(rows, columns=columns)
```

#### Annotation of Algorithmic Listing 4
- **Deduplication Logic:** `format_camera_name()` intelligently consolidates manufacturer and model strings. If the make (`"Canon"`) is already embedded inside the model (`"Canon EOS 5D Mark IV"`), it eliminates redundant duplication.
- **Categorical Aggregations:** Batch tallies isolate geolocation leaks (`with_gps_count`), metadata presence (`with_exif_count`), cumulative storage bytes, and categorical threat distributions (`HIGH`, `MEDIUM`, `LOW`).
- **Structured Relational Projections:** `build_comparison_dataframe()` translates variable-length, nested dataclass objects into a normalized 10-column relational matrix, facilitating direct export to CSV/Excel or visual display via Streamlit data grids.

---

### 9.3.5 Algorithmic Listing 5: Automated Forensic PDF Report Generation (`exif_extractor/pdf_export.py`)

Compiles cryptographic integrity digests, camera telemetry, GPS mapping URLs, and complete raw tag tables into a court-admissible, multi-page PDF document using `fpdf2`.

```python
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
    """Generate a clean, professional forensic PDF report for an ExifReport."""
    pdf = ForensicReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # File Overview & Privacy Risk Box
    risk = getattr(report, "privacy_risk", "LOW")
    reasons = getattr(report, "privacy_reasons", [])

    if risk == "HIGH":
        pdf.set_fill_color(254, 242, 242)
        pdf.set_draw_color(239, 68, 68)
        risk_label = "[HIGH PRIVACY RISK] - Sensitive Identity/Location Data Detected"
    elif risk == "MEDIUM":
        pdf.set_fill_color(255, 251, 235)
        pdf.set_draw_color(245, 158, 11)
        risk_label = "[MEDIUM PRIVACY RISK] - Identifying Telemetry Present"
    else:
        pdf.set_fill_color(240, 253, 244)
        pdf.set_draw_color(34, 197, 94)
        risk_label = "[LOW PRIVACY RISK] - Minimal Metadata Found"

    pdf.set_line_width(0.5)
    pdf.cell(0, 7, risk_label, border=1, fill=True, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(2)

    # Cryptographic Hashes Section
    pdf.chapter_title("1. Cryptographic File Integrity & Hashing")
    pdf.key_value_row("File Path / Source", os.path.basename(report.file_path) if report.file_path else "In-Memory Buffer")
    pdf.key_value_row("File Size", f"{report.file_size:,} bytes ({_human_size(report.file_size)})")
    pdf.key_value_row("MD5 Checksum", getattr(report, "md5", "N/A") or "N/A")
    pdf.key_value_row("SHA-1 Checksum", getattr(report, "sha1", "N/A") or "N/A")
    pdf.key_value_row("SHA-256 Checksum", getattr(report, "sha256", "N/A") or "N/A")
    pdf.ln(2)

    # Camera & Exposure Telemetry Section
    pdf.chapter_title("2. Hardware & Exposure Telemetry")
    pdf.key_value_row("Camera Make", report.camera_make or "Unknown / Not Recorded")
    pdf.key_value_row("Camera Model", report.camera_model or "Unknown / Not Recorded")
    pdf.key_value_row("Lens Model", report.lens_model or "N/A")
    pdf.key_value_row("Date/Time Original", report.datetime_original or "N/A")
    pdf.key_value_row("Exposure Time", report.exposure_time or "N/A")
    pdf.key_value_row("F-Number", report.f_number or "N/A")
    pdf.key_value_row("ISO Speed", str(report.iso) if report.iso else "N/A")
    pdf.key_value_row("Flash Status", getattr(report, "flash_description", "N/A") or "N/A")
    pdf.ln(2)

    # GPS Coordinates Section
    if report.has_gps and report.gps:
        pdf.chapter_title("3. Geolocation & Satellite Telemetry")
        pdf.key_value_row("Latitude", f"{report.gps.latitude:.6f} deg")
        pdf.key_value_row("Longitude", f"{report.gps.longitude:.6f} deg")
        pdf.key_value_row("DMS Representation", report.gps.dms_string)
        if report.gps.altitude is not None:
            pdf.key_value_row("Altitude", f"{report.gps.altitude} meters")
        if report.gps.maps_link:
            pdf.key_value_row("Google Maps Pin", report.gps.maps_link)
        pdf.ln(2)

    # Complete Raw Tag Explorer Table
    if report.all_tags:
        pdf.add_page()
        pdf.chapter_title("4. Complete Raw EXIF Tag Manifest")
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(226, 232, 240)
        pdf.cell(55, 6, "Tag Name", border=1, fill=True)
        pdf.cell(0, 6, "Recorded Value", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 7)
        for tag_name, val in sorted(report.all_tags.items()):
            pdf.cell(55, 5, _clean_text(tag_name)[:32], border=1)
            pdf.cell(0, 5, _clean_text(str(val))[:100], border=1, new_x="LMARGIN", new_y="NEXT")

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
```

#### Annotation of Algorithmic Listing 5
- **Typography and String Sanitization:** The `_clean_text()` helper filters Unicode symbols, replacing non-Latin-1 typographical artifacts (degrees symbols, curly quotes, dashes, alerts) with standard ISO-8859-1 equivalents, preventing runtime exceptions within standard core PDF font tables.
- **Dynamic Layout & Header/Footer Anchors:** Subclasses `FPDF` to inject professional running headers, timestamps, and page numbers (`Page X of Y` via alias replacement).
- **Evidentiary Categorization:** Systematically structures reports into logical sections: Risk Rating Banner, Cryptographic Hashes, Hardware Telemetry, Geodetic Positioning, and Exhaustive Raw Tag Tables.
- **In-Memory Buffer Streaming:** The resulting PDF binary is written to an in-memory `io.BytesIO()` stream, upholding the zero-disk footprint principle.
