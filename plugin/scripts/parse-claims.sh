#!/usr/bin/env bash
# parse-claims.sh — regex pre-filter for candidate claim lines
# Usage: parse-claims.sh <file_path>
# Output: line_number:line_content for each matching line
# Exit 0 + empty output if no matches. Non-zero on error.

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: parse-claims.sh <file_path>" >&2
  exit 1
fi

FILE="$1"

if [ ! -f "$FILE" ]; then
  echo "Error: file not found: $FILE" >&2
  exit 1
fi

if [ ! -r "$FILE" ]; then
  echo "Error: permission denied: $FILE" >&2
  exit 1
fi

# Match lines containing benchmark/claim patterns
grep -niE '[0-9]+(\.[0-9]+)?%|[0-9]+(\.[0-9]+)?x[[:space:]]|outperform|faster than|better than|compared to|\b(accuracy|F1|BLEU|ROUGE|MTEB|MMLU|SQuAD|GLUE|WER|perplexity)\b|state.of.the.art|SOTA|surpasses|latency|throughput|tokens per second|memory|VRAM' "$FILE" 2>/dev/null || true
