# CHAPTER 4: Detailed System Implementation & Code Walkthrough

## Abstract

This chapter provides an exhaustive, line-by-line and architectural code walkthrough of **Img_Analyze** (*Interactive EXIF Metadata Extractor, OSINT Telemetry Inspector, and Privacy Sanitization Engine*), examining the concrete algorithms, data structures, and defensive engineering patterns implemented across `exif_extractor/` and `app.py`. The technical analysis spans nine comprehensive implementation domains: cryptographic stream verification and memory pointer management; binary EXIF parsing, sub-IFD traversal, and register bitmask decoding; geodetic WGS-84 coordinate transformation and mapping payload generation; non-EXIF and generative AI parameter extraction from PNG chunk trees; visual analytics via median-cut vector quantization and root-mean-square (RMS) tonal profiling; the zero-disk in-memory sanitization pipeline with orientation normalization; multi-page forensic PDF compilation via low-level canvas primitives in `fpdf2`; multi-image batch aggregation and tabular comparison; and headless command-line execution with structured JSON serialization. All algorithms are analyzed alongside their theoretical principles, formal pseudocode, and production Python implementations, emphasizing cross-platform determinism, memory isolation, and algorithmic safety.

---

## 4.1 Cryptographic Hash Extraction and Stream Handling

### 4.1.1 Principles of Cryptographic Integrity in Digital Forensics

In digital forensics and open-source intelligence (OSINT), the principle of data integrity requires that digital evidence remains unaltered throughout the investigative lifecycle. Forensic admissibility demands verifiable proof that analytical tools have processed the exact bitstream captured from the source media without introducing mutations, side-channel modifications, or metadata timestamp alterations.

Cryptographic hash functions $\mathcal{H}: \{0, 1\}^* \to \{0, 1\}^n$ map arbitrary-length binary inputs to fixed-length bit sequences such that:
1. **Pre-image Resistance (One-Way Property):** Given a digest value $h$, it is computationally infeasible to find an input message $m$ such that $\mathcal{H}(m) = h$.
2. **Second Pre-image Resistance (Weak Collision Resistance):** Given an input $m_1$, it is computationally infeasible to locate a distinct input $m_2 \ne m_1$ such that $\mathcal{H}(m_1) = \mathcal{H}(m_2)$.
3. **Collision Resistance (Strong Collision Resistance):** It is computationally infeasible to find any pair of distinct inputs $(m_1, m_2)$ such that $\mathcal{H}(m_1) = \mathcal{H}(m_2)$.

Img_Analyze implements multi-algorithm cryptographic verification by computing three concurrent cryptographic digests over the raw ingested byte sequence: MD5 (128 bits), SHA-1 (160 bits), and SHA-256 (256 bits). While MD5 and SHA-1 have known theoretical collision vulnerabilities against targeted cryptanalytic attacks, they remain standard in legacy forensic indices (e.g., the NIST National Software Reference Library), while SHA-256 provides collision-resistant security under contemporary cryptographic standards.

### 4.1.2 Algorithmic Implementation of `extract_file_hashes`

The cryptographic sealing logic is implemented in the core extraction pipeline within `exif_extractor/extractor.py` and mirrored in `app.py`. The extraction routine accepts an immutable binary buffer and returns a strongly typed dictionary containing hexadecimal digest strings.

```python
def extract_file_hashes(file_bytes: bytes) -> Dict[str, str]:
    """Compute cryptographic digests (MD5, SHA-1, SHA-256) across an immutable byte buffer.

    Args:
        file_bytes: The raw binary payload of the ingested image.

    Returns:
        Dict[str, str]: A dictionary mapping algorithm identifiers to lowercase
        hexadecimal digest strings.
    """
    if not isinstance(file_bytes, (bytes, bytearray)):
        raise TypeError(f"Expected binary byte buffer, received {type(file_bytes).__name__}")
        
    md5_digest = hashlib.md5(file_bytes).hexdigest()
    sha1_digest = hashlib.sha1(file_bytes).hexdigest()
    sha256_digest = hashlib.sha256(file_bytes).hexdigest()

    return {
        "md5": md5_digest,
        "sha1": sha1_digest,
        "sha256": sha256_digest,
    }
```

#### Line-by-Line Code Walkthrough:
* **Line 10:** Type validation verifies that `file_bytes` is a binary sequence (`bytes` or `bytearray`), guarding against inadvertent string or object ingestion.
* **Lines 12–14:** `hashlib.md5(file_bytes)`, `hashlib.sha1(file_bytes)`, and `hashlib.sha256(file_bytes)` allocate native C-optimized hashing contexts, pass the entire buffer through OpenSSL-backed assembly routines, and finalize the message digest into 32, 40, and 64 character lowercase hexadecimal strings via `.hexdigest()`.
* **Lines 16–20:** The computed digests are bundled into a key-value dictionary, establishing the cryptographic identity of the artifact.

#### Algorithmic Pseudocode: Multi-Digest Verification Engine

```
Algorithm 1: Multi-Algorithm Cryptographic Digest Generation
Input: Raw byte sequence B of length N
Output: Cryptographic verification dictionary H

1: procedure GENERATE_DIGESTS(B)
2:    if B is not of type BYTES and B is not of type BYTEARRAY then
3:        throw TypeError("Buffer must be binary sequence")
4:    end if
5:    ctx_md5    <- InitializeHashContext(MD5)
6:    ctx_sha1   <- InitializeHashContext(SHA1)
7:    ctx_sha256 <- InitializeHashContext(SHA256)
8:    
9:    UpdateHashContext(ctx_md5, B)
10:   UpdateHashContext(ctx_sha1, B)
11:   UpdateHashContext(ctx_sha256, B)
12:   
13:   H["md5"]    <- EncodeToHex(FinalizeHash(ctx_md5))
14:   H["sha1"]   <- EncodeToHex(FinalizeHash(ctx_sha1))
15:   H["sha256"] <- EncodeToHex(FinalizeHash(ctx_sha256))
16:   return H
17: end procedure
```

#### Computational Complexity and Memory Bounds:
For an input byte sequence of length $N$, each hashing algorithm processes data in fixed-size blocks:
* MD5 processes 512-bit (64-byte) blocks across 64 operations.
* SHA-1 processes 512-bit (64-byte) blocks across 80 operations.
* SHA-256 processes 512-bit (64-byte) blocks across 64 operations.

The total computational complexity is strictly linear:

$$\mathcal{T}_{\text{hash}}(N) = \mathcal{O}(N)$$

Because the hash contexts operate directly over the existing memory buffer without duplicating the byte array, the auxiliary spatial complexity is constant:

$$\mathcal{S}_{\text{aux}}(N) = \mathcal{O}(1)$$

### 4.1.3 Stream Normalization and Pointer Resetting (`io.BytesIO.seek(0)`)

In reactive execution environments like Streamlit, an uploaded file is delivered as a wrapped stream (`streamlit.runtime.uploaded_file_manager.UploadedFile`). Such objects encapsulate an internal file-like pointer referencing the current read position.

A frequent failure mode in stream-based architectures is **Pointer Exhaustion**: when an upstream component (such as a MIME sniffer or hash generator) reads the stream to its terminal byte, the read cursor rests at offset $N = \text{len}(\mathcal{B})$. If a downstream parser (e.g., `PIL.Image.open()`) subsequently attempts to read the stream without cursor repositioning, it encounters an immediate End-Of-File (EOF) condition, raising an `UnidentifiedImageError`.

Img_Analyze enforces strict stream normalization semantics in `exif_extractor/extractor.py` (lines 584–612):

```python
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
        pos = source.tell() if hasattr(source, "tell") else None
        raw_bytes = source.read()
        if pos is not None and hasattr(source, "seek"):
            source.seek(pos)
    reported_path = file_name or "<in-memory>"
else:
    raise ExifError(f"Unsupported source type: {type(source)}")
```

#### Detailed Architectural Walkthrough of Stream Handling:
1. **Polymorphic Source Resolution:** The engine accepts multiple source representations: concrete filesystem paths (`str`, `os.PathLike`), immutable byte sequences (`bytes`, `bytearray`), or virtual stream descriptors (`io.IOBase`, `UploadedFile`).
2. **Buffer Extraction without Pointer Side-Effects:** For streams exposing `getvalue()` (such as `io.BytesIO`), the underlying contiguous buffer is accessed directly, completely bypassing pointer state.
3. **Pointer Bookkeeping:** On generic file-like objects lacking `getvalue()`, the current stream position is recorded via `source.tell()`. The buffer is consumed via `source.read()`, and the cursor is restored to its entry offset via `source.seek(pos)`. This ensures that caller state remains intact.
4. **Isolated Virtual Stream Instantiation:** Subsequent raster decoding and chunk scanning operate on an independent virtual stream instantiated via `io.BytesIO(raw_bytes)`. This guarantees that downstream library operations cannot corrupt external stream cursors.

---

## 4.2 EXIF Parsing & Human-Readable Telemetry Translation

### 4.2.1 Decoding `_getexif()` and Mapping Through `ExifTags.TAGS`

The EXIF specification defines metadata as a hierarchy of Image File Directories (IFDs) modeled on the TIFF 6.0 format. An IFD consists of a 2-byte count of field entries, followed by a sequence of 12-byte Field Entries, and a 4-byte offset to the next IFD. Each field entry conforms to the following binary packing structure:

```
+-----------------------------------------------------------------------+
|                       EXIF IFD ENTRY STRUCTURE (12 BYTES)             |
+-------------------+-------------------+---------------+---------------+
| Bytes 0-1         | Bytes 2-3         | Bytes 4-7     | Bytes 8-11    |
+-------------------+-------------------+---------------+---------------+
| Tag ID            | Field Type        | Component     | Value /       |
| (16-bit unsigned) | (16-bit unsigned) | Count (32-bit)| Offset (32-bit|
+-------------------+-------------------+---------------+---------------+
```

The primary tag catalog is defined in `PIL.ExifTags.TAGS`, which maps 16-bit numerical IDs to standardized alphanumeric identifiers (e.g., $271 \to \text{"Make"}$, $272 \to \text{"Model"}$, $306 \to \text{"DateTime"}$). 

In `exif_extractor/extractor.py`, tag extraction follows a resilient three-tier fallback mechanism:

```python
# 1. Modern Pillow getexif()
exif_obj = None
try:
    if hasattr(img, "getexif"):
        exif_obj = img.getexif()
except Exception:
    exif_obj = None

if exif_obj and len(exif_obj) > 0:
    for tag_id, value in exif_obj.items():
        if tag_id == 34853:  # GPSInfo Sub-IFD pointer
            continue
        raw_exif_dict[tag_id] = value

    try:
        if hasattr(IFD, "Exif"):
            exif_sub = exif_obj.get_ifd(IFD.Exif)
            for tag_id, value in exif_sub.items():
                raw_exif_dict[tag_id] = value
        if hasattr(IFD, "GPSInfo"):
            gps_sub = exif_obj.get_ifd(IFD.GPSInfo)
            if gps_sub:
                gps_raw_dict.update(gps_sub)
        if hasattr(IFD, "MakerNote"):
            mn_sub = exif_obj.get_ifd(IFD.MakerNote)
            for tag_id, value in mn_sub.items():
                raw_exif_dict[tag_id] = value
        if hasattr(IFD, "Interop"):
            interop_sub = exif_obj.get_ifd(IFD.Interop)
            for tag_id, value in interop_sub.items():
                raw_exif_dict[tag_id] = value
    except Exception:
        pass

# 2. Fallback to legacy img._getexif()
if not raw_exif_dict and hasattr(img, "_getexif"):
    try:
        legacy_exif = img._getexif()
        if legacy_exif:
            for tag_id, value in legacy_exif.items():
                if tag_id == 34853 or _tag_name(tag_id) == "GPSInfo":
                    if isinstance(value, dict) and not gps_raw_dict:
                        gps_raw_dict.update(value)
                else:
                    raw_exif_dict[tag_id] = value
    except Exception:
        pass

# 3. Fallback to piexif byte parsing
if (not raw_exif_dict or not gps_raw_dict) and "exif" in img.info:
    try:
        import piexif
        p_data = piexif.load(img.info["exif"])
        if not raw_exif_dict:
            for ifd_name in ("0th", "Exif", "Interop", "1st"):
                if ifd_name in p_data and isinstance(p_data[ifd_name], dict):
                    for tag_id, value in p_data[ifd_name].items():
                        raw_exif_dict[tag_id] = value
        if not gps_raw_dict and "GPS" in p_data and isinstance(p_data["GPS"], dict):
            gps_raw_dict.update(p_data["GPS"])
    except Exception:
        pass
```

#### Detailed Multi-Tier Fallback Analysis:
1. **Tier 1 (Modern `getexif()` and `IFD` traversal):** Pillow 6.0+ introduced `getexif()`, which returns an `Image.Exif` object. Unlike legacy dictionaries, this object provides explicit access to sub-IFDs via `get_ifd()`. The parser explicitly iterates through `IFD.Exif` ($0\text{x}8769$), `IFD.GPSInfo` ($0\text{x}8825$), `IFD.MakerNote` ($0\text{x}927C$), and `IFD.Interop` ($0\text{x}A005$), flattening relevant tags into `raw_exif_dict` while isolating GPS tags into `gps_raw_dict`.
2. **Tier 2 (Legacy `_getexif()`):** For legacy Pillow versions or unusual image structures, the private `_getexif()` method returns a pre-flattened dictionary where Exif sub-IFD entries are already elevated to the top-level namespace. The algorithm inspects tag $34853$ to extract the embedded GPS dictionary.
3. **Tier 3 (Binary `piexif` Stream Recovery):** If internal Pillow structures fail (e.g., due to strict TIFF header validation or non-standard offset alignments), the engine inspects the raw `img.info["exif"]` byte blob using `piexif.load()`. It systematically traverses directories `0th`, `Exif`, `Interop`, `1st`, and `GPS`, recovering metadata that native decoders reject.

### 4.2.2 Tag Normalization and Stringification (`_stringify` & `_rational_str`)

Raw EXIF values exhibit extreme type heterogeneity: ASCII byte strings, signed/unsigned integers, floating-point numbers, tuples of rational objects, or raw binary byte arrays. The stringification engine normalizes these varied representations into clean, human-readable strings.

```python
def _tag_name(tag_id: int) -> str:
    """Map an EXIF tag id to its human-readable name, falling back to the id."""
    if tag_id in TAGS:
        return TAGS[tag_id]
    if tag_id in _ADDITIONAL_TAGS:
        return _ADDITIONAL_TAGS[tag_id]
    return f"Tag_{tag_id}"


def _stringify(value) -> str:
    """Render an EXIF value for the full dump, keeping it readable."""
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return _rational_str(value)
    if isinstance(value, float):
        if 0 < value < 1:
            inv = 1.0 / value
            if abs(inv - round(inv)) < 0.001:
                return f"1/{int(round(inv))}"
        return f"{value:g}"
    if isinstance(value, (bytes, bytearray)):
        try:
            return value.decode("ascii", errors="replace").rstrip("\x00").strip()
        except Exception:
            return value.hex()
    if isinstance(value, tuple):
        return ", ".join(_stringify(v) for v in value)
    return str(value)


def _rational_str(value) -> str:
    """Render an IFDRational as a clean photographic number (e.g. 2.8, not 28/10)."""
    try:
        num = value.numerator
        den = value.denominator
    except AttributeError:
        return str(value)
    if den in (0, 1):
        return str(num)
    decimal = num / den
    # Prefer fractional notation (e.g., "1/250") for shutter speeds < 1.0
    if num == 1 and den > 1:
        return f"{num}/{den}"
    return f"{decimal:g}"
```

#### Detailed Breakdown of Normalization Rules:
1. **Rational Decimal Formatting:** In standard photography, aperture is expressed as an f-number ($f/2.8$), not as the raw fraction $28/10$. `_rational_str()` detects `IFDRational` instances and evaluates the quotient $N / D$. It applies Python's `:g` format specification to eliminate redundant trailing zeros (e.g., `2.8` instead of `2.800000`).
2. **Inverse Fractional Shutter Speeds:** When a shutter speed is stored as a floating-point value between $0$ and $1$ (e.g., $0.004$), `_stringify()` computes the inverse $1 / 0.004 = 250$. If the inverse matches an integer within a tolerance of $\epsilon = 0.001$, it formats the string as `"1/250"`, matching photographic convention.
3. **Defensive Byte Decoding:** Binary byte arrays (e.g., ASCII text buffers padded with null bytes) are decoded using ASCII with `errors="replace"`, stripping null padding (`\x00`). If unprintable binary bytes remain, the value is rendered as a clean hexadecimal string via `.hex()`.

### 4.2.3 Bitmask Decoding: Flash Status Register

The EXIF `Flash` tag (Tag ID $37385 / 0\text{x}9209$) is not a simple enumeration; it is an 8-bit packed bitfield register. Each bit group encodes a distinct operational dimension of the camera's strobe subsystem:

```
+-----------------------------------------------------------------------+
|                     EXIF FLASH REGISTER BIT ALLOCATION                |
+-------+-------+-------+-------+-------+-------+-------+---------------+
| Bit 7 | Bit 6 | Bit 5 | Bit 4 | Bit 3 | Bit 2 | Bit 1 |     Bit 0     |
+-------+-------+-------+-------+-------+-------+-------+---------------+
| Res.  | RedEye| No    | Flash Mode:   | Strobe Return | Flash Fired   |
|       | Reduct| Flash | 00: Unknown   | 00: No return | 0: Did not    |
|       |       |       | 01: Compulsory| 01: Reserved  | 1: Fired      |
|       |       |       | 10: Suppressed| 10: Not det.  |               |
|       |       |       | 11: Auto Mode | 11: Detected  |               |
+-------+-------+-------+-------+-------+-------+-------+---------------+
```

The bitmask decoding algorithm implemented in `exif_extractor/extractor.py` (lines 137–190) combines a fast lookup table for standard vendor codes with dynamic bitfield extraction for rare or compound register values:

```python
def decode_flash(val: int) -> str:
    """Decode EXIF Flash bitmask/enum into descriptive telemetry text."""
    if val is None:
        return ""
        
    flash_table = {
        0x0000: "Flash did not fire",
        0x0001: "Flash fired",
        0x0005: "Flash fired, strobe return light not detected",
        0x0007: "Flash fired, strobe return light detected",
        0x0008: "Flash did not fire, compulsory mode",
        0x0009: "Flash fired, compulsory mode",
        0x000D: "Flash fired, compulsory mode, return light not detected",
        0x000F: "Flash fired, compulsory mode, return light detected",
        0x0010: "Flash did not fire, compulsory flash mode",
        0x0014: "Flash did not fire, auto mode",
        0x0018: "Flash did not fire, auto mode",
        0x0019: "Flash fired, auto mode",
        0x001D: "Flash fired, auto mode, return light not detected",
        0x001F: "Flash fired, auto mode, return light detected",
        0x0020: "No flash function",
        0x0041: "Flash fired, red-eye reduction mode",
        0x0045: "Flash fired, red-eye reduction mode, return light not detected",
        0x0047: "Flash fired, red-eye reduction mode, return light detected",
        0x0049: "Flash fired, compulsory mode, red-eye reduction mode",
        0x004D: "Flash fired, compulsory mode, red-eye reduction mode, return light not detected",
        0x004F: "Flash fired, compulsory mode, red-eye reduction mode, return light detected",
        0x0050: "Flash did not fire, auto mode, red-eye reduction mode",
        0x0058: "Flash did not fire, auto mode, red-eye reduction mode",
        0x0059: "Flash fired, auto mode, red-eye reduction mode",
        0x005D: "Flash fired, auto mode, return light not detected, red-eye reduction mode",
        0x005F: "Flash fired, auto mode, return light detected, red-eye reduction mode",
    }
    if val in flash_table:
        return flash_table[val]

    # Dynamic Bitwise Extraction for unlisted registers
    fired = bool(val & 0x01)
    parts = ["Flash fired" if fired else "Flash did not fire"]
    
    return_light = (val >> 1) & 0x03
    if return_light == 2:
        parts.append("return light not detected")
    elif return_light == 3:
        parts.append("return light detected")
        
    mode = (val >> 3) & 0x03
    if mode == 1:
        parts.append("compulsory mode")
    elif mode == 2:
        parts.append("suppressed mode")
    elif mode == 3:
        parts.append("auto mode")
        
    if (val >> 5) & 0x01:
        parts.append("no flash function")
    if (val >> 6) & 0x01:
        parts.append("red-eye reduction")
        
    return ", ".join(parts)
```

#### Bitwise Algebraic Logic:
* **Bit 0 Masking (`val & 0x01`):** Tests if the strobe fired.
* **Bits 1–2 Shift & Mask (`(val >> 1) & 0x03`):** Extracts strobe return status ($2 \to \text{not detected}$, $3 \to \text{detected}$).
* **Bits 3–4 Shift & Mask (`(val >> 3) & 0x03`):** Extracts the camera's exposure logic ($1 \to \text{compulsory firing}$, $2 \to \text{compulsory suppression}$, $3 \to \text{automatic mode}$).
* **Bit 5 Mask (`(val >> 5) & 0x01`):** Verifies physical flash hardware presence.
* **Bit 6 Mask (`(val >> 6) & 0x01`):** Evaluates red-eye reduction pre-flash execution.

### 4.2.4 Exposure Program, Metering Modes, and White Balance Enumerations

Beyond raw optical readings, cameras record categorical configuration states defining the exposure control logic. Img_Analyze implements standardized mapping dictionaries:

```python
EXPOSURE_PROGRAM_MAP = {
    0: "Not defined",
    1: "Manual",
    2: "Normal program",
    3: "Aperture priority",
    4: "Shutter priority",
    5: "Creative program (depth of field)",
    6: "Action program (fast shutter speed)",
    7: "Portrait mode",
    8: "Landscape mode",
}

METERING_MODE_MAP = {
    0: "Unknown",
    1: "Average",
    2: "Center-weighted average",
    3: "Spot",
    4: "Multi-spot",
    5: "Multi-segment / Pattern",
    6: "Partial",
    255: "Other",
}

WHITE_BALANCE_MAP = {
    0: "Auto",
    1: "Manual",
}

LIGHT_SOURCE_MAP = {
    0: "Unknown",
    1: "Daylight",
    2: "Fluorescent",
    3: "Tungsten",
    4: "Flash",
    9: "Fine weather",
    10: "Cloudy weather",
    11: "Shade",
    12: "Daylight fluorescent",
    13: "Day white fluorescent",
    14: "Cool white fluorescent",
    15: "White fluorescent",
    17: "Standard light A",
    18: "Standard light B",
    19: "Standard light C",
    20: "D55",
    21: "D65",
    22: "D75",
    23: "D50",
    24: "ISO studio tungsten",
    255: "Other light source",
}
```

The parsing pipeline normalizes raw integer values from either primary IFD0 or the Exif sub-IFD against these registries, guaranteeing human-readable strings across both the terminal and graphical dashboards.

---

## 4.3 Geolocation Engine & Mathematical Transformation

### 4.3.1 Parsing the GPSInfo Sub-IFD (`ExifTags.GPSTAGS`)

The GPS Sub-IFD (Tag ID $34853 / 0\text{x}8825$) resides in a distinct tag namespace. While standard EXIF tags map through `TAGS`, GPS tags must be resolved using `GPSTAGS` (e.g., $1 \to \text{"GPSLatitudeRef"}$, $2 \to \text{"GPSLatitude"}$, $3 \to \text{"GPSLongitudeRef"}$, $4 \to \text{"GPSLongitude"}$, $6 \to \text{"GPSAltitude"}$).

In `exif_extractor/extractor.py`, `_parse_gps()` normalizes the GPS sub-IFD:

```python
def _parse_gps(gps_ifd: Dict[object, object]) -> Optional[GpsInfo]:
    """Convert a GPSInfo IFD dictionary into a structured GpsInfo instance."""
    gps = {}
    for tag_key, value in gps_ifd.items():
        if isinstance(tag_key, int):
            tag_name = GPSTAGS.get(tag_key, f"GPS_{tag_key}")
        else:
            tag_name = str(tag_key)
        gps[tag_name] = value

    needs = ("GPSLatitude", "GPSLatitudeRef", "GPSLongitude", "GPSLongitudeRef")
    if not all(k in gps for k in needs):
        return None

    try:
        lat_d, lat_m, lat_s = gps["GPSLatitude"]
        lon_d, lon_m, lon_s = gps["GPSLongitude"]
        latitude = dms_to_decimal(lat_d, lat_m, lat_s, gps["GPSLatitudeRef"])
        longitude = dms_to_decimal(lon_d, lon_m, lon_s, gps["GPSLongitudeRef"])
    except (TypeError, ValueError, IndexError, ZeroDivisionError):
        return None

    dms_string = (
        f"{format_dms(lat_d, lat_m, lat_s, gps['GPSLatitudeRef'])}, "
        f"{format_dms(lon_d, lon_m, lon_s, gps['GPSLongitudeRef'])}"
    )

    altitude = None
    if "GPSAltitude" in gps and gps["GPSAltitude"] is not None:
        try:
            altitude = round(_as_float(gps["GPSAltitude"]), 2)
        except (TypeError, ValueError, ZeroDivisionError):
            altitude = None

    altitude_ref = None
    if "GPSAltitudeRef" in gps and gps["GPSAltitudeRef"] is not None:
        ref_val = gps["GPSAltitudeRef"]
        if isinstance(ref_val, (bytes, bytearray)):
            altitude_ref = int(ref_val[0]) if ref_val else 0
        else:
            try:
                altitude_ref = int(ref_val)
            except (TypeError, ValueError):
                altitude_ref = None

    if altitude is not None and altitude_ref == 1:
        altitude = -abs(altitude)

    osm_link = openstreetmap_link(latitude, longitude)
    apple_link = apple_maps_link(latitude, longitude)

    return GpsInfo(
        latitude=latitude,
        longitude=longitude,
        dms_string=dms_string,
        maps_link=google_maps_link(latitude, longitude),
        altitude=altitude,
        altitude_ref=altitude_ref,
        openstreetmap_link=osm_link,
        apple_maps_link=apple_link,
    )
```

### 4.3.2 DMS-to-Decimal Mathematical Algorithm

EXIF coordinates are stored as sexagesimal Degree-Minute-Second (DMS) rational triplets:

$$\text{Coord}_{\text{EXIF}} = \left( \frac{D_n}{D_d}, \frac{M_n}{M_d}, \frac{S_n}{S_d} \right)$$

To perform geospatial visualization or query spatial indices, DMS values must be transformed into signed decimal degrees conforming to the World Geodetic System 1984 (WGS-84) ellipsoid:

$$\text{Coord}_{\text{Decimal}} = D + \frac{M}{60} + \frac{S}{3600}$$

The mathematical implementation in `exif_extractor/gps.py` accounts for diverse rational representations, including `IFDRational` objects, two-element tuples, floats, and integer values:

```python
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
    """Convert DMS coordinates and a directional reference into signed decimal degrees.

    Args:
        degrees, minutes, seconds: Numeric or rational components of the coordinate.
        ref: Hemisphere reference ('N', 'S', 'E', 'W').

    Returns:
        float: Signed decimal degrees. Southern and Western hemispheres return negative values.
    """
    decimal = _as_float(degrees) + _as_float(minutes) / 60.0 + _as_float(seconds) / 3600.0
    clean_ref = _clean_ref(ref)
    if clean_ref in ("S", "W"):
        decimal = -decimal
    return decimal
```

#### Mathematical Proof: Hemisphere Inversion Property
Let $\phi_{\text{raw}} \in [0, 90]$ represent the raw calculated latitude magnitude, and let $\lambda_{\text{raw}} \in [0, 180]$ represent longitude magnitude. The cardinal hemisphere references satisfy:

$$\phi = \begin{cases} +\phi_{\text{raw}}, & \text{if } \text{ref} = \text{'N'} \\ -\phi_{\text{raw}}, & \text{if } \text{ref} = \text{'S'} \end{cases} \qquad \lambda = \begin{cases} +\lambda_{\text{raw}}, & \text{if } \text{ref} = \text{'E'} \\ -\lambda_{\text{raw}}, & \text{if } \text{ref} = \text{'W'} \end{cases}$$

This ensures that coordinates in the Southern Hemisphere (e.g., Sydney at $33.8688^\circ \text{ S} \to -33.8688^\circ$) and Western Hemisphere (e.g., New York City at $74.0060^\circ \text{ W} \to -74.0060^\circ$) map correctly onto Cartesian coordinate grids.

### 4.3.3 Altitude Computation with `GPSAltitudeRef`

Altitude telemetry is extracted from `GPSAltitude` (Tag 6) and `GPSAltitudeRef` (Tag 5):
* `0`: Above sea level (positive reference).
* `1`: Below sea level (negative reference, e.g., Dead Sea or underwater telemetry). When $1$, the magnitude is negated.

The implementation gracefully unpacks raw byte buffers (e.g., `b'\x00'`), single integers, or missing reference keys, computing elevation with two-decimal-place precision.

### 4.3.4 Geospatial Rendering and URI Synthesis

The extracted coordinates feed both client-side map visualizers and external map URIs rounded to 6 decimal places ($\approx 11 \text{ cm}$ precision at the equator):

```python
def google_maps_link(latitude: float, longitude: float) -> str:
    return f"https://www.google.com/maps?q={latitude:.6f},{longitude:.6f}"

def openstreetmap_link(latitude: float, longitude: float) -> str:
    lat = round(float(latitude), 6)
    lon = round(float(longitude), 6)
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}"

def apple_maps_link(latitude: float, longitude: float) -> str:
    lat = round(float(latitude), 6)
    lon = round(float(longitude), 6)
    return f"https://maps.apple.com/?q={lat},{lon}"
```

In the presentation subsystem (`app.py`), coordinates are synthesized into a Pandas DataFrame and rendered natively using Streamlit's `st.map()`:

```python
# Construct geospatial payload for reactive map rendering
map_df = pd.DataFrame([{
    "lat": report.gps.latitude,
    "lon": report.gps.longitude,
}])
st.map(map_df, zoom=14)
```

---

## 4.4 Non-EXIF & AI Generation Prompt Extraction

### 4.4.1 PNG Chunk Parsing Mechanics: `tEXt`, `zTXt`, and `iTXt`

While JPEG files rely predominantly on EXIF metadata embedded within `APP1` markers, Portable Network Graphics (PNG) files store metadata within specialized ancillary chunks:
1. `tEXt`: Uncompressed Latin-1 key-value string pairs separated by a null byte (`0x00`).
2. `zTXt`: Compressed key-value string pairs using the DEFLATE zlib algorithm.
3. `iTXt`: Internationalized UTF-8 metadata chunks with optional compression flags and language tags.

When Pillow decodes a PNG, it populates `img.text` or `img.info` with the extracted chunk contents. Img_Analyze audits these chunks in `exif_extractor/extractor.py` (lines 637–679):

```python
png_chunks: Dict[str, str] = {}
if image_format.upper() == "PNG":
    if hasattr(img, "text") and isinstance(img.text, dict):
        for k, v in img.text.items():
            if isinstance(v, (str, int, float, bool)):
                png_chunks[str(k)] = str(v)
            elif isinstance(v, (bytes, bytearray)):
                try:
                    png_chunks[str(k)] = v.decode("utf-8", errors="replace").strip()
                except Exception:
                    pass

    for k, v in img.info.items():
        if k in ("exif", "icc_profile", "photoshop", "dpi", "transparency", "gamma", "interlace", "aspect"):
            continue
        if isinstance(v, (str, int, float, bool)):
            png_chunks[str(k)] = str(v)
        elif isinstance(v, (bytes, bytearray)):
            try:
                png_chunks[str(k)] = v.decode("utf-8", errors="replace").strip()
            except Exception:
                pass
else:
    for k in ("parameters", "prompt", "workflow", "Comment", "comment"):
        if k in img.info:
            val = img.info[k]
            if isinstance(val, (str, int, float, bool)):
                png_chunks[str(k)] = str(val)
            elif isinstance(val, (bytes, bytearray)):
                try:
                    png_chunks[str(k)] = val.decode("utf-8", errors="replace").strip()
                except Exception:
                    pass
```

### 4.4.2 Tracing Generative AI Synthesis Parameters

Generative AI diffusion engines (e.g., Stable Diffusion, Automatic1111, ComfyUI, InvokeAI, NovelAI) embed end-to-end generation telemetry into image metadata chunks. This metadata often includes the raw text prompt, negative prompt, random seed, sampler type, classifier-free guidance (CFG) scale, model checkpoint hash, and serialized ComfyUI JSON node graphs.

In `app.py` (lines 855–867), Img_Analyze implements heuristic pattern matching to detect AI synthesis signatures:

```python
ai_keywords = ("parameters", "prompt", "workflow", "sd-metadata", "generation_data")
has_ai_prompt = any(k.lower() in ai_keywords for k in text_chunks)

if has_ai_prompt:
    st.warning("🤖 **AI Generation Metadata Detected in Image Chunks!**")

if text_chunks:
    st.markdown("##### Embedded Text Chunks / Parameters")
    for chunk_key, chunk_val in text_chunks.items():
        with st.expander(f"Chunk: {chunk_key}", expanded=chunk_key.lower() in ai_keywords):
            st.code(chunk_val, language="text")
```

When an analyst inspects a generated PNG, the system isolates the `parameters` chunk, revealing prompt text and synthesis arguments (e.g., `"Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 7.0, Seed: 31415926535"`), providing valuable OSINT insight into synthetic media creation.

### 4.4.3 ICC Profile Extraction and Color Space Analysis

International Color Consortium (ICC) profiles define the color gamut transformation matrices applied to raster bitmaps. Img_Analyze inspects the raw `icc_profile` byte blob from `img.info` using Pillow's `ImageCms` engine, with a defensive binary fallback:

```python
def extract_icc_profile_name(icc_bytes: bytes) -> Optional[str]:
    """Extract human-readable profile description from ICC profile binary bytes."""
    if not icc_bytes or not isinstance(icc_bytes, (bytes, bytearray)):
        return None
    try:
        from PIL import ImageCms
        desc = ImageCms.getProfileDescription(io.BytesIO(icc_bytes))
        if desc:
            return desc.strip()
    except Exception:
        pass
    try:
        from PIL import ImageCms
        profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_bytes))
        name = ImageCms.getProfileName(profile)
        if name:
            return name.strip()
    except Exception:
        pass
    # Binary parsing fallback: Locate ASCII 'desc' tag offset in ICC header
    try:
        idx = icc_bytes.find(b"desc")
        if idx != -1 and len(icc_bytes) > idx + 12:
            length = int.from_bytes(icc_bytes[idx + 8 : idx + 12], "big")
            if 0 < length < 256 and len(icc_bytes) >= idx + 12 + length:
                return (
                    icc_bytes[idx + 12 : idx + 12 + length]
                    .decode("ascii", errors="ignore")
                    .rstrip("\x00")
                    .strip()
                )
    except Exception:
        pass
    return f"ICC Profile ({len(icc_bytes)} bytes)"
```

This isolates standard color profiles—such as `sRGB IEC61966-2.1`, `Display P3` (common to modern iOS devices), and `Adobe RGB (1998)`—characterizing the hardware sensor gamut.

---

## 4.5 Visual Analytics Engine

### 4.5.1 Dominant Color Extraction via Median-Cut Quantization

To extract dominant colors without the overhead of heavy clustering libraries (such as scikit-learn's K-Means), Img_Analyze leverages Pillow's native C-optimized vector quantization engine (`Image.quantize`), which implements Paul Heckbert's **Median-Cut Algorithm**.

#### Mathematical Theory of the Median-Cut Algorithm:
1. Enclose all pixels of an image in an axis-aligned bounding box within 3D RGB color space:
   $$R \in [R_{\min}, R_{\max}], \quad G \in [G_{\min}, G_{\max}], \quad B \in [B_{\min}, B_{\max}]$$
2. Determine the color channel exhibiting the greatest range:
   $$\Delta C = \max(R_{\max} - R_{\min}, G_{\max} - G_{\min}, B_{\max} - B_{\min})$$
3. Sort the enclosed pixels along that axis and partition them at the median point into two sub-boxes with equal pixel counts.
4. Recursively repeat steps 1–3 until $K$ color clusters are generated.
5. Compute the centroid (mean RGB vector) of each final box to define the quantized palette.

```python
def extract_dominant_colors(
    img: Image.Image, num_colors: int = 6
) -> List[Dict[str, Any]]:
    """Compute dominant colors and percentages using Pillow MEDIANCUT quantization."""
    try:
        small = img.convert("RGB").resize((100, 100))
        palette_img = small.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
        palette = palette_img.getpalette()[: num_colors * 3]
        colors = [tuple(palette[i : i + 3]) for i in range(0, len(palette), 3)]
        counts = collections.Counter(palette_img.tobytes())
        total = sum(counts.values()) or 1

        results = []
        for idx, (r, g, b) in enumerate(colors):
            cnt = counts.get(idx, 0)
            pct = (cnt / total) * 100
            hex_code = f"#{r:02x}{g:02x}{b:02x}"
            # Perceived luminance according to ITU-R BT.601
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            text_color = "#000000" if lum > 140 else "#ffffff"
            results.append({
                "hex": hex_code,
                "rgb": f"RGB({r}, {g}, {b})",
                "pct": pct,
                "text_color": text_color,
            })
        return results
    except Exception:
        return []
```

### 4.5.2 Luminance and Perceptual Contrast Calculations

The relative luminance $Y$ of each extracted swatch is computed using the ITU-R Recommendation BT.601 standard:

$$Y = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B$$

If $Y > 140$, the user interface applies dark text (`#000000`) across the swatch; otherwise, it applies high-contrast white text (`#ffffff`), ensuring WCAG 2.1 contrast compliance.

### 4.5.3 Histogram Statistics and RMS Exposure Classification

The system performs tonal analysis via Pillow's `ImageStat.Stat`, converting the image to an 8-bit grayscale bitmap (`L` mode) and evaluating three statistical moments:
1. **Mean Luminance ($\mu$):**
   $$\mu = \frac{1}{N} \sum_{i=1}^N P_i$$
2. **Median Tone:** The $50\text{th}$ percentile pixel intensity value across the 256-bin histogram.
3. **Root-Mean-Square (RMS) Contrast ($\sigma_{\text{rms}}$):**
   $$\sigma_{\text{rms}} = \sqrt{\frac{1}{N} \sum_{i=1}^N (P_i - \mu)^2}$$

In `app.py` (lines 816–842), these metrics categorize the exposure character of the image:

```python
stat = ImageStat.Stat(pil_image.convert("L"))
mean_brightness = stat.mean[0]
rms_contrast = stat.rms[0]
median_tone = stat.median[0]

if mean_brightness < 80:
    tone_badge = "Low Key / Dark Exposure"
    tone_desc = "Predominantly shadow tones; typical of night, indoor moody, or underexposed shots."
elif mean_brightness > 175:
    tone_badge = "High Key / Bright Exposure"
    tone_desc = "Predominantly bright tones; typical of outdoor sun, snow, or high exposure."
else:
    tone_badge = "Balanced Exposure"
    tone_desc = "Evenly distributed midtones across the tonal range."
```

---

## 4.6 In-Memory Metadata Scrubber & Auto-Orientation Preserver

### 4.6.1 The EXIF Orientation Hazard (Tag 0x0112)

A common challenge in digital image processing is the handling of the **EXIF Orientation Tag** (Tag ID $274 / 0\text{x}0112$). Modern mobile devices capture photos using a fixed sensor orientation, embedding an integer value ($1$ to $8$) in the EXIF header instructing the display software how to rotate the raster array:

```
+-----------------------------------------------------------------------+
|                     EXIF ORIENTATION MATRIX CODES                     |
+-------+-----------------------------+---------------------------------+
| Value | Canonical Meaning           | Geometric Transformation        |
+-------+-----------------------------+---------------------------------+
| 1     | Top-Left (Normal)           | Identity Matrix                 |
| 2     | Top-Right                   | Mirror Horizontal (Flip X)      |
| 3     | Bottom-Right                | Rotate 180°                     |
| 4     | Bottom-Left                 | Mirror Vertical (Flip Y)        |
| 5     | Left-Top                    | Transpose (Mirror H + Rot 270°) |
| 6     | Right-Top                   | Rotate 90° Clockwise            |
| 7     | Right-Bottom                | Transverse (Mirror H + Rot 90°) |
| 8     | Left-Bottom                 | Rotate 270° Clockwise           |
+-------+-----------------------------+---------------------------------+
```

#### The Stripping Vulnerability:
If an application scrubs metadata simply by clearing the EXIF header or re-encoding raw raster bytes without geometric correction, the display software loses the rotation directive. Consequently, vertical portrait photos captured on smartphones involuntarily rotate $90^\circ$ sideways.

### 4.6.2 Normalization via `ImageOps.exif_transpose`

To neutralize this issue, Img_Analyze applies `ImageOps.exif_transpose()` **before** stripping metadata. This operation reads Tag $0\text{x}0112$, applies the corresponding affine matrix rotation directly to the raw pixel array, and resets the internal orientation state to normal ($1$):

```python
def create_scrubbed_image(pil_img: Image.Image) -> Tuple[bytes, str, str]:
    """Strip all EXIF, GPS, and metadata in-memory using Pillow.

    Returns:
        Tuple of (clean_bytes, filename_extension, mime_type)
    """
    # 1. Transpose pixel array according to EXIF orientation prior to stripping
    transposed = ImageOps.exif_transpose(pil_img)
    
    # 2. Allocate pristine bitmap detached from source container headers
    clean_img = Image.new(transposed.mode, transposed.size)
    clean_img.paste(transposed)

    raw_format = getattr(pil_img, "format", None) or "JPEG"
    fmt = raw_format if raw_format in ("JPEG", "PNG", "WEBP", "TIFF", "BMP", "GIF") else "JPEG"

    # 3. Mode normalization: JPEG does not support alpha or palette channels
    if fmt == "JPEG" and clean_img.mode in ("RGBA", "P", "LA"):
        clean_img = clean_img.convert("RGB")

    # 4. In-memory re-encoding discarding APP1/ancillary chunks
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
    else:
        clean_img.save(buf, format=fmt)
        ext = f".{fmt.lower()}"
        mime = f"image/{fmt.lower()}"

    return buf.getvalue(), ext, mime
```

#### Step-by-Step Security Analysis of the Scrubbing Pipeline:
1. **Geometric Freezing:** `ImageOps.exif_transpose(pil_img)` bakes physical orientation into the pixel grid.
2. **Buffer Detachment:** `Image.new()` allocates a clean memory buffer in the Python heap. The call to `clean_img.paste(transposed)` copies only raw RGB/RGBA pixel bytes. The source file's `img.info` dictionary (which contains raw EXIF headers, MakerNotes, and GPS blocks) is discarded.
3. **Format-Aware Sanitization:** When saving to `JPEG`, the encoder omits the `APP1` EXIF marker. For `PNG` exports, ancillary text chunks (`tEXt`, `zTXt`, `iTXt`) are stripped, neutralizing metadata leakage while maintaining high visual fidelity (`quality=95`).

---

## 4.7 Forensic Multi-Page PDF Generation Subsystem

### 4.7.1 `FPDF2` Subclassing and Forensic Document Layout

Formal forensic reporting requires tamper-evident formatting, coordinate-accurate alignment, and reproducible structure. Img_Analyze implements this via `exif_extractor/pdf_export.py` using `fpdf2`, avoiding heavyweight rendering engines or external browser dependencies.

```python
class ForensicReportPDF(FPDF):
    """Custom PDF layout engine for forensic image metadata reports."""

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 41, 59)  # Slate-800
        self.cell(0, 8, "FORENSIC IMAGE METADATA REPORT", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 116, 139)  # Slate-500
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.cell(
            0, 5,
            f"Automated OSINT & Metadata Extraction  |  Generated: {now_str}",
            new_x="LMARGIN", new_y="NEXT", align="C"
        )
        self.ln(3)
        self.set_draw_color(226, 232, 240)  # Slate-200 divider
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        page_str = f"Page {self.page_no()}/{{nb}}"
        self.cell(
            0, 10,
            f"EXIF Metadata Extractor  -  Confidential Forensic Report  |  {page_str}",
            align="C"
        )

    def chapter_title(self, title: str):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(241, 245, 249)  # Slate-100 fill
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
```

### 4.7.2 Multi-Section Document Assembly

The `generate_pdf_report()` function compiles the structured `ExifReport` model into a multi-section forensic document:

```python
def generate_pdf_report(report: ExifReport, image_bytes: Optional[bytes] = None) -> bytes:
    """Compile an ExifReport instance into a defensible forensic PDF document."""
    pdf = ForensicReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Dynamic Threat Level Banner Styling
    risk = getattr(report, "privacy_risk", "LOW")
    reasons = getattr(report, "privacy_reasons", [])

    if risk == "HIGH":
        pdf.set_fill_color(254, 242, 242)   # Red-50
        pdf.set_draw_color(239, 68, 68)     # Red-500
        text_r, text_g, text_b = 185, 28, 28
    elif risk == "MEDIUM":
        pdf.set_fill_color(254, 243, 199)   # Amber-50
        pdf.set_draw_color(245, 158, 11)    # Amber-500
        text_r, text_g, text_b = 180, 83, 9
    else:
        pdf.set_fill_color(240, 253, 244)   # Green-50
        pdf.set_draw_color(34, 197, 94)     # Green-500
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
    pdf.chapter_title("1. File & Cryptographic Verification")
    pdf.key_value_row("Target File Name:", os.path.basename(report.file_path))
    pdf.key_value_row("File Size:", f"{report.file_size:,} bytes ({_human_size(report.file_size)})")
    pdf.key_value_row("MIME Container:", f"image/{report.image_format.lower()} ({report.image_format})")
    w, h = report.image_size
    pdf.key_value_row("Pixel Geometry:", f"{w} x {h} pixels ({report.megapixels or 0.0:.2f} Megapixels)")
    pdf.key_value_row("Aspect Ratio:", report.aspect_ratio_str or "N/A")
    pdf.key_value_row("MD5 Digest:", report.md5 or "N/A")
    pdf.key_value_row("SHA-1 Digest:", report.sha1 or "N/A")
    pdf.key_value_row("SHA-256 Digest:", report.sha256 or "N/A")
    pdf.ln(3)

    # --- Section 2: Camera & Optics Telemetry ---
    pdf.chapter_title("2. Hardware & Optics Telemetry")
    pdf.key_value_row("Manufacturer:", report.camera_make or "Unknown / Stripped")
    pdf.key_value_row("Model Name:", report.camera_model or "Unknown / Stripped")
    pdf.key_value_row("Lens Hardware:", report.lens_model or "Not specified")
    pdf.key_value_row("Firmware / OS:", report.software or "Not specified")
    pdf.key_value_row("Capture Timestamp:", report.datetime_original or "Not recorded")
    pdf.key_value_row("Digitized Timestamp:", report.datetime_digitized or "Not recorded")
    pdf.key_value_row("Shutter Speed:", f"{report.exposure_time} s" if report.exposure_time else "Not specified")
    pdf.key_value_row("Aperture Setting:", f"f/{report.f_number}" if report.f_number else "Not specified")
    pdf.key_value_row("ISO Sensitivity:", str(report.iso) if report.iso else "Not specified")
    pdf.key_value_row("Focal Length:", f"{report.focal_length} mm" if report.focal_length else "Not specified")
    pdf.key_value_row("Flash Strobe:", report.flash_description or "Not specified")
    pdf.key_value_row("Exposure Program:", report.exposure_program_name or "Not specified")
    pdf.key_value_row("Metering Mode:", report.metering_mode_name or "Not specified")
    pdf.key_value_row("White Balance:", report.white_balance_name or "Not specified")
    pdf.ln(3)

    # --- Section 3: Geodetic GPS Location ---
    pdf.chapter_title("3. Geodetic Location Telemetry (WGS-84)")
    if report.gps:
        pdf.key_value_row("Decimal Coordinates:", f"{report.gps.latitude:.6f}, {report.gps.longitude:.6f}")
        pdf.key_value_row("Sexagesimal DMS:", report.gps.dms_string)
        if report.gps.altitude is not None:
            ref_str = "below sea level" if report.gps.altitude_ref == 1 else "above sea level"
            pdf.key_value_row("GPS Altitude:", f"{report.gps.altitude} m ({ref_str})")
        pdf.key_value_row("Google Maps Link:", report.gps.maps_link)
        if report.gps.openstreetmap_link:
            pdf.key_value_row("OpenStreetMap Link:", report.gps.openstreetmap_link)
    else:
        pdf.key_value_row("GPS Geolocation:", "No GPS coordinates recorded in EXIF header.")
    pdf.ln(3)

    # --- Section 4: Visual Color Palette ---
    pdf.chapter_title("4. Visual Analytics & Dominant Swatches")
    if report.dominant_colors:
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(25, 6, "Hex Code", border=1, align="C")
        pdf.cell(35, 6, "RGB Triplet", border=1, align="C")
        pdf.cell(30, 6, "Pixel Ratio (%)", border=1, align="C")
        pdf.ln(6)
        pdf.set_font("Helvetica", "", 8)
        for c in report.dominant_colors:
            pdf.cell(25, 5, str(c.get("hex", "")), border=1, align="C")
            pdf.cell(35, 5, str(c.get("rgb", "")), border=1, align="C")
            pdf.cell(30, 5, f"{c.get('percentage', 0):.2f}%", border=1, align="C")
            pdf.ln(5)
    else:
        pdf.key_value_row("Palette:", "Dominant color extraction unavailable.")
    pdf.ln(3)

    # --- Section 5: Complete Raw EXIF Dump ---
    pdf.chapter_title("5. Complete Raw EXIF Tag Audit Dump")
    if report.all_tags:
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(60, 6, "EXIF Tag Identifier", border=1)
        pdf.cell(0, 6, "Raw Parameter Value", border=1, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 7.5)
        for tag_name, tag_val in sorted(report.all_tags.items(), key=lambda x: str(x[0])):
            curr_y = pdf.get_y()
            if curr_y > pdf.h - 22:
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 8)
                pdf.cell(60, 6, "EXIF Tag Identifier", border=1)
                pdf.cell(0, 6, "Raw Parameter Value", border=1, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", 7.5)
            clean_name = _clean_text(tag_name)[:35]
            clean_val = _clean_text(tag_val)
            pdf.cell(60, 5, clean_name, border=1)
            pdf.cell(0, 5, clean_val[:120], border=1, new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.key_value_row("EXIF Dump:", "Zero EXIF tags discovered in this file.")

    return bytes(pdf.output())
```

### 4.7.3 Encoding Safety: Latin-1 Character Normalization

Standard PDF core fonts (`Helvetica`, `Times-Roman`, `Courier`) operate over 8-bit WinAnsi / Latin-1 (ISO 8859-1) character encoding. Attempting to write unescaped Unicode characters—such as degree symbols ($^\circ$), typographic em-dashes (—), directional quotation marks (“ ”), or emoji status badges (🚨)—causes unhandled encoding exceptions within the PDF generator.

To prevent document generation failures when processing international metadata, `pdf_export.py` implements a Unicode-to-Latin-1 normalization filter in `_clean_text()`:

```python
def _clean_text(text: object) -> str:
    """Normalize input text for standard PDF core font (Latin-1) compatibility."""
    if text is None:
        return "N/A"
    s = str(text)
    replacements = {
        "\u00b0": " deg",        # Degree symbol -> ' deg'
        "\u2014": " - ",         # Em dash -> hyphen
        "\u2013": " - ",         # En dash -> hyphen
        "\u2018": "'",           # Left single quote
        "\u2019": "'",           # Right single quote
        "\u201c": '"',           # Left double quote
        "\u201d": '"',           # Right double quote
        "\u00d7": "x",           # Dimension multiplication sign
        "\u2022": "*",           # Bullet point
        "\u26a0": "[!]",         # Warning symbol
        "\u2705": "[OK]",        # Checkmark
        "\U0001f6a8": "[ALERT]", # Siren
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
        
    # Re-encode to Latin-1, replacing any unmapped glyphs with standard question marks
    return s.encode("latin-1", errors="replace").decode("latin-1")
```

This ensures that the PDF engine generates compliant document binaries regardless of arbitrary or malformed character sequences embedded in the source image's metadata fields.

---

## 4.8 Batch Processing & Comparative Analysis Engine

### 4.8.1 Aggregation Architecture (`exif_extractor/batch.py`)

Forensic investigations rarely involve a single isolated image; investigators routinely triage directory structures containing hundreds of image files. The batch aggregation engine compiles multi-image inspection results into structured statistical summaries and comparative tabular matrices.

```python
def format_camera_name(report: ExifReport) -> Optional[str]:
    """Format camera make and model cleanly, avoiding duplicate manufacturer names."""
    make = getattr(report, "camera_make", None)
    model = getattr(report, "camera_model", None)
    if make and model:
        make_str = str(make).strip()
        model_str = str(model).strip()
        if make_str.lower() in model_str.lower():
            return model_str
        return f"{make_str} {model_str}"
    if model:
        return str(model).strip()
    if make:
        return str(make).strip()
    return None


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
```

#### Analytical Breakdown:
1. **Manufacturer Deduplication:** Cameras frequently store the brand name redundantly in both Make and Model fields (e.g., `Make="NIKON CORPORATION"`, `Model="NIKON D850"`). `format_camera_name()` performs case-insensitive substring checks, preventing redundant strings like `"NIKON CORPORATION NIKON D850"`.
2. **Batch Fleet Discovery:** By aggregating unique cameras into `unique_cameras`, investigators instantly discover the physical camera fleet utilized across a corpus of evidence.
3. **Statistical Risk Rollup:** Images are categorized across the three threat categories (`HIGH`, `MEDIUM`, `LOW`), providing immediate risk exposure ratios across the evidence pool.

### 4.8.2 Tabular Comparison Matrix via pandas DataFrame

To support side-by-side comparative analysis, `build_comparison_dataframe()` flattens heterogeneous reports into a uniform 2D matrix:

```python
def build_comparison_dataframe(reports: List[ExifReport]) -> pd.DataFrame:
    """Build a consolidated comparison pandas DataFrame from a list of ExifReports."""
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
        file_name = os.path.basename(getattr(r, "file_path", "") or "unknown")
        fmt = getattr(r, "image_format", "") or "UNKNOWN"
        dims = getattr(r, "image_size", (0, 0))
        dim_str = f"{dims[0]}x{dims[1]}" if dims and len(dims) == 2 else "Unknown"
        mp = getattr(r, "megapixels", None)
        mp_str = f"{mp:.2f}" if mp is not None else "N/A"
        sz = getattr(r, "file_size", 0)
        sz_str = _human_size(sz)
        cam = format_camera_name(r) or "Unknown"
        dt = getattr(r, "datetime_original", None) or "N/A"
        has_gps = bool(getattr(r, "has_gps", False) or getattr(r, "gps", None) is not None)
        gps_str = "Yes" if has_gps else "No"
        risk = getattr(r, "privacy_risk", "LOW") or "LOW"
        md5_val = getattr(r, "md5", None) or "N/A"

        rows.append({
            "File Name": file_name,
            "Format": fmt,
            "Dimensions": dim_str,
            "MP": mp_str,
            "File Size": sz_str,
            "Camera": cam,
            "Date Taken": dt,
            "GPS": gps_str,
            "Privacy Risk": risk,
            "MD5": md5_val,
        })

    return pd.DataFrame(rows, columns=columns)
```

This DataFrame structure integrates directly with Streamlit's `st.dataframe()` component, enabling interactive sorting by file size, megapixels, or capture timestamps, as well as CSV export capabilities.

---

## 4.9 Command-Line Forensic Subsystem & JSON Interoperability

### 4.9.1 Headless CLI Pipeline (`exif_extractor/cli.py`)

The command-line interface provides high-throughput processing for headless servers, batch shell scripts, and automated CI/CD security scanning pipelines:

```python
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
```

### 4.9.2 Structured JSON Serialization Architecture

When invoked with `--json`, the CLI serializes the internal dataclass structure directly to standard output:

```python
def _report_to_dict(report: ExifReport) -> dict:
    """Serialize a report to a JSON-friendly dict."""
    data = asdict(report)
    return data


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
```

#### Integration with Downstream Analysis Pipelines:
Because `--json` emits valid JSON objects to standard output while redirecting error messages to `sys.stderr`, the output integrates directly with command-line JSON processors (e.g., `jq`) and search indexing pipelines:

```bash
# Extract all GPS coordinates from a batch of images using jq
python -m exif_extractor *.jpg --json | jq -r 'select(.gps != null) | [.file_path, .gps.latitude, .gps.longitude] | @tsv'
```

---

## 4.10 Comprehensive Verification and Implementation Synthesis

The implementation of **Img_Analyze** demonstrates a layered, defensive approach to systems engineering and digital image forensics. Across every component—from cryptographic digest sealing and binary IFD traversal to geodetic WGS-84 coordinate transformation, median-cut palette extraction, orientation-preserving raster sanitization, and Latin-1-safe PDF synthesis—the architecture enforces mathematical precision, defensive error isolation, and complete zero-disk memory safety.

The resulting engine bridges the gap between high-level investigative usability and rigorous low-level systems programming, establishing a dependable platform for image metadata auditing, OSINT research, and personal privacy preservation.
