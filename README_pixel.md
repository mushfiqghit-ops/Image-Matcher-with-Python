# Pixel-Match Image Detector

**Python** — Pixel-Perfect Duplicate Image Finder

A command-line tool that detects exact duplicate images by comparing pixel data between a set of reference images and a large production image library. Designed for large-scale document digitization workflows where the same scanned image may appear across multiple production series.

---

> **Built by:** Mushfiqur Rahman
> **AI Assistance:** Claude (Anthropic) — architecture, logic design, and iterative development support
> *Concept, requirements, and domain knowledge by Mushfiqur Rahman. Code structure and implementation developed collaboratively with Claude.*

---

## How It Works

| Step | What Happens |
|---|---|
| 1 | Load all reference images → generate SHA-256 hash from pixel data |
| 2 | Load production series images → hash each one |
| 3 | Hash match found → confirm with pixel-by-pixel array comparison |
| 4 | Save all confirmed matches to a timestamped CSV report |

Two-stage matching (hash → pixel comparison) ensures zero false positives.

---

## Features

- SHA-256 pixel hashing for fast first-pass matching
- Pixel-by-pixel `numpy` array comparison for exact confirmation
- Handles case-insensitive filename duplicates within folders
- Processes multiple reference folders and hundreds of production series
- Generates timestamped CSV report with match details
- Supports JPG, JPEG, PNG, BMP, TIFF, GIF

---

## Requirements

```
Pillow
numpy
```

Install:

```bash
pip install Pillow numpy
```

---

## Usage

```bash
python image_matcher.py
```

The tool guides you through 5 steps via dialog boxes:

1. Select report output folder
2. Select reference image folders (one or more)
3. Select a `.txt` file listing production series numbers (one per line)
4. Select the parent folder containing all production series subfolders
5. Confirm and run

### Series list file format

```
109325054
007815689
109328197
```

---

## Output

A CSV file saved to your chosen report folder:

```
image_matches_20260915_143022.csv
```

| Column | Description |
|---|---|
| `Reference_Image` | Filename of the matched reference image |
| `Reference_Folder` | Which reference folder it came from |
| `Production_Image` | Filename of the matched production image |
| `Production_Series` | Which production series it belongs to |

---

## Project Context

Built for a production operations role managing large-scale image digitization. The tool was used to cross-check reference scan sets against production batches processed by a team of 250+ operators, ensuring no image was duplicated or misassigned across series.

---

## Folder Structure

```
pixel-match-image-detector/
├── image_matcher.py
└── README.md
```
