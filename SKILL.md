---
name: video2ppt
description: Convert video files to PowerPoint presentations. Use when user asks to convert video to PPT, video2ppt, extract frames from video to slides, or generate PowerPoint from video. Triggers when user mentions video-to-ppt, video to presentation, video conversion, or any task involving turning a video into a PowerPoint file.
---

# Video2PPT Skill

Converts video files to PowerPoint presentations by extracting frames at specified intervals with intelligent deduplication.

## Workflow

### Step 1: Install Dependencies

Run the following command to install required packages:

```bash
pip install opencv-python python-pptx Pillow numpy imagehash
```

### Step 2: Find the Video File

Locate the video file path from the user's context or working directory.

**Supported formats:** MP4, AVI, MOV, MKV, FLV, WMV

### Step 3: Execute Conversion

Choose the appropriate command based on user's interval preference:

```bash
# Basic conversion (1 frame per second)
python main.py video.mp4

# Custom interval - recommended for balance
python main.py video.mp4 -i 5 -o output.pptx

# Fast mode (1 frame every 10 seconds)
python main.py video.mp4 -i 10

# High quality (1 frame every 2 seconds)
python main.py video.mp4 -i 2 -o detailed.pptx
```

### Step 4: Verify Output

Confirm the PPT file was created successfully:
- Check output file exists
- Report slide count and file size

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `-i N` | Frame extraction interval in seconds | 1 |
| `-o file.pptx` | Output file path | `{video_name}_output.pptx` |

## Interval Guidelines

| Interval | Speed | Quality | Use Case |
|----------|-------|---------|----------|
| `-i 1` | Slow | Maximum | Detailed presentations |
| `-i 2` | Medium | High | Standard use |
| `-i 5` | Fast | Balanced | **Recommended** |
| `-i 10` | Fastest | Low | Quick previews |

## Tips

- Always install dependencies first before running
- Output file will be placed in the same directory as the video by default
- The tool automatically cleans up temporary files after conversion
- Use `-i 5` for best balance between quality and file size
