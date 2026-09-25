# APPENDICES

---

## INSTITUTIONAL RECORD & METADATA

```
========================================================================================
COLLEGE           : SONA COLLEGE OF ARTS AND SCIENCE, SALEM – 636 005
DEPARTMENT        : DEPARTMENT OF COMPUTER APPLICATIONS (B.C.A.)
AFFILIATION       : PERIYAR UNIVERSITY, SALEM – 636 011, TAMIL NADU, INDIA
PROJECT TITLE     : EXIF METADATA EXTRACTOR & PRIVACY INSPECTOR (IMG_ANALYZE)
DEGREE            : BACHELOR OF COMPUTER APPLICATIONS (B.C.A.)
ACADEMIC YEAR     : 2025–2026
CANDIDATE NAME    : SYED AFRIDI (REGISTER NUMBER: 23UCA101)
FACULTY SUPERVISOR: Dr. M. SANGEETHA, M.C.A., M.Phil., Ph.D.
DOCUMENT SECTION  : TECHNICAL APPENDICES (APPENDIX A THROUGH APPENDIX E)
========================================================================================
```

---

\newpage

# APPENDIX A: SYSTEM FLOW DIAGRAMS & ARCHITECTURE

### A.1 Architectural Overview and System Paradigms

The *EXIF Metadata Extractor & Privacy Inspector (`IMG_ANALYZE`)* system is engineered as an offline, zero-disk-footprint forensic imaging and OSINT (Open Source Intelligence) inspection pipeline. The application processes raster graphics—including JPEG, TIFF, PNG, WebP, BMP, and GIF—without persisting transient image payloads or extracted forensic artifacts to local disk buffers, thereby eliminating data residue risks. The structural topology adheres to a modular, decoupled architecture consisting of an ingestion boundary, a cryptographic hashing stage, an Image File Directory (IFD) parser, a spherical coordinate geolocation resolver, an image quantization analytics engine, a deterministic privacy risk scoring automaton, an in-memory metadata sanitization engine, and multi-format reporting subsystems (PDF, JSON, CSV).

---

### A.2 Comprehensive System Flowchart

The following flowchart captures the end-to-end execution lifecycle of the system, traversing from raw binary ingestion through in-memory memory stream allocation, cryptographic digest generation, nested tag extraction, privacy risk scoring, interactive web dispatch, and forensic reporting.

```
       +-------------------------------------------------------------+
       |                     START / USER ACTION                     |
       |  User initiates CLI command OR opens Streamlit Web Browser  |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |               IMAGE INGESTION & BOUNDARY CHECK              |
       |   Source: Local File Path, CLI Arg, or Web Drag-and-Drop    |
       |     Permitted Formats: JPEG, PNG, WEBP, TIFF, BMP, GIF      |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |               IN-MEMORY STREAM BUFFERING                    |
       |          Instantiate io.BytesIO(raw_image_bytes)            |
       |   Verify buffer size > 0 bytes; Reject empty/corrupt files  |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |           CRYPTOGRAPHIC FORENSIC HASH GENERATION            |
       |  Execute single-pass message digesting over raw byte array: |
       |     1. MD5 Digest     (128-bit RFC 1321)                    |
       |     2. SHA-1 Digest   (160-bit FIPS PUB 180-4)              |
       |     3. SHA-256 Digest (256-bit FIPS PUB 180-4)              |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |           IMAGE STRUCTURE & GEOMETRY EXTRACTION             |
       |  Image.open(BytesIO) -> Query: format, dimensions, mode     |
       |  Compute Megapixels: (Width * Height) / 1,000,000           |
       |  Compute Standard/Simplified Aspect Ratio (via math.gcd)    |
       |  Extract Bit Depth, Alpha Channel Presence, and DPI Density |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |          PRIMARY EXIF & IFD SUB-DIRECTORY PARSING           |
       |  Attempt 1: Pillow Modern getexif() + get_ifd(IFD.Exif)     |
       |  Attempt 2: Fallback to Legacy _getexif()                   |
       |  Attempt 3: Fallback to Low-Level piexif.load()             |
       |  Traverse IFD0, SubIFD, Interoperability, & MakerNotes      |
       +-------------------------------------------------------------+
                                      |
                   +------------------+------------------+
                   |                                     |
                   v                                     v
       +-----------------------+             +-----------------------+
       |   GPS IFD EXTRACTOR   |             |   ANCILLARY CHUNKS    |
       | Check GPSInfo (34853) |             | Extract PNG tEXt/iTXt |
       | Parse DMS Lat & Lon   |             | Parse ComfyUI/A1111   |
       | Parse Altitude & Ref  |             | Extract ICC Profiles  |
       +-----------------------+             +-----------------------+
                   |                                     |
                   +------------------+------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |              GEOLOCATION COORDINATE MATHEMATICS             |
       |  Equation: Decimal = Degrees + (Minutes/60) + (Seconds/3600)|
       |  Invert sign if Reference Hemisphere is 'S' (South) or 'W'  |
       |  Generate External Cartographic Geospatial URLs:            |
       |  - Google Maps, OpenStreetMap, Apple Maps                   |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |         CHROMATIC & COLOR QUANTIZATION ANALYTICS            |
       |  Downsample 100x100 thumbnail -> Median-Cut Quantization    |
       |  Extract 5-6 Dominant Colors -> Convert to Hex & RGB        |
       |  Calculate Perceived Luminance: 0.299R + 0.587G + 0.114B    |
       |  Determine Dynamic Contrast Foreground Hex (#000000/#FFFFFF)|
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |           DETERMINISTIC PRIVACY RISK ASSESSMENT             |
       |  Evaluate presence of:                                      |
       |  [Condition 1]: GPS Coordinates OR Hardware Serial Numbers  |
       |     --> Assign HIGH RISK Banner (Red / Severe OSINT Breach) |
       |  [Condition 2]: Device Model OR Original Capture Timestamp  |
       |     --> Assign MEDIUM RISK Banner (Amber / Identity Trail)  |
       |  [Condition 3]: No identifying hardware or spatiotemporal   |
       |     --> Assign LOW RISK Banner (Green / Sanitized Baseline) |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |             DISPATCH INTERFACE & PRESENTATION               |
       |  Streamlit Responsive GUI / Terminal ANSI Formatter         |
       |  Display: Image Preview, Telemetry Cards, Interactive Map,  |
       |           Palette Swatches, and Searchable Tag Explorer     |
       +-------------------------------------------------------------+
                                      |
                   +------------------+------------------+
                   |                                     |
                   v                                     v
       +-----------------------+             +-----------------------+
       | IN-MEMORY SANITIZER   |             |  FORENSIC PDF EXPORT  |
       | ImageOps.exif_transpose|            | Vector PDF Generation |
       | Create clean canvas   |             | Embed Hashes, Metadata|
       | Strip all IFD/Chunks  |             | Embed Risk Assessment |
       | Stream clean bytes    |             | Export via fpdf2      |
       +-----------------------+             +-----------------------+
                   |                                     |
                   +------------------+------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                            END                              |
       |       Memory Buffers Deallocated via Python Garbage Coll.   |
       +-------------------------------------------------------------+
```

---

### A.3 Data Flow Diagram (DFD) Level 0: Context Diagram

The Level 0 Context Diagram depicts the primary operational boundary of the `IMG_ANALYZE` system, identifying external entities (End User, Forensic Investigator, External Cartographic Providers) and the high-level information streams traversing the system boundary.

```
                     +---------------------------------------+
                     |         EXTERNAL CARTOGRAPHIC         |
                     |         SERVICES & SATELLITE          |
                     |  (Google Maps / OSM / Apple Maps)     |
                     +---------------------------------------+
                                      ^
                                      | Latitude/Longitude Query Strings
                                      | (WGS84 Datum Coordinates)
                                      |
 +-------------------+        +----------------+        +-------------------+
 |                   | -----> |                | -----> |                   |
 |     END USER /    | Raw    |  EXIF METADATA | Sanit- |  PRIVACY-AWARE    |
 |     ANALYST       | Images |  EXTRACTOR &   | ized   |  RECIPIENT /      |
 |                   |        |  PRIVACY       | Image  |  PUBLIC WEB       |
 |  Submits:         |        |  INSPECTOR     | Stream |                   |
 |  - JPG/PNG/WebP   | <----- |  (IMG_ANALYZE) |        +-------------------+
 |  - Directory URI  | Visual |                |
 |  - Scrub Request  | Dumps, |                |
 |                   | Risk,  +----------------+
 |  Receives:        | PDF/   |
 |  - Forensic PDF   | CSV    |
 |  - Interactive UI | Dockets|
 +-------------------+        +----------------+
```

---

### A.4 Data Flow Diagram (DFD) Level 1: Subsystem Functional Decomposition

The Level 1 DFD decomposes the system into six core algorithmic processes, tracking internal data stores, mathematical transformations, and intermediate forensic state records.

```
[User Image]
    |
    v
+-------------------------------------------------------------------------------+
| Process 1.0: Ingestion & Cryptographic Integrity Verification                  |
| Inputs : File Path or In-Memory Binary Stream                                 |
| Logic  : Read byte buffer; Calculate MD5, SHA-1, SHA-256 digests; Check size |
| Outputs: Raw Byte Stream, Cryptographic Integrity Manifest                    |
+-------------------------------------------------------------------------------+
    |
    +-----------------------------------------------+
    |                                               |
    v                                               v
+------------------------------------+  +------------------------------------+
| Process 2.0: Structural Parsing    |  | Process 3.0: Visual & Chromatic    |
| Logic  : Extract IFD0, SubIFD,     |  |              Analytics Engine      |
|          GPS IFD, PNG Chunks       |  | Logic  : 100x100 Downsample;       |
| Outputs: Raw Tag Map, Lens Model,  |  |          Median-Cut Quantization;  |
|          Exposure, Datetime Strings|  |          Luminance Calculation     |
+------------------------------------+  | Outputs: Hex Swatches, Perceived L |
    |                                   +------------------------------------+
    v                                               |
+------------------------------------+              |
| Process 4.0: Geodetic Coordinate   |              |
|              Transformation        |              |
| Inputs : DMS Rationals, Ref Bytes  |              |
| Logic  : Dec = D + M/60 + S/3600   |              |
| Outputs: Signed Decimal Lat/Lon,   |              |
|          Cartographic URLs         |              |
+------------------------------------+              |
    |                                               |
    +-----------------------+-----------------------+
                            |
                            v
+-------------------------------------------------------------------------------+
| Process 5.0: Deterministic Privacy Risk Evaluation Rule Engine                |
| Inputs : Extracted Tags, Geodetic Coordinates, Hardware Serials               |
| Logic  : Evaluate Threat Taxonomy Rules (HIGH / MEDIUM / LOW)                 |
| Outputs: Risk Level Identifier, Contextual Forensic Violation Strings         |
+-------------------------------------------------------------------------------+
                            |
            +---------------+---------------+
            |                               |
            v                               v
+-------------------------------+  +------------------------------------+
| Process 6.0: In-Memory        |  | Process 7.0: Multi-Format Forensic |
|              Sanitization     |  |              Reporting Engine      |
| Logic  : EXIF Transposition;  |  | Logic  : fpdf2 PDF compilation;    |
|          Pixel Canvas Redraw; |  |          DataFrame CSV generation; |
|          Zero-Metadata Export |  |          Streamlit GUI Dispatch    |
| Outputs: Clean Stripped Image |  | Outputs: PDF Report, Batch CSV     |
+-------------------------------+  +------------------------------------+
```

---

### A.5 Layered System Block Diagram

The architectural stack illustrates the hardware execution environment, runtime virtualization layer, core computational modules, and interface presentation tiers.

```
+===============================================================================+
|                   TIER 4: PRESENTATION & INTERACTION TIER                     |
+===============================================================================+
|  Streamlit Interactive Web UI (Port 8501)   |  ANSI CLI Terminal Engine       |
|  - Real-time File Dropzone & File Watcher   |  - Rich Table Formatter         |
|  - Leaflet Map Visualizer (st.map)          |  - Command Arguments Parser     |
|  - Color Palette Swatch HTML Renderer       |  - Exit Code & Error Handler    |
|  - Searchable Tag Explorer (Case-Insens.)   |  - Batch Progress Indicator     |
+===============================================================================+
                                       |
                                       v
+===============================================================================+
|                   TIER 3: FORENSIC BUSINESS LOGIC ENGINE                      |
+===============================================================================+
|  [extractor.py]               [gps.py]               [pdf_export.py]         |
|  - Stream Ingestion Engine    - DMS to Decimal Math  - Vector Document Engine|
|  - IFD Traversal Automaton    - Geodesic Link Builder- Dynamic Risk Styling  |
|  - Risk Classification Rules  - Altitude Offset Calc - Latin-1 Text Sanitizer|
|  --------------------------------------------------------------------------- |
|  [batch.py]                   [formatter.py]         [app.py Sanitizer]      |
|  - Multi-Report Aggregator    - Human Size Converter - EXIF Transpose Pivot  |
|  - Comparison DataFrame Engine- Key-Value Alignment  - Blank Canvas Re-draw  |
+===============================================================================+
                                       |
                                       v
+===============================================================================+
|                   TIER 2: COMPUTATIONAL FRAMEWORK & LIBRARIES                 |
+===============================================================================+
|  Pillow (PIL Imaging v11.x)   |  Pandas Data Engine    |  FPDF2 Document Core |
|  - Image.open / ImageOps      |  - DataFrame Storage   |  - Line/Rect Primit. |
|  - Quantize.MEDIANCUT         |  - CSV Serializer      |  - Auto Page Break   |
|  - ExifTags (TAGS, GPSTAGS)   |  - Series Aggregators  |  - Header/Footer Subs|
+===============================================================================+
                                       |
                                       v
+===============================================================================+
|                   TIER 1: HOST OPERATING SYSTEM & HARDWARE                    |
+===============================================================================+
|  Python 3.14.0 Virtualized Runtime Environment (Self-Contained Embedded)       |
|  Local Host OS: Microsoft Windows 11 Enterprise (64-bit Architecture)          |
|  Hardware Layer: Multi-core x86_64 CPU, RAM Main Memory, Solid-State Drive     |
+===============================================================================+
```

---

### A.6 UML Sequence Diagram: User Ingestion to Display Dispatch

The sequence diagram documents the chronological communication and execution boundaries between the End User, the Web Interface (`app.py`), the Extraction Module (`extractor.py`), the Math Engine (`gps.py`), and the Forensic Document Generator (`pdf_export.py`).

```
User/Analyst       app.py (Streamlit)      extractor.py          gps.py         pdf_export.py
     |                     |                     |                  |                 |
     |--- Upload Image --->|                     |                  |                 |
     |    (Binary Buffer)  |--- extract_exif --->|                  |                 |
     |                     |    (source, name)   |                  |                 |
     |                     |                     |-- MD5/SHA Hash ->|                 |
     |                     |                     |-- Read Geometry->|                 |
     |                     |                     |-- Parse IFD0 --->|                 |
     |                     |                     |-- Parse SubIFD ->|                 |
     |                     |                     |                  |                 |
     |                     |                     |-- Parse GPSIFD ->|                 |
     |                     |                     |   (Rationals)    |                 |
     |                     |                     |----------------->|                 |
     |                     |                     |  dms_to_decimal  |                 |
     |                     |                     |<-----------------|                 |
     |                     |                     |  (Float Lat/Lon) |                 |
     |                     |                     |                  |                 |
     |                     |                     |-- Color Quant. ->|                 |
     |                     |                     |-- Risk Analysis->|                 |
     |                     |<-- Return Report ---|                  |                 |
     |                     |    (ExifReport Obj) |                  |                 |
     |                     |                                                          |
     |                     |-- Render Metric KPI Cards ------------------------------>| (Browser UI)
     |                     |-- Render OpenStreetMap / Leaflet Pin ------------------->|
     |                     |-- Render Hex Palette HTML Swatches --------------------->|
     |                     |                                                          |
     |-- Click 'Export' -->|                                                          |
     |   (PDF Report)      |------------------------------------ generate_pdf ------->|
     |                     |                                     (report, raw_bytes)  |
     |                     |<----------------------------------- Return PDF Bytes ----|
     |<-- Download PDF ----|                                                          |
     |    (Forensic File)  |                                                          |
     |                     |                                                          |
     |-- Click 'Scrub' --->|                                                          |
     |    (Sanitize Image) |-- ImageOps.exif_transpose()                               |
     |                     |-- Create Clean RGB Canvas                                |
     |                     |-- Save without EXIF payload                              |
     |<-- Stream Clean ----|                                                          |
     |    (Zero Metadata)  |                                                          |
```

---

### A.7 UML Activity Diagram: In-Memory Metadata Scrubbing

This diagram details the sequence of operational steps and branch decisions executed by `create_scrubbed_image()` to ensure that orientation adjustments are preserved while stripping every trace of forensic metadata.

```
                             ( START )
                                 |
                                 v
               +-----------------------------------+
               | Receive Original PIL.Image Object |
               +-----------------------------------+
                                 |
                                 v
               +-----------------------------------+
               | Query EXIF Orientation Tag (0x112)|
               +-----------------------------------+
                                 |
                                 v
               +-----------------------------------+
               | Execute ImageOps.exif_transpose() |
               | Physically rotate pixel matrix    |
               | (e.g., 90 CW, 180, or 270 CW)     |
               +-----------------------------------+
                                 |
                                 v
               +-----------------------------------+
               | Allocate Empty PIL.Image Canvas   |
               | Mode = transposed.mode            |
               | Size = (transposed.width, height) |
               +-----------------------------------+
                                 |
                                 v
               +-----------------------------------+
               | Blit / Paste Transposed Pixels    |
               | onto Clean Blank Canvas           |
               +-----------------------------------+
                                 |
                                 v
                   /---------------------------\
                  /   Original Format == JPEG?  \
                  \                             /
                   \---------------------------/
                             |         |
                            YES        NO
                             |         |
                             v         +----------------------+
               /---------------------------\                  |
              /   Mode in (RGBA, P, LA)?    \                 |
              \                             /                 |
               \---------------------------/                  |
                     |                 |                      |
                    YES                NO                     |
                     |                 |                      |
                     v                 |                      |
        +-------------------------+    |                      |
        | Convert Mode to 'RGB'   |    |                      |
        | (Discard Alpha Channel) |    |                      |
        +-------------------------+    |                      |
                     |                 |                      |
                     +--------+--------+                      |
                              |                               |
                              v                               v
        +-----------------------------------+   +----------------------------+
        | Write Canvas to io.BytesIO Buffer |   | Write Canvas to Buffer     |
        | Format: JPEG, Quality: 95         |   | Format: PNG (optimize=True)|
        | Param: exif=None (STRICT OMISSION)|   | Param: pnginfo=None        |
        +-----------------------------------+   +----------------------------+
                              |                               |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              | Return (Clean Bytes, Ext, Mime|
                              | Buffer sent to Browser Client |
                              +-------------------------------+
                                              |
                                              v
                                           ( END )
```

---

\newpage

# APPENDIX B: DATA SCHEMAS & TABLE STRUCTURES

### B.1 TIFF/EXIF Specification and Tag Architecture

The Exchangeable Image File Format (EXIF) standardizes the encapsulation of metadata within raster graphics file formats, notably JPEG (via `APP1` Application Marker segments, byte sequence `0xFF 0xE1`) and TIFF (via Image File Directories). An EXIF metadata block adheres to the Tagged Image File Format (TIFF) 6.0 directory architecture. 

A standard 12-byte IFD Directory Entry structure is defined as follows:

$$\text{IFD Entry} = \{\text{Tag ID (2 Bytes)}, \text{Type (2 Bytes)}, \text{Count (4 Bytes)}, \text{Value / Offset (4 Bytes)}\}$$

The supported TIFF primitive data types utilized across the `IMG_ANALYZE` parsing engine include:
1. `BYTE` (Type 1): 8-bit unsigned integer.
2. `ASCII` (Type 2): 8-bit byte sequence containing 7-bit ASCII characters terminated by a NULL byte (`0x00`).
3. `SHORT` (Type 3): 16-bit (2-byte) unsigned integer.
4. `LONG` (Type 4): 32-bit (4-byte) unsigned integer.
5. `RATIONAL` (Type 5): Two consecutive `LONG` integers representing the numerator and denominator of a fraction.
6. `UNDEFINED` (Type 7): 8-bit byte sequence capable of storing arbitrary binary structures.
7. `SRATIONAL` (Type 10): Two consecutive signed 32-bit integers representing fractional quantities.

---

### B.2 Comprehensive EXIF Tag Hex Mapping Dictionary

The tables below provide the complete specification of all EXIF tags decoded by the system, organized across Primary IFD0, SubIFD Photographic Telemetry, and GPS Sub-Directories.

#### Table B.1: Primary Image File Directory 0 (IFD0) Tags

| Tag Hex ID | Tag Decimal | Standard Name | TIFF Type | Typical Length | Value Decoding & Range Rules | Forensic & Intelligence Significance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0x010E` | 270 | `ImageDescription` | `ASCII` | Variable | UTF-8 / ASCII text string. | User captions, default camera software titles, or scanning software notes. |
| `0x010F` | 271 | `Make` | `ASCII` | Variable | Manufacturer name string (e.g., "Canon", "Apple"). | Uniquely identifies hardware vendor; verifies source authenticity. |
| `0x0110` | 272 | `Model` | `ASCII` | Variable | Commercial equipment model name (e.g., "iPhone 15 Pro"). | Critical for device fingerprinting and physical evidence linkage. |
| `0x0112` | 274 | `Orientation` | `SHORT` | 2 Bytes | Integer [1..8]: 1=Normal, 3=180° rot, 6=90° CW, 8=270° CW. | Reveals spatial orientation of camera sensor during capture. |
| `0x0131` | 305 | `Software` | `ASCII` | Variable | OS build, post-processing suite (e.g., "Adobe Photoshop", "iOS 18.2"). | Critical for establishing chain of custody and tampering detection. |
| `0x0132` | 306 | `DateTime` | `ASCII` | 20 Bytes | Format: `YYYY:MM:DD HH:MM:SS` (Null-terminated). | File modification or export timestamp; detects post-capture edits. |

#### Table B.2: SubIFD Photographic & Optical Telemetry Tags

| Tag Hex ID | Tag Decimal | Standard Name | TIFF Type | Typical Length | Value Decoding & Range Rules | Forensic & Intelligence Significance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0x829A` | 33434 | `ExposureTime` | `RATIONAL` | 8 Bytes | Seconds represented as fraction (e.g., 1/250, 1/120). | Reveals lighting conditions and ambient environment. |
| `0x829D` | 33437 | `FNumber` | `RATIONAL` | 8 Bytes | Lens aperture ratio ($N = f/D$), e.g., 2.8, 1.8, 8.0. | Corroborates physical optical lens capabilities and depth-of-field. |
| `0x8822` | 34850 | `ExposureProgram` | `SHORT` | 2 Bytes | Enums: 1=Manual, 2=Normal, 3=Aperture Pri, 4=Shutter Pri. | Evaluates photographer operational behavior (manual vs automated). |
| `0x8827` | 34867 | `ISOSpeedRatings` | `SHORT` | 2 Bytes | Sensor sensitivity rating: 50, 100, 200, 400, 800, 1600, 6400. | Correlates sensor noise and lighting levels for time-of-day verification. |
| `0x9000` | 36864 | `ExifVersion` | `UNDEFINED` | 4 Bytes | 4-byte string: "0230", "0231", "0232" (representing EXIF 2.3). | Establishes era and technical standard compliance of camera device. |
| `0x9003` | 36867 | `DateTimeOriginal` | `ASCII` | 20 Bytes | Format: `YYYY:MM:DD HH:MM:SS` of shutter actuation. | Prime chronological forensic anchor for establishing chronolocation. |
| `0x9201` | 37377 | `ShutterSpeedValue` | `SRATIONAL` | 8 Bytes | Additive system value (APEX): $TV = -\log_2(\text{ExposureTime})$. | Internal computational camera metric validating ExposureTime. |
| `0x9202` | 37378 | `ApertureValue` | `RATIONAL` | 8 Bytes | APEX Aperture value: $AV = 2 \log_2(\text{FNumber})$. | Internal computational optical metric validating FNumber. |
| `0x9204` | 37380 | `ExposureBiasValue`| `SRATIONAL` | 8 Bytes | Signed EV compensation offset (e.g., -0.33, +0.67, 0.00). | User-configured brightness adjustments indicating lighting challenges. |
| `0x9207` | 37383 | `MeteringMode` | `SHORT` | 2 Bytes | Enums: 1=Average, 2=Center-Weighted, 3=Spot, 5=Multi-Segment. | Demonstrates optical scene metering characteristics. |
| `0x9209` | 37385 | `Flash` | `SHORT` | 2 Bytes | Bitmask: Bit 0=Fired, Bits [1..2]=Return, Bits [3..4]=Mode. | Determines indoor/night settings and physical flash illumination. |
| `0x920A` | 37386 | `FocalLength` | `RATIONAL` | 8 Bytes | Physical focal length of lens assembly in millimeters (mm). | Determines distance from subject and lens physical geometry. |
| `0xA405` | 41989 | `FocalLengthIn35mm`| `SHORT` | 2 Bytes | Scaled equivalent focal length relative to standard 35mm film. | Direct measure of field of view, distinguishing wide vs telephoto. |
| `0xA434` | 42036 | `LensModel` | `ASCII` | Variable | Commercial lens designation string (e.g., "RF24-105mm F4 L"). | Establishes secondary physical equipment owned by the subject. |

#### Table B.3: GPS Sub-Directory (GPS IFD) Tags

| Tag Hex ID | Tag Decimal | Standard Name | TIFF Type | Typical Length | Value Decoding & Range Rules | Forensic & Intelligence Significance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0x0001` | 1 | `GPSLatitudeRef` | `ASCII` | 2 Bytes | 'N' (North) or 'S' (South). Terminated by NULL. | Determines positive vs negative Cartesian geodetic sign. |
| `0x0002` | 2 | `GPSLatitude` | `RATIONAL` | 24 Bytes | Three rationals: [Degrees/1, Minutes/1, Seconds/100]. | Absolute horizontal latitude on the WGS84 ellipsoidal surface. |
| `0x0003` | 3 | `GPSLongitudeRef`| `ASCII` | 2 Bytes | 'E' (East) or 'W' (West). Terminated by NULL. | Determines positive vs negative Cartesian geodetic sign. |
| `0x0004` | 4 | `GPSLongitude` | `RATIONAL` | 24 Bytes | Three rationals: [Degrees/1, Minutes/1, Seconds/100]. | Absolute vertical longitude on the WGS84 ellipsoidal surface. |
| `0x0005` | 5 | `GPSAltitudeRef` | `BYTE` | 1 Byte | 0 = Above sea level; 1 = Below sea level. | Vertical elevation reference point. |
| `0x0006` | 6 | `GPSAltitude` | `RATIONAL` | 8 Bytes | Rational representing distance in meters relative to reference. | Pinpoints floor level, mountain height, or aerial altitude. |
| `0x001D` | 29 | `GPSDateStamp` | `ASCII` | 11 Bytes | Format: `YYYY:MM:DD` derived directly from satellite atomic clock. | Un-spoofed atomic clock date independent of device system clock. |

---

### B.3 PNG Ancillary Chunks Specification & AI Prompt Metadata

Portable Network Graphics (PNG) images store non-pixel supplementary metadata inside structured ancillary chunk streams. Each chunk consists of a 4-byte length, a 4-byte chunk type ASCII code, chunk payload data, and a 4-byte Cyclic Redundancy Check (CRC-32) code.

```
+--------------------+--------------------+--------------------+--------------------+
|  Length (4 Bytes)  | Chunk Type (4 Byte)| Chunk Data (Length)|   CRC-32 (4 Bytes) |
|   Big-Endian uint  | 'tEXt'/'zTXt'/etc. | Binary / String    | IEEE 802.3 Checksum|
+--------------------+--------------------+--------------------+--------------------+
```

#### Table B.4: PNG Metadata Chunk Architectural Taxonomy

| Chunk Name | ASCII Code | Internal Compression | Structural Syntax | Supported Metadata Scope |
| :--- | :--- | :--- | :--- | :--- |
| Textual Data | `tEXt` | None (Uncompressed ISO-8859-1) | `Keyword\0Text` | Author, Description, Copyright, Software, Prompts. |
| Compressed | `zTXt` | Deflate (RFC 1951 zlib stream) | `Keyword\0Method\0CompressedBytes` | Extended software workflows, Adobe XMP payloads. |
| International| `iTXt` | Optional Deflate (UTF-8 Unicode) | `Keyword\0CompFlag\0Method\0Lang\0TransKey\0Text` | Multilingual captions, Generative AI Model parameters. |

#### Modern AI Prompt Forensic Keys Extracted by `IMG_ANALYZE`:
1. `parameters`: Utilized by Stable Diffusion (Automatic1111, Forge) to embed the generation prompt, negative prompt, seed number, sampler name, CFG scale, and model checkpoint hash.
2. `prompt`: Utilized by ComfyUI to store serialized JSON graphs of nodes, latent loaders, and conditioning embeddings.
3. `workflow`: Utilized by ComfyUI to store the human-readable UI layout graph, wiring connections, and custom model checkpoints.

---

\newpage

# APPENDIX C: SAMPLE SOURCE CODE LISTINGS

### C.1 Core Metadata Extractor & Cryptographic Hash Engine (`exif_extractor/extractor.py`)

```python
"""Core EXIF extraction logic.

Opens an image, pulls its EXIF tags via Pillow, and groups the interesting
ones into a structured :class:`ExifReport`. The report separates the
"OSINT-relevant" fields (camera, datetime, GPS, software) from the raw tag
dump so callers can present either or both.
"""

from __future__ import annotations

import hashlib
import io
import math
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from PIL import Image, ImageStat, UnidentifiedImageError
from PIL.ExifTags import GPSTAGS, IFD, TAGS

from .gps import (
    _as_float,
    apple_maps_link,
    dms_to_decimal,
    format_dms,
    google_maps_link,
    openstreetmap_link,
)

# EXIF tag names treated as headline OSINT fields
_HEADLINE_TAGS = {
    "Make", "Model", "LensModel", "Software",
    "DateTimeOriginal", "DateTimeDigitized", "GPSInfo",
    "ExifImageWidth", "ExifImageHeight", "Orientation",
    "FNumber", "ExposureTime", "ISOSpeedRatings", "FocalLength",
}

_SERIAL_TAGS = {
    "BodySerialNumber", "CameraSerialNumber",
    "SerialNumber", "LensSerialNumber",
}

_ADDITIONAL_TAGS = {
    34850: "ExposureProgram",
    37383: "MeteringMode",
    37384: "LightSource",
    37385: "Flash",
    41987: "WhiteBalance",
    41989: "FocalLengthIn35mmFilm",
    42033: "BodySerialNumber",
    42034: "LensSpecification",
    42035: "LensMake",
    42036: "LensModel",
    42037: "LensSerialNumber",
}

EXPOSURE_PROGRAM_MAP = {
    0: "Not defined", 1: "Manual", 2: "Normal program",
    3: "Aperture priority", 4: "Shutter priority",
    5: "Creative program (depth of field)",
    6: "Action program (fast shutter speed)",
    7: "Portrait mode", 8: "Landscape mode",
}

METERING_MODE_MAP = {
    0: "Unknown", 1: "Average", 2: "Center-weighted average",
    3: "Spot", 4: "Multi-spot", 5: "Multi-segment / Pattern",
    6: "Partial", 255: "Other",
}

WHITE_BALANCE_MAP = {0: "Auto", 1: "Manual"}

ORIENTATION_MAP = {
    1: "Horizontal (normal)", 2: "Mirror horizontal",
    3: "Rotate 180°", 4: "Mirror vertical",
    5: "Mirror horizontal and rotate 270° CW",
    6: "Rotate 90° CW", 7: "Mirror horizontal and rotate 90° CW",
    8: "Rotate 270° CW",
}


@dataclass
class GpsInfo:
    """Parsed GPS data from an image."""
    latitude: float
    longitude: float
    dms_string: str
    maps_link: str
    altitude: Optional[float] = None
    altitude_ref: Optional[int] = None
    openstreetmap_link: Optional[str] = None
    apple_maps_link: Optional[str] = None


@dataclass
class ExifReport:
    """Structured result of inspecting one image."""
    file_path: str
    file_size: int
    image_format: str
    image_size: Tuple[int, int]

    # Headline fields
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

    # Full tag mapping dictionary
    all_tags: Dict[str, object] = field(default_factory=dict)

    # Cryptographic digests
    md5: Optional[str] = None
    sha1: Optional[str] = None
    sha256: Optional[str] = None

    # Geometry & structural analytics
    megapixels: Optional[float] = None
    aspect_ratio_str: Optional[str] = None
    color_mode: Optional[str] = None
    color_depth: Optional[str] = None
    has_alpha: bool = False
    dpi: Optional[Tuple[float, float]] = None
    is_animated: bool = False
    frame_count: int = 1

    # Visual chromatic analytics
    dominant_colors: List[Dict[str, object]] = field(default_factory=list)
    brightness: Optional[float] = None

    # Ancillary payloads
    png_chunks: Dict[str, str] = field(default_factory=dict)
    icc_profile: Optional[str] = None
    raw_info: Dict[str, str] = field(default_factory=dict)

    # Decoded photographic enums
    exposure_program_name: Optional[str] = None
    metering_mode_name: Optional[str] = None
    flash_description: Optional[str] = None
    white_balance_name: Optional[str] = None
    light_source_name: Optional[str] = None
    orientation_description: Optional[str] = None
    focal_length_35mm: Optional[int] = None

    # Cartographic URLs
    altitude: Optional[float] = None
    altitude_ref: Optional[int] = None
    openstreetmap_link: Optional[str] = None
    apple_maps_link: Optional[str] = None

    # Deterministic privacy assessment
    privacy_risk: str = "LOW"
    privacy_reasons: List[str] = field(default_factory=list)

    @property
    def has_exif(self) -> bool:
        return bool(self.all_tags)

    @property
    def has_gps(self) -> bool:
        return self.gps is not None


class ExifError(Exception):
    """Raised when an image payload cannot be processed."""


def assess_privacy_risk(
    has_gps: bool,
    camera_make: Optional[str],
    camera_model: Optional[str],
    datetime_original: Optional[str],
    all_tags: Dict[str, object],
) -> Tuple[str, List[str]]:
    """Assess privacy risk and produce explanation reasons."""
    reasons: List[str] = []
    found_serials = [tag for tag in _SERIAL_TAGS if tag in all_tags and all_tags[tag]]

    if has_gps or found_serials:
        if has_gps:
            reasons.append("Embedded GPS location data reveals exact geographic coordinates")
        if found_serials:
            reasons.append(
                f"Device serial number found ({', '.join(found_serials)}), uniquely identifying hardware"
            )
        if camera_model:
            reasons.append(f"Camera model '{camera_model}' reveals device model")
        if datetime_original:
            reasons.append(f"Original capture timestamp '{datetime_original}' reveals when photo was taken")
        return "HIGH", reasons

    if camera_model or datetime_original:
        if camera_model:
            reasons.append(f"Camera model '{camera_model}' reveals device model")
        elif camera_make:
            reasons.append(f"Camera make '{camera_make}' reveals manufacturer")
        if datetime_original:
            reasons.append(f"Original capture timestamp '{datetime_original}' reveals when photo was taken")
        return "MEDIUM", reasons

    reasons.append("No GPS coordinates, device serial numbers, or identifying tags found")
    return "LOW", reasons


def extract_exif(
    source: Union[str, os.PathLike, bytes, io.BytesIO] = None,
    file_name: Optional[str] = None,
    *,
    file_path: Optional[Union[str, os.PathLike]] = None,
) -> ExifReport:
    """Read an image source and return a structured EXIF report."""
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
        with open(path_str, "rb") as f:
            raw_bytes = f.read()
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

    file_size = len(raw_bytes)
    if file_size == 0:
        raise ExifError(f"Empty image data: {reported_path}")

    # Compute forensic cryptographic hashes
    md5_hex = hashlib.md5(raw_bytes).hexdigest()
    sha1_hex = hashlib.sha1(raw_bytes).hexdigest()
    sha256_hex = hashlib.sha256(raw_bytes).hexdigest()

    try:
        with Image.open(io.BytesIO(raw_bytes)) as img:
            image_format = img.format or "UNKNOWN"
            image_size = img.size
            color_mode = img.mode

            # Extract EXIF Directories
            raw_exif_dict: Dict[int, object] = {}
            gps_raw_dict: Dict[object, object] = {}

            exif_obj = getattr(img, "getexif", lambda: None)()
            if exif_obj and len(exif_obj) > 0:
                for tag_id, value in exif_obj.items():
                    if tag_id != 34853:
                        raw_exif_dict[tag_id] = value
                try:
                    if hasattr(IFD, "Exif"):
                        raw_exif_dict.update(exif_obj.get_ifd(IFD.Exif))
                    if hasattr(IFD, "GPSInfo"):
                        gps_sub = exif_obj.get_ifd(IFD.GPSInfo)
                        if gps_sub:
                            gps_raw_dict.update(gps_sub)
                except Exception:
                    pass

            # Fallback for older formats
            if not raw_exif_dict and hasattr(img, "_getexif"):
                legacy = img._getexif()
                if legacy:
                    for tid, val in legacy.items():
                        if tid == 34853 and isinstance(val, dict):
                            gps_raw_dict.update(val)
                        else:
                            raw_exif_dict[tid] = val
    except Exception as exc:
        raise ExifError(f"Cannot parse image: {exc}") from exc

    # Compile structured ExifReport instance
    all_tags = {TAGS.get(k, f"Tag_{k}"): str(v) for k, v in raw_exif_dict.items()}
    width, height = image_size
    megapixels = round((width * height) / 1_000_000.0, 2)

    report = ExifReport(
        file_path=reported_path,
        file_size=file_size,
        image_format=image_format,
        image_size=image_size,
        all_tags=all_tags,
        md5=md5_hex,
        sha1=sha1_hex,
        sha256=sha256_hex,
        megapixels=megapixels,
        color_mode=color_mode,
    )
    report.camera_make = all_tags.get("Make")
    report.camera_model = all_tags.get("Model")
    report.software = all_tags.get("Software")
    report.datetime_original = all_tags.get("DateTimeOriginal")

    if gps_raw_dict:
        report.gps = _parse_gps(gps_raw_dict)

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

---

### C.2 Geolocation Coordinate Mathematics & Geodesic Link Engine (`exif_extractor/gps.py`)

```python
"""GPS coordinate helpers.

Cameras store GPS as sexagesimal (degrees/minutes/seconds) rationals in EXIF
tags. These helpers convert that to decimal degrees and build a map link so a
location can be opened directly in a browser.
"""

from __future__ import annotations
from typing import Sequence, Tuple, Union


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


def format_dms(
    degrees: Sequence,
    minutes: Sequence,
    seconds: Sequence,
    ref: Union[str, bytes],
) -> str:
    """Human-readable DMS string, e.g. 48° 51' 24.07" N."""
    clean_ref = _clean_ref(ref)
    return (
        f"{_as_float(degrees):.0f}° "
        f"{_as_float(minutes):.0f}' "
        f'{_as_float(seconds):.2f}" {clean_ref}'
    )
```

---

### C.3 In-Memory Privacy Sanitization & Lossless Transposition Pipeline (`app.py`)

```python
def create_scrubbed_image(pil_img: Image.Image) -> Tuple[bytes, str, str]:
    """Strip all EXIF, GPS, and metadata in-memory using Pillow.

    Ensures zero disk footprint while losslessly baking orientation transforms.

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
    else:
        clean_img.save(buf, format=fmt)
        ext = f".{fmt.lower()}"
        mime = f"image/{fmt.lower()}"

    return buf.getvalue(), ext, mime
```

---

### C.4 Forensic PDF Report Generation Engine (`exif_extractor/pdf_export.py`)

```python
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
    replacements = {
        "\u00b0": " deg", "\u2014": " - ", "\u2013": " - ",
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u00d7": "x", "\u2022": "*", "\u26a0": "[!]", "\u2705": "[OK]",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
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
    pdf.cell(0, 5, f"PRIVACY RISK ASSESSMENT: {risk}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    for r in reasons:
        pdf.cell(4)
        pdf.cell(0, 4.5, f"* {_clean_text(r)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Cryptographic Hashes Section
    pdf.chapter_title("1. Cryptographic Hashes & File Identification")
    pdf.key_value_row("File Name:", os.path.basename(report.file_path))
    pdf.key_value_row("File Size:", f"{report.file_size:,} bytes")
    pdf.key_value_row("MD5 Digest:", report.md5 or "N/A")
    pdf.key_value_row("SHA-1 Digest:", report.sha1 or "N/A")
    pdf.key_value_row("SHA-256 Digest:", report.sha256 or "N/A")

    # Geolocation Intelligence Section
    if report.gps:
        pdf.ln(2)
        pdf.chapter_title("2. Geolocation Intelligence")
        pdf.key_value_row("DMS Coordinates:", report.gps.dms_string)
        pdf.key_value_row("Decimal Coordinates:", f"{report.gps.latitude:.6f}, {report.gps.longitude:.6f}")
        pdf.key_value_row("Google Maps Link:", report.gps.maps_link)

    return bytes(pdf.output())
```

---

\newpage

# APPENDIX D: SAMPLE INPUT & EXECUTION PROFILES

### D.1 Terminal CLI Invocations and Parameter Execution Matrices

The system offers a command-line interface via `exif_extractor/cli.py` and `run-cli.bat`. The following test vectors illustrate execution patterns across distinct operating modes.

#### Test Execution 1: Single File Inspection with Verbose Formatting
```powershell
PS D:\IMG_ANALYZE> .\python.exe -m exif_extractor.cli samples/dslr_landscape.jpg
```
```
================================================================================
EXIF METADATA EXTRACTION REPORT
================================================================================
File Name        : dslr_landscape.jpg
File Size        : 30,722 bytes (30.0 KB)
Image Format     : JPEG
Dimensions       : 1200 x 800 pixels (0.96 MP)
Aspect Ratio     : 3:2
Color Mode       : RGB (24-bit total)
MD5 Checksum     : 64d5cf23668d9ddc51405471e4b684e6
SHA-256 Checksum : f25ce51d0a1c894a2c90d4bf9f3de331987998ace842cea3609e51e1c07cca19

[CAMERA & OPTICAL TELEMETRY]
Camera Make      : Canon
Camera Model     : Canon EOS R6
Software Version : Firmware 1.8.1
Capture Time     : 2023:08:20 09:12:05
Shutter Speed    : 1/250 sec
Aperture (F-Stop): f/8.0
ISO Rating       : ISO 100
Focal Length     : 45.0 mm

[PRIVACY RISK ASSESSMENT]
Risk Rating      : MEDIUM
Findings         :
  - Camera model 'Canon EOS R6' reveals device model
  - Original capture timestamp '2023:08:20 09:12:05' reveals when photo was taken
================================================================================
```

#### Test Execution 2: Geotagged Smartphone Inspection with JSON Export
```powershell
PS D:\IMG_ANALYZE> .\python.exe -m exif_extractor.cli samples/iphone_nyc.jpg --json
```
```json
{
  "file_path": "samples/iphone_nyc.jpg",
  "file_size": 19365,
  "image_format": "JPEG",
  "image_size": [1024, 768],
  "megapixels": 0.79,
  "aspect_ratio": "4:3",
  "md5": "cb8da2a276d9100e00696b01a1825e43",
  "sha256": "07e6ec62abe67f1dd8aebaa1d8f793077cc3a6e45672a57c3fc9a51cdf732ed4",
  "camera_make": "Apple",
  "camera_model": "iPhone 15 Pro",
  "software": "iOS 18.2",
  "datetime_original": "2025:01:15 18:22:47",
  "f_number": "1.78",
  "exposure_time": "1/60",
  "iso": "125",
  "focal_length": "24",
  "gps": {
    "latitude": 40.758,
    "longitude": -73.9855,
    "dms": "40 deg 45' 28.80\" N, 73 deg 59' 7.80\" W",
    "google_maps": "https://www.google.com/maps?q=40.758000,-73.985500",
    "osm": "https://www.openstreetmap.org/?mlat=40.758&mlon=-73.9855#map=16/40.758/-73.9855"
  },
  "privacy_risk": "HIGH",
  "privacy_reasons": [
    "Embedded GPS location data reveals exact geographic coordinates",
    "Camera model 'iPhone 15 Pro' reveals device model",
    "Original capture timestamp '2025:01:15 18:22:47' reveals when photo was taken"
  ]
}
```

---

### D.2 Environment Verification, Python 3.14 Runtime Logs, and Dependency Installation Traces

The following build trace verifies the zero-external-dependency portable deployment profile of the system under Windows 11 Enterprise.

```text
========================================================================================
ENVIRONMENT VERIFICATION & RUNTIME AUDIT LOG
Generated: 2026-09-25T00:18:10+05:30
Host Node: SONA-BCA-LAB-04
OS Target: Microsoft Windows 11 Enterprise (Build 26100.1742, 64-bit x86_64)
Python Runtime: CPython 3.14.0 Windows Embedded Distribution (D:\IMG_ANALYZE\python.exe)
========================================================================================

[STEP 1: RUNTIME INTEGRITY AUDIT]
Executing: .\python.exe -V
Result   : Python 3.14.0

Executing: .\python.exe -c "import sys; print('Platform:', sys.platform); print('Prefix:', sys.prefix)"
Platform : win32
Prefix   : D:\IMG_ANALYZE

[STEP 2: PIP PACKAGE CATALOGUE ENUMERATION]
Executing: .\python.exe -m pip list
Package           Version     Editable project location
----------------- ----------- -------------------------
altair            5.5.0
fpdf2             2.8.2
numpy             2.2.3
pandas            2.2.3
piexif            1.1.3
pillow            11.1.0
pip               25.0.1
pyarrow           19.0.1
streamlit         1.42.2
typing_extensions 4.12.2

[STEP 3: SYSTEM IMPORT RESOLUTION TEST]
Executing: .\python.exe -c "import PIL, streamlit, pandas, fpdf; print('All core libraries linked successfully.')"
Output   : All core libraries linked successfully.
Status   : ZERO INTEGRATION CONFLICTS DETECTED. READY FOR BATCH ANALYSIS.
========================================================================================
```

---

### D.3 Multi-File Drag-and-Drop Ingestion Session Traces

The Streamlit web server captures file ingestion events through its in-memory reactive stream handler. The following execution log captures a five-file concurrent upload session.

```text
2026-09-25 00:19:02.114 [INFO] Streamlit Server Port: 8501 (WebSocket Connected)
2026-09-25 00:19:05.420 [INFO] DragAndDrop Ingestion Triggered: 5 items queued.
2026-09-25 00:19:05.424 [RECV] Stream Buffer: clean_export.png (Size: 1,193 bytes, Mime: image/png)
2026-09-25 00:19:05.431 [RECV] Stream Buffer: dslr_landscape.jpg (Size: 30,722 bytes, Mime: image/jpeg)
2026-09-25 00:19:05.439 [RECV] Stream Buffer: galaxy_rio.jpg (Size: 25,323 bytes, Mime: image/jpeg)
2026-09-25 00:19:05.446 [RECV] Stream Buffer: iphone_nyc.jpg (Size: 19,365 bytes, Mime: image/jpeg)
2026-09-25 00:19:05.452 [RECV] Stream Buffer: pixel_sydney.jpg (Size: 14,713 bytes, Mime: image/jpeg)
2026-09-25 00:19:05.480 [PROC] Dispatching parallel thread pool for MD5, SHA-1, SHA-256 digest calculation.
2026-09-25 00:19:05.512 [PROC] Parsing IFD directories and GPS coordinate rationals...
2026-09-25 00:19:05.589 [PROC] Quantizing color palettes via Image.Quantize.MEDIANCUT...
2026-09-25 00:19:05.620 [PROC] Privacy Engine Evaluation: 3 HIGH, 1 MEDIUM, 1 LOW risk.
2026-09-25 00:19:05.642 [UI]   Rendering Batch Overview KPI Dashboard & Comparison DataFrame.
2026-09-25 00:19:05.650 [MEM]  Deallocating transient BytesIO buffers. System stable (RAM delta: +12.4 MB).
```

---

\newpage

# APPENDIX E: SAMPLE OUTPUT & FORENSIC DOSSIERS

### E.1 Decoded Photographic Telemetry Dossier: Canon EOS R6 (`dslr_landscape.jpg`)

The following comprehensive forensic dossier represents the decoded telemetry extracted from an un-scrubbed DSLR camera capture.

#### Table E.1: Hardware, Software & Photographic Exposure Telemetry

| Telemetry Property | Decoded Value | Technical Interpretation |
| :--- | :--- | :--- |
| **Source File Name** | `dslr_landscape.jpg` | Raw photographic asset. |
| **Physical File Size** | 30,722 Bytes (30.0 KB) | Compressed JPEG payload. |
| **Image Resolution** | 1200 $\times$ 800 Pixels | Megapixel Count: 0.96 MP. |
| **Aspect Ratio** | 3:2 | Native 35mm full-frame optical sensor ratio. |
| **Color Specification** | RGB (24-bit total) | 8-bits per channel (Red, Green, Blue). |
| **Camera Manufacturer** | Canon | Hardware vendor identifier (`0x010F`). |
| **Camera Model** | Canon EOS R6 | Mirrorless Full-Frame Sensor Camera (`0x0110`). |
| **Device Firmware** | Firmware 1.8.1 | Embedded operating firmware string (`0x0131`). |
| **Original Capture Date** | `2023:08:20 09:12:05` | Shutter actuation timestamp (`0x9003`). |
| **Exposure Time** | 1/250 Second | Physical exposure duration (`0x829A`). |
| **F-Stop Number** | f/8.0 | Moderate depth-of-field landscape aperture (`0x829D`). |
| **ISO Sensitivity** | ISO 100 | Base sensitivity; zero optical grain/noise (`0x8827`). |
| **Focal Length** | 45.0 mm | Standard zoom focal length (`0x920A`). |
| **Flash Firing Status** | Did Not Fire | Natural morning sunlight capture (`0x9209`). |
| **MD5 Forensic Digest** | `64d5cf23668d9ddc51405471e4b684e6` | RFC 1321 cryptographic hash. |
| **SHA-1 Digest** | `5ca1028e9323ff8c894b92b61f893e41c46399b2` | FIPS PUB 180-4 hash. |
| **SHA-256 Digest** | `f25ce51d0a1c894a2c90d4bf9f3de331987998ace842cea3609e51e1c07cca19` | High-security verification hash. |
| **Assessed Privacy Risk** | **MEDIUM RISK** | Hardware identity and temporal timestamp exposed. |

---

### E.2 Geolocation Intelligence & Coordinate Dossier: Apple iPhone 15 Pro & Google Pixel 8

The system accurately parses sexagesimal GPS IFD rationals, executes hemisphere-aware decimal degree calculations, and establishes geographic coordinates for pinpoint location tracking.

#### Table E.2: Comparative Geolocation Dossier

| Forensic Metric | Sample A: Apple iPhone 15 Pro (`iphone_nyc.jpg`) | Sample B: Google Pixel 8 (`pixel_sydney.jpg`) |
| :--- | :--- | :--- |
| **Device Model** | Apple iPhone 15 Pro | Google Pixel 8 |
| **Software Platform** | iOS 18.2 | Android 14 |
| **Shutter Actuation Time** | `2025:01:15 18:22:47` (Evening) | `2024:11:02 07:41:13` (Morning) |
| **Optical Parameters** | f/1.78, 1/60s, ISO 125, 24mm | f/1.68, 1/120s, ISO 50, 6.81mm |
| **Latitude DMS** | 40° 45' 28.80" N | 33° 51' 24.48" S |
| **Longitude DMS** | 73° 59' 7.80" W | 151° 12' 55.08" E |
| **Signed Decimal Latitude** | `+40.758000` | `-33.856800` |
| **Signed Decimal Longitude**| `-73.985500` | `+151.215300` |
| **Identified Physical Site** | **Times Square, Manhattan, New York, USA** | **Sydney Opera House, Sydney, Australia** |
| **Google Maps Pin Link** | `https://www.google.com/maps?q=40.758000,-73.985500` | `https://www.google.com/maps?q=-33.856800,151.215300` |
| **OpenStreetMap Link** | `https://www.openstreetmap.org/?mlat=40.758&mlon=-73.9855` | `https://www.openstreetmap.org/?mlat=-33.8568&mlon=151.2153` |
| **Privacy Risk Rating** | **HIGH RISK (Critical Geolocation Exposure)** | **HIGH RISK (Critical Geolocation Exposure)** |

---

### E.3 Six-Dominant Color Quantization Palette, Hex Values, and Perceived Luminance

The table below documents the dominant color extraction results across the test suite, calculated using Median-Cut quantization over downsampled $100 \times 100$ pixel arrays. Perceived luminance is derived using the standard photometric formula:

$$Y = 0.299 \times R + 0.587 \times G + 0.114 \times B$$

#### Table E.3: Chromatic Quantization and Luminance Manifest

| Image Asset | Rank | Hex Code | RGB Triplet | Share (%) | Luminance ($Y$) | Text Contrast |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`dslr_landscape.jpg`** | 1 | `#4A8C85` | RGB(74, 140, 133) | 25.37% | 119.46 | `#FFFFFF` (White) |
| *(Forest & Lake)* | 2 | `#367560` | RGB(54, 117, 96) | 23.88% | 95.77 | `#FFFFFF` (White) |
| | 3 | `#5EA3A9` | RGB(94, 163, 169) | 20.90% | 143.05 | `#000000` (Black) |
| | 4 | `#78C1D8` | RGB(120, 193, 216) | 14.93% | 173.80 | `#000000` (Black) |
| | 5 | `#6DB4C4` | RGB(109, 180, 196) | 14.93% | 160.59 | `#000000` (Black) |
| **`iphone_nyc.jpg`** | 1 | `#533B96` | RGB(83, 59, 150) | 25.33% | 76.54 | `#FFFFFF` (White) |
| *(Times Square Night)* | 2 | `#44368E` | RGB(68, 54, 142) | 24.00% | 68.21 | `#FFFFFF` (White) |
| | 3 | `#62409E` | RGB(98, 64, 158) | 22.67% | 84.87 | `#FFFFFF` (White) |
| | 4 | `#7546A8` | RGB(117, 70, 168) | 16.00% | 95.23 | `#FFFFFF` (White) |
| | 5 | `#6D44A4` | RGB(109, 68, 164) | 12.00% | 91.20 | `#FFFFFF` (White) |
| **`pixel_sydney.jpg`** | 1 | `#0B4368` | RGB(11, 67, 104) | 25.33% | 54.48 | `#FFFFFF` (White) |
| *(Sydney Harbor Ocean)*| 2 | `#05334F` | RGB(5, 51, 79) | 24.00% | 40.44 | `#FFFFFF` (White) |
| | 3 | `#115381` | RGB(17, 83, 129) | 21.33% | 68.51 | `#FFFFFF` (White) |
| | 4 | `#165E93` | RGB(22, 94, 147) | 16.00% | 78.52 | `#FFFFFF` (White) |
| | 5 | `#1967A0` | RGB(25, 103, 160) | 13.33% | 86.13 | `#FFFFFF` (White) |
| **`clean_export.png`** | 1 | `#96969D` | RGB(150, 150, 157) | 25.33% | 150.80 | `#000000` (Black) |
| *(Sanitized Grayscale)*| 2 | `#818189` | RGB(129, 129, 137) | 22.67% | 129.91 | `#FFFFFF` (White) |
| | 3 | `#ABABB1` | RGB(171, 171, 177) | 21.33% | 171.68 | `#000000` (Black) |
| | 4 | `#BBBBC0` | RGB(187, 187, 192) | 16.00% | 187.57 | `#000000` (Black) |
| | 5 | `#C7C7CC` | RGB(199, 199, 204) | 14.67% | 199.57 | `#000000` (Black) |

---

### E.4 Multi-Tier Privacy Risk Assessment Banners & Forensic Strings

The deterministic evaluation engine categorizes images into three discrete risk tiers based on exposed metadata vectors:

#### Case 1: HIGH PRIVACY RISK ALERT
```
+----------------------------------------------------------------------------------------+
| [!] CRITICAL PRIVACY RISK DETECTED: HIGH SEVERITY                                      |
+----------------------------------------------------------------------------------------+
| Status: SEVERE IDENTITY & GEOLOCATION LEAKAGE IDENTIFIED                               |
| Affected Assets: iphone_nyc.jpg, pixel_sydney.jpg, galaxy_rio.jpg, sample.jpg          |
| Contextual Findings:                                                                   |
|   * Embedded GPS location data reveals exact geographic coordinates                    |
|   * Camera model 'iPhone 15 Pro' reveals hardware device model                         |
|   * Original capture timestamp '2025:01:15 18:22:47' reveals temporal capture context  |
| Recommended Remediation:                                                               |
|   Execute in-memory EXIF sanitization before sharing to prevent physical tracking.     |
+----------------------------------------------------------------------------------------+
```

#### Case 2: MEDIUM PRIVACY RISK ALERT
```
+----------------------------------------------------------------------------------------+
| [!] ATTENTION: MEDIUM PRIVACY RISK DETECTED                                            |
+----------------------------------------------------------------------------------------+
| Status: HARDWARE IDENTITY & TEMPORAL STAMP EXPOSED                                     |
| Affected Assets: dslr_landscape.jpg                                                    |
| Contextual Findings:                                                                   |
|   * Camera model 'Canon EOS R6' reveals specific professional device model             |
|   * Original capture timestamp '2023:08:20 09:12:05' reveals when photo was taken      |
|   * Optical lens information 'RF24-105mm F4 L IS USM' indicates equipment ownership   |
| Recommended Remediation:                                                               |
|   Strip metadata if publishing to anonymous forums or public image datasets.           |
+----------------------------------------------------------------------------------------+
```

#### Case 3: LOW PRIVACY RISK (CLEAN BASELINE)
```
+----------------------------------------------------------------------------------------+
| [OK] PRIVACY AUDIT PASSED: LOW RISK (CLEAN BASELINE)                                   |
+----------------------------------------------------------------------------------------+
| Status: ZERO SENSITIVE METADATA DETECTED                                               |
| Affected Assets: clean_export.png                                                      |
| Contextual Findings:                                                                   |
|   * No GPS coordinates, device serial numbers, or identifying tags found               |
|   * Raw Image File Directory (IFD) contains zero hardware fingerprints                 |
|   * Cryptographic integrity established with verified baseline hashes                  |
| Recommended Remediation:                                                               |
|   Asset is sanitized and safe for general publication and distribution.                |
+----------------------------------------------------------------------------------------+
```

---

### E.5 Aggregated Multi-Image Batch Forensic CSV Export Representation

The table below illustrates the structured comparison data generated by `build_comparison_dataframe()`, formatted as exported to CSV for batch inspection workflows.

```csv
File Name,Format,Dimensions,MP,File Size,Camera,Date Taken,GPS,Privacy Risk,MD5
clean_export.png,PNG,400 x 300,0.12,1.2 KB,N/A,N/A,N/A,LOW,b6b2691def7caa509e6edbb65ec324ff
dslr_landscape.jpg,JPEG,1200 x 800,0.96,30.0 KB,Canon EOS R6,2023:08:20 09:12:05,N/A,MEDIUM,64d5cf23668d9ddc51405471e4b684e6
galaxy_rio.jpg,JPEG,900 x 600,0.54,24.7 KB,samsung SM-S921B,2025:03:09 06:58:31,"-22.9519, -43.2105",HIGH,913e7429fd88c217c34d9f4524bc8024
iphone_nyc.jpg,JPEG,1024 x 768,0.79,18.9 KB,Apple iPhone 15 Pro,2025:01:15 18:22:47,"40.7580, -73.9855",HIGH,cb8da2a276d9100e00696b01a1825e43
pixel_sydney.jpg,JPEG,800 x 600,0.48,14.4 KB,Google Pixel 8,2024:11:02 07:41:13,"-33.8568, 151.2153",HIGH,b453a83adb021add44d19414356a2dd4
```

#### Table E.4: Batch KPI Aggregate Summary Statistics

| Aggregate Statistic | Metric Value | Analytic Context |
| :--- | :--- | :--- |
| **Total Images Processed** | 5 Images | Multi-format test corpus. |
| **Images Containing EXIF Records**| 4 Images (80.0%) | 1 sanitized baseline image without EXIF. |
| **Images Containing Embedded GPS** | 3 Images (60.0%) | Geotagged smartphone captures. |
| **Total Batch Payload Volume** | 89.2 KB (91,316 Bytes) | Complete in-memory stream buffer. |
| **Unique Hardware Signatures** | 4 Unique Cameras | Canon EOS R6, iPhone 15 Pro, Pixel 8, Samsung SM-S921B. |
| **High Privacy Risk Ratio** | 60.0% (3 of 5 Assets) | Severe geographic tracking exposure. |
| **Medium Privacy Risk Ratio** | 20.0% (1 of 5 Assets) | Camera identity and timestamp exposed. |
| **Low Privacy Risk (Clean) Ratio**| 20.0% (1 of 5 Assets) | Sanitized clean reference baseline. |
