#!/usr/bin/env bash
# sandbox-run.sh — isolated benchmark execution wrapper
# Usage: sandbox-run.sh <output_json> <working_dir> <command> [args...]

set -euo pipefail

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

START_MS=$(python3 -c "import time; print(int(time.time()*1000))")

set +e
(
  cd "$WORKING_DIR"
  ulimit -v $((2 * 1024 * 1024)) 2>/dev/null || true
  timeout 300 "${CMD[@]}" >"$STDOUT_FILE" 2>"$STDERR_FILE"
)
EXIT_CODE=$?
set -e

END_MS=$(python3 -c "import time; print(int(time.time()*1000))")
DURATION_MS=$((END_MS - START_MS))

SANDBOX_EXIT="$EXIT_CODE" \
SANDBOX_DURATION="$DURATION_MS" \
SANDBOX_STDOUT="$STDOUT_FILE" \
SANDBOX_STDERR="$STDERR_FILE" \
SANDBOX_OUTPUT="$OUTPUT_JSON" \
python3 - <<'PYEOF'
import json, os

with open(os.environ["SANDBOX_STDOUT"]) as f:
    stdout = f.read(102400)
with open(os.environ["SANDBOX_STDERR"]) as f:
    stderr = f.read(10240)

data = {
    "exit_code": int(os.environ["SANDBOX_EXIT"]),
    "duration_ms": int(os.environ["SANDBOX_DURATION"]),
    "stdout": stdout,
    "stderr": stderr
}

with open(os.environ["SANDBOX_OUTPUT"], "w") as f:
    json.dump(data, f, indent=2)
PYEOF
