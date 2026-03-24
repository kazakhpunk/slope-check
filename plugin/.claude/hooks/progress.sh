#!/usr/bin/env bash
# PostToolUse hook for slope-check pipeline progress.
# Fires after each Agent tool call. Checks which output files have appeared
# in the active slope-reports/{slug}/ directory and prints progress to stderr.

set -euo pipefail

REPORTS_DIR="slope-reports"

# --- Slug discovery ---
# Prefer .current-slug marker written by SKILL.md orchestrator.
# Fall back to most-recently-modified subdirectory.
if [[ -f "$REPORTS_DIR/.current-slug" ]]; then
    SLUG=$(cat "$REPORTS_DIR/.current-slug")
else
    SLUG=$(ls -td "$REPORTS_DIR"/*/ 2>/dev/null | head -1 | xargs basename 2>/dev/null || true)
fi

# No active audit — nothing to do.
if [[ -z "$SLUG" ]]; then
    exit 0
fi

SLUG_DIR="$REPORTS_DIR/$SLUG"
SEEN_FILE="$SLUG_DIR/.progress-seen"

# Create seen file if it doesn't exist.
touch "$SEEN_FILE"

# --- Check each artifact ---
report_if_new() {
    local file="$1"
    local message="$2"

    if [[ -f "$SLUG_DIR/$file" ]] && ! grep -qxF "$file" "$SEEN_FILE" 2>/dev/null; then
        echo "$file" >> "$SEEN_FILE"
        echo "$message" >&2
    fi
}

# Count helper — counts array entries in a JSON file.
jcount() {
    python3 -c "import json; print(len(json.load(open('$1'))))" 2>/dev/null || echo "?"
}

# Count red flags across all claims in audit.json.
red_flag_count() {
    python3 -c "
import json
audit = json.load(open('$1'))
print(sum(len(e.get('red_flags', [])) for e in audit))
" 2>/dev/null || echo "?"
}

# Replicable/blocked counts from env-status.json.
env_counts() {
    python3 -c "
import json
data = json.load(open('$1'))
claims = data.get('claims', data) if isinstance(data, dict) else data
r = sum(1 for e in claims if e.get('status') == 'replicable')
b = sum(1 for e in claims if e.get('status') == 'blocked')
print(f'{r} replicable, {b} blocked')
" 2>/dev/null || echo "? replicable, ? blocked"
}

# Result count from results.json.
result_count() {
    python3 -c "
import json
data = json.load(open('$1'))
print(sum(1 for e in data if e.get('status') == 'measured'))
" 2>/dev/null || echo "?"
}

# --- Emit progress for new files ---
# Only compute counts when the file is new (not yet in .progress-seen).
if [[ -f "$SLUG_DIR/claims.json" ]] && ! grep -qxF "claims.json" "$SEEN_FILE" 2>/dev/null; then
    N=$(jcount "$SLUG_DIR/claims.json")
    report_if_new "claims.json" "claim-extractor: $N claims extracted"
fi

if [[ -f "$SLUG_DIR/audit.json" ]] && ! grep -qxF "audit.json" "$SEEN_FILE" 2>/dev/null; then
    N=$(jcount "$SLUG_DIR/audit.json")
    RF=$(red_flag_count "$SLUG_DIR/audit.json")
    report_if_new "audit.json" "static-auditor: $N claims scored, $RF red flags found"
fi

if [[ -f "$SLUG_DIR/charts/slope-bar.png" ]]; then
    report_if_new "charts/slope-bar.png" "chart-generator: charts rendered"
fi

if [[ -f "$SLUG_DIR/env-status.json" ]] && ! grep -qxF "env-status.json" "$SEEN_FILE" 2>/dev/null; then
    COUNTS=$(env_counts "$SLUG_DIR/env-status.json")
    report_if_new "env-status.json" "env-replicator: $COUNTS"
fi

if [[ -f "$SLUG_DIR/results.json" ]] && ! grep -qxF "results.json" "$SEEN_FILE" 2>/dev/null; then
    N=$(result_count "$SLUG_DIR/results.json")
    report_if_new "results.json" "benchmark-runner: $N benchmarks executed"
fi

report_if_new "slope-report.md" "slope-reporter: report complete"
