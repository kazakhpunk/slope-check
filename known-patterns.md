# Known Benchmark Inflation Patterns

This file is consulted by the static-auditor before any web search.
Entries marked [DRAFT] require human review before becoming active.

---

## Pattern: mteb-subset-cherry-picking
- Benchmark: MTEB
- Signal: Paper reports MTEB score without specifying which tasks were run
- Red flag type: methodology_mismatch
- Detection: claim references "MTEB" but no task subset or task count listed in methodology section
- Notes: Full MTEB covers 56 tasks across retrieval, clustering, classification, etc. Reporting on a favorable subset inflates apparent performance. Always check if the paper specifies which tasks.

---

## Pattern: squad-version-confusion
- Benchmark: SQuAD
- Signal: Paper uses SQuAD v1.1 numbers as a SQuAD 2.0 baseline comparison
- Red flag type: weak_baseline
- Detection: claim references "SQuAD" baseline without specifying version; check if cited score is ~88 F1 (v1.1) used as v2.0 comparison
- Notes: SQuAD 2.0 includes unanswerable questions, making it significantly harder. Using v1.1 scores as a v2.0 baseline artificially inflates the apparent improvement.

---

## Pattern: bm25-version-mismatch
- Benchmark: BM25 retrieval baseline
- Signal: Paper compares against an outdated BM25 implementation
- Red flag type: weak_baseline
- Detection: BM25 baseline score is more than 5 points below current Pyserini BM25 on the same dataset
- Notes: BM25 implementations vary significantly. Older implementations score lower, making neural retrieval improvements appear larger than they are.

---

## Pattern: single-batch-latency
- Benchmark: Inference speed / latency
- Signal: Speed claim tested only at batch_size=1
- Red flag type: methodology_mismatch
- Detection: eval script or paper mentions only batch_size=1 for latency measurements; no throughput at larger batch sizes reported
- Notes: batch_size=1 latency is optimal for transformer-based models and unrepresentative of real serving conditions. Reporting only this metric inflates apparent speed advantages.

---

## Pattern: huggingface-leaderboard-drift
- Benchmark: HuggingFace Open LLM Leaderboard
- Signal: Baseline model version on leaderboard changed after paper publication
- Red flag type: weak_baseline
- Detection: baseline model name matches a model on the leaderboard but the score has changed since the paper's submission date
- Notes: Models on the HuggingFace leaderboard are sometimes re-evaluated with updated harnesses, changing their scores. Papers citing old scores may be comparing against a weaker (or stronger) version.
