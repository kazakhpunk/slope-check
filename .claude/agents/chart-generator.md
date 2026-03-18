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

### Chart 1: Slope Bar Chart (slope-bar.png)

- X-axis: claim IDs (e.g., claim_01, claim_02)
- Y-axis: 0-100 scale representing "percentage of claimed value"
- Bar A (always): rendered at 100 — the claimed value baseline. Omit for non-numeric claims (value is null); label row as NON-NUMERIC instead.
- Bar B (always): Reproducibility Confidence Score (0-100). If data_quality is "insufficient": render as hatched grey bar with "?" label instead.
- Bar C (runmerge mode only): `(actual_value / claimed_value) * 100`. Omit if actual_value is null or claimed_value is 0.
- Bar color based on confidence score: yellow #FFD966 if >= 80, orange #F4A261 if 50-79, red #E63946 if < 50.
- Chart title: "Slope Report: Claimed vs Reproducibility Confidence"

### Chart 2: Red Flag Distribution (red-flags.png)

- X-axis: claim IDs
- Y-axis: count of red flag signals triggered
- Stacked bar segments by red flag type: hardcoded_result, missing_eval_script, missing_dataset, weak_baseline, no_error_bars, methodology_mismatch
- Colors: #E63946, #F4A261, #E9C46A, #2A9D8F, #457B9D, #8338EC (warm-to-cool palette, one per type)
- Chart title: "Red Flag Distribution by Claim"

### After generating PNGs

Embed charts as base64 for inline markdown use:

```python
import base64
for fname in ['slope-bar.png', 'red-flags.png']:
    with open(f'charts/{fname}', 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    with open(f'charts/{fname}.b64', 'w') as f:
        f.write(f'data:image/png;base64,{b64}')
```

## Output

- `slope-reports/{project-slug}/charts/slope-bar.png` (300dpi)
- `slope-reports/{project-slug}/charts/red-flags.png` (300dpi)
- `slope-reports/{project-slug}/charts/slope-bar.png.b64`
- `slope-reports/{project-slug}/charts/red-flags.png.b64`

In runmerge mode, these files are overwritten in-place. This is the only exception to the rule that agents do not modify files written by prior agents.
