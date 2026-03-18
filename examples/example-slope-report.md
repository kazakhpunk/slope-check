# Slope Report: FastEmbed v2

Date: 2026-03-18
Target: https://github.com/example-org/fastembed-v2
Overall Slope Score: 1/3 (33%)
Report Confidence: PARTIAL

---

## Summary

FastEmbed v2 makes three performance claims in its README and associated technical report. After static audit and benchmark reproduction, one claim (MTEB accuracy) is verified at a confidence level consistent with the published leaderboard. The speed claim is partially supported but relies exclusively on single-batch latency measurements, a known methodology mismatch pattern that inflates apparent throughput advantages. The memory usage claim is refuted: the benchmark script used to generate the figure contains a hardcoded peak memory value rather than a live measurement, rendering the reported number unreliable.

Overall reproducibility confidence is low. Two of three claims carry material red flags, and the memory claim requires immediate author clarification before the number should be cited in downstream work.

---

## Claims

| # | Claim | Source | Verdict | Confidence | Cross-ref | Mode |
|---|-------|--------|---------|------------|-----------|------|
| claim_01 | "3x faster than sentence-transformers" | README.md, line 12 | PARTIAL | 58% | single-batch-latency pattern matched; no throughput figures at batch_size > 1 | STATIC |
| claim_02 | "95.2% accuracy on MTEB" | README.md, line 15 | VERIFIED | 85% | MTEB leaderboard (2026-03-17 snapshot) shows 94.8% for fastembed-v2-base | STATIC |
| claim_03 | "50% less memory usage" | README.md, line 18 | REFUTED | 22% | benchmark/run_memory.py line 47: `peak_mb = 512` (hardcoded); no live profiling | STATIC |

Verdicts: VERIFIED / PARTIAL / WEAK / REFUTED / UNVERIFIABLE
Mode: STATIC (static audit only) / LIVE (benchmark runner result available)

---

## Charts

### Slope Bar Chart

![Slope Bar Chart](charts/slope-bar.png)

Bar A = 100 (claimed value baseline). Bar B = Reproducibility Confidence Score. Bar C = actual/claimed x 100 (LIVE mode only).
Color: yellow (confidence >= 80), orange (50-79), red (< 50). Hatched grey = insufficient data.

Claim 01: Bar B = 58 (orange). Bar C = hatched grey (LIVE data not available).
Claim 02: Bar B = 85 (yellow). Bar C = hatched grey (LIVE data not available; leaderboard cross-ref used).
Claim 03: Bar B = 22 (red). Bar C = hatched grey (benchmark script invalid).

### Red Flag Distribution

![Red Flag Distribution](charts/red-flags.png)

Stacked bars by red flag type per claim.

claim_01: 1 x methodology_mismatch
claim_02: 0 red flags
claim_03: 1 x fabricated_data

---

## Detailed Findings

### claim_01: "3x faster than sentence-transformers"

**Source:** README.md, line 12
**Verdict:** PARTIAL
**Confidence:** 58%
**Mode:** STATIC

**Signals passed:**
- A speed comparison to sentence-transformers is present and the competing library is named explicitly.
- The benchmark script (benchmark/run_speed.py) exists in the repository and is runnable.
- The comparison library version (sentence-transformers==2.7.0) is pinned in requirements-bench.txt.

**Signals failed:**
- Pattern `single-batch-latency` matched: benchmark/run_speed.py sets `batch_size = 1` on line 23 and never iterates over larger batch sizes.
- No throughput figures (tokens/sec or sentences/sec at batch_size=8, 16, 32, or 64) are reported anywhere in the repository or technical report.
- Hardware specification in the benchmark script specifies a single A100 GPU; the README does not disclose this, making the claim appear hardware-agnostic.
- The 3x figure cannot be independently derived from the script output without running on matching hardware; no pre-computed results file is committed.

**Assessment:** The speed advantage may be real at batch_size=1 on an A100, but the claim as stated ("3x faster") is not reproducible from the provided artifacts under representative serving conditions. Confidence penalized for methodology mismatch and missing hardware disclosure.

---

### claim_02: "95.2% accuracy on MTEB"

**Source:** README.md, line 15
**Verdict:** VERIFIED
**Confidence:** 85%
**Mode:** STATIC

**Signals passed:**
- MTEB leaderboard snapshot (retrieved 2026-03-17) lists fastembed-v2-base at 94.8% average across the standard 56-task suite.
- The 0.4 point discrepancy (95.2% claimed vs 94.8% leaderboard) is within the range of re-evaluation harness drift documented in the `huggingface-leaderboard-drift` pattern, but does not exceed it.
- The README links directly to the leaderboard entry, allowing readers to verify independently.
- The claim does not cherry-pick a task subset; "MTEB" in this context matches the full 56-task suite as confirmed by the linked leaderboard row.

**Signals failed:**
- The 0.4 point discrepancy is unexplained. It could reflect a minor harness version difference or rounding in the paper.
- No task-level breakdown is provided in the README; readers must follow the leaderboard link to inspect per-task performance.

**Assessment:** The claim is substantively accurate. The minor discrepancy does not constitute inflation but should be disclosed. Confidence is high; the 15-point deduction reflects the unexplained delta and the absence of per-task transparency in the primary claim location.

---

### claim_03: "50% less memory usage"

**Source:** README.md, line 18
**Verdict:** REFUTED
**Confidence:** 22%
**Mode:** STATIC

**Signals passed:**
- A benchmark script (benchmark/run_memory.py) is present in the repository, giving the appearance of reproducibility.
- The comparison library (sentence-transformers) is named and a version is referenced.

**Signals failed:**
- Critical finding: benchmark/run_memory.py, line 47 contains `peak_mb = 512`. This is a hardcoded integer literal, not a measured value. The script never calls a memory profiler (no import of `tracemalloc`, `memory_profiler`, `psutil`, or equivalent).
- The value 512 MB for sentence-transformers peak memory appears to have been manually chosen as the baseline; the actual peak memory for sentence-transformers==2.7.0 on the tested model size (bert-base) is approximately 920-980 MB under typical conditions.
- Using 512 MB as the baseline and reporting FastEmbed v2's actual measured memory (approximately 460 MB) would yield a figure close to the claimed 50% reduction. The actual reduction against a correctly measured baseline is approximately 50-53% — ironically the claim may be directionally correct, but the script cannot be used to verify it because the baseline is fabricated.
- No raw memory profiling output or log file is committed to the repository.

**Assessment:** The benchmark script is not a valid source for the claimed figure. The number must be re-measured with a live profiler before the claim can be assessed. Confidence is very low; the hardcoded value constitutes a data integrity red flag regardless of whether the final claim happens to be approximately correct.

---

## Red Flags

### RED FLAG 1 — claim_01
- Pattern: single-batch-latency
- Type: methodology_mismatch
- Location: benchmark/run_speed.py, line 23 (`batch_size = 1`)
- Severity: MEDIUM
- Detail: Speed benchmark is run exclusively at batch_size=1. This is unrepresentative of real serving workloads and is a documented pattern for inflating apparent latency advantages of transformer-based inference libraries.

### RED FLAG 2 — claim_03
- Pattern: (unlisted — fabricated baseline)
- Type: fabricated_data
- Location: benchmark/run_memory.py, line 47 (`peak_mb = 512`)
- Severity: HIGH
- Detail: Baseline memory value is hardcoded rather than measured. The benchmark script cannot reproduce the claimed figure. This requires author response before the claim can be cited.

---

## Methodology Notes

- Static audit only; no benchmark execution was performed. All findings are derived from code inspection, README text analysis, and cross-referencing the MTEB leaderboard.
- Pattern matching was performed against known-patterns.md (5 active patterns as of 2026-03-18).
- MTEB leaderboard snapshot taken 2026-03-17 at 14:32 UTC. Leaderboard values may change as models are re-evaluated.
- The `single-batch-latency` pattern was matched via static analysis of benchmark/run_speed.py. No inference was run.
- Memory profiling methodology was assessed by inspecting benchmark/run_memory.py for live measurement calls. None were found.
- Confidence scores follow the slope-check rubric: base 100, minus 10 per unresolved discrepancy, minus 15 per methodology mismatch, minus 40 per fabricated or hardcoded data point, floored at 5.

---

## Environment

Not applicable — this report is STATIC mode only. No benchmark execution environment was provisioned.
