"""Smoke tests for the Streamlit frontend, run without a browser.

Uses Streamlit's AppTest harness to execute app.py headlessly:
  - landing state renders without exceptions
  - loading the sample image produces the full report incl. GPS metrics
  - main page chips load fixtures instantly
  - clean image scrubber strips all EXIF and GPS tags in-memory
  - extract_exif supports in-memory bytes without temporary disk files

Usage:
    python tests/test_streamlit_app.py
    pytest tests/test_streamlit_app.py
"""

import io
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit.testing.v1 import AppTest

from app import create_scrubbed_image, extract_exif

APP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"
)
SAMPLE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample.jpg"
)


def test_landing_page():
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()
    assert not at.exception, f"Landing page raised: {at.exception}"
    # Verify main page file uploader and sidebar uploader exist
    assert len(at.file_uploader) >= 1, "File uploader missing on landing page"
    print("  landing page: no exceptions, uploader present")


def test_demo_picker_options():
    """The demo selectbox must list the bundled fixtures."""
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()
    assert not at.exception
    assert len(at.selectbox) == 1, "Demo picker selectbox missing"
    options = at.selectbox[0].options
    assert len(options) >= 2, f"Expected several demo images, got: {options}"
    print(f"  demo picker: {len(options)} demo images listed")


def test_negative_coordinate_demo():
    """Sydney fixture must load with a negative (southern) latitude."""
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()
    label = next(
        (o for o in at.selectbox[0].options if "pixel_sydney" in o), None
    )
    assert label, f"pixel_sydney.jpg not in demo options: {at.selectbox[0].options}"
    at.selectbox[0].select(label)
    # The sidebar demo button triggers the fixture load
    load_btn = next(
        (b for b in at.button if "Load demo" in (b.label or "")),
        at.sidebar.button[0],
    )
    load_btn.click()
    at.run()
    assert not at.exception, f"Sydney demo raised: {at.exception}"
    values = [m.value or "" for m in at.metric]
    assert any("-33.8568" in v for v in values), f"S-latitude missing: {values}"
    assert any("151.2153" in v for v in values), f"E-longitude missing: {values}"
    print("  negative-coordinate demo: S latitude rendered correctly")


def test_sample_image():
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()
    assert not at.exception

    # Load demo button from sidebar
    load_btn = next(
        (b for b in at.button if "Load demo" in (b.label or "")),
        at.sidebar.button[0],
    )
    load_btn.click().run()
    assert not at.exception, f"Sample run raised: {at.exception}"

    # GPS metrics from the Eiffel Tower fixture must be rendered.
    values = [m.value or "" for m in at.metric]
    assert any("48.8584" in v for v in values), f"Latitude metric missing: {values}"
    assert any("2.2945" in v for v in values), f"Longitude metric missing: {values}"
    print(f"  sample image: {len(values)} metrics, GPS coordinates present")


def test_main_page_demo_chips():
    """Main page quick chips must load the sample directly."""
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()
    assert not at.exception

    chip_eiffel = next(
        (b for b in at.button if "Eiffel" in (b.label or "")), None
    )
    assert chip_eiffel is not None, "Eiffel Tower chip missing on main page"
    chip_eiffel.click().run()
    assert not at.exception, f"Main page chip click raised: {at.exception}"

    values = [m.value or "" for m in at.metric]
    assert any("48.8584" in v for v in values), f"Latitude metric missing: {values}"
    assert any("2.2945" in v for v in values), f"Longitude metric missing: {values}"
    print("  main page demo chips: Eiffel Tower loaded successfully")


def test_no_exif_png():
    """A PNG without EXIF must render the friendly notice, not crash."""
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()

    # Click the Clean PNG demo chip on main page
    chip_clean = next(
        (b for b in at.button if "Clean PNG" in (b.label or "")), None
    )
    assert chip_clean is not None, "Clean PNG chip button missing"
    chip_clean.click().run()
    assert not at.exception, f"Clean PNG run raised: {at.exception}"

    # Assert LOW RISK badge is shown
    assert any("LOW PRIVACY RISK" in s.value for s in at.success)
    print("  no-exif branch: verified clean PNG loads and reports low risk")


def test_extract_exif_direct_bytes():
    """Direct in-memory bytes extraction without writing to temporary files."""
    assert os.path.exists(SAMPLE_PATH), f"Sample path {SAMPLE_PATH} not found"
    with open(SAMPLE_PATH, "rb") as f:
        file_bytes = f.read()

    report = extract_exif(file_bytes, file_name="sample.jpg")
    assert report is not None
    assert report.file_size == len(file_bytes)
    assert report.has_gps is True
    assert getattr(report.gps, "latitude", None) is not None
    assert abs(report.gps.latitude - 48.8584) < 1e-4
    assert abs(report.gps.longitude - 2.2945) < 1e-4
    assert len(report.all_tags) > 0
    print("  extract_exif: direct bytes processed in-memory without temp files")


def test_in_memory_metadata_scrubbing():
    """Verify create_scrubbed_image removes all EXIF and GPS data in-memory."""
    with open(SAMPLE_PATH, "rb") as f:
        orig_bytes = f.read()

    orig_img = Image.open(io.BytesIO(orig_bytes))
    clean_bytes, ext, mime = create_scrubbed_image(orig_img)

    assert len(clean_bytes) > 0
    assert mime in ("image/jpeg", "image/png", "image/webp")

    # Inspect cleaned image with PIL
    clean_img = Image.open(io.BytesIO(clean_bytes))
    raw_exif = clean_img._getexif() if hasattr(clean_img, "_getexif") else None
    assert not raw_exif, f"Expected no raw EXIF in scrubbed image, got: {raw_exif}"

    # Verify extract_exif on clean bytes reports no GPS and no tags
    clean_report = extract_exif(clean_bytes, file_name="clean.jpg")
    assert clean_report.has_gps is False
    assert len(clean_report.all_tags) == 0
    print("  in-memory metadata scrubber: all EXIF/GPS stripped successfully")


if __name__ == "__main__":
    print("Running Streamlit app smoke tests...")
    test_landing_page()
    test_demo_picker_options()
    test_sample_image()
    test_negative_coordinate_demo()
    test_main_page_demo_chips()
    test_no_exif_png()
    test_extract_exif_direct_bytes()
    test_in_memory_metadata_scrubbing()
    print("All app smoke tests passed.")
