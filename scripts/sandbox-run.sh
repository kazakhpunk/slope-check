#!/usr/bin/env bash
# sandbox-run.sh — isolated benchmark execution wrapper
# Usage: sandbox-run.sh <output_json> <working_dir> <command> [args...]

set -uo pipefail

if [ $# -lt 3 ]; then
  echo "Usage: sandbox-run.sh <output_json> <working_dir> <command> [args...]" >&2
  exit 1
fi

OUTPUT_JSON="$1"
WORKING_DIR="$2"
shift 2
CMD=("$@")

TMPDIR_WORK=$(mktemp -d)
STDOUT_FILE="$TMPDIR_WORK/stdout.txt"
STDERR_FILE="$TMPDIR_WORK/stderr.txt"

cleanup() {
  rm -rf "$TMPDIR_WORK"
}
trap cleanup EXIT

# Cross-platform millisecond timing
start_time() { python3 -c "import time; print(int(time.time()*1000))"; }
START_MS=$(start_time)

(
  cd "$WORKING_DIR"
  ulimit -v $((2 * 1024 * 1024)) 2>/dev/null || true
  timeout 300 "${CMD[@]}" >"$STDOUT_FILE" 2>"$STDERR_FILE"
)
EXIT_CODE=$?

END_MS=$(start_time)
DURATION_MS=$((END_MS - START_MS))

python3 - <<PYEOF
import json
with open("$STDOUT_FILE") as f:
    stdout = f.read(102400)
with open("$STDERR_FILE") as f:
    stderr = f.read(10240)
data = {
    "exit_code": $EXIT_CODE,
    "duration_ms": $DURATION_MS,
    "stdout": stdout,
    "stderr": stderr
}
with open("$OUTPUT_JSON", "w") as f:
    json.dump(data, f, indent=2)
PYEOF
