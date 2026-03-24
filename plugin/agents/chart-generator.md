---
name: chart-generator
description: Generates slope bar and red flag distribution charts from audit and results data. Single agent file invoked in two modes via --mode flag: static (after static-auditor) and runmerge (after benchmark-runner, --run only).
---

# Chart Generator

You generate two matplotlib charts from audit data. You are invoked with a mode context: either `static` (no live results) or `runmerge` (live results available from benchmark-runner).

## Input

**static mode:** `slope-reports/{project-slug}/claims.json` + `slope-reports/{project-slug}/audit.json`
**runmerge mode:** same as static + `slope-reports/{project-slug}/results.json`

## Process

Create `slope-reports/{project-slug}/charts/` directory if it does not exist.

Write a Python script to `slope-reports/{project-slug}/generate_charts.py` and execute it with `python3`. Pass the mode as an environment variable: `CHART_MODE=static` or `CHART_MODE=runmerge`.

### Design System

The charts use a restrained, high-contrast dark theme inspired by Bloomberg Terminal and Linear. Every visual choice should feel intentional and minimal. When in doubt, remove rather than add.

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import rcParams
import numpy as np

# --- Palette ---
BG = '#0c0e12'
SURFACE = '#13161c'
TEXT = '#c9d1d9'
TEXT_MUTED = '#484f58'
TEXT_DIM = '#30363d'
ACCENT = '#58a6ff'          # primary blue
ACCENT_STRONG = '#79c0ff'   # high-confidence blue
ACCENT_MID = '#388bfd'      # mid-confidence blue
ACCENT_WEAK = '#1f3a5f'     # low-confidence blue (muted)
DANGER = '#f85149'           # refuted / critical flags
BORDER = '#1b1f27'
RULE = '#21262d'

def confidence_color(score):
    """Single blue family — intensity maps to confidence."""
    if score >= 80: return ACCENT_STRONG
    if score >= 50: return ACCENT
    if score >= 30: return ACCENT_MID
    return ACCENT_WEAK

def verdict_color(verdict):
    """Verdict label colors — subtle, not the bar color."""
    v = (verdict or '').upper()
    if v == 'VERIFIED': return '#3fb950'
    if v == 'PARTIAL': return '#d29922'
    if v == 'REFUTED': return DANGER
    if v == 'UNVERIFIABLE': return TEXT_MUTED
    return TEXT_MUTED  # WEAK

# --- Global rcParams ---
rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor': BG,
    'axes.edgecolor': 'none',
    'axes.labelcolor': TEXT_MUTED,
    'axes.grid': False,
    'text.color': TEXT,
    'xtick.color': TEXT_MUTED,
    'ytick.color': TEXT_MUTED,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Inter', 'SF Pro Display', 'Helvetica Neue', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.5,
    'savefig.facecolor': BG,
})
```

### Chart 1: Confidence Score (slope-bar.png)

Horizontal bar chart. Claims on Y-axis (top to bottom, sorted by confidence descending). Bars extend right from 0 to the confidence score.

**Layout:**
- Figure size: `(10, max(4, len(claims) * 0.55))`
- Horizontal bars, height 0.45, with 2px rounded caps via `matplotlib.patches.FancyBboxPatch` or `bar(..., linewidth=0)` with clipping
- Left margin: claim labels (C01, C02, etc.) in `TEXT_MUTED`, 9pt, monospace-style alignment
- Bars colored by `confidence_color(score)` — single blue family, intensity = confidence
- Score value as white text at the end of each bar (inside if bar is long enough, outside if short). 9pt, semibold.
- Verdict label (VERIFIED, PARTIAL, WEAK, REFUTED, UNVERIFIABLE) right-aligned at x=105 area, colored by `verdict_color()`, 8pt, uppercase

**Threshold zones:**
- Two subtle vertical bands as background fills (not lines):
  - x=0 to x=50: no fill (implied weak zone)
  - x=50 to x=80: subtle fill `ACCENT_WEAK` at alpha 0.06
  - x=80 to x=100: subtle fill `ACCENT_WEAK` at alpha 0.12
- Small labels "PARTIAL" at x=50 and "VERIFIED" at x=80, top of chart, in `TEXT_DIM`, 7pt

**Runmerge overlay (--run mode only):**
- For claims with actual results: add a thin vertical marker (diamond or short horizontal tick) at `(actual_value / claimed_value) * 100` position, color `DANGER` if below confidence, `#3fb950` if at or above
- Small "actual" label next to marker, 7pt

**Title block:**
- Title: "Confidence Scores" — 15pt, semibold, `TEXT`, left-aligned with generous top padding
- Subtitle: "{project-name} — {date}" — 10pt, `TEXT_MUTED`, directly below title
- 16px gap between subtitle and first bar

**Axes:**
- X-axis: 0 to 100, ticks at 0, 25, 50, 75, 100 only. Thin tick marks, no axis line.
- Y-axis: no axis line, no ticks. Just the labels.
- No grid lines. One subtle horizontal rule (`RULE` color, 0.5px) between each claim for scanability.
- Remove all spines.

**Data quality:**
- If `data_quality` is "insufficient": bar rendered in `TEXT_DIM` with diagonal hatch pattern, "?" instead of score value

### Chart 2: Red Flag Matrix (red-flags.png)

Dot matrix (not stacked bars). Claims on Y-axis, flag types on X-axis. Filled circle = flag present, empty circle = flag absent.

**Layout:**
- Figure size: `(max(8, num_flag_types * 1.2), max(3.5, len(claims) * 0.45))`
- Claims on Y-axis (same order as Chart 1 — sorted by confidence descending)
- Flag types on X-axis, labels rotated 35 degrees, 8pt, `TEXT_MUTED`
- Use `pattern_id` field for flag identification when available (more specific than `type`). Fall back to `type` if `pattern_id` is null. This means "mteb-subset-cherry-picking" instead of generic "methodology_mismatch".
- Clean flag labels: replace underscores/hyphens with spaces, title case (e.g., "mteb-subset-cherry-picking" → "Mteb Subset Cherry Picking")

**Dots:**
- Filled circle: `DANGER` color (#f85149), size 80 (scatter marker size)
- Empty position: small circle outline in `TEXT_DIM`, size 30, linewidth 0.5
- This creates a scannable presence/absence grid

**Title block:**
- Title: "Red Flags" — 15pt, semibold, `TEXT`, left-aligned
- Subtitle: "{count} flags across {n} claims" — 10pt, `TEXT_MUTED`

**Axes:**
- No grid, no spines, no axis lines
- Subtle horizontal rules between claims (same as Chart 1)
- If a flag type has zero occurrences across all claims, omit it from the X-axis entirely

**Edge cases:**
- If zero red flags total: generate a minimal chart with centered text "No red flags detected" in `TEXT_MUTED`, 12pt
- Only show flag types that actually appear in the data (no empty columns)

### After generating PNGs

Do NOT generate base64 files. They are not needed — Claude Code displays PNGs inline via the Read tool.

## Output

- `slope-reports/{project-slug}/charts/slope-bar.png` (300dpi)
- `slope-reports/{project-slug}/charts/red-flags.png` (300dpi)

In runmerge mode, these files are overwritten in-place. This is the only exception to the rule that agents do not modify files written by prior agents.
