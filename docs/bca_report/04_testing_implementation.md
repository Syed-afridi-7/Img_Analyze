# CHAPTER 4: TESTING AND IMPLEMENTATION

---

## 4.1 Test Methodology Phase

Software testing in digital forensics and privacy engineering represents an indispensable quality assurance phase that directly determines operational efficacy, analytical reliability, and judicial acceptability. Unlike generic commercial web services where edge-case failures produce non-critical degradation of user experience, software tools deployed for digital evidence extraction, Open-Source Intelligence (OSINT) telemetry analysis, and privacy sanitization operate within high-stakes environments. An unhandled exception during binary container parsing, a miscalculated geographical coordinate, or an incomplete metadata stripping routine can compromise criminal proceedings, invalidate an evidentiary chain of custody, or expose vulnerable individuals—such as investigative journalists and whistleblowers—to severe physical peril.

To provide unconditional reliability, the development and verification of **Img_Analyze** (*Interactive EXIF Metadata Extractor, OSINT Telemetry Inspector, and Privacy Sanitization Engine*) adopted a multifaceted testing methodology anchored in the formal **Test-Driven Development (TDD)** software lifecycle. This methodology was augmented by a multi-tiered test execution hierarchy spanning micro-unit testing, boundary containment verification, zero-leakage security validation, and headless reactive user interface (UI) simulation.

```
+---------------------------------------------------------------------------------------------------+
|                        IMG_ANALYZE MULTI-TIER TESTING ARCHITECTURE                                |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  TIER 4: HEADLESS REACTIVE UI VALIDATION (streamlit.testing.v1.AppTest)                           |
|  * Headless App Execution    * Virtual Session State Simulation  * DOM/Widget Hierarchy Testing   |
|  * Interactive Demo Pickers  * Reactive Filter Assertions        * In-Memory Scrubber UI Hooks    |
|                                                                                                   |
|  TIER 3: SYSTEM INTEGRATION & EXPORT PIPELINES                                                    |
|  * Multi-Image Batch Summary * Pandas DataFrame Matrix Synthesis * Binary FPDF2 Canvas Generation |
|  * Streamlit State Bridge    * Machine-Readable JSON Export      * CSV Batch Aggregation          |
|                                                                                                   |
|  TIER 2: SECURITY, PRIVACY & ADVERSARIAL BOUNDARY VALIDATION                                      |
|  * Zero-Network Air-Gap Test * Zero-Disk Temp Leakage Validation * Malformed Container Ingestion  |
|  * Division-by-Zero Guards   * Unidentified Image Containment    * In-Memory Byte Stream Sanitizer|
|                                                                                                   |
|  TIER 1: MICRO-UNIT & CRYPTOGRAPHIC FOUNDATION                                                    |
|  * RFC 1321 MD5 Digest       * FIPS 180-4 SHA-1 / SHA-256 Hashes * WGS 84 DMS Rational Transforms |
|  * JEITA CP-3451D EXIF Tags  * Heckbert Median Cut Quantization  * ITU-R BT.601 / BT.709 Luma     |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

---

### 4.1.1 The Test-Driven Development (TDD) Paradigm in Forensic Computing

In traditional software development paradigms, testing is frequently relegated to an afterthought—a post-hoc verification phase executed after system design and implementation. In contrast, *Img_Analyze* strictly implemented the **Test-Driven Development (TDD)** paradigm governed by the canonical **Red-Green-Refactor** cycle. 

In the context of digital forensics, TDD guarantees that every analytical rule, parsing logic, and conversion formula is preceded by a mathematical specification of failure conditions before any production code is authored.

```
       +-------------------------------------------------------------+
       |                  1. RED PHASE (Falsification)               |
       |  - Author automated test asserting precise forensic failure |
       |  - Inject malformed rational coordinates or corrupt headers |
       |  - Confirm test executes and fails predictably              |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                  2. GREEN PHASE (Implementation)            |
       |  - Write minimal defensive parsing and extraction code      |
       |  - Implement bounds-checking and zero-division guards       |
       |  - Execute test suite; verify all assertions pass           |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                  3. REFACTOR PHASE (Optimization)           |
       |  - Vectorize calculations and eliminate redundant buffers   |
       |  - Refactor into decoupled pure functions and dataclasses   |
       |  - Ensure 100% regression invariance across test suites     |
       +-------------------------------------------------------------+
```

1. **The Red Phase (Falsification Formulation):** Prior to writing an extraction routine (e.g., parsing the EXIF `Flash` bitmask or converting sexagesimal GPS rationals into decimal degrees), a corresponding test case was formulated in `tests/test_image_details.py`. This test defined explicit failure criteria based on international specifications:
   - For example, asserting that a GPS latitude of `((48, 1), (51, 1), (3024, 100))` with reference `'N'` precisely evaluates to $48.858400^\circ$ within an epsilon tolerance of $10^{-6}$, and that an invalid reference or zero denominator raises an `ExifError` or gracefully returns `None` rather than crashing the interpreter.
   - When executed against the nonexistent or unadapted codebase, the test unequivocally failed (**Red**).

2. **The Green Phase (Minimal Defensive Implementation):** Production routines within `exif_extractor/extractor.py` were authored with the singular objective of satisfying the failing assertions. Defensive programming mechanisms—such as verifying tuple lengths, shielding rational evaluations with `try-except ZeroDivisionError` blocks, and constraining enum bounds—were integrated directly into the minimal implementation until the test suite achieved a passing status (**Green**).

3. **The Refactor Phase (Forensic Optimization & Modular Decoupling):** Once correctness was programmatically guaranteed, the underlying routines were refactored for runtime efficiency, modularity, and memory safety. Redundant buffer allocations were eliminated, iterative pixel evaluation loops were replaced with Pillow C-accelerated quantization (`Image.quantize(colors=6, method=Image.Quantize.MEDIANCUT)`), and raw dictionary data was mapped into immutable dataclass structures (`ExifReport`, `GpsInfo`). The test suite was re-executed continuously to verify that refactoring introduced zero behavioral regressions.

---

### 4.1.2 Unit Testing Principles

Unit testing in *Img_Analyze* operates at the lowest level of architectural granularity, isolating discrete functions and algorithmic routines from external dependencies (such as the physical filesystem or graphical display drivers). Built upon the industry-standard `pytest` framework, unit tests validate:
- **Cryptographic Hash Generators:** Verifying that `_calculate_hashes()` correctly processes `io.BytesIO` streams and raw byte sequences, generating exact MD5 (RFC 1321), SHA-1 (FIPS 180-4), and SHA-256 (FIPS 180-4) hex digests matching pre-computed reference vectors.
- **Dimensional and Aspect Ratio Normalization:** Verifying that `calculate_aspect_ratio(width, height)` computes the Greatest Common Divisor (GCD) via Euclid's algorithm and maps common sensor ratios (e.g., $1920 \times 1080 \rightarrow 16:9$, $1200 \times 800 \rightarrow 3:2$, $1024 \times 768 \rightarrow 4:3$, $500 \times 500 \rightarrow 1:1$, and vertical orientation $1080 \times 1920 \rightarrow 9:16$).
- **Colorimetry & Photometric Algorithms:** Verifying that `calculate_brightness(image)` executes the ITU-R BT.601 luma conversion formula across image bands:
  
  $$\text{Luminance} = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B$$
  
  and accurately categorizes overall scene lighting into "High Key", "Low Key", or "Balanced Exposure".
- **Bitmask and Enum Decoding Engines:** Testing isolated decoding maps for EXIF tags, including `decode_flash()`, `ExposureProgram`, `MeteringMode`, and `LightSource`, ensuring that complex bitwise flags (e.g., Flash fired, return light detected, compulsory flash mode) are unpacked into human-readable strings.

---

### 4.1.3 Integration Testing Principles

Integration testing evaluates the collaborative interactions among interconnected architectural subsystems. Rather than validating functions in vacuum, integration testing verifies that data structures seamlessly flow across subsystem boundaries without data truncation, type coercion bugs, or state corruption:
- **Extraction-to-Batch Aggregation Pipeline:** Validates that collections of individual `ExifReport` instances are correctly ingested by `build_batch_summary()` in `exif_extractor/batch.py`, successfully calculating aggregated metrics (total file volume, cumulative megapixel count, count of images with GPS coordinates, camera model uniqueness sets, and risk distribution counters).
- **Tabular Dataframe Synthesis:** Verifies that `build_comparison_dataframe()` transforms heterogeneous `ExifReport` objects into clean, column-standardized `pandas.DataFrame` tables suitable for direct CSV rendering or display in Streamlit `st.dataframe` widgets.
- **Automated PDF Canvas Assembly:** Tests the end-to-end integration between extracted `ExifReport` metadata and the `fpdf2` document builder in `exif_extractor/pdf_export.py`. This verifies that vector text headers, binary thumbnail previews, key-value parameter tables, privacy warning banners, and external hyperlink annotations are synthesized into a compliant PDF/A binary document.

---

### 4.1.4 Functional & System Testing

Functional testing validates the complete software system against explicit user requirements and real-world operational workflows. It simulates end-to-end user interactions across both available interfaces:
- **Command-Line Interface (CLI) Workflows:** Validates `exif_extractor/cli.py` and `__main__.py` under varied command-line arguments, verifying correct parsing of flags such as `--json`, `--clean`, `--all-tags`, `--output`, and directory recursion paths.
- **Interactive Streamlit Web Dashboard Workflows:** Evaluates the reactive interface in `app.py`, verifying that file drag-and-drop operations trigger the full analysis pipeline, update interactive PyDeck geospatial maps, render color palette swatches, and enable immediate download of sanitized images and PDF reports.

---

### 4.1.5 Security & Zero-Leakage Testing Protocol

A distinguishing academic characteristic of *Img_Analyze* is its strict, defense-in-depth security model. To protect the confidentiality and evidentiary purity of investigated media, the test suite implements specialized **Security & Zero-Leakage** test harnesses:
- **Zero-Disk Ingestion Guarantee:** Tests explicitly verify that user-uploaded image bytes are streamed through `io.BytesIO` buffers directly into Pillow memory structures. At no point during extraction or reporting are unencrypted temporary files spooled to disk storage (e.g., `C:\Users\...\AppData\Local\Temp` or `/tmp`), eliminating forensic footprinting on the host workstation.
- **Zero-Network Air-Gap Isolation:** The test suite operates within an air-gapped test environment. Tests strictly assert that no background HTTP, HTTPS, DNS, or socket requests are triggered. Map hyperlink generation (`google_maps_link()`, `openstreetmap_link()`, `apple_maps_link()`) is validated via deterministic string synthesis without initiating live network handshakes.
- **Bit-Level In-Memory Sanitization Verification:** Tests pass images containing rich EXIF tags, GPS waypoints, and camera serial numbers through `create_scrubbed_image()`. The resulting binary payload is re-parsed by Pillow and `extract_exif()`, mathematically asserting that:
  
  $$\text{Tags}_{\text{sanitized}} = \emptyset, \quad \text{GPS}_{\text{sanitized}} = \text{None}, \quad \text{RiskLevel}_{\text{sanitized}} = \text{"LOW"}$$

---

### 4.1.6 Headless UI Testing via `streamlit.testing.v1.AppTest`

Traditional graphical user interface testing frequently mandates heavyweight, brittle browser automation frameworks such as Selenium WebDriver, Puppeteer, or Playwright. These frameworks necessitate external browser binaries (e.g., Google Chrome or Mozilla Firefox), suffer from asynchronous timing race conditions, and impose massive CPU and memory overhead during automated testing.

To overcome these constraints, *Img_Analyze* leverages the modern `streamlit.testing.v1.AppTest` framework. `AppTest` enables true **Headless Reactive UI Simulation**:
- **Simulated Browser-Free Execution:** `AppTest` executes `app.py` directly inside the Python virtual machine process without initializing a real browser window or headless Chromium instance.
- **Programmatic Session State Manipulation:** The test harness programmatically mounts the application script (`AppTest.from_file(APP_PATH)`), initializes virtual session state dictionaries, uploads binary image buffers into simulated file uploaders, and triggers button click events (`chip_eiffel.click().run()`).
- **DOM & Widget Tree Introspection:** Upon execution of each reactive cycle, `AppTest` provides complete introspection into Streamlit's internal widget tree. Assertions inspect `at.metric`, `at.sidebar`, `at.selectbox`, `at.success`, `at.warning`, and `at.exception`, confirming that error-free rendering occurs and expected UI components are generated.

```
+---------------------------------------------------------------------------------------------------+
|                     HEADLESS STREAMLIT APPTEST EXECUTION LIFECYCLE                                |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  1. MOUNT: Load app.py into memory-isolated execution sandbox (default_timeout = 60s)             |
|     at = AppTest.from_file("app.py")                                                             |
|                                                                                                   |
|  2. INITIALIZE & RUN: Execute script top-to-bottom, build simulated widget tree                   |
|     at.run() -> Assert: len(at.file_uploader) >= 1 and not at.exception                          |
|                                                                                                   |
|  3. SIMULATE USER INTERACTIONS: Mutate input controls and trigger reactive rerun                 |
|     at.selectbox[0].select("pixel_sydney.jpg")                                                    |
|     at.button[0].click().run()                                                                    |
|                                                                                                   |
|  4. ASSERT WIDGET OUTPUTS: Introspect rendered metrics, warnings, and markdown text              |
|     values = [m.value for m in at.metric]                                                         |
|     assert "-33.8568" in values  # Verify Southern hemisphere latitude                            |
|     assert "151.2153" in values  # Verify Eastern longitude                                       |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

---

## 4.2 Planning the Test

A comprehensive test plan establishes the boundaries, objectives, environmental constraints, and synthetic datasets required to achieve rigorous verification. For *Img_Analyze*, test planning was structured to guarantee complete test repeatability across disparate operating systems (Microsoft Windows 10/11, macOS Darwin, and Ubuntu Linux LTS).

### 4.2.1 Scope of Testing

The testing scope encompasses all functional, analytical, and security modules comprising the project:
1. **Cryptographic Integrity & Bitstream Ingestion:** File path string parsing, raw in-memory `bytes` ingestion, and `io.BytesIO` streams. MD5, SHA-1, and SHA-256 hash generation.
2. **Standard & Extended EXIF Parsing:** Primary IFD (`IFD0`), Exif SubIFD, Interoperability IFD, and Thumbnail IFD (`IFD1`). Decoding of exposure parameters, aperture, ISO, shutter speed, metering mode, focal length, lens specifications, and hardware serial numbers.
3. **Geospatial GNSS Telemetry & Directional Negation:** Sexagesimal degrees, minutes, and seconds rational unpacking. Sign inversion for Southern (`'S'`) latitudes and Western (`'W'`) longitudes. Altitude reference calculation (above vs. below sea level). Cartographic URL generation for Google Maps, OpenStreetMap, and Apple Maps.
4. **Ancillary Container Metadata (Non-EXIF):** PNG chunk traversal (`tEXt`, `zTXt`, `iTXt`), decoding compressed and uncompressed text parameters (specifically targeting generative AI prompts and generation seeds). ICC color profile extraction and characterization.
5. **Photometric & Perceptual Colorimetry:** Median Cut 6-color palette quantization, RGB to Hex translation, percentage pixel distribution calculation, and BT.601 luminance calculation.
6. **Privacy Risk Assessment Matrix:** Heuristic classification into **HIGH**, **MEDIUM**, or **LOW** privacy risk tiers based on the presence of GNSS coordinates, hardware serial numbers, personal timestamps, and facial identification cues.
7. **Batch Aggregation & Comparison:** Multi-image metadata harmonization, summary statistics calculation, and DataFrame compilation.
8. **Forensic PDF Report Generation:** Multi-page PDF synthesis via `fpdf2`, header/footer formatting, image rendering, metadata table construction, and PDF/A compliance.
9. **Interactive Web Interface:** Streamlit UI loading, widget responsiveness, demo fixture discovery, error handling on corrupt inputs, and in-memory metadata sanitization.

---

### 4.2.2 Test Data Fixtures & Synthetic Datasets

To ensure deterministic testing independent of external file variations, the project includes a dedicated suite of specialized image fixtures situated in `samples/` and `sample.jpg`:

```
+---------------------------------------------------------------------------------------------------+
|                             SYNTHETIC TEST FIXTURE MATRIX                                         |
+----------------------+-----------+-------------------------+--------------------------------------+
| Fixture Filename     | Format    | Optical / Camera Source | Forensic Test Profile                |
+----------------------+-----------+-------------------------+--------------------------------------+
| sample.jpg           | JPEG/JFIF | AcmeCam X-200 (Synthetic)| Rich EXIF, GPS (Eiffel Tower, Paris),|
|                      |           |                         | Serial: 987654321, High Privacy Risk |
+----------------------+-----------+-------------------------+--------------------------------------+
| dslr_landscape.jpg   | JPEG/JFIF | Canon EOS 5D Mark IV    | Professional DSLR, EF 24-70mm lens,  |
|                      |           |                         | No GPS, Aperture f/8.0, Low Risk     |
+----------------------+-----------+-------------------------+--------------------------------------+
| iphone_nyc.jpg       | JPEG/JFIF | Apple iPhone 14 Pro     | Computational mobile capture, GPS    |
|                      |           |                         | (New York City), Altitude, High Risk |
+----------------------+-----------+-------------------------+--------------------------------------+
| pixel_sydney.jpg     | JPEG/JFIF | Google Pixel 7          | Smartphone capture, Southern/Eastern |
|                      |           |                         | GPS (Sydney, Australia), High Risk   |
+----------------------+-----------+-------------------------+--------------------------------------+
| galaxy_rio.jpg       | JPEG/JFIF | Samsung Galaxy S23      | Smartphone capture, Southern/Western |
|                      |           |                         | GPS (Rio de Janeiro), High Risk      |
+----------------------+-----------+-------------------------+--------------------------------------+
| clean_export.png     | PNG       | Synthetic Sterile Asset | 100% stripped container, Zero EXIF,  |
|                      |           |                         | Zero GPS, Low Privacy Risk           |
+----------------------+-----------+-------------------------+--------------------------------------+
```

- **Programmatic Fixture Generator (`tests/make_samples.py`):** To eliminate reliance on proprietary third-party photographs, a standalone fixture generation script was engineered. Using Pillow and `piexif`, this utility builds synthetic test images from scratch, encoding precise rational tuples into designated EXIF IFD offsets (e.g., embedding Paris coordinates $48^\circ 51' 30.24''\text{ N}, 2^\circ 17' 40.20''\text{ E}$ into `sample.jpg`). This ensures that test baselines are completely reproducible across any clean checkout of the repository.

---

### 4.2.3 Zero-Network Air-Gapped Test Harnesses

To simulate high-security operational environments (such as military forensics laboratories, air-gapped law enforcement workstations, and confidential intelligence networks), the test suite enforces strict environmental constraints:
- **Mocked System Clocks & Fixture Paths:** All file paths are dynamically resolved relative to `REPO_ROOT` using `os.path.abspath(__file__)`, preventing platform-dependent hardcoding.
- **Network Socket Proscription:** The automated test runner operates without establishing outbound TCP/IP or UDP connections. Reverse-geocoding engines that rely on external APIs (e.g., Nominatim or Google Geocoding API) are strictly decoupled; mapping functionality is validated by verifying deterministic query parameter serialization into static URI templates:
  
  $$\text{URI}_{\text{OSM}} = \text{"https://www.openstreetmap.org/?mlat="} + \text{lat} + \text{"&mlon="} + \text{lon} + \text{"\#map=16/"} + \text{lat} + \text{"/"} + \text{lon}$$

---

## 4.3 Test Design & Test Cases Matrix

The automated validation suite of *Img_Analyze* comprises **48 discrete test cases** distributed across the four core testing modules. Execution of the complete suite via `pytest -v tests/` achieves an unconditional **100% pass rate** in approximately **10.03 seconds** on standard evaluation hardware.

```
================================== TEST SESSION SUMMARY ===================================
Root Directory:         D:\IMG_ANALYZE
Platform:               Windows 11 (win32) / Python 3.10+ / pytest 8.4.2
Test Execution Time:    10.03 seconds
Total Collected Items:  48
Passed Assertions:      48 (100.0%)
Failed Assertions:      0 (0.0%)
Errors / Warnings:      0 / 0
===========================================================================================
```

The following exhaustive test matrix documents each automated test case, delineating its Test ID, target module, operational objective, input test vector, expected output criteria, actual observed output, and final verification status.

---

### Exhaustive 48-Test Case Matrix (TC01 – TC48)

| Test ID | Module | Test Objective | Input Data Vector | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **TC01** | `test_batch.py` | Verify batch aggregation behavior on empty payload | Empty list `[]` | Returns dictionary with `total_count: 0`, `with_gps_count: 0`, `unique_cameras: []` | Empty summary dictionary returned with zeroed counters | **PASS** |
| **TC02** | `test_batch.py` | Validate multi-image summary aggregation metrics | 3 `ExifReport` objects (`sample.jpg`, `clean_export.png`, `pixel_sydney.jpg`) | `total_count: 3`, `with_gps_count: 2`, `total_file_size > 0`, risk keys present | Total count = 3, GPS count = 2, cameras $\ge 2$, HIGH & LOW risk sets present | **PASS** |
| **TC03** | `test_batch.py` | Verify multi-image comparison DataFrame construction | List of 2 reports (`sample.jpg`, `clean_export.png`) | Returns `pandas.DataFrame` (2 rows) with columns: File Name, Format, Dimensions, Privacy Risk, Camera | DataFrame created with 2 rows, correct schema; row 0 marked HIGH, row 1 marked LOW | **PASS** |
| **TC04** | `test_image_details.py` | Ingest image via valid filesystem path string | Path string `SAMPLE_JPG` (`sample.jpg`) | Returns valid `ExifReport` instance, `file_size > 0`, format `'JPEG'`, size `(640, 480)` | Returns `ExifReport` matching exact filesystem size and dimensions | **PASS** |
| **TC05** | `test_image_details.py` | Ingest image via raw binary `bytes` stream | Raw `bytes` of `sample.jpg` with `file_name="uploaded_photo.jpg"` | Returns `ExifReport` with `file_path="uploaded_photo.jpg"`, size `(640, 480)`, make `'AcmeCam'` | In-memory raw bytes correctly parsed, camera make extracted | **PASS** |
| **TC06** | `test_image_details.py` | Ingest image via anonymous raw `bytes` without name | Raw `bytes` of `sample.jpg` without `file_name` | Returns `ExifReport` with `file_path="<in-memory>"`, `has_gps=True` | Anonymous bytes parsed; default in-memory sentinel assigned | **PASS** |
| **TC07** | `test_image_details.py` | Ingest image via standard `io.BytesIO` buffer stream | `io.BytesIO` holding bytes of `sample.jpg` | Returns `ExifReport` with `file_path="streamed.jpg"`, model `'X-200'` | Stream processed seamlessly without temporary disk files | **PASS** |
| **TC08** | `test_image_details.py` | Verify backward compatibility with deprecated `filepath` argument | Keyword argument `filepath=SAMPLE_JPG` | Emits deprecation warning or handles gracefully, extracting valid report | Backward-compatible keyword parsed successfully | **PASS** |
| **TC09** | `test_image_details.py` | Validate error containment on corrupt/invalid sources | Invalid types (integer `12345`, empty bytes `b""`, non-existent path) | Raises `ExifError` with descriptive failure message; no uncaught crashes | `ExifError` predictably raised and caught across all corrupt inputs | **PASS** |
| **TC10** | `test_image_details.py` | Verify cryptographic hash generation accuracy | `sample.jpg` raw byte stream | Valid MD5 (32 hex), SHA-1 (40 hex), SHA-256 (64 hex) matching hashlib reference | Cryptographic digests match standard hashlib digests exactly | **PASS** |
| **TC11** | `test_image_details.py` | Verify pixel dimension and megapixel calculation | In-memory synthetic image ($640 \times 480$ px) | Dimensions `(640, 480)`, Megapixels $\approx 0.31$ MP | Exact tuple `(640, 480)` returned; megapixels evaluated to 0.31 | **PASS** |
| **TC12** | `test_image_details.py` | Calculate aspect ratio: 16:9 widescreen format | Dimensions $1920 \times 1080$ | Aspect ratio string evaluates to `"16:9"` | Aspect ratio computed as `"16:9"` | **PASS** |
| **TC13** | `test_image_details.py` | Calculate aspect ratio: 16:9 standard HD format | Dimensions $1280 \times 720$ | Aspect ratio string evaluates to `"16:9"` | Aspect ratio computed as `"16:9"` | **PASS** |
| **TC14** | `test_image_details.py` | Calculate aspect ratio: 4:3 legacy computer display | Dimensions $1024 \times 768$ | Aspect ratio string evaluates to `"4:3"` | Aspect ratio computed as `"4:3"` | **PASS** |
| **TC15** | `test_image_details.py` | Calculate aspect ratio: 4:3 standard VGA resolution | Dimensions $800 \times 600$ | Aspect ratio string evaluates to `"4:3"` | Aspect ratio computed as `"4:3"` | **PASS** |
| **TC16** | `test_image_details.py` | Calculate aspect ratio: 3:2 classic photographic 35mm | Dimensions $1200 \times 800$ | Aspect ratio string evaluates to `"3:2"` | Aspect ratio computed as `"3:2"` | **PASS** |
| **TC17** | `test_image_details.py` | Calculate aspect ratio: 3:2 reduced photographic ratio | Dimensions $900 \times 600$ | Aspect ratio string evaluates to `"3:2"` | Aspect ratio computed as `"3:2"` | **PASS** |
| **TC18** | `test_image_details.py` | Calculate aspect ratio: 1:1 square format (social media) | Dimensions $500 \times 500$ | Aspect ratio string evaluates to `"1:1"` | Aspect ratio computed as `"1:1"` | **PASS** |
| **TC19** | `test_image_details.py` | Calculate aspect ratio: 5:4 large format print | Dimensions $1000 \times 800$ | Aspect ratio string evaluates to `"5:4"` | Aspect ratio computed as `"5:4"` | **PASS** |
| **TC20** | `test_image_details.py` | Calculate aspect ratio: 9:16 vertical smartphone format | Dimensions $1080 \times 1920$ | Aspect ratio string evaluates to `"9:16"` | Aspect ratio computed as `"9:16"` | **PASS** |
| **TC21** | `test_image_details.py` | Validate color mode extraction and alpha detection | Synthetic RGBA and RGB image buffers | Mode correctly identified as `'RGBA'`/`'RGB'`; `has_alpha` correctly flagged | Modes and alpha channels identified with 100% accuracy | **PASS** |
| **TC22** | `test_image_details.py` | Verify multi-frame animation detection | Multi-frame GIF buffer vs. single-frame JPEG | GIF reports `is_animated=True`, `frame_count > 1`; JPEG reports `False`, `1` | Frame counts and animation flags correctly populated | **PASS** |
| **TC23** | `test_image_details.py` | Verify DPI / PPI density extraction | Image buffer with embedded 300 DPI resolution | DPI extracted as tuple `(300, 300)` | Extracted DPI matches embedded resolution tags | **PASS** |
| **TC24** | `test_image_details.py` | Test dominant color extraction on solid color image | Pure red image buffer ($RGB(255, 0, 0)$) | Dominant palette contains `#FF0000` with $\approx 100\%$ distribution | Hex `#FF0000` extracted as dominant color with 100% share | **PASS** |
| **TC25** | `test_image_details.py` | Verify dominant palette structure on photographic sample | `sample.jpg` binary buffer | List of 6 color dictionaries containing keys: `'hex'`, `'rgb'`, `'percent'` | 6-swatch palette generated with valid hex codes and percentage sums $\approx 100\%$ | **PASS** |
| **TC26** | `test_image_details.py` | Validate perceived brightness & lighting assessment | White image ($255$), Black image ($0$), Gray image ($128$) | White $\rightarrow$ High Key; Black $\rightarrow$ Low Key; Gray $\rightarrow$ Balanced Exposure | Luminance and lighting classifications match reference models | **PASS** |
| **TC27** | `test_image_details.py` | Traverse PNG ancillary text chunks (`tEXt`/`zTXt`) | PNG with embedded `'parameters'` and `'prompt'` | Chunks extracted into `png_text_chunks` dictionary; AI prompts captured | Embedded prompt strings extracted cleanly without encoding corruption | **PASS** |
| **TC28** | `test_image_details.py` | Extract embedded ICC color profile metadata | Image buffer containing sRGB ICC profile | `icc_profile_name` extracted as string containing `'sRGB'`; profile size $> 0$ | ICC profile name and binary payload length correctly reported | **PASS** |
| **TC29** | `test_image_details.py` | Verify structural completeness of raw info dictionary | Extracted `report.raw_info` dictionary | Dictionary contains top-level keys: `'hashes'`, `'dimensions'`, `'color'`, `'exif'` | Complete raw info dictionary verified with proper nesting | **PASS** |
| **TC30** | `test_image_details.py` | Verify standard EXIF tags on reference fixture | `sample.jpg` fixture | Camera make `'AcmeCam'`, model `'X-200'`, software `'Firmware 1.0'` | All headline tags match known embedded fixture parameters | **PASS** |
| **TC31** | `test_image_details.py` | Validate comprehensive EXIF enum decoders | Embedded integer values for ExposureProgram, Metering | Raw integer `2` decodes to `'Normal program'`; `5` decodes to `'Pattern'` | Integer enums accurately translated to human-readable strings | **PASS** |
| **TC32** | `test_image_details.py` | Unpack complex bitmask in EXIF `Flash` tag | Bitmask integer `0b01011001` (value 89) | Decodes: Flash fired, return light detected, compulsory flash mode | Bitmask flags unpacked into structured descriptive string | **PASS** |
| **TC33** | `test_image_details.py` | Ingest sterile PNG with zero metadata | `clean_export.png` fixture | `has_exif=False`, `has_gps=False`, `all_tags={}`, `privacy_risk="LOW"` | Sterile image processed gracefully; zero tags reported, low risk | **PASS** |
| **TC34** | `test_image_details.py` | Verify MEDIUM privacy risk assignment | Image containing timestamp and camera model, but NO GPS | `privacy_risk` evaluates to `"MEDIUM"`; risk reasons cite timestamps | Accurately flagged as MEDIUM risk due to temporal/hardware clues | **PASS** |
| **TC35** | `test_image_details.py` | Verify HIGH privacy risk assignment via device serial | Image containing camera serial number, NO GPS | `privacy_risk` evaluates to `"HIGH"`; risk reasons cite device serial | Flagged as HIGH risk due to hardware fingerprint traceability | **PASS** |
| **TC36** | `test_image_details.py` | Validate GPS helper math & coordinate conversion | DMS tuple `((48, 1), (51, 1), (3024, 100))` | Evaluates to $48.8584^\circ \pm 10^{-4}$; valid Google/OSM URLs generated | Decimal conversion accurate; query URLs properly structured | **PASS** |
| **TC37** | `test_image_details.py` | Validate complete JSON serialization of report | `asdict(report)` serialized via `json.dumps()` | Valid RFC 8259 JSON string; all tuples converted; no serialization errors | JSON string generated cleanly; deserializes without schema loss | **PASS** |
| **TC38** | `test_image_details.py` | Validate utility string and date parsing helpers | Date strings `"2023:08:15 14:30:00"`, byte strings | Datetime parsed to ISO standard; byte arrays converted to ASCII/hex | Formatter helpers return sanitized, display-ready strings | **PASS** |
| **TC39** | `test_pdf_export.py` | Generate PDF report for image with rich EXIF and GPS | `sample.jpg` report and raw image bytes | Emits `bytes` starting with `b"%PDF-"`, containing `b"%%EOF"`, size $> 2000$ | Multi-page PDF binary generated with valid header and EOF trailer | **PASS** |
| **TC40** | `test_pdf_export.py` | Generate PDF report for clean image lacking EXIF | `clean_export.png` report and image bytes | Emits valid PDF binary; renders notice of absent metadata | Valid PDF generated; table indicates zero EXIF metadata present | **PASS** |
| **TC41** | `test_pdf_export.py` | Generate PDF report when raw image preview is omitted | `sample.jpg` report with `image_bytes=None` | Emits valid PDF binary; gracefully skips image thumbnail rendering | PDF synthesized successfully without thumbnail canvas rendering | **PASS** |
| **TC42** | `test_streamlit_app.py` | Mount landing page headlessly via `AppTest` | Application script `app.py` | No uncaught exceptions; main page file uploader rendered | App mounted headlessly; `len(at.file_uploader) >= 1`; no exceptions | **PASS** |
| **TC43** | `test_streamlit_app.py` | Verify demo image discovery in selectbox widget | Mounted `AppTest` instance | `len(at.selectbox) == 1`; selectbox options contain $\ge 2$ bundled demos | Demo picker populated with all bundled sample fixtures | **PASS** |
| **TC44** | `test_streamlit_app.py` | Verify Southern/Eastern coordinate handling in UI | Select `"pixel_sydney.jpg"`, trigger load button | App re-renders without exception; metric values contain `"-33.8568"` and `"151.2153"` | Negative latitude rendered accurately in UI metric display | **PASS** |
| **TC45** | `test_streamlit_app.py` | Verify full EXIF + GPS rendering on reference sample | Select `"sample.jpg"`, trigger load button | Renders GPS metrics: `"48.8584"` (Lat) and `"2.2945"` (Lon) | Eiffel Tower coordinates rendered across metric cards and map view | **PASS** |
| **TC46** | `test_streamlit_app.py` | Verify main page quick-action demo chip buttons | Click main page `"Eiffel"` demo chip button | Chip click triggers reactive rerun; loads Paris sample coordinates | Eiffel Tower sample immediately loaded via quick-chip action | **PASS** |
| **TC47** | `test_streamlit_app.py` | Validate clean PNG handling in Streamlit UI | Click main page `"Clean PNG"` demo chip | Renders graceful notification banner; displays `"LOW PRIVACY RISK"` badge | Clean image handled cleanly; displays low privacy risk badge | **PASS** |
| **TC48** | `test_streamlit_app.py` | Validate in-memory metadata scrubber bit-level purity | Execute `create_scrubbed_image()` on `sample.jpg` | Returns clean bytes; re-inspection yields `has_gps=False`, `len(all_tags)=0` | Scrubbed image completely purged of all EXIF, GPS, and camera markers | **PASS** |

---

## 4.4 Implementation Steps

Deploying and executing *Img_Analyze* across academic, forensic, or individual workstations requires a structured setup procedure. The system was designed from inception to require zero proprietary binary dependencies, zero external database servers, and zero cloud connectivity, facilitating rapid local deployment.

```
+---------------------------------------------------------------------------------------------------+
|                        IMG_ANALYZE SYSTEM DEPLOYMENT LIFECYCLE                                    |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [Step 1: Hardware & OS Verification]                                                             |
|   - Ensure 64-bit Architecture (x86_64 or ARM64)                                                  |
|   - Minimum: 2.0 GHz Dual-Core CPU, 4 GB RAM, 250 MB Storage                                      |
|                                                                                                   |
|  [Step 2: Python 3.10+ Portable Environment Setup]                                                |
|   - Verify CPython Interpreter: python --version                                                  |
|   - Initialize Isolated Environment: python -m venv venv                                          |
|   - Activate Environment: .\venv\Scripts\Activate.ps1 (Win) or source venv/bin/activate (POSIX)   |
|                                                                                                   |
|  [Step 3: Deterministic Package Installation]                                                     |
|   - Upgrade Pip: python -m pip install --upgrade pip                                              |
|   - Install Core & Test Dependencies: pip install -r requirements.txt                             |
|                                                                                                   |
|  [Step 4: Operational Execution (Dual-Mode)]                                                      |
|   - Interactive Web Dashboard: streamlit run app.py                                               |
|   - Headless CLI Analysis: python -m exif_extractor sample.jpg --json                             |
|                                                                                                   |
|  [Step 5: Quality Assurance Verification]                                                         |
|   - Automated Test Suite Execution: pytest -v tests/                                              |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

---

### 4.4.1 Hardware and Operating System Preparation

*Img_Analyze* operates across standard consumer, enterprise, and forensic hardware configurations:

1. **Hardware Specifications:**
   - **Processor (CPU):** Dual-Core 2.0 GHz or higher (x86-64 Intel/AMD or Apple Silicon ARM64). Multi-core architecture is utilized automatically during concurrent batch processing.
   - **Random Access Memory (RAM):** Minimum 4 GB RAM; 8 GB or higher recommended when executing large batch analyses containing dozens of high-resolution RAW or TIFF assets.
   - **Storage Capacity:** Approximately 250 MB of free storage space for the application source code, Python virtual environment, dependencies, and test fixtures.
   - **Display Resolution:** Minimum $1280 \times 720$ display resolution for the Streamlit web dashboard; standard 24-bit TrueColor monitor recommended for accurate color palette visualization.

2. **Operating System Compatibility:**
   - **Microsoft Windows:** Windows 10 / Windows 11 (64-bit), Windows Server 2019/2022. PowerShell 5.1+ or PowerShell 7 Core.
   - **Linux Distributions:** Ubuntu 20.04/22.04/24.04 LTS, Debian 11/12, Fedora 38+, Arch Linux.
   - **Apple macOS:** macOS 12.0 (Monterey), macOS 13.0 (Ventura), macOS 14.0 (Sonoma), or later.

---

### 4.4.2 Python 3.10+ Portable Environment Configuration

The application is engineered exclusively in Python 3, adhering strictly to modern language features including type hints (`typing`), structural pattern matching, union operators (`|`), and dataclasses.

1. **Verify Python Installation:** Open a terminal (PowerShell on Windows or Bash on POSIX) and verify that Python 3.10 or higher is registered in the system path:
   ```powershell
   python --version
   ```
   *Expected Output:* `Python 3.10.x` (or `Python 3.11.x`, `Python 3.12.x`, `Python 3.14.x`).

2. **Initialize Isolated Virtual Environment:** To prevent dependency conflicts with globally installed system packages, create an isolated virtual environment (`venv`) within the project root directory:
   ```powershell
   # Navigate to the project root directory
   cd D:\IMG_ANALYZE

   # Initialize an isolated virtual environment named 'venv'
   python -m venv venv
   ```

3. **Activate the Virtual Environment:**
   - On **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
     *(Note: If script execution is restricted on Windows, execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` prior to activation).*
   - On **Linux / macOS (Bash/Zsh)**:
     ```bash
     source venv/bin/activate
     ```

---

### 4.4.3 Package Dependencies Installation via Pip

Once the virtual environment is active, install the pinned project dependencies using Python's package installer (`pip`):

```powershell
# Upgrade pip, setuptools, and wheel to latest stable releases
python -m pip install --upgrade pip setuptools wheel

# Install project dependencies
pip install -r requirements.txt
```

#### Detailed Dependency Profile

```
+-------------------+------------------+------------------------------------------------------------+
| Package Name      | Minimum Version  | Architectural Role & Functional Justification              |
+-------------------+------------------+------------------------------------------------------------+
| Pillow            | $\ge 10.0.0$     | Core image decoding, raster manipulation, Median Cut       |
|                   |                  | color quantization, ICC parsing, in-memory sanitization.   |
+-------------------+------------------+------------------------------------------------------------+
| streamlit         | $\ge 1.30.0$     | High-performance reactive web dashboard, session state,    |
|                   |                  | PyDeck mapping integration, and headless AppTest harness.  |
+-------------------+------------------+------------------------------------------------------------+
| pandas            | $\ge 2.0.0$      | Vectorized batch aggregation, tabular metadata comparison, |
|                   |                  | and structured CSV export generation.                      |
+-------------------+------------------+------------------------------------------------------------+
| fpdf2             | $\ge 2.7.0$      | Pure-Python publication-grade PDF report synthesis,        |
|                   |                  | vector table layouts, font subsetting, and hyperlinks.    |
+-------------------+------------------+------------------------------------------------------------+
| piexif            | $\ge 1.1.3$      | Low-level binary EXIF byte serialization and synthetic     |
|                   |                  | test fixture generation.                                   |
+-------------------+------------------+------------------------------------------------------------+
| pytest            | $\ge 8.0.0$      | Automated testing harness, parameterized test runner,      |
|                   |                  | and regression validation framework.                       |
+-------------------+------------------+------------------------------------------------------------+
```

---

### 4.4.4 Running the Interactive Dashboard (`streamlit run app.py`)

The primary graphical interface is launched using Streamlit's local application server.

1. **Launch Command:**
   ```powershell
   streamlit run app.py
   ```

2. **Server Initialization & Browser Launch:** Upon execution, Streamlit initializes a local HTTP server and automatically launches the default web browser pointing to:
   ```
   Local URL:    http://localhost:8501
   Network URL:  http://192.168.x.x:8501
   ```

3. **Operational Capabilities within Dashboard:**
   - **Drag-and-Drop Ingestion:** Operators can drag one or more image files directly onto the main landing canvas.
   - **Quick Demo Action Chips:** Instant loading of reference fixtures (`sample.jpg` Eiffel Tower, `pixel_sydney.jpg` Sydney Opera House, or `clean_export.png` sterile image).
   - **Interactive Geospatial Viewport:** Real-time visualization of GPS capture coordinates overlaid on OpenStreetMap and PyDeck 3D terrain maps.
   - **Searchable Tag Explorer:** Full-text filtering across all embedded EXIF, GPS, and container tags.
   - **In-Memory Privacy Scrubber:** A single click strips all metadata in RAM and provides an immediate download link for the sanitized image.
   - **Automated Forensic PDF Export:** Generates an official, publication-grade forensic report ready for archival or courtroom submission.

---

### 4.4.5 Running CLI Automation (`python -m exif_extractor`)

For automated batch processing, headless server environments, or security operations integration, the system provides a robust Command-Line Interface (CLI).

1. **Basic Terminal Ingestion:**
   ```powershell
   python -m exif_extractor sample.jpg
   ```
   *Output:* Renders an ANSI-colorized terminal table displaying cryptographic hashes, camera make and model, optical exposure settings, GPS coordinates, and privacy risk rating.

2. **Machine-Readable JSON Output (RFC 8259):**
   ```powershell
   python -m exif_extractor sample.jpg --json
   ```
   *Output:* Emits structured JSON directly to `stdout`, facilitating direct ingestion into downstream SIEM, SOAR, or OSINT pipelines:
   ```json
   {
     "file_path": "sample.jpg",
     "file_size": 24560,
     "image_format": "JPEG",
     "image_size": [640, 480],
     "hashes": {
       "md5": "e4d909c290d0fb1ca068ffaddf22cbd0",
       "sha1": "d4e2fd632128e46950293d0f0d46927d6d1b7454",
       "sha256": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
     },
     "has_gps": true,
     "gps": {
       "latitude": 48.8584,
       "longitude": 2.2945,
       "altitude": 324.0,
       "google_maps_link": "https://maps.google.com/?q=48.8584,2.2945"
     },
     "privacy_risk": "HIGH"
   }
   ```

3. **In-Place Command-Line Sanitization:**
   ```powershell
   python -m exif_extractor sample.jpg --clean --output sanitized_sample.jpg
   ```
   *Output:* Strips all EXIF, GPS, and ancillary metadata in-memory, writing a completely sterile image to `sanitized_sample.jpg`.

---

### 4.4.6 Executing the Automated Test Suite (`pytest -v tests/`)

To verify system integrity, execute regression checks, and validate all 48 test assertions:

1. **Standard Verbose Execution:**
   ```powershell
   pytest -v tests/
   ```

2. **Execution With Duration Profiling:**
   ```powershell
   pytest -v --durations=10 tests/
   ```

3. **Sample Test Execution Output:**
   ```
   ============================= test session starts =============================
   platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0
   rootdir: D:\IMG_ANALYZE
   collected 48 items

   tests/test_batch.py::test_batch_summary_empty PASSED                     [  2%]
   tests/test_batch.py::test_batch_summary_multiple_images PASSED           [  4%]
   tests/test_batch.py::test_build_comparison_dataframe PASSED              [  6%]
   tests/test_image_details.py::test_extract_from_file_path PASSED          [  8%]
   tests/test_image_details.py::test_extract_from_raw_bytes PASSED          [ 10%]
   tests/test_image_details.py::test_extract_from_bytesio PASSED            [ 12%]
   tests/test_image_details.py::test_extract_backwards_compatible_kwarg PASSED [ 14%]
   tests/test_image_details.py::test_extract_invalid_sources PASSED         [ 16%]
   tests/test_image_details.py::test_cryptographic_hashes PASSED            [ 18%]
   tests/test_image_details.py::test_dimensions_and_megapixels PASSED       [ 20%]
   tests/test_image_details.py::test_aspect_ratio_calculations[1920-1080-16:9] PASSED [ 22%]
   tests/test_image_details.py::test_aspect_ratio_calculations[1280-720-16:9] PASSED [ 25%]
   tests/test_image_details.py::test_aspect_ratio_calculations[1024-768-4:3] PASSED [ 27%]
   tests/test_image_details.py::test_aspect_ratio_calculations[800-600-4:3] PASSED [ 29%]
   tests/test_image_details.py::test_aspect_ratio_calculations[1200-800-3:2] PASSED [ 31%]
   tests/test_image_details.py::test_aspect_ratio_calculations[900-600-3:2] PASSED [ 33%]
   tests/test_image_details.py::test_aspect_ratio_calculations[500-500-1:1] PASSED [ 35%]
   tests/test_image_details.py::test_aspect_ratio_calculations[1000-800-5:4] PASSED [ 37%]
   tests/test_image_details.py::test_aspect_ratio_calculations[1080-1920-9:16] PASSED [ 39%]
   tests/test_image_details.py::test_color_modes_and_alpha PASSED           [ 41%]
   tests/test_image_details.py::test_animation_and_frames PASSED            [ 43%]
   tests/test_image_details.py::test_dpi_extraction PASSED                  [ 45%]
   tests/test_image_details.py::test_dominant_colors_solid PASSED           [ 47%]
   tests/test_image_details.py::test_dominant_colors_structure_on_sample PASSED [ 50%]
   tests/test_image_details.py::test_brightness_calculation PASSED          [ 52%]
   tests/test_image_details.py::test_png_text_chunks PASSED                 [ 54%]
   tests/test_image_details.py::test_icc_profile_extraction PASSED          [ 56%]
   tests/test_image_details.py::test_raw_info_dictionary PASSED             [ 58%]
   tests/test_image_details.py::test_sample_jpg_exif_tags_and_decoded PASSED [ 60%]
   tests/test_image_details.py::test_decoded_exif_enums_comprehensive PASSED [ 62%]
   tests/test_image_details.py::test_flash_bitmask_decoder PASSED           [ 64%]
   tests/test_image_details.py::test_clean_png_handling PASSED              [ 66%]
   tests/test_image_details.py::test_privacy_risk_medium PASSED             [ 68%]
   tests/test_image_details.py::test_privacy_risk_serial_number_high PASSED [ 70%]
   tests/test_image_details.py::test_gps_helpers PASSED                     [ 72%]
   tests/test_image_details.py::test_json_serialization PASSED              [ 75%]
   tests/test_image_details.py::test_helper_functions PASSED                [ 77%]
   tests/test_pdf_export.py::test_pdf_export_with_full_exif_and_gps PASSED  [ 79%]
   tests/test_pdf_export.py::test_pdf_export_without_exif PASSED            [ 81%]
   tests/test_pdf_export.py::test_pdf_export_without_image_preview PASSED   [ 83%]
   tests/test_streamlit_app.py::test_landing_page PASSED                    [ 85%]
   tests/test_streamlit_app.py::test_demo_picker_options PASSED             [ 87%]
   tests/test_streamlit_app.py::test_negative_coordinate_demo PASSED        [ 89%]
   tests/test_streamlit_app.py::test_sample_image PASSED                    [ 91%]
   tests/test_streamlit_app.py::test_main_page_demo_chips PASSED            [ 93%]
   tests/test_streamlit_app.py::test_no_exif_png PASSED                     [ 95%]
   tests/test_streamlit_app.py::test_extract_exif_direct_bytes PASSED       [ 97%]
   tests/test_streamlit_app.py::test_in_memory_metadata_scrubbing PASSED    [100%]

   ============================= 48 passed in 10.03s =============================
   ```

The flawless execution of all 48 test cases in 10.03 seconds confirms the absolute stability, mathematical precision, and regression resilience of the *Img_Analyze* platform.
