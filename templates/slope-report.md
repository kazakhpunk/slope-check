# Slope Report: {project_name}

Date: {date}
Target: {target_url_or_path}
Overall Slope Score: {verified_count}/{scoreable_count} claims verified ({percentage}%)
Report Confidence: {confidence_level}

---

## Summary

{narrative_summary}

---

## Claims

| # | Claim | Source | Verdict | Confidence | Cross-ref | Mode |
|---|-------|--------|---------|------------|-----------|------|
{claims_table_rows}

Verdicts: VERIFIED / PARTIAL / WEAK / REFUTED / UNVERIFIABLE
Mode: STATIC (static audit only) / LIVE (benchmark runner result available)

---

## Charts

### Slope Bar Chart

![Slope Bar Chart](charts/slope-bar.png)

Bar A = 100 (claimed value baseline). Bar B = Reproducibility Confidence Score. Bar C = actual/claimed x 100 (LIVE mode only).
Color: yellow (confidence >= 80), orange (50-79), red (< 50). Hatched grey = insufficient data.

### Red Flag Distribution

![Red Flag Distribution](charts/red-flags.png)

Stacked bars by red flag type per claim.

---

## Detailed Findings

{detailed_findings_per_claim}

---

## Red Flags

{red_flags_list_or_none_detected}

---

## Methodology Notes

{methodology_notes}

---

## Environment

{environment_section_run_only}
