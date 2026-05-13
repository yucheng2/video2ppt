# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Video2PPT converts video files to PowerPoint presentations by extracting key frames and generating slides.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run conversion (default: 1 frame per second)
python main.py video.mp4

# Custom interval (1 frame every 5 seconds)
python main.py video.mp4 -i 5 -o output.pptx
```

## Architecture

- `main.py` - Entry point containing the `Video2PPT` class
- `Video2PPT.convert()` - Main flow: extract_frames() → generate_ppt()
- `Video2PPT.extract_frames()` - Extracts frames at intervals with two-tier deduplication:
  1. Pixel difference (fast) - if diff > pixel_threshold, save directly
  2. pHash comparison (precise) - for similar frames, compare perceptual hashes
- `Video2PPT.generate_ppt()` - Creates PPT with title slide + frame slides

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `fps_interval` / `-i` | 1 | Frame extraction interval in seconds |
| `pixel_threshold` | 30 | Pixel diff threshold - above this saves directly |
| `hash_threshold` | 15 | pHash diff threshold - above this keeps frame |

## Tech Stack

- OpenCV (cv2) - Video frame extraction
- python-pptx - PPT generation
- Pillow - Image processing
- imagehash - Perceptual hashing for deduplication
- numpy - Numerical operations
