@echo off
REM Hybrid Recorder Launcher
REM Usage: hybrid_recorder.bat [URL] [output_directory]

set URL=%1
set OUTPUT_DIR=%2

if "%URL%"=="" set URL=about:blank
if "%OUTPUT_DIR%"=="" set OUTPUT_DIR=recordings

echo Starting Hybrid Recorder...
echo URL: %URL%
echo Output Directory: %OUTPUT_DIR%
echo.

node hybrid_recorder.js "%URL%" "%OUTPUT_DIR%"
