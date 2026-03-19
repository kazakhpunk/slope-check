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

### Styling (apply to ALL charts)

Use this exact matplotlib configuration for a polished dark theme:

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Dark theme colors
BG_DARK = '#0d1117'
BG_CARD = '#161b22'
TEXT_PRIMARY = '#e6edf3'
TEXT_SECONDARY = '#8b949e'
GRID_COLOR = '#21262d'
BORDER_COLOR = '#30363d'

# Verdict colors
COLOR_VERIFIED = '#3fb950'    # green
COLOR_PARTIAL = '#d29922'     # amber
COLOR_WEAK = '#f85149'        # red
COLOR_REFUTED = '#da3633'     # dark red
COLOR_GREY_BAR = '#30363d'    # baseline grey

# Red flag palette
FLAG_COLORS = {
    'hardcoded_result': '#f85149',
    'missing_eval_script': '#f0883e',
    'missing_dataset': '#d29922',
    'weak_baseline': '#3fb950',
    'no_error_bars': '#58a6ff',
    'methodology_mismatch': '#bc8cff',
    'single-batch-latency': '#f0883e',
    'mteb-subset-cherry-picking': '#d29922',
    'internal-numeric-inconsistency': '#f85149',
}

def confidence_color(score):
    if score >= 80: return COLOR_VERIFIED
    if score >= 50: return COLOR_PARTIAL
    return COLOR_WEAK

# Global style
rcParams.update({
    'figure.facecolor': BG_DARK,
    'axes.facecolor': BG_CARD,
    'axes.edgecolor': BORDER_COLOR,
    'axes.labelcolor': TEXT_PRIMARY,
    'axes.grid': True,
    'grid.color': GRID_COLOR,
    'grid.alpha': 0.5,
    'grid.linewidth': 0.5,
    'text.color': TEXT_PRIMARY,
    'xtick.color': TEXT_SECONDARY,
    'ytick.color': TEXT_SECONDARY,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica Neue', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.3,
    'savefig.facecolor': BG_DARK,
})
```

### Chart 1: Slope Bar Chart (slope-bar.png)

- Figure size: `(max(10, len(claims) * 1.4), 5)`
- X-axis: claim IDs (e.g., C01, C02 — abbreviated)
- Y-axis: 0-100 scale, label "Confidence (%)"
- Bar A (always): rendered at 100, color `COLOR_GREY_BAR`, alpha 0.3, label "Claimed (100%)". Omit for non-numeric claims (value is null); add "NON-NUMERIC" text annotation at x position instead.
- Bar B (always): Reproducibility Confidence Score (0-100), colored by `confidence_color()`, with rounded top edges (`plt.bar(..., linewidth=0)`). If data_quality is "insufficient": render as hatched bar with "?" label.
- Bar C (runmerge mode only): `(actual_value / claimed_value) * 100`. Omit if actual_value is null or claimed_value is 0. Use a thin outline bar overlaid.
- Add value labels on top of each confidence bar (white text, 8pt, bold)
- Add a subtle horizontal dashed line at y=80 (VERIFIED threshold) and y=50 (PARTIAL threshold), with small right-aligned labels
- Title: "Slope Report: Claimed vs Confidence" — left-aligned, 14pt, bold
- Subtitle below title: project name and date in TEXT_SECONDARY, 10pt
- Remove top and right spines
- X-axis labels rotated 0 degrees (horizontal), use abbreviated IDs

### Chart 2: Red Flag Distribution (red-flags.png)

- Figure size: `(max(10, len(claims) * 1.4), 4)`
- X-axis: claim IDs (abbreviated as C01, C02)
- Y-axis: count of red flag signals triggered, integer ticks only
- Stacked bar segments by red flag type, using `FLAG_COLORS` dict (fall back to `#8b949e` for unknown types)
- Bar width 0.5, slight rounded appearance
- Legend: horizontal, below chart, small font (8pt), no frame, TEXT_SECONDARY color
- Title: "Red Flag Distribution" — left-aligned, 14pt, bold
- Remove top and right spines
- If a claim has zero flags, leave gap (no bar)

### After generating PNGs

Do NOT generate base64 files. They are not needed — Claude Code displays PNGs inline via the Read tool.

## Output

- `slope-reports/{project-slug}/charts/slope-bar.png` (150dpi, optimized for inline terminal display)
- `slope-reports/{project-slug}/charts/red-flags.png` (150dpi)

In runmerge mode, these files are overwritten in-place. This is the only exception to the rule that agents do not modify files written by prior agents.
