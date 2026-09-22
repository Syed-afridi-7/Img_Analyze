@echo off
rem ============================================================
rem  EXIF Metadata Extractor - command line (self-contained)
rem  Usage examples:
rem     run-cli.bat sample.jpg --all
rem     run-cli.bat samples\pixel_sydney.jpg --json
rem     run-cli.bat photo1.jpg photo2.png
rem ============================================================
cd /d "%~dp0"
python.exe -m exif_extractor %*
