# slope-check

Audit AI papers, repos, and product pages against their quantitative claims.

"Slope" is the gap between what is promised and what is real.

## Install

```bash
claude plugin install slope-check-plugin
```

## Usage

```bash
/slope-check <url-or-path> [<url-or-path>...] [--run]
```

**Examples:**

```bash
# Audit a GitHub repo's README claims
/slope-check https://github.com/user/fastembed

# Audit an arxiv paper
/slope-check https://arxiv.org/abs/2310.01469

# Audit both repo and paper together
/slope-check https://github.com/user/repo https://arxiv.org/abs/2310.01469

# Include live benchmark replication attempt
/slope-check https://github.com/user/repo --run
```

## What you get

Every run produces a `slope-reports/{project}/slope-report.md` containing:

- **Overall Slope Score** — fraction of claims that pass verification
- **Verdict per claim** — VERIFIED / PARTIAL / WEAK / REFUTED / UNVERIFIABLE
- **Reproducibility Confidence Score** — 0-100, based on 6 static signals
- **Cross-reference results** — checked against known leaderboards and public benchmarks
- **Charts** — slope bar chart and red flag distribution (warm gradient palette)
- **Detailed findings** — exact evidence for every verdict

## Verdict guide

| Verdict | Meaning |
|---|---|
| VERIFIED | Confidence >= 80% and baseline is fair |
| PARTIAL | Confidence 50-79% or methodology differs from claim |
| WEAK | Confidence < 50% and no contradicting evidence found |
| REFUTED | Positive evidence against the claim (hardcoded result, weak baseline, etc.) |
| UNVERIFIABLE | Cannot score — missing code, inaccessible data |

## Inputs supported

- GitHub repo URL
- arxiv / paper URL
- Product page URL
- Local file path
- Any combination of the above

## What --run does

With `--run`, the plugin also attempts to set up the environment and execute benchmark scripts for claims that appear replicable. This requires your explicit confirmation before any code from the target repo is executed.

Most runs will hit blockers (GPU requirements, paywalled datasets, proprietary models). When that happens, the report falls back to static analysis and clearly notes what was blocked and why.

## Limitations

- Cannot test GPU-dependent claims on CPU hardware
- Cannot access paywalled datasets or proprietary models
- Speed benchmarks depend on hardware — results will differ from the original environment
- Live replication may fail for complex multi-step eval pipelines

## Known patterns

The plugin ships with `known-patterns.md` — a versioned library of documented benchmark inflation patterns. Seed patterns include:

- MTEB subset cherry-picking
- SQuAD v1/v2 version confusion
- BM25 implementation version mismatch
- Single batch-size latency benchmarks
- HuggingFace leaderboard version drift

The static-auditor consults this file before any web search. When a novel red flag is detected, slope-reporter appends a `[DRAFT]` entry to known-patterns.md for human review. Remove the `[DRAFT]` tag to promote it to active.

## Output location

All reports are saved to `./slope-reports/{project-slug}/` relative to where you invoke the plugin.

## Example output

See `examples/example-slope-report.md` for a realistic example using the fictional FastEmbed v2 project.
