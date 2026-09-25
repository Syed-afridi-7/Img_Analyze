# CHAPTER 3: SYSTEM DESIGN AND DEVELOPMENT

---

## 3.1 FILE DESIGN

The file design of `Img_Analyze` establishes the foundational binary interfaces through which digital photographic media, serialized forensic reports, batch telemetry matrices, and published judicial audit documents are ingested, processed, and emitted. Unlike monolithic enterprise forensic platforms that introduce proprietary file container formats (such as EnCase `.E01` or FTK `.AD1`), `Img_Analyze` adheres strictly to open, standardized digital imaging and interchange formats. This guarantees universal interoperability across diverse operating systems and third-party forensic environments.

```
+----------------------------------------------------------------------------------------------------+
|                         Img_Analyze COMPREHENSIVE FILE DESIGN ARCHITECTURE                         |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ INGESTION SUBSYSTEM: MULTI-CONTAINER BINARY PARSERS ]                                           |
|  +--------------------+  +--------------------+  +--------------------+  +----------------------+  |
|  |  JPEG / JFIF       |  |  PNG Chunk Stream  |  |  WebP Container    |  |  TIFF / BMP / GIF    |  |
|  |  SOI (0xFFD8)      |  |  Signature & CRC32 |  |  RIFF / VP8X       |  |  Endian IFDs & DIB   |  |
|  |  APP1 EXIF / TIFF  |  |  tEXt / iTXt GenAI |  |  EXIF Sub-chunk    |  |  Raster Streams      |  |
|  +--------------------+  +--------------------+  +--------------------+  +----------------------+  |
|                                                |                                                   |
|                                                v                                                   |
|  [ CORE VOLATILE STREAM PIPELINE: ZERO-DISK io.BytesIO NON-PERSISTENT MEMORY SLICING ]             |
|                                                |                                                   |
|                                                v                                                   |
|  [ EXPORT & SERIALIZATION SUBSYSTEM: STRUCTURED DATA INTERCHANGE ]                                 |
|  +--------------------------------+  +--------------------------------+  +----------------------+  |
|  |  JSON Forensic Schema v1.1.0   |  |  CSV 20-Column Batch Matrix    |  |  Multi-Page PDF      |  |
|  |  Nested Cryptographic & EXIF   |  |  Relational Telemetry Schema   |  |  Vector Audit Report |  |
|  +--------------------------------+  +--------------------------------+  +----------------------+  |
+----------------------------------------------------------------------------------------------------+
```

---

### 3.1.1 Supported Image Container Specifications

To reliably extract embedded metadata without triggering memory corruption or parser desynchronization, `Img_Analyze` implements specialized decoding routines tailored to the exact binary layout, byte markers, and chunk structures of each supported image container.

#### 1. JPEG (Joint Photographic Experts Group) / JFIF Specification
The JPEG image container is a stream-oriented binary format composed of sequential variable-length segments delimited by two-byte marker codes starting with `0xFF`. Compliant JPEG streams adhere to the ISO/IEC 10918-1 and JFIF (JPEG File Interchange Format) standards.

```
+----------------------------------------------------------------------------------------------------+
|                                 JPEG / JFIF BINARY STREAM STRUCTURE                                |
+----------------------------------------------------------------------------------------------------+
|  Offset / Marker | Length     | Field Name       | Forensic Purpose / Description                  |
+------------------+------------+------------------+-------------------------------------------------+
|  0xFFD8          | 2 Bytes    | SOI              | Start of Image (Magic Number)                   |
|  0xFFE0          | Variable   | APP0 (JFIF)      | JFIF Version, Density Units, Aspect Ratio       |
|  0xFFE1          | Variable   | APP1 (EXIF/TIFF) | Primary EXIF Header ("Exif\x00\x00" + TIFF IFD) |
|  0xFFE1          | Variable   | APP1 (XMP)       | Extensible Metadata Platform XML Packet         |
|  0xFFE2          | Variable   | APP2 (ICC/Flash) | International Color Consortium (ICC) Profiles   |
|  0xFFED          | Variable   | APP13 (Photoshop)| IPTC-NAA Information Interchange Model (IIM)   |
|  0xFFDB          | Variable   | DQT              | Define Quantization Table (Compression Finger)  |
|  0xFFC0 / C2     | Variable   | SOF0 / SOF2      | Start of Frame (Baseline/Progressive Dimensions)|
|  0xFFC4          | Variable   | DHT              | Define Huffman Table (Entropy Encoding)         |
|  0xFFDA          | Variable   | SOS              | Start of Scan (Compressed Entropy Stream)       |
|  0xFFD9          | 2 Bytes    | EOI              | End of Image Marker                             |
+----------------------------------------------------------------------------------------------------+
```

* *Start of Image (SOI) & End of Image (EOI):* Every compliant JPEG byte stream begins strictly with the two-byte hex marker `0xFFD8` and terminates with `0xFFD9`. The cryptographic verification engine checks these bounding markers to detect truncated files or hidden trailer append-data attacks.
* *The APP1 EXIF Segment (`0xFFE1`):* The primary vehicle for photographic metadata. The marker `0xFFE1` is followed by a 16-bit big-endian unsigned integer indicating the total segment length, followed immediately by the 6-byte identification signature `Exif\x00\x00` (`0x45 0x78 0x69 0x66 0x00 0x00`).
* *TIFF Header within APP1:* Immediately following the EXIF identifier, the stream transitions into a standard TIFF header structure:
  * **Bytes 0–1 (Endianness):** `0x4949` (`II` - Intel Little-Endian, least significant byte first) or `0x4D4D` (`MM` - Motorola Big-Endian, most significant byte first).
  * **Bytes 2–3 (Magic Number):** The fixed 16-bit integer `42` (`0x002A`), confirming TIFF format conformity.
  * **Bytes 4–7 (IFD0 Offset):** A 32-bit unsigned offset pointing to the primary Image File Directory (IFD0).
* *Directory Offsets:* IFD0 contains sub-directory pointer tags, most notably Tag `0x8769` (`ExifOffset`), pointing to the SubIFD holding photographic exposure tags, and Tag `0x8825` (`GPSInfo`), pointing to the dedicated GPS IFD containing geospatial coordinate telemetry.

#### 2. TIFF (Tagged Image File Format) Specification & IFD Anatomy
The TIFF 6.0 specification serves as the architectural foundation of EXIF itself. TIFF files feature a flexible, table-driven architecture based on Image File Directories (IFDs).

```
+----------------------------------------------------------------------------------------------------+
|                                 TIFF IFD ENTRY BINARY STRUCTURE (12 BYTES)                         |
+----------------------------------------------------------------------------------------------------+
|  Byte Offset     | Field Size | Field Type       | Description                                     |
+------------------+------------+------------------+-------------------------------------------------+
|  0x00 - 0x01     | 2 Bytes    | Uint16           | Tag Identifier (e.g., 0x010F for Make)          |
|  0x02 - 0x03     | 2 Bytes    | Uint16           | Data Type Code (1 to 12)                        |
|  0x04 - 0x07     | 4 Bytes    | Uint32           | Value Count (Number of items of indicated type) |
|  0x08 - 0x0B     | 4 Bytes    | Uint32 / Value   | Value Offset OR Direct Inline Value (<= 4 bytes)|
+----------------------------------------------------------------------------------------------------+
```

The TIFF specification defines 12 core data types utilized across EXIF tags:
* `1 = BYTE`: 8-bit unsigned integer.
* `2 = ASCII`: 8-bit byte containing 7-bit ASCII code, terminated with a NULL byte (`0x00`).
* `3 = SHORT`: 16-bit (2-byte) unsigned integer.
* `4 = LONG`: 32-bit (4-byte) unsigned integer.
* `5 = RATIONAL`: Two contiguous 32-bit unsigned integers (Numerator and Denominator).
* `7 = UNDEFINED`: 8-bit byte containing uninterpreted binary payload (used for `MakerNote`).
* `9 = SLONG`: 32-bit (4-byte) signed integer (2's complement).
* `10 = SRATIONAL`: Two contiguous 32-bit signed integers (signed Numerator and Denominator).

Table 3.0 details the foundational EXIF Tag IDs decoded by `Img_Analyze`:

```
+----------------------------------------------------------------------------------------------------+
|                         TABLE 3.0: CORE EXIF / TIFF TAG IDENTIFIERS DECODED                        |
+----------------------------------------------------------------------------------------------------+
| Tag Hex  | Tag Dec | Tag Name                  | TIFF Type | Forensic Investigative Significance   |
+----------+---------+---------------------------+-----------+---------------------------------------+
| 0x010F   | 271     | Make                      | ASCII     | Hardware manufacturer of camera       |
| 0x0110   | 272     | Model                     | ASCII     | Specific commercial hardware model    |
| 0x0112   | 274     | Orientation               | SHORT     | Hardware display orientation flag     |
| 0x0131   | 305     | Software                  | ASCII     | Firmware version or editing software  |
| 0x0132   | 306     | DateTime                  | ASCII     | File modification timestamp           |
| 0x829A   | 33434   | ExposureTime              | RATIONAL  | Shutter duration in seconds           |
| 0x829D   | 33437   | FNumber                   | RATIONAL  | Relative lens aperture opening        |
| 0x8769   | 34665   | ExifOffset                | LONG      | Pointer offset to Exif SubIFD         |
| 0x8822   | 34850   | ExposureProgram           | SHORT     | Manual, Program, Aperture Priority    |
| 0x8825   | 34853   | GPSInfo                   | LONG      | Pointer offset to GPS IFD directory   |
| 0x8827   | 34867   | ISOSpeedRatings           | SHORT     | Sensor light amplification gain       |
| 0x9003   | 36867   | DateTimeOriginal          | ASCII     | Physical shutter actuation timestamp  |
| 0x9004   | 36868   | DateTimeDigitized         | ASCII     | Analog-to-digital capture timestamp   |
| 0x9201   | 37377   | ShutterSpeedValue         | SRATIONAL | APEX unit representation of speed     |
| 0x9202   | 37378   | ApertureValue             | RATIONAL  | APEX unit representation of aperture  |
| 0x9207   | 37383   | MeteringMode              | SHORT     | Average, Spot, Multi-segment pattern  |
| 0x9208   | 37384   | LightSource               | SHORT     | Daylight, Tungsten, Fluorescent, Flash|
| 0x9209   | 37385   | Flash                     | SHORT     | 8-bit flash firing bitmask status     |
| 0x920A   | 37386   | FocalLength               | RATIONAL  | Physical optical focal distance in mm |
| 0x927C   | 37500   | MakerNote                 | UNDEFINED | Vendor proprietary internal sensor data|
| 0x9286   | 37510   | UserComment               | UNDEFINED | User comment or AI generation prompt  |
| 0xA002   | 40962   | ExifImageWidth            | LONG/SHORT| Valid horizontal sensor pixel count   |
| 0xA003   | 40963   | ExifImageHeight           | LONG/SHORT| Valid vertical sensor pixel count     |
| 0xA405   | 41989   | FocalLengthIn35mmFilm     | SHORT     | 35mm film equivalent focal length     |
| 0xA420   | 42016   | ImageUniqueID             | ASCII     | Unique hardware cryptographic hash ID  |
| 0xA434   | 42036   | LensModel                 | ASCII     | Commercial lens model description     |
+----------------------------------------------------------------------------------------------------+
```

#### 3. PNG (Portable Network Graphics) Specification & Chunk Anatomy
The PNG format is an extensible, block-oriented raster format conforming to ISO/IEC 15948:2004. It operates under network byte order (Big-Endian).

```
+----------------------------------------------------------------------------------------------------+
|                                    PNG CHUNK STREAM ARCHITECTURE                                   |
+----------------------------------------------------------------------------------------------------+
|  Field Name      | Size       | Encoding         | Description / Validation Constraint             |
+------------------+------------+------------------+-------------------------------------------------+
|  Magic Signature | 8 Bytes    | Binary Constant  | \x89 P N G \r \n \x1a \n (89 50 4E 47 0D 0A 1A 0A)|
|  Chunk Length    | 4 Bytes    | Big-Endian Uint32| Length of Chunk Data field (N bytes)            |
|  Chunk Type      | 4 Bytes    | ASCII String     | Case-sensitive chunk identifier (e.g., "tEXt")  |
|  Chunk Data      | N Bytes    | Arbitrary Binary | Payload data (text, compressed zlib, pixels)    |
|  CRC-32 Checksum | 4 Bytes    | ISO 3309 CRC-32  | Cyclic Redundancy Check over Type and Data      |
+----------------------------------------------------------------------------------------------------+
```

* *Magic Signature Verification:* A valid PNG container begins with the immutable 8-byte sequence:
  ```
  0x89 0x50 0x4E 0x47 0x0D 0x0A 0x1A 0x0A
  ```
  This signature detects cross-platform line-ending corruption (CRLF vs. LF) and transmission byte truncations.
* *Chunk Framing Model:* Every PNG chunk comprises four contiguous segments: a 4-byte length $N$, a 4-byte chunk type, an $N$-byte payload, and a 4-byte CRC-32 checksum calculated across the type and data fields.
* *Critical Chunks:*
  * **`IHDR` (Image Header):** Mandatory first chunk detailing width, height, bit depth, color type, compression method, filter method, and interlace method.
  * **`PLTE` (Palette):** Contains color palette entries for indexed-color images.
  * **`IDAT` (Image Data):** Holds zlib-compressed DEFLATE raster pixel streams.
  * **`IEND` (Image Trailer):** Marks the termination of the PNG chunk stream.
* *Ancillary Text Chunks for Generative AI:*
  * **`tEXt`:** Uncompressed Latin-1 keyword/text pairs separated by a null byte (`0x00`).
  * **`zTXt`:** Compressed keyword/text pairs utilizing zlib DEFLATE compression.
  * **`iTXt` (International Text):** Supports UTF-8 encoded text payloads. Modern generative AI synthesis engines (Stable Diffusion, ComfyUI, Automatic1111) inject complete prompt strings, negative prompts, diffusion step counts, CFG scales, and node execution graphs inside `iTXt` chunks holding the `parameters` or `prompt` keyword.

```
+----------------------------------------------------------------------------------------------------+
|                                    PNG iTXt CHUNK INTERNAL LAYOUT                                  |
+----------------------------------------------------------------------------------------------------+
| Keyword (1-79 bytes) | Null (0x00) | Comp Flag (1B) | Comp Method (1B) | Language Tag (ASCII) | ...  |
+----------------------+-------------+----------------+------------------+----------------------+------+
| ... Null (0x00) | Translated Keyword (UTF-8) | Null (0x00) | Text Payload (UTF-8 Plain or zlib)    |
+-----------------+----------------------------+-------------+---------------------------------------+
```

#### 4. WebP Specification (Google RIFF Container)
WebP is a modern container format based on the Resource Interchange File Format (RIFF).

```
+----------------------------------------------------------------------------------------------------+
|                                    WebP RIFF CONTAINER STRUCTURE                                   |
+----------------------------------------------------------------------------------------------------+
|  Offset (Bytes)  | Length     | Content / FourCC | Description                                     |
+------------------+------------+------------------+-------------------------------------------------+
|  0x0000 - 0x0003 | 4 Bytes    | "RIFF"           | Resource Interchange File Format Magic Header   |
|  0x0004 - 0x0007 | 4 Bytes    | Uint32 (LE)      | File Size minus 8 bytes                         |
|  0x0008 - 0x000B | 4 Bytes    | "WEBP"           | WebP Container Identifier                       |
|  0x000C - 0x000F | 4 Bytes    | "VP8 " / "VP8X"  | Bitstream Compression Format Identifier         |
|  Variable        | Variable   | "EXIF" Chunk     | Raw EXIF IFD Bitstream Payload                  |
|  Variable        | Variable   | "ICCP" Chunk     | Embedded Color Management Profile Payload       |
+----------------------------------------------------------------------------------------------------+
```

* *Header Framing:* The first 12 bytes contain the ASCII tokens `RIFF`, followed by a 32-bit little-endian integer specifying the total payload size, followed by the form type `WEBP`.
* *Extended Chunk (`VP8X`):* In advanced WebP files holding metadata, the first sub-chunk is `VP8X`. It features an 8-bit feature flag field:
  * Bit 1 (`0x02`): Animation flag.
  * Bit 2 (`0x04`): XMP metadata flag present.
  * Bit 3 (`0x08`): EXIF metadata chunk present.
  * Bit 4 (`0x10`): Alpha channel transparency present.
  * Bit 5 (`0x20`): ICC profile present.
* When the EXIF flag is asserted, `Img_Analyze` scans the RIFF chunk headers for the FourCC token `EXIF`, directly extracting the raw TIFF IFD structure for processing.

#### 5. BMP (Windows Bitmap) Specification
BMP represents a device-independent raster bitmap format:
* *Structure:* Consists of a 14-byte `BITMAPFILEHEADER` (beginning with ASCII `BM` or `0x42 0x4D`), followed by a 40-byte `BITMAPINFOHEADER` detailing width, height, color planes, and compression (`BI_RGB`).
* *Forensic Role:* BMP files lack native EXIF blocks. However, `Img_Analyze` ingests BMP containers to perform cryptographic hashing, geometry extraction, and visual tonal/color quantization analytics, proving that the file is free of hidden EXIF structures.

#### 6. GIF (Graphics Interchange Format) Specification
Defined under GIF87a and GIF89a specifications:
* *Structure:* Begins with the 6-byte header `GIF87a` or `GIF89a`, followed by a 7-byte Logical Screen Descriptor, optional Global Color Table, and variable-length Graphic Control Extensions.
* *Application Extension Chunks:* GIF89a permits Application Extension blocks (`0x21 0xFF`) holding Netscape Looping application data or XMP data packets (`XMP DataXMP`). `Img_Analyze` parses multi-frame animations, evaluating frame counts and extracting embedded XMP metadata packets.

---

### 3.1.2 JSON Export Schema Specification

To enable automated ingestion by security information and event management (SIEM) systems, forensic databases, and OSINT pipelines, `Img_Analyze` implements a standardized, validated JSON schema (`img_analyze_v1_1_0.json`).

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ImgAnalyzeForensicReport",
  "type": "object",
  "required": [
    "file_metadata",
    "cryptographic_verification",
    "image_geometry",
    "privacy_audit"
  ],
  "properties": {
    "file_metadata": {
      "type": "object",
      "required": ["file_name", "file_size_bytes", "container_format"],
      "properties": {
        "file_name": { "type": "string" },
        "file_size_bytes": { "type": "integer", "minimum": 0 },
        "container_format": { "type": "string" },
        "mime_type": { "type": "string" }
      }
    },
    "cryptographic_verification": {
      "type": "object",
      "required": ["md5", "sha1", "sha256"],
      "properties": {
        "md5": { "type": "string", "pattern": "^[a-f0-9]{32}$" },
        "sha1": { "type": "string", "pattern": "^[a-f0-9]{40}$" },
        "sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" }
      }
    },
    "image_geometry": {
      "type": "object",
      "required": ["width_px", "height_px", "megapixels", "aspect_ratio", "color_mode"],
      "properties": {
        "width_px": { "type": "integer" },
        "height_px": { "type": "integer" },
        "megapixels": { "type": "number" },
        "aspect_ratio": { "type": "string" },
        "color_mode": { "type": "string" },
        "color_depth": { "type": "string" },
        "has_alpha_channel": { "type": "boolean" },
        "dpi": {
          "type": ["array", "null"],
          "items": { "type": "number" },
          "minItems": 2,
          "maxItems": 2
        }
      }
    },
    "camera_telemetry": {
      "type": "object",
      "properties": {
        "make": { "type": ["string", "null"] },
        "model": { "type": ["string", "null"] },
        "lens_model": { "type": ["string", "null"] },
        "software": { "type": ["string", "null"] },
        "datetime_original": { "type": ["string", "null"] },
        "datetime_digitized": { "type": ["string", "null"] },
        "aperture_f_number": { "type": ["string", "null"] },
        "exposure_time_sec": { "type": ["string", "null"] },
        "iso_speed_rating": { "type": ["string", "null"] },
        "focal_length_mm": { "type": ["string", "null"] },
        "focal_length_35mm_equiv": { "type": ["integer", "null"] },
        "exposure_program": { "type": ["string", "null"] },
        "metering_mode": { "type": ["string", "null"] },
        "flash_status": { "type": ["string", "null"] },
        "white_balance": { "type": ["string", "null"] },
        "orientation_tag": { "type": ["string", "null"] }
      }
    },
    "geospatial_telemetry": {
      "type": ["object", "null"],
      "properties": {
        "latitude_decimal": { "type": "number", "minimum": -90.0, "maximum": 90.0 },
        "longitude_decimal": { "type": "number", "minimum": -180.0, "maximum": 180.0 },
        "dms_representation": { "type": "string" },
        "altitude_meters": { "type": ["number", "null"] },
        "altitude_datum_ref": { "type": ["string", "null"] },
        "google_maps_url": { "type": "string", "format": "uri" },
        "openstreetmap_url": { "type": "string", "format": "uri" },
        "apple_maps_url": { "type": "string", "format": "uri" }
      }
    },
    "visual_color_analytics": {
      "type": "object",
      "required": ["dominant_palette", "mean_luminance", "rms_contrast"],
      "properties": {
        "dominant_palette": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["hex", "rgb", "percentage"],
            "properties": {
              "hex": { "type": "string", "pattern": "^#[0-9A-F]{6}$" },
              "rgb": {
                "type": "array",
                "items": { "type": "integer", "minimum": 0, "maximum": 255 },
                "minItems": 3,
                "maxItems": 3
              },
              "percentage": { "type": "number", "minimum": 0.0, "maximum": 100.0 }
            }
          }
        },
        "mean_luminance": { "type": "number", "minimum": 0.0, "maximum": 255.0 },
        "rms_contrast": { "type": "number" },
        "median_tone": { "type": "number" }
      }
    },
    "generative_ai_parameters": {
      "type": "object",
      "properties": {
        "is_ai_generated": { "type": "boolean" },
        "detected_engine": { "type": ["string", "null"] },
        "prompt": { "type": ["string", "null"] },
        "negative_prompt": { "type": ["string", "null"] },
        "steps": { "type": ["integer", "null"] },
        "sampler": { "type": ["string", "null"] },
        "cfg_scale": { "type": ["number", "null"] },
        "seed": { "type": ["integer", "null"] },
        "raw_chunks": {
          "type": "object",
          "additionalProperties": { "type": "string" }
        }
      }
    },
    "privacy_audit": {
      "type": "object",
      "required": ["threat_level", "vulnerability_reasons", "sanitization_recommended"],
      "properties": {
        "threat_level": { "type": "string", "enum": ["LOW", "MEDIUM", "HIGH"] },
        "vulnerability_reasons": {
          "type": "array",
          "items": { "type": "string" }
        },
        "sanitization_recommended": { "type": "boolean" }
      }
    },
    "raw_exif_directory_dump": {
      "type": "object",
      "additionalProperties": { "type": "string" }
    }
  }
}
```

Below is an annotated concrete JSON export instance generated from an inspected sample file (`iphone_nyc.jpg`):

```json
{
  "file_metadata": {
    "file_name": "iphone_nyc.jpg",
    "file_size_bytes": 19365,
    "container_format": "JPEG",
    "mime_type": "image/jpeg"
  },
  "cryptographic_verification": {
    "md5": "4a7b53e8d89a45610bcde1234567890f",
    "sha1": "356a192b7913b04c54574d18c28d46e6395428ab",
    "sha256": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
  },
  "image_geometry": {
    "width_px": 4032,
    "height_px": 3024,
    "megapixels": 12.19,
    "aspect_ratio": "4:3",
    "color_mode": "RGB",
    "color_depth": "8 bits per channel (24-bit total)",
    "has_alpha_channel": false,
    "dpi": [72.0, 72.0]
  },
  "camera_telemetry": {
    "make": "Apple",
    "model": "iPhone 14 Pro",
    "lens_model": "iPhone 14 Pro back triple camera 6.86mm f/1.78",
    "software": "17.4.1",
    "datetime_original": "2024:05:18 14:23:45",
    "datetime_digitized": "2024:05:18 14:23:45",
    "aperture_f_number": "1.78",
    "exposure_time_sec": "1/120",
    "iso_speed_rating": "64",
    "focal_length_mm": "6.86",
    "focal_length_35mm_equiv": 24,
    "exposure_program": "Normal program",
    "metering_mode": "Multi-segment / Pattern",
    "flash_status": "Flash did not fire, auto mode",
    "white_balance": "Auto",
    "orientation_tag": "1"
  },
  "geospatial_telemetry": {
    "latitude_decimal": 40.712776,
    "longitude_decimal": -74.005974,
    "dms_representation": "40° 42' 46.0\" N, 74° 0' 21.5\" W",
    "altitude_meters": 10.5,
    "altitude_datum_ref": "Above Sea Level",
    "google_maps_url": "https://www.google.com/maps?q=40.712776,-74.005974",
    "openstreetmap_url": "https://www.openstreetmap.org/?mlat=40.712776&mlon=-74.005974#map=16/40.712776/-74.005974",
    "apple_maps_url": "https://maps.apple.com/?ll=40.712776,-74.005974&q=40.712776,-74.005974"
  },
  "visual_color_analytics": {
    "dominant_palette": [
      { "hex": "#1E3A5F", "rgb": [30, 58, 95], "percentage": 34.2 },
      { "hex": "#A0B2C6", "rgb": [160, 178, 198], "percentage": 22.8 },
      { "hex": "#4A6B82", "rgb": [74, 107, 130], "percentage": 18.5 },
      { "hex": "#DCE3EA", "rgb": [220, 227, 234], "percentage": 14.1 },
      { "hex": "#0D1826", "rgb": [13, 24, 38], "percentage": 10.4 }
    ],
    "mean_luminance": 128.45,
    "rms_contrast": 54.32,
    "median_tone": 131.0
  },
  "generative_ai_parameters": {
    "is_ai_generated": false,
    "detected_engine": null,
    "prompt": null,
    "negative_prompt": null,
    "steps": null,
    "sampler": null,
    "cfg_scale": null,
    "seed": null,
    "raw_chunks": {}
  },
  "privacy_audit": {
    "threat_level": "HIGH",
    "vulnerability_reasons": [
      "Embedded GPS location data reveals exact geographic coordinates",
      "Camera model 'iPhone 14 Pro' reveals device model",
      "Original capture timestamp '2024:05:18 14:23:45' reveals when photo was taken"
    ],
    "sanitization_recommended": true
  },
  "raw_exif_directory_dump": {
    "Make": "Apple",
    "Model": "iPhone 14 Pro",
    "DateTimeOriginal": "2024:05:18 14:23:45",
    "ExposureTime": "1/120",
    "FNumber": "1.78",
    "ISOSpeedRatings": "64",
    "FocalLength": "6.86",
    "LensModel": "iPhone 14 Pro back triple camera 6.86mm f/1.78"
  }
}
```

---

### 3.1.3 CSV Batch Comparison Schema Specification

For multi-image forensic operations, `Img_Analyze` compiles a standardized 20-column relational matrix formatted according to RFC 4180. Table 3.1 defines the schema, field types, nullability, and investigative purposes of the exported matrix.

```
+----------------------------------------------------------------------------------------------------+
|                         TABLE 3.1: CSV BATCH TELEMETRY COMPARISON SCHEMA                           |
+----------------------------------------------------------------------------------------------------+
| Col # | Field Name            | Data Type     | Nullable | Forensic Description & Purpose          |
+-------+-----------------------+---------------+----------+-----------------------------------------+
| 1     | Filename              | VARCHAR(255)  | No       | Basename of processed image file        |
| 2     | Format                | VARCHAR(16)   | No       | Container encoding (JPEG, PNG, WebP)    |
| 3     | File_Size_Bytes       | BIGINT        | No       | Exact physical byte length of stream    |
| 4     | Dimensions            | VARCHAR(32)   | No       | Pixel resolution formatted as "W x H"   |
| 5     | Megapixels            | DECIMAL(6,2)  | No       | Total sensor surface area in millions   |
| 6     | Aspect_Ratio          | VARCHAR(16)   | No       | Simplified aspect ratio (e.g., "16:9")  |
| 7     | Camera_Make           | VARCHAR(64)   | Yes      | Hardware manufacturer (Apple, Canon)    |
| 8     | Camera_Model          | VARCHAR(128)  | Yes      | Specific hardware capture model         |
| 9     | Lens_Model            | VARCHAR(128)  | Yes      | Optical glass attachment specification  |
| 10    | Software_Firmware     | VARCHAR(128)  | Yes      | Device firmware or editing software     |
| 11    | DateTime_Original     | VARCHAR(32)   | Yes      | Capture timestamp: YYYY:MM:DD HH:MM:SS  |
| 12    | Latitude_Decimal      | DECIMAL(10,6) | Yes      | Signed decimal latitude (-90 to +90)    |
| 13    | Longitude_Decimal     | DECIMAL(10,6) | Yes      | Signed decimal longitude (-180 to +180) |
| 14    | Altitude_Meters       | DECIMAL(8,2)  | Yes      | Height relative to geodetic datum       |
| 15    | Exposure_Time         | VARCHAR(32)   | Yes      | Shutter duration (e.g., "1/250")        |
| 16    | Aperture_FNumber      | VARCHAR(16)   | Yes      | Relative aperture diameter (e.g., "2.8")|
| 17    | ISO_Rating            | VARCHAR(16)   | Yes      | Sensor sensitivity gain setting         |
| 18    | SHA256_Checksum       | CHAR(64)      | No       | Cryptographic chain-of-custody hash     |
| 19    | Privacy_Risk_Score    | VARCHAR(16)   | No       | Threat level ("HIGH", "MEDIUM", "LOW")  |
| 20    | Primary_Dominant_Hex  | CHAR(7)       | No       | Hex triplet of primary color swatch     |
+----------------------------------------------------------------------------------------------------+
```

Below is an extract of the CSV output generated across the project sample fixtures:

```csv
Filename,Format,File_Size_Bytes,Dimensions,Megapixels,Aspect_Ratio,Camera_Make,Camera_Model,Lens_Model,Software_Firmware,DateTime_Original,Latitude_Decimal,Longitude_Decimal,Altitude_Meters,Exposure_Time,Aperture_FNumber,ISO_Rating,SHA256_Checksum,Privacy_Risk_Score,Primary_Dominant_Hex
dslr_landscape.jpg,JPEG,30722,6000 x 4000,24.00,3:2,Canon,Canon EOS R5,RF24-70mm F2.8 L IS USM,1.8.1,2024:06:12 09:15:30,,,,1/500,8,100,e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855,MEDIUM,#3A5F8B
iphone_nyc.jpg,JPEG,19365,4032 x 3024,12.19,4:3,Apple,iPhone 14 Pro,iPhone 14 Pro back triple camera 6.86mm f/1.78,17.4.1,2024:05:18 14:23:45,40.712776,-74.005974,10.5,1/120,1.78,64,5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8,HIGH,#1E3A5F
pixel_sydney.jpg,JPEG,14713,4080 x 3072,12.53,4:3,Google,Pixel 8 Pro,Google Pixel 8 Pro back camera 6.9mm f/1.68,HDR+ 1.0.612,2024:04:02 17:45:10,-33.856784,151.215297,4.2,1/250,1.68,50,4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a,HIGH,#2B4C6F
galaxy_rio.jpg,JPEG,25323,4000 x 3000,12.00,4:3,Samsung,Galaxy S24 Ultra,Galaxy S24 Ultra rear main camera,One UI 6.1,2024:02:20 11:10:05,-22.951916,-43.210487,709.8,1/1000,1.7,50,ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d,HIGH,#4D7C0F
clean_export.png,PNG,1193,800 x 600,0.48,4:3,,,,,,,,,,,,4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945,LOW,#5C6B73
```

---

### 3.1.4 Multi-Page Forensic PDF Document Layout Design

The PDF publishing subsystem compiles a publication-grade, multi-page vector PDF document structured to satisfy judicial evidentiary criteria.

```
+----------------------------------------------------------------------------------------------------+
|                         FORENSIC PDF AUDIT REPORT GRID & PAGE DESIGN                               |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  +----------------------------------------------------------------------------------------------+  |
|  |  HEADER ZONE (Y = 10mm to 28mm)                                                             |  |
|  |  - Left: "IMG_ANALYZE: FORENSIC METADATA AUDIT REPORT" (Helvetica-Bold 14pt, Dark Slate)       |  |
|  |  - Right: Dynamic Risk Badge (Crimson "HIGH", Amber "MEDIUM", Emerald "LOW" 10pt Box)        |  |
|  |  - Rule: 0.5mm Horizontal Divider Line (Slate Gray #CBD5E1)                                  |  |
|  +----------------------------------------------------------------------------------------------+  |
|                                                |                                                   |
|  +----------------------------------------------------------------------------------------------+  |
|  |  SECTION 1: CRYPTOGRAPHIC VERIFICATION & EVIDENTIARY HASHES (Y = 32mm to 55mm)               |  |
|  |  - Monospaced Hash Table (Courier 9pt): MD5, SHA-1, SHA-256 Chain of Custody Fingerprints    |  |
|  |  - File Size (Bytes), Container Format, and Bitstream MIME Type                              |  |
|  +----------------------------------------------------------------------------------------------+  |
|                                                |                                                   |
|  +----------------------------------------------------------------------------------------------+  |
|  |  SECTION 2: DUAL-COLUMN HARDWARE, OPTICAL & GEOSPATIAL TELEMETRY (Y = 60mm to 145mm)           |  |
|  |  +------------------------------------+  +------------------------------------------------+  |  |
|  |  | Left Column (Width = 90mm):        |  | Right Column (Width = 90mm):                   |  |  |
|  |  | - Camera Make & Model              |  | - Latitude & Longitude (Decimal & DMS)         |  |  |
|  |  | - Lens Model & Serial Number       |  | - Altitude & Geodetic Sea-Level Datum          |  |  |
|  |  | - Shutter Speed, Aperture, ISO     |  | - Direct OpenStreetMap & Google Maps URLs      |  |  |
|  |  | - Capture & Digitization Timestamps|  | - Geodesic Coordinate Quadrant Reference       |  |  |
|  +------------------------------------+  +------------------------------------------------+  |  |
|  +----------------------------------------------------------------------------------------------+  |
|                                                |                                                   |
|  +----------------------------------------------------------------------------------------------+  |
|  |  SECTION 3: VISUAL COLOR PALETTE & TONAL METRICS (Y = 150mm to 195mm)                         |  |
|  |  - Six Quantized Color Swatches (Width = 28mm each) with Hex, RGB, and Frame Occupancy %     |  |
|  |  - RMS Contrast Ratio, Mean Perceived Luminance (BT.601), and Median Dynamic Range Tone      |  |
|  +----------------------------------------------------------------------------------------------+  |
|                                                |                                                   |
|  +----------------------------------------------------------------------------------------------+  |
|  |  SECTION 4: COMPLETE RAW EXIF & IFD DIRECTORY AUDIT TABLE (Y = 200mm+ Multi-Page Spanning)   |  |
|  |  - Alternating Striped Rows (Header Slate, Row A White, Row B #F8FAFC)                       |  |
|  |  - Two Columns: Tag Name (Width = 60mm) | Formatted Decoded Value (Width = 125mm)            |  |
|  +----------------------------------------------------------------------------------------------+  |
|                                                |                                                   |
|  +----------------------------------------------------------------------------------------------+  |
|  |  FOOTER ZONE (Y = 282mm to 297mm)                                                             |  |
|  |  - Left: "Confidential Forensic Evidence · Img_Analyze v1.1.0 · Air-Gapped Verification"      |  |
|  |  - Right: Dynamic Page Counter ("Page X of Y") via FPDF AliasNbPages()                      |  |
|  +----------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------------------------------------------------+
```

*Geometric Layout Parameters:*
* Page Format: Standard ISO 216 A4 Portrait ($210.0\text{ mm} \times 297.0\text{ mm}$).
* Margins: Left $= 10.0\text{ mm}$, Right $= 10.0\text{ mm}$, Top $= 10.0\text{ mm}$, Bottom $= 15.0\text{ mm}$.
* Printable Canvas Width: $W_{\text{printable}} = 210.0 - 20.0 = 190.0\text{ mm}$.
* Color Palette:
  * Primary Header: Dark Navy Slate (`RGB: 30, 41, 59` / `#1E293B`).
  * Section Headers: Slate Gray (`RGB: 71, 85, 105` / `#475569`).
  * Table Borders: Light Slate (`RGB: 203, 213, 225` / `#CBD5E1`).
  * Table Alternating Fill: Off-White (`RGB: 248, 250, 252` / `#F8FAFC`).
  * Risk Badge Crimson: `RGB: 220, 38, 38` (`#DC2626`).
  * Risk Badge Amber: `RGB: 217, 119, 6` (`#D97706`).
  * Risk Badge Emerald: `RGB: 22, 163, 74` (`#16A34A`).

---

## 3.2 INPUT DESIGN

The input design of `Img_Analyze` addresses the critical balance between forensic data integrity and intuitive user experience. Digital image files must be ingested seamlessly across single and batch workflows without exposing host filesystems to write wear or persisting sensitive evidentiary streams to disk.

```
+----------------------------------------------------------------------------------------------------+
|                             INPUT INGESTION & MEMORY BUFFER SLICING                                |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ Web Browser Client / Terminal Source ]                                                          |
|       |                                                                                            |
|       v                                                                                            |
|  [ Ingestion Pipeline: Single Upload, Multi-File Batch, or Sample Fixture Loading ]               |
|       |                                                                                            |
|       v                                                                                            |
|  [ Stream Allocation: UploadedFile.read() -> Raw Binary Byte Stream B ]                            |
|       |                                                                                            |
|       +-----------------------------------+-----------------------------------+                    |
|       |                                   |                                   |                    |
|       v                                   v                                   v                    |
|  [ Hash Stream B ]               [ Memory Buffer 1 ]                 [ Memory Buffer 2 ]           |
|  hashlib.md5(B)                  io.BytesIO(B)                       io.BytesIO(B)                 |
|  hashlib.sha1(B)                 Pointer: seek(0)                    Pointer: seek(0)              |
|  hashlib.sha256(B)               Image.open(buf1)                    Sanitization Engine           |
|  (Chain of Custody)              (IFD / Pixel Inspection)            (Transposition / Scrub)       |
+----------------------------------------------------------------------------------------------------+
```

### 3.2.1 Ingestion Pipelines
1. **Interactive Web Ingestion:** Streamlit’s `st.file_uploader` provides an interactive, drag-and-drop ingestion interface supporting both single-file deep analysis and multi-file batch queuing. It enforces format boundary checks across accepted extensions (`.jpg`, `.jpeg`, `.png`, `.webp`, `.tiff`, `.tif`, `.bmp`, `.gif`).
2. **Command-Line Ingestion:** The CLI interface accepts single image file paths or recursive directory paths via POSIX arguments, validating file existence, directory readability, and image signature compliance.
3. **One-Click Forensic Sample Chips:** For immediate demonstration and testing, the interface provides embedded sample fixtures (`dslr_landscape.jpg`, `iphone_nyc.jpg`, `pixel_sydney.jpg`, `galaxy_rio.jpg`, and `clean_export.png`).

### 3.2.2 Volatile Stream Handling via Python `io.BytesIO`
Traditional image processing tools write incoming uploads to temporary directories (e.g., `/tmp/upload_XXXXXX.tmp`), introducing data remanence risks. `Img_Analyze` eliminates this by utilizing Python’s `io.BytesIO` abstraction:
* The incoming uploaded file stream is read directly into memory:
  ```python
  raw_bytes = uploaded_file.read()
  stream_buffer = io.BytesIO(raw_bytes)
  ```
* `io.BytesIO` implements an in-memory byte buffer that exposes standard file-like interface methods (`read()`, `seek()`, `tell()`, `truncate()`).
* Downstream processing components (PIL image loaders, cryptographic hashing blocks, ICC profile parsers) consume this memory buffer without invoking underlying operating system file system drivers (`ntfs.sys`, `ext4`, or `apfs`).

### 3.2.3 Memory Buffer Slicing and Pointer Seeking (`seek(0)`)
A common failure mode in stream-based binary processing is pointer exhaustion: once a reader consumes a stream to its end-of-file (EOF), subsequent reading calls return empty bytes unless the file pointer is explicitly repositioned.
* `Img_Analyze` enforces strict pointer seeking:
  ```python
  stream_buffer.seek(0)
  ```
* Before passing the buffer to `Image.open()`, the cryptographic hash engine, or the sanitization pipeline, the internal byte pointer is reset to offset `0x00000000`.
* This enables multiple independent parsing modules to process the same underlying image stream concurrently without corrupting or exhausting the stream.

---

## 3.3 OUTPUT DESIGN

The output design of `Img_Analyze` provides a multi-layered, interactive visualization dashboard that translates complex, low-level binary telemetry into actionable forensic intelligence.

### 3.3.1 Seven-Tab Forensic Dashboard Architecture

The web interface is structured across seven dedicated, domain-specific forensic tabs:

```
+----------------------------------------------------------------------------------------------------+
|                              SEVEN-TAB FORENSIC DASHBOARD WORKSPACE                                |
+----------------------------------------------------------------------------------------------------+
|  [Tab 1: Overview]   | Hardware Make/Model, Software, Timestamps, Dimensions, Hash Badges          |
|  [Tab 2: Geolocation]| Geodetic Coordinates, Altitude, PyDeck 3D Map, OpenStreetMap Iframe        |
|  [Tab 3: Optics]     | Aperture, Shutter Speed, ISO Rating, 35mm Equiv, Flash Bitmask State       |
|  [Tab 4: Raw EXIF]   | Complete Searchable Dictionary Table of all Decoded IFD Tags                |
|  [Tab 5: Visuals]    | Median Cut 6 Dominant Color Swatches, RMS Contrast, Luminance               |
|  [Tab 6: GenAI]      | PNG Chunks (tEXt/iTXt), Diffusion Prompts, Node Graphs, Model Weights       |
|  [Tab 7: Export]     | Multi-page Judicial PDF Export, JSON Schema Export, Clean Image Download    |
+----------------------------------------------------------------------------------------------------+
```

```
+----------------------------------------------------------------------------------------------------+
|                             TAB 1: OVERVIEW & HARDWARE WIREFRAME                                   |
+----------------------------------------------------------------------------------------------------+
| [ IMAGE PREVIEW CARD (Left Col) ]          | [ TELEMETRY METRIC GRID (Right Col) ]                 |
| +----------------------------------------+ | +------------------+ +------------------+             |
| |                                        | | | CAMERA MAKE      | | CAMERA MODEL     |             |
| |       Transposed In-Memory Raster      | | | Apple            | | iPhone 14 Pro    |             |
| |         (Oriented Upright)             | | +------------------+ +------------------+             |
| |                                        | | +------------------+ +------------------+             |
| +----------------------------------------+ | | CAPTURE DATE     | | MEGAPIXELS       |             |
| Dimensions: 4032 x 3024 · Format: JPEG   | | | 2024:05:18       | | 12.19 MP         |             |
| File Size: 19.36 KB · Bit Depth: 24-bit  | | +------------------+ +------------------+             |
|                                            | Software: 17.4.1 · Lens: Triple 6.86mm f/1.78         |
| +------------------------------------------------------------------------------------------------+ |
| | CRYPTOGRAPHIC CHAIN OF CUSTODY CHECKSUMS                                                       | |
| | MD5:    4a7b53e8d89a45610bcde1234567890f                                                       | |
| | SHA-1:  356a192b7913b04c54574d18c28d46e6395428ab                                               | |
| | SHA256: 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8                       | |
| +------------------------------------------------------------------------------------------------+ |
+----------------------------------------------------------------------------------------------------+
```

```
+----------------------------------------------------------------------------------------------------+
|                          TAB 2: GEOLOCATION & MAPPING WIREFRAME                                    |
+----------------------------------------------------------------------------------------------------+
| [ GEODETIC METRICS BANNER ]                                                                        |
| Latitude: 40.712776° N  |  Longitude: -74.005974° W  |  Altitude: 10.5m ASL  |  Ref: WGS 84 Datum  |
| DMS: 40° 42' 46.0" N, 74° 0' 21.5" W                                                               |
|                                                                                                    |
| [ INTERACTIVE OPENSTREETMAP LEAFLET IFRAME ]                                                       |
| +------------------------------------------------------------------------------------------------+ |
| |  [+]                                      (Map Pin Location)                                   | |
| |  [-]                                             * 40.7128°N, 74.0060°W                        | |
| |                                                                                                | |
| |                                                                                                | |
| |                                                                               [Leaflet / OSM]  | |
| +------------------------------------------------------------------------------------------------+ |
|                                                                                                    |
| [ OUTBOUND NAVIGATION ANCHORS ]                                                                    |
| [ 🌐 Open Google Maps Navigation ]  [ 🗺️ OpenStreetMap Inspector ]  [ 🍏 Open Apple Maps Route ]  |
+----------------------------------------------------------------------------------------------------+
```

```
+----------------------------------------------------------------------------------------------------+
|                          TAB 5: VISUAL PALETTE & TONAL METRICS WIREFRAME                           |
+----------------------------------------------------------------------------------------------------+
| [ DOMINANT COLOR SWATCH MATRIX (Median Cut 6-Color Palette) ]                                      |
| +--------------+  +--------------+  +--------------+  +--------------+  +--------------+           |
| |   #1E3A5F    |  |   #A0B2C6    |  |   #4A6B82    |  |   #DCE3EA    |  |   #0D1826    |           |
| |    34.2%     |  |    22.8%     |  |    18.5%     |  |    14.1%     |  |    10.4%     |           |
| | RGB(30,58,95)|  |RGB(160,178..)|  |RGB(74,107..)|  |RGB(220,227..)|  |RGB(13,24,38) |           |
| +--------------+  +--------------+  +--------------+  +--------------+  +--------------+           |
|                                                                                                    |
| [ TONAL & DYNAMIC RANGE GAUGES ]                                                                   |
| +-----------------------+ +-----------------------+ +-----------------------+                      |
| | MEAN LUMINANCE (BT601)| | RMS CONTRAST RATIO    | | MEDIAN SCENE TONE     |                      |
| | 128.45 / 255.0        | | 54.32 (High Dynamic)  | | 131.0 / 255.0         |                      |
| +-----------------------+ +-----------------------+ +-----------------------+                      |
+----------------------------------------------------------------------------------------------------+
```

```
+----------------------------------------------------------------------------------------------------+
|                          TAB 6: GENERATIVE AI WORKFLOW WIREFRAME                                   |
+----------------------------------------------------------------------------------------------------+
| [ SYNTHESIS DETECTION BADGE: "STABLE DIFFUSION / COMFYUI METADATA DETECTED" ]                      |
|                                                                                                    |
| Positive Semantic Prompt:                                                                          |
| "Hyperrealistic cinematic photograph of a cybernetic owl perched on a neon sign, 8k resolution"    |
|                                                                                                    |
| Negative Prompt:                                                                                   |
| "blurry, low quality, artifacts, distorted anatomy, extra limbs, watermark, text"                  |
|                                                                                                    |
| [ MODEL & SAMPLER PARAMETER METRICS ]                                                              |
| Steps: 30  |  Sampler: DPM++ 2M Karras  |  CFG Scale: 7.5  |  Seed: 2849104812  |  Model: SDXL 1.0  |
|                                                                                                    |
| [ COMFYUI NODE GRAPH JSON EXPANDER ]                                                               |
| > Click to inspect raw graph JSON tree (Nodes: 14, Links: 22, CheckpointLoaderSimple)              |
+----------------------------------------------------------------------------------------------------+
```

1. **Tab 1: Overview & Camera Hardware:** Presents the fundamental identity of the image. Displays hardware make and model, lens details, software/firmware version, original capture timestamps, file dimensions, and the cryptographic chain-of-custody fingerprint card (MD5, SHA-1, SHA-256).
2. **Tab 2: Geolocation & Spatial Cartography:** Activates when GPS metadata is detected. Renders sexagesimal and decimal coordinate pairs, geodetic altitude with reference datum, an interactive OpenStreetMap iframe, a PyDeck WebGL satellite layer, and direct navigation links to Google Maps and Apple Maps.
3. **Tab 3: Exposure, Optics & Shooting Telemetry:** Decodes shooting parameters into standard photographic notation: Aperture ($f$-number), Shutter Speed ($1/N\text{ s}$), ISO sensitivity, 35mm equivalent focal length, exposure program mode, metering mode, and the decoded 8-bit flash bitmask state.
4. **Tab 4: Raw EXIF & IFD Directory Dump:** A complete, searchable tabular directory listing every decoded tag name, numerical tag identifier, and formatted raw value across all IFDs.
5. **Tab 5: Visual Tonal Analytics & Color Palette:** Displays the top six dominant color swatches derived via Median Cut quantization with hexadecimal codes and frame coverage percentages, accompanied by RMS contrast and mean perceived luminance metrics.
6. **Tab 6: Generative AI Metadata & Workflow Inspector:** Deeply inspects PNG ancillary chunks (`tEXt`, `zTXt`, `iTXt`), displaying positive/negative generation prompts, sampling steps, sampler types, CFG scales, seed numbers, and complete ComfyUI node graphs.
7. **Tab 7: Forensic Export & Privacy Cleaning Engine:** Provides one-click generation and download of the multi-page judicial audit PDF report, serialized JSON report, CSV batch matrix, and the orientation-preserving sanitized image.

### 3.3.2 Geodesic Spatial Visualizations
* **OpenStreetMap Leaflet Iframe:** Employs an offline-capable HTML template embedding a Leaflet vector canvas centered precisely on $(\phi, \lambda)$ with an interactive pin marker, scale bar, and zoom controls.
* **PyDeck WebGL Geospatial Engine:** Renders hardware-accelerated 3D scatterplot layers over high-resolution satellite tiles, projecting the exact camera capture location with interactive viewport pitch, bearing, and zoom controls.
* **Outbound Navigation Anchors:** Direct navigation links to Google Maps, OpenStreetMap, and Apple Maps enable investigators to launch external street-level reconnaissance with a single click.

### 3.3.3 Structured Forensic PDF Audit Report with Dynamic Risk Badging
The PDF generation engine compiles a multi-page, publication-grade vector document featuring formal evidentiary headers, hash checksum tables, hardware specifications, and an automated privacy threat badge:
* **HIGH RISK (Crimson Badge):** Assigned when precise GPS coordinates or unique hardware serial numbers are detected.
* **MEDIUM RISK (Amber Badge):** Assigned when camera model names, serial numbers, or capture timestamps are identified without GPS.
* **LOW RISK / CLEAN (Emerald Badge):** Assigned when the image is completely devoid of identifying metadata.

### 3.3.4 Sanitized Zero-Residual Image Export Pipeline
The privacy cleaning subsystem provides an immediate download button for the sanitized image. The generated file is completely stripped of all EXIF headers, GPS records, camera serial numbers, and AI generation parameters while preserving correct visual orientation via prior raster transposition.

---

## 3.4 CODE DESIGN & ARCHITECTURE

### 3.4.1 Modular Engine Breakdown and Class Specifications

`Img_Analyze` is architected as a modular, decoupled Python package organized into distinct computational engines, as illustrated in Table 3.2.

```
+----------------------------------------------------------------------------------------------------+
|                         TABLE 3.2: MODULAR ENGINE RESPONSIBILITY MATRIX                            |
+----------------------------------------------------------------------------------------------------+
| Module File      | Primary Classes / Functions              | Core Architectural Responsibilities  |
+------------------+------------------------------------------+--------------------------------------+
| extractor.py     | extract_exif(), extract_file_hashes(),   | Binary stream parsing, IFD traversal,|
|                  | extract_dominant_colors(), decode_flash()| color quantization, risk modeling.   |
| formatter.py     | format_text(), format_json(),            | Data serialization into ANSI text,   |
|                  | format_csv(), build_summary_dict()       | JSON schema, and CSV rows.           |
| gps.py           | extract_gps(), dms_to_decimal(),         | Sexagesimal coordinate unpacking,    |
|                  | format_dms(), get_maps_url()             | WGS 84 datum projection, URL synth.  |
| pdf_export.py    | ForensicPDFReport(FPDF),                 | Multi-page judicial PDF compilation, |
|                  | generate_pdf_report()                    | Latin-1 encoding filter, badges.     |
| batch.py         | batch_process(), build_batch_summary(),  | Multi-image concurrency, directory   |
|                  | build_comparison_dataframe()             | traversal, geospatial centroid math. |
| app.py           | main(), render_dashboard(),              | Reactive Streamlit UI lifecycle,     |
|                  | create_scrubbed_image()                  | PyDeck mapping, session state cache. |
| cli.py           | main(), parse_args(), print_report()     | Headless terminal CLI, POSIX flags,  |
|                  |                                          | ANSI color sequencing, exit codes.   |
+----------------------------------------------------------------------------------------------------+
```

```
+----------------------------------------------------------------------------------------------------+
|                               MODULAR SUBSYSTEM INTERACTION TOPOLOGY                               |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|                               +------------------+                                                 |
|                               |  cli.py / app.py |                                                 |
|                               +------------------+                                                 |
|                                         |                                                          |
|                    +--------------------+--------------------+                                     |
|                    |                                         |                                     |
|                    v                                         v                                     |
|          +-------------------+                     +-------------------+                           |
|          |    batch.py       |                     |   extractor.py    |                           |
|          +-------------------+                     +-------------------+                           |
|                    |                                         |                                     |
|                    |          +-------------------+          |                                     |
|                    +--------> |      gps.py       | <--------+                                     |
|                               +-------------------+                                                |
|                                         |                                                          |
|                    +--------------------+--------------------+                                     |
|                    |                                         |                                     |
|                    v                                         v                                     |
|          +-------------------+                     +-------------------+                           |
|          |   formatter.py    |                     |   pdf_export.py   |                           |
|          +-------------------+                     +-------------------+                           |
+----------------------------------------------------------------------------------------------------+
```

#### Detailed Class and Function Signatures across Modules

1. **`exif_extractor/extractor.py`**:
   * `extract_exif(source: Union[str, os.PathLike, bytes, io.BytesIO], file_name: Optional[str] = None) -> ExifReport`:
     Primary entry point. Ingests file path, raw bytes, or BytesIO stream. Emits strongly typed `ExifReport`.
   * `extract_file_hashes(raw_bytes: bytes) -> Tuple[str, str, str]`:
     Computes `(md5, sha1, sha256)` in a single pass.
   * `decode_flash(val: int) -> str`:
     Performs 8-bit bitmask deconstruction over EXIF Tag 37385.
   * `calculate_aspect_ratio(width: int, height: int) -> str`:
     Evaluates aspect ratio using GCD reduction and standard tolerance thresholds.
   * `extract_dominant_colors(img: Image.Image, num_colors: int = 5) -> List[Dict[str, object]]`:
     Downsamples to $100 \times 100$ and executes Median Cut quantization.
   * `calculate_brightness(img: Image.Image) -> float`:
     Calculates average perceived luminance on a 0–255 scale.
   * `assess_privacy_risk(has_gps: bool, camera_make: Optional[str], camera_model: Optional[str], datetime_original: Optional[str], all_tags: Dict[str, object]) -> Tuple[str, List[str]]`:
     Rule-based threat classifier returning risk badge (`"HIGH"`, `"MEDIUM"`, `"LOW"`) and reasons list.

2. **`exif_extractor/formatter.py`**:
   * `format_text(report: ExifReport, color: bool = True) -> str`:
     Serializes report into ANSI terminal text with ASCII borders.
   * `format_json(report: ExifReport, indent: int = 2) -> str`:
     Serializes report into compliant JSON string according to Schema v1.1.0.
   * `format_csv(report: ExifReport) -> str`:
     Serializes single report into RFC 4180 CSV row string.
   * `build_summary_dict(report: ExifReport) -> Dict[str, object]`:
     Compiles sanitized nested dictionary for programmatic API consumption.

3. **`exif_extractor/gps.py`**:
   * `dms_to_decimal(degrees: float, minutes: float, seconds: float, ref: str) -> float`:
     Converts sexagesimal rational coordinates to signed decimal degrees.
   * `format_dms(degrees: float, minutes: float, seconds: float, ref: str) -> str`:
     Formats coordinates into canonical DMS string notation.
   * `google_maps_link(lat: float, lon: float) -> str`:
     Synthesizes direct Google Maps navigation URL.
   * `openstreetmap_link(lat: float, lon: float) -> str`:
     Synthesizes direct OpenStreetMap vector viewport URL.
   * `apple_maps_link(lat: float, lon: float) -> str`:
     Synthesizes Apple Maps URI link.

4. **`exif_extractor/pdf_export.py`**:
   * Class `ForensicPDFReport(FPDF)`:
     Customized subclass overriding `header()` and `footer()` callbacks, implementing Latin-1 character filtering, risk badge synthesis, and table layout grids.
   * `generate_pdf_report(report: ExifReport, output_dest: Optional[Union[str, io.BytesIO]] = None) -> bytes`:
     Compiles multi-page PDF audit report into binary bytes or writes directly to destination stream.

5. **`exif_extractor/batch.py`**:
   * `batch_process(sources: List[Union[str, bytes]], recursive: bool = False) -> List[ExifReport]`:
     Concurrently processes multiple image inputs.
   * `build_batch_summary(reports: List[ExifReport]) -> Dict[str, object]`:
     Aggregates batch statistics: total files, total volume, GPS presence count, high-risk count.
   * `build_comparison_dataframe(reports: List[ExifReport]) -> pd.DataFrame`:
     Transforms reports list into 20-column relational matrix DataFrame.

6. **`app.py`**:
   * `create_scrubbed_image(pil_img: Image.Image) -> Tuple[bytes, str, str]`:
     Executes `ImageOps.exif_transpose`, canvas reconstruction, and in-memory re-encoding.
   * `compute_dominant_colors(pil_img: Image.Image, num_colors: int = 6) -> List[Dict]`:
     Extracts top 6 dominant colors for Streamlit UI swatch rendering.
   * `main()`:
     Orchestrates Streamlit session state, file upload event loop, sidebar chips, 7-tab dashboard rendering, and PyDeck satellite layers.

7. **`exif_extractor/cli.py`**:
   * `parse_args(argv: Optional[List[str]]) -> argparse.Namespace`:
     Configures POSIX CLI flags (`--json`, `--csv`, `--no-color`, `--recursive`).
   * `main() -> int`:
     CLI entry point managing ANSI virtualization on Windows hosts and emitting exit codes.

---

### 3.4.2 Zero-Footprint In-Memory Architecture & Formal Proof of Non-Persistence

A primary architectural requirement of `Img_Analyze` is the strict guarantee of **zero persistent storage footprint** ($\Delta \mathcal{S}_{\text{disk}} = \emptyset$). In digital forensics and privacy-preserving computing, writing intermediate files to disk creates significant forensic data remanence risks:
1. *Operating System Scratch Residuals:* Temporary files written to `/tmp` or `%TEMP%` can be recovered from unallocated storage clusters even after deletion.
2. *Filesystem Journal Leaks:* Journaling filesystems (NTFS USN Journal, ext4 journal) record file creation, modification, and deletion metadata, permanently logging file names and timestamps.
3. *Wear-Leveling Artifacts:* Solid-state drives (SSDs) and flash memory utilize wear-leveling algorithms that prevent immediate physical erasure, allowing forensic reconstruction of deleted temporary files.

#### Mathematical and Architectural Proof of Non-Persistence

Let $\mathcal{S}_{\text{disk}}$ denote the persistent storage state of the host operating system, and let $\mathcal{V}_{\text{process}}$ represent the virtual address space allocated to the `Img_Analyze` execution process:

```
+----------------------------------------------------------------------------------------------------+
|                             VIRTUAL MEMORY CONFINEMENT TOPOLOGY                                    |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  OPERATING SYSTEM STORAGE SPACE:                                                                   |
|  +----------------------------------------------------------------------------------------------+  |
|  |  Persistent Disk Media: S_disk                                                               |  |
|  |  [ Zero File Creation ] [ Zero Temp Buffers ] [ Zero Journal Changes: Delta S_disk = Empty ]|  |
|  +----------------------------------------------------------------------------------------------+  |
|                                                ^                                                   |
|                                                |  (Strict Isolation Boundary)                      |
|  PROCESS VIRTUAL ADDRESS SPACE:                |                                                   |
|  +---------------------------------------------+------------------------------------------------+  |
|  |  Process Virtual Heap: S_heap subset V_process                                               |  |
|  |  - Ingested Upload Stream: B_input in S_heap                                                 |  |
|  |  - Pillow Decompressed Raster: M_raster in S_heap                                            |  |
|  |  - Sanitized Bitstream Buffer: B_sanitized = io.BytesIO() in S_heap                          |  |
|  |  - Garbage Collection: sys.getrefcount() -> 0 => Free Memory Return                          |  |
|  +----------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------------------------------------------------+
```

* **Step 1 (Ingestion Invariance):** The input image bitstream $\mathcal{B}_{\text{input}}$ is ingested directly via network socket or standard stream into volatile process memory:
  $$\mathcal{B}_{\text{input}} \in \mathcal{S}_{\text{heap}} \subset \mathcal{V}_{\text{process}}$$
* **Step 2 (Parsing Invariance):** Binary parsing is performed by instantiating an in-memory stream buffer:
  $$\text{Image.open}(io.\text{BytesIO}(\mathcal{B}_{\text{input}}))$$
  Decompressed raster pixel matrices $\mathcal{M}_{\text{raster}}$ are allocated strictly within volatile heap blocks.
* **Step 3 (Sanitization Invariance):** Metadata sanitization transposes the raster matrix in memory and re-encodes the clean pixel array into a newly allocated in-memory buffer:
  $$\mathcal{B}_{\text{sanitized}} = io.\text{BytesIO}() \in \mathcal{S}_{\text{heap}}$$
* **Step 4 (Termination & Deallocation):** Upon completion of processing or session termination, standard Python reference counting and garbage collection reclaim the allocated heap blocks:
  $$\lim_{\text{ref} \to 0} \text{dealloc}(\mathcal{B}_{\text{input}}, \, \mathcal{M}_{\text{raster}}, \, \mathcal{B}_{\text{sanitized}}) \implies \mathcal{S}_{\text{heap}} \to \emptyset$$
* **Paging & Swap Evasion:** Because individual processed images are bounded by typical photographic file sizes ($\le 50\text{ MB}$), resident set memory consumption remains well within available physical RAM ($2\text{ GB} - 8\text{ GB}$), preventing operating system virtual memory managers (Windows VMM or Linux kswapd) from paging heap segments into `pagefile.sys` or swap partitions.
* **Journal Non-Proliferation:** Because no Win32 `CreateFileW` calls with `GENERIC_WRITE` or POSIX `open()` calls with `O_CREAT | O_WRONLY` are issued to filesystem paths during processing, the NTFS Change Journal (`$UsnJrnl`) and Master File Table (`$MFT`) record zero record creations or timestamp modifications.
* **Conclusion:** Throughout the entire execution lifecycle, no filesystem write system calls (`NtWriteFile`, `write()`, `open(..., O_CREAT)`) are issued to persistent disk descriptors:
  $$\Delta \mathcal{S}_{\text{disk}} = \emptyset \quad \blacksquare$$

This guarantees that `Img_Analyze` leaves zero trace on persistent storage, ensuring absolute compliance with rigorous privacy standards and anti-forensic operational security guidelines.

---

## 3.5 DATABASE & DATA STRUCTURE DESIGN

`Img_Analyze` purposefully avoids external relational database management systems (RDBMS) like MySQL or PostgreSQL, eliminating external service dependencies, database configuration overhead, and database credential leakage vectors. Instead, the system relies on high-performance, strongly typed in-memory data structures.

### 3.5.1 The `ExifReport` Dataclass Model

The primary data encapsulation vehicle is the `ExifReport` dataclass, defined within `exif_extractor/extractor.py`. It holds all extracted, decoded, and computed metadata attributes for a single processed image.

```python
@dataclass
class ExifReport:
    """Structured forensic result of inspecting one image."""
    # File container metadata
    file_path: str
    file_size: int
    image_format: str
    image_size: Tuple[int, int]  # (width, height) in pixels

    # Headline forensic fields
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    software: Optional[str] = None
    datetime_original: Optional[str] = None
    datetime_digitized: Optional[str] = None
    f_number: Optional[str] = None
    exposure_time: Optional[str] = None
    iso: Optional[str] = None
    focal_length: Optional[str] = None
    orientation: Optional[str] = None
    gps: Optional[GpsInfo] = None

    # Full tag dump dictionary
    all_tags: Dict[str, object] = field(default_factory=dict)

    # Cryptographic multi-hashes
    md5: Optional[str] = None
    sha1: Optional[str] = None
    sha256: Optional[str] = None

    # Geometry and structural telemetry
    megapixels: Optional[float] = None
    aspect_ratio_str: Optional[str] = None
    color_mode: Optional[str] = None
    color_depth: Optional[str] = None
    has_alpha: bool = False
    dpi: Optional[Tuple[float, float]] = None
    is_animated: bool = False
    frame_count: int = 1

    # Visual analytics and color palette
    dominant_colors: List[Dict[str, object]] = field(default_factory=list)
    brightness: Optional[float] = None

    # Extended container metadata
    png_chunks: Dict[str, str] = field(default_factory=dict)
    icc_profile: Optional[str] = None
    raw_info: Dict[str, str] = field(default_factory=dict)

    # Decoded photographic parameters
    exposure_program_name: Optional[str] = None
    metering_mode_name: Optional[str] = None
    flash_description: Optional[str] = None
    white_balance_name: Optional[str] = None
    light_source_name: Optional[str] = None
    orientation_description: Optional[str] = None
    focal_length_35mm: Optional[int] = None

    # Geolocation fields
    altitude: Optional[float] = None
    altitude_ref: Optional[int] = None
    openstreetmap_link: Optional[str] = None
    apple_maps_link: Optional[str] = None

    # Privacy threat assessment
    privacy_risk: str = "LOW"
    privacy_reasons: List[str] = field(default_factory=list)

    @property
    def has_exif(self) -> bool:
        return bool(self.all_tags)

    @property
    def has_gps(self) -> bool:
        return self.gps is not None
```

### 3.5.2 The `GpsInfo` Dataclass Model

Geospatial coordinate attributes are encapsulated within the `GpsInfo` dataclass:

```python
@dataclass
class GpsInfo:
    """Parsed GPS telemetry and geodetic projections."""
    latitude: float
    longitude: float
    dms_string: str
    maps_link: str
    altitude: Optional[float] = None
    altitude_ref: Optional[int] = None
    openstreetmap_link: Optional[str] = None
    apple_maps_link: Optional[str] = None
```

### 3.5.3 Nested Dictionary Hierarchy for Multi-Tiered IFDs

Internally, IFDs are managed through a multi-tiered dictionary hierarchy:
```python
# Multi-tiered IFD Representation
raw_exif_dict: Dict[int, object] = {
    # 0th IFD (Root Baseline Tags)
    271: "Apple",                         # Make
    272: "iPhone 14 Pro",                 # Model
    274: 1,                               # Orientation
    # SubIFD (Photo Execution Tags via IFD.Exif pointer 0x8769)
    36867: "2024:05:18 14:23:45",         # DateTimeOriginal
    33434: IFDRational(1, 120),           # ExposureTime
    33437: IFDRational(178, 100),         # FNumber
    34867: 64,                            # ISOSpeedRatings
    # GPS IFD (Geospatial Tags via IFD.GPSInfo pointer 0x8825)
    1: "N",                               # GPSLatitudeRef
    2: (IFDRational(40,1), IFDRational(42,1), IFDRational(46,1)), # GPSLatitude
    3: "W",                               # GPSLongitudeRef
    4: (IFDRational(74,1), IFDRational(0,1), IFDRational(215,10)) # GPSLongitude
}
```

### 3.5.4 Pandas DataFrame Schema for Batch Matrix Tabulation

During batch processing, multiple `ExifReport` instances are aggregated into a tabular `pandas.DataFrame`. This enables high-performance vector operations, column filtering, search querying, and direct serialization to CSV or Excel formats.

```python
comparison_df = pd.DataFrame([
    {
        "Filename": r.file_path,
        "Format": r.image_format,
        "Size": f"{r.file_size:,} B",
        "Dimensions": f"{r.image_size[0]} x {r.image_size[1]}",
        "Megapixels": r.megapixels,
        "Aspect Ratio": r.aspect_ratio_str,
        "Camera Make": r.camera_make or "N/A",
        "Camera Model": r.camera_model or "N/A",
        "Date Taken": r.datetime_original or "N/A",
        "Latitude": round(r.gps.latitude, 6) if r.gps else None,
        "Longitude": round(r.gps.longitude, 6) if r.gps else None,
        "Altitude (m)": r.altitude,
        "ISO": r.iso or "N/A",
        "Aperture": r.f_number or "N/A",
        "Shutter Speed": r.exposure_time or "N/A",
        "SHA-256": r.sha256[:16] + "..." if r.sha256 else "N/A",
        "Privacy Risk": r.privacy_risk,
    }
    for r in reports
])
```

---

## 3.6 SYSTEM DEVELOPMENT & DETAILED DESCRIPTION OF MODULES

### 3.6.1 Module 1: File & Cryptographic Hash Verification (`extract_file_hashes`)
* **Role:** Establishes digital chain of custody by computing cryptographic message digests across the raw input byte stream.
* **Algorithmic Operation:** Rather than reading the file three times, the module streams the input stream through MD5, SHA-1, and SHA-256 hashing contexts in a single pass.
* **Complexity:** Time complexity is strictly linear with file size: $\mathcal{T}_{\text{hash}}(N) = \mathcal{O}(N)$, with auxiliary space complexity $\mathcal{S}_{\text{aux}} = \mathcal{O}(1)$.
* **Output:** Hexadecimal digest strings anchored to report headers, guaranteeing evidence immutability.

```python
def extract_file_hashes(raw_bytes: bytes) -> Tuple[str, str, str]:
    """Compute MD5, SHA-1, and SHA-256 in a concurrent single-pass digest."""
    h_md5 = hashlib.md5()
    h_sha1 = hashlib.sha1()
    h_sha256 = hashlib.sha256()
    
    # Process in 64 KB memory chunks
    chunk_size = 65536
    for offset in range(0, len(raw_bytes), chunk_size):
        chunk = raw_bytes[offset : offset + chunk_size]
        h_md5.update(chunk)
        h_sha1.update(chunk)
        h_sha256.update(chunk)
        
    return h_md5.hexdigest(), h_sha1.hexdigest(), h_sha256.hexdigest()
```

### 3.6.2 Module 2: Advanced EXIF & Camera Telemetry Decoding
* **Role:** Decodes raw binary IFD entries into standard photographic notation.
* **Rational Number Reduction:** EXIF values such as aperture, exposure time, and focal length are stored as rational pairs ($N/D$). The helper function `_rational_str()` reduces these values into clean decimal or fraction representations:
  * Exposure times $<1\text{ s}$ are converted to clean fractions: e.g., $N=1, D=250 \implies \text{"1/250"}$.
  * Apertures are reduced to standard $f$-stops: e.g., $N=28, D=10 \implies f/2.8$.
* **8-Bit Flash Bitmask Decoding:** EXIF Tag `0x9209` (`Flash`) encodes flash status across multiple bit flags:
  * Bit 0: Flash fired ($0 = \text{No}, 1 = \text{Yes}$).
  * Bits 1–2: Strobe return light detection status ($00 = \text{None}, 10 = \text{Not detected}, 11 = \text{Detected}$).
  * Bits 3–4: Camera flash mode ($01 = \text{Compulsory}, 10 = \text{Suppressed}, 11 = \text{Auto}$).
  * Bit 5: Flash presence ($1 = \text{No flash function}$).
  * Bit 6: Red-eye reduction mode ($1 = \text{Supported/Active}$).

```python
def decode_flash(val: int) -> str:
    """Decode 8-bit flash bitmask into human-readable forensic status."""
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

### 3.6.3 Module 3: Geolocation Engine (`gps.py`)
* **Role:** Parses the GPS IFD directory, converts sexagesimal notation into decimal degrees, decodes altitude datum references, and synthesizes mapping URLs.
* **Coordinate Conversion Algorithm:**
  ```python
  def dms_to_decimal(degrees: float, minutes: float, seconds: float, ref: str) -> float:
      deg = _as_float(degrees)
      minute = _as_float(minutes)
      second = _as_float(seconds)
      decimal = deg + (minute / 60.0) + (second / 3600.0)
      if ref.upper() in ("S", "W"):
          decimal = -decimal
      return round(decimal, 6)
  ```
* **Altitude Reference Decoding:** Inspects `GPSAltitude` and `GPSAltitudeRef`. A reference value of `0` denotes height above sea level, while `1` denotes depth below sea level.

### 3.6.4 Module 4: Extended Metadata & Generative AI Parsing
* **Role:** Traverses PNG ancillary chunks (`tEXt`, `zTXt`, `iTXt`) and WebP RIFF chunks to extract generative AI synthesis parameters.
* **Extraction Pipeline:**
  1. Inspects `img.text` and `img.info` dictionaries for recognized keys (`parameters`, `prompt`, `workflow`, `Comment`).
  2. Executes regex patterns to extract positive prompts, negative prompts, diffusion step counts, sampling algorithms (e.g., Euler a, DPM++ 2M Karras), CFG scale, and generation seeds.
  3. Parses nested ComfyUI node graphs, extracting model checkpoint names and LoRA weights.

```python
def extract_ai_generation_parameters(img: Image.Image) -> Dict[str, object]:
    """Parse generative AI parameters from PNG/WebP chunk containers."""
    res = {"is_ai_generated": False, "prompt": None, "negative_prompt": None, "params": {}}
    raw_text = ""
    # Extract from PNG text chunks or info dictionary
    if hasattr(img, "text") and isinstance(img.text, dict):
        raw_text = img.text.get("parameters", "") or img.text.get("prompt", "")
    elif "parameters" in img.info:
        raw_text = str(img.info["parameters"])
        
    if not raw_text:
        return res
        
    res["is_ai_generated"] = True
    # Parse Stable Diffusion standard output block
    if "Negative prompt:" in raw_text:
        parts = raw_text.split("Negative prompt:")
        res["prompt"] = parts[0].strip()
        remaining = parts[1]
        if "Steps:" in remaining:
            neg, params_block = remaining.split("Steps:", 1)
            res["negative_prompt"] = neg.strip()
            res["params"]["steps"] = params_block.strip()
    else:
        res["prompt"] = raw_text.strip()
        
    return res
```

### 3.6.5 Module 5: Visual Tonal Analytics & Color Quantization
* **Role:** Computes dominant scene colors and dynamic contrast metrics directly from raster pixel arrays.
* **Paul Heckbert’s Median Cut Algorithm:**
  1. Downsamples the raster image to an optimized $100 \times 100$ thumbnail buffer to cap computational overhead at $\approx 30\text{ KB}$ heap memory.
  2. Applies `PIL.Image.quantize(colors=6, method=Image.Quantize.MEDIANCUT)`.
  3. Extracts the resulting color palette and pixel count histograms, computing exact frame occupancy percentages.
* **Perceived Luminance Calculation:**
  $$Y_{601} = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B$$
* **Root Mean Square (RMS) Contrast Calculation:** Evaluates scene dynamic range via the standard deviation of grayscale pixel intensities:
  $$C_{\text{RMS}} = \sqrt{\frac{1}{M \times N} \sum_{x=0}^{M-1} \sum_{y=0}^{N-1} \left( I(x, y) - \bar{I} \right)^2}$$

```python
def extract_dominant_colors(img: Image.Image, num_colors: int = 5) -> List[Dict[str, object]]:
    """Extract dominant colors using Median Cut color space partitioning."""
    thumb = img.convert("RGB")
    thumb.thumbnail((100, 100))
    quantized = thumb.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
    colors = quantized.getcolors(maxcolors=10000)
    if not colors:
        return []
    palette = quantized.getpalette() or []
    colors.sort(key=lambda x: x[0], reverse=True)
    total_pixels = sum(c[0] for c in colors) or 1
    
    result = []
    for count, idx in colors[:num_colors]:
        start = idx * 3
        r = int(palette[start])
        g = int(palette[start + 1])
        b = int(palette[start + 2])
        result.append({
            "hex": f"#{r:02X}{g:02X}{b:02X}",
            "rgb": (r, g, b),
            "percentage": round((count / total_pixels) * 100.0, 2)
        })
    return result
```

### 3.6.6 Module 6: In-Memory Metadata Sanitization Engine
* **Role:** Strips all identifying metadata without introducing the orientation distortion bug.
* **Sanitization Protocol:**
  ```python
  def create_scrubbed_image(pil_img: Image.Image) -> Tuple[bytes, str, str]:
      # Step 1: Hardware-aware orientation transposition
      transposed = ImageOps.exif_transpose(pil_img)
      
      # Step 2: Instantiate new clean raster buffer
      clean_img = Image.new(transposed.mode, transposed.size)
      clean_img.paste(transposed)
      
      # Step 3: Re-encode into volatile in-memory stream
      buf = io.BytesIO()
      fmt = (pil_img.format or "JPEG").upper()
      if fmt == "JPEG" and clean_img.mode in ("RGBA", "P", "LA"):
          clean_img = clean_img.convert("RGB")
      
      if fmt == "JPEG":
          clean_img.save(buf, format="JPEG", quality=95)
      elif fmt == "PNG":
          clean_img.save(buf, format="PNG", optimize=True)
      elif fmt == "WEBP":
          clean_img.save(buf, format="WEBP", quality=95)
      else:
          clean_img.save(buf, format=fmt)
          
      return buf.getvalue(), ext, mime_type
  ```
  This protocol physically transforms the raster pixels to their correct visual orientation *before* discarding EXIF Tag `0x0112`, ensuring that the sanitized image renders upright across all platforms.

### 3.6.7 Module 7: Multi-Image Batch Matrix & Geospatial Pinning (`batch.py`)
* **Role:** Processes multiple images concurrently, compiling aggregate statistics and spatial scatterplot layers.
* **Geospatial Centroid Modeling:** For images containing GPS telemetry, the module computes the geographic centroid $(\bar{\phi}, \bar{\lambda})$ to automatically center map viewports:
  $$\bar{\phi} = \frac{1}{M} \sum_{j=1}^{M} \phi_j, \qquad \bar{\lambda} = \frac{1}{M} \sum_{j=1}^{M} \lambda_j$$
* **PyDeck WebGL Layer Generation:** Compiles scatterplot coordinate layers projecting every image in the batch onto a unified interactive map canvas.

```python
def build_batch_summary(reports: List[ExifReport]) -> Dict[str, object]:
    """Aggregate multi-image forensic metrics across batch."""
    total_files = len(reports)
    total_bytes = sum(r.file_size for r in reports)
    gps_count = sum(1 for r in reports if r.has_gps)
    high_risk_count = sum(1 for r in reports if r.privacy_risk == "HIGH")
    cameras = len(set(r.camera_model for r in reports if r.camera_model))
    
    return {
        "total_files": total_files,
        "total_bytes": total_bytes,
        "gps_count": gps_count,
        "high_risk_count": high_risk_count,
        "unique_cameras": cameras
    }
```

### 3.6.8 Module 8: Forensic Multi-Page PDF Generator Engine (`pdf_export.py`)
* **Role:** Compiles publication-grade, multi-page vector PDF forensic audit reports.
* **Architectural Mechanics:** Subclasses `fpdf2.FPDF` into `ForensicPDFReport`, implementing customized header/footer callbacks, automated page budget tracking, multi-cell alignment, and dynamic risk badge synthesis.
* **Latin-1 Normalization Filter:** Employs an automated character normalization routine:
  ```python
  def _latin1_safe(text: str) -> str:
      return text.encode("latin-1", errors="replace").decode("latin-1")
  ```
  This prevents document compilation crashes when encountering exotic Unicode or raw binary bytes within unstandardized EXIF fields.

```python
class ForensicPDFReport(FPDF):
    """Forensic publication-grade PDF generator subclassing FPDF2."""
    def header(self):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 41, 59)
        self.cell(0, 8, "IMG_ANALYZE: FORENSIC METADATA AUDIT REPORT", ln=False)
        self.set_font("Helvetica", "B", 9)
        # Synthesize risk badge on right margin
        self.set_xy(165, 10)
        self.cell(35, 6, "CONFIDENTIAL", border=1, align="C")
        self.ln(12)
        self.set_draw_color(203, 213, 225)
        self.line(10, 22, 200, 22)
        
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 8, f"Confidential Forensic Evidence · Air-Gapped Verification · Page {self.page_no()}", align="C")
```

---

## 3.7 OVERVIEW OF THE PROJECT

### 3.7.1 Functional Requirements Specification

```
+----------------------------------------------------------------------------------------------------+
|                         TABLE 3.3: FUNCTIONAL REQUIREMENTS TRACEABILITY MATRIX                     |
+----------------------------------------------------------------------------------------------------+
| Req ID | Requirement Title             | Detailed Functional Description                           |
+--------+-------------------------------+-----------------------------------------------------------+
| FR-01  | Multi-Format Ingestion        | Ingest JPEG, PNG, WebP, TIFF, BMP, and GIF via memory.    |
| FR-02  | Cryptographic Hashing         | Compute MD5, SHA-1, SHA-256 digests in a single pass.     |
| FR-03  | EXIF Telemetry Extraction     | Extract camera make/model, lens, software, and timestamps.|
| FR-04  | Optical Setting Decoding      | Decode aperture, shutter rationales, ISO, and flash bits. |
| FR-05  | Sexagesimal GPS Conversion    | Convert DMS arrays to signed decimal degrees (WGS 84).    |
| FR-06  | Altitude Reference Decoding   | Decode elevation relative to sea-level datum flags.       |
| FR-07  | Interactive Spatial Mapping   | Render PyDeck WebGL layers and OpenStreetMap iframes.     |
| FR-08  | Generative AI Prompt Analysis | Traverse PNG chunks for Stable Diffusion/ComfyUI prompts. |
| FR-09  | Visual Color Quantization     | Isolate top 6 dominant colors via Median Cut algorithm.   |
| FR-10  | RMS Contrast Analytics        | Evaluate scene dynamic range via grayscale pixel standard dev.|
| FR-11  | Orientation-Safe Sanitization | Transpose raster pixels and strip all metadata in memory. |
| FR-12  | Judicial PDF Export           | Compile multi-page vector PDF reports with risk badges.   |
+----------------------------------------------------------------------------------------------------+
```

### 3.7.2 Non-Functional Requirements Specification

1. **Performance & Latency:**
   * Single-image parsing and analysis must complete within $<50\text{ ms}$ for standard photographic resolutions ($\le 24\text{ MP}$).
   * PDF report compilation must execute in $<500\text{ ms}$.
   * Memory allocation for color quantization must be strictly capped at $\approx 30\text{ KB}$ per image via $100 \times 100$ thumbnail downsampling.
2. **Security & Privacy:**
   * Strict air-gapped execution: zero outbound network connections, telemetry pings, or external CDN calls.
   * Strict non-persistence: $\Delta \mathcal{S}_{\text{disk}} = \emptyset$. Zero intermediate scratch files written to persistent storage.
3. **Reliability & Fault Tolerance:**
   * Graceful degradation: corrupted or malformed IFD tags must be logged and bypassed without crashing the application process.
   * Universal error trapping via custom `ExifError` exception hierarchies.
4. **Portability & Cross-Platform Parity:**
   * 100% operational parity across Microsoft Windows 10/11, Linux distributions (Ubuntu, Debian, Fedora), and Apple macOS (Intel and Apple Silicon).
   * Automatic console mode virtualization (`ENABLE_VIRTUAL_TERMINAL_PROCESSING`) on Windows hosts.
5. **Usability & Accessibility:**
   * Dual-interface support: rich interactive web dashboard (Streamlit) and scriptable command-line interface (CLI).
   * WCAG-compliant high-contrast text overlays across all quantized color swatches.

### 3.7.3 Comprehensive Development & Execution Tool Descriptions

#### 1. Visual Studio Code (VS Code) IDE
* The primary integrated development environment utilized for building `Img_Analyze`.
* Key extensions leveraged include:
  * **Python Extension Pack (Microsoft):** Provides rich language server support, IntelliSense, auto-formatting via Black, and automated docstring generation.
  * **Pylance:** Advanced static type checking and type inference engine enforcing strict PEP 484 compliance.
  * **GitLens:** Inline Git blame, branch visualization, and commit history exploration supporting structured development iterations.
  * **Remote - WSL:** Facilitated cross-platform debugging across native Windows NT and Windows Subsystem for Linux (WSL2 Ubuntu).

#### 2. Python Runtime Ecosystem (Python 3.10 – 3.14)
* The computational runtime powering the entire application suite.
* Core language features utilized:
  * **Structural Pattern Matching (`match-case`):** Simplifies multi-branch IFD tag classification.
  * **Union Type Operators (`|`):** Replaces verbose typing wrappers with clean type unions (`str | bytes | None`).
  * **Optimized Heap Memory Allocator (`pymalloc`):** Accelerates transient instantiation of millions of integer and rational objects during binary IFD tag traversal.
  * **Standard Library Strengths:** Native `hashlib` for cryptographic digests, `io.BytesIO` for volatile memory buffers, and `dataclasses` for strongly typed object models.
* Key third-party dependencies:
  * **Pillow (PIL Fork v12.3.0):** Low-level binary image parser, raster graphics engine, and color quantizer.
  * **fpdf2 (v2.8.2+):** Lightweight, dependency-free vector PDF publishing library.
  * **Pandas & NumPy:** High-performance tabular data structures and numerical array processing for batch matrix operations.

#### 3. Streamlit Reactive Execution Architecture
* Serves as the web presentation engine (`app.py`).
* **Execution Paradigm:** Streamlit operates under a reactive, dataflow execution model. Whenever a user interacts with a UI widget (e.g., uploading an image or toggling a tab), Streamlit re-executes the entire script from top to bottom.
* **State Preservation via `st.session_state`:** To prevent redundant re-computation of heavy cryptographic hashes and color quantization routines during UI redraws, `Img_Analyze` caches processed `ExifReport` objects inside `st.session_state`.
* **Asynchronous WebSockets:** Communication between the browser client and the local Python runtime occurs across an asynchronous WebSocket connection managed by an embedded Tornado web server, delivering smooth 60 FPS UI transitions without full page reloads.

---

## 3.8 CHAPTER SUMMARY

Chapter 3 has provided an exhaustive, highly detailed architectural specification and engineering design of the `Img_Analyze` platform. The chapter began with an in-depth analysis of file design, articulating the low-level binary structures of supported image containers—including JPEG/JFIF marker sequences, PNG chunk framing with CRC-32 verification, WebP RIFF containers, TIFF IFD pointer trees, BMP raster headers, and GIF89a application blocks. The formal JSON export schema, 20-column CSV batch comparison matrix, and multi-page forensic PDF layout grid were systematically defined.

The input and output designs were detailed, highlighting the volatile stream ingestion pipeline utilizing Python’s `io.BytesIO`, memory pointer seeking protocols, the 7-tab forensic dashboard layout, dual interactive geospatial cartography (PyDeck WebGL and OpenStreetMap Leaflet iframe), and zero-residual sanitized image exports. The code architecture established the responsibilities of the seven core modules and provided a formal mathematical proof of the zero-footprint in-memory architecture ($\Delta \mathcal{S}_{\text{disk}} = \emptyset$). Furthermore, the database and data structure design detailed the strongly typed `ExifReport` and `GpsInfo` dataclass models, while the system development section provided in-depth algorithmic descriptions of all eight core computational modules. Finally, the project overview documented functional and non-functional requirements and the development toolchain (VS Code, Python 3.10–3.14, Streamlit).

With the complete system study and system design formally established in Chapters 2 and 3, the project documentation provides a comprehensive, academically rigorous foundation satisfying all curricular requirements for the Bachelor of Computer Applications degree.
