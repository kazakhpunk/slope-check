---
name: slope-check
description: Audit an AI paper, GitHub repo, or product page against its quantitative claims. Produces a structured slope report with confidence scores and charts. Invoke when the user asks to "verify claims", "check benchmarks", "audit results", "slope check", "reproduce results", or any similar request about whether an AI tool's performance claims are accurate.
arguments: "<url-or-path> [<url-or-path>...] [--run]"
---

# /slope-check

Audits one or more sources against their quantitative claims.

## Usage

```
/slope-check <url-or-path> [<url-or-path>...] [--run]
```

**Arguments:**
- One or more: GitHub repo URL, arxiv URL, product page URL, or local path
- `--run`: opt-in live benchmark replication (requires explicit user confirmation before any code is executed)

**Examples:**
```
/slope-check https://github.com/user/fastembed
/slope-check https://arxiv.org/abs/2310.01469
/slope-check https://github.com/user/repo https://arxiv.org/abs/2310.01469
/slope-check https://github.com/user/repo --run
```

## When to auto-invoke

Invoke this skill when the user says any of:
- "check the benchmarks for X"
- "verify the claims in this paper"
- "audit X's results"
- "slope check X"
- "can you reproduce the results from X"
- "is X's performance claim legit"
- "does X actually perform as claimed"

## What it does

1. Extracts all testable quantitative claims from the source(s)
2. Scores each claim's reproducibility confidence via static analysis (6 binary signals)
3. Cross-references claims against known benchmark inflation patterns (known-patterns.md) and public leaderboards
4. Generates charts comparing claimed values against confidence scores
5. Produces a structured slope report with a verdict per claim: VERIFIED / PARTIAL / WEAK / REFUTED / UNVERIFIABLE

With `--run`: also attempts to set up the environment and execute benchmark scripts where conditions permit.

## Orchestration

### Step 1: claim-extractor

Invoke the claim-extractor agent with all provided source URLs/paths (excluding the `--run` flag).

After it completes: check if `slope-reports/{project-slug}/inconclusive.txt` exists. If it does: stop and inform the user:

```
Slope check stopped: insufficient testable claims found.
{contents of inconclusive.txt}
```

### Step 2: static-auditor (always) + env-replicator (--run only, in parallel)

Invoke the static-auditor agent.

If `--run` was specified: before invoking env-replicator, ask the user for confirmation:

```
I found {N} claims in {project-slug}. Running with --run will attempt to execute benchmark scripts from the target repo. Do you confirm? (yes/no)
```

If the user confirms: invoke env-replicator in parallel with static-auditor.
If the user declines or does not confirm: proceed with static-only (skip env-replicator and benchmark-runner). Note in the report header: "NOTE: --run was not approved. Results reflect static audit only."

### Step 3: chart-generator (static mode)

After static-auditor completes: invoke chart-generator in static mode.

### Step 4: benchmark-runner (--run only, after env-replicator)

If `--run` was approved and env-replicator has completed: invoke benchmark-runner.

### Step 5: chart-generator (runmerge mode, --run only)

After benchmark-runner completes: invoke chart-generator in runmerge mode to overlay live results onto the charts.

### Step 6: slope-reporter

After all prior agents complete: invoke slope-reporter.

### Step 7: Present summary to user

After slope-reporter completes, print to the terminal:

```
Slope Check Complete
====================
Project: {project_name}
Score:   {verified}/{scoreable} claims verified ({pct}%)
Confidence: {level}

{one-sentence summary from report}

Full report: slope-reports/{project-slug}/slope-report.md
```

If the slope score is N/A (all claims unverifiable): note that explicitly.
