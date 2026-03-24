#!/usr/bin/env python3
"""Slope-check MCP server — stateless query layer over slope-reports/ JSON artifacts."""

import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("slope-check")

REPORTS_DIR = Path(os.environ.get("SLOPE_REPORTS_DIR", "slope-reports"))


def _read_json(slug: str, filename: str) -> list | dict | None:
    path = REPORTS_DIR / slug / filename
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def _parse_report_header(slug: str) -> dict:
    """Extract date, target, and overall score from slope-report.md header."""
    report_path = REPORTS_DIR / slug / "slope-report.md"
    header = {"slug": slug, "date": None, "target": None, "overall_score": None}
    if not report_path.exists():
        return header
    with open(report_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("# Slope Report:"):
                header["target"] = line.removeprefix("# Slope Report:").strip()
            elif line.startswith("**Generated:**"):
                header["date"] = line.removeprefix("**Generated:**").strip()
            elif line.startswith("**Overall Slope Score:**"):
                header["overall_score"] = line.removeprefix("**Overall Slope Score:**").strip()
                break
    return header


@mcp.tool()
def list_audits() -> list[dict]:
    """List all completed audits in slope-reports/ with date, target, and overall score."""
    if not REPORTS_DIR.exists():
        return []
    results = []
    for entry in sorted(REPORTS_DIR.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            header = _parse_report_header(entry.name)
            results.append(header)
    return results


@mcp.tool()
def query_claims(slug: str, type_filter: str | None = None) -> dict:
    """Query extracted claims for an audit. Optionally filter by claim type (speed/accuracy/memory/quality/capability).

    Args:
        slug: The audit slug (directory name under slope-reports/)
        type_filter: Optional claim type to filter by
    """
    claims = _read_json(slug, "claims.json")
    if claims is None:
        return {"error": f"No claims.json found for slug '{slug}'"}
    if type_filter:
        claims = [c for c in claims if c.get("type") == type_filter]
    return {"slug": slug, "count": len(claims), "claims": claims}


def _extract_verdicts(slug: str) -> dict[str, str]:
    """Parse verdict table from slope-report.md to map claim_id -> verdict."""
    report_path = REPORTS_DIR / slug / "slope-report.md"
    verdicts = {}
    if not report_path.exists():
        return verdicts
    in_table = False
    with open(report_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("| ID "):
                in_table = True
                continue
            if in_table and line.startswith("|---"):
                continue
            if in_table and line.startswith("|"):
                cols = [c.strip() for c in line.split("|")]
                # cols: ['', 'claim_01', 'Claim text...', 'type', 'score', 'quality', 'verdict', 'tag', '']
                if len(cols) >= 8:
                    verdicts[cols[1]] = cols[6]
            elif in_table and not line.startswith("|"):
                in_table = False
    return verdicts


@mcp.tool()
def query_audit(
    slug: str,
    confidence_lt: int | None = None,
    confidence_gt: int | None = None,
    verdict: str | None = None,
    has_red_flags: bool | None = None,
) -> dict:
    """Query audit results with optional filters.

    Args:
        slug: The audit slug (directory name under slope-reports/)
        confidence_lt: Only return claims with confidence score below this value
        confidence_gt: Only return claims with confidence score above this value
        verdict: Filter by verdict (VERIFIED/PARTIAL/WEAK/REFUTED/UNVERIFIABLE)
        has_red_flags: If true, only return claims that have red flags
    """
    audit = _read_json(slug, "audit.json")
    if audit is None:
        return {"error": f"No audit.json found for slug '{slug}'"}

    report_verdicts = _extract_verdicts(slug) if verdict else {}

    filtered = []
    for entry in audit:
        cid = entry.get("id", "")
        score = entry.get("confidence_score", 0)

        if confidence_lt is not None and score >= confidence_lt:
            continue
        if confidence_gt is not None and score <= confidence_gt:
            continue
        if has_red_flags is True and not entry.get("red_flags"):
            continue
        if has_red_flags is False and entry.get("red_flags"):
            continue
        if verdict and report_verdicts.get(cid, "").upper() != verdict.upper():
            continue

        filtered.append(entry)

    return {"slug": slug, "count": len(filtered), "entries": filtered}


@mcp.tool()
def get_claim_detail(slug: str, claim_id: str) -> dict:
    """Get full detail for a single claim: claim data + audit + results (if available).

    Args:
        slug: The audit slug (directory name under slope-reports/)
        claim_id: The claim ID (e.g. "claim_01")
    """
    claims = _read_json(slug, "claims.json")
    if claims is None:
        return {"error": f"No claims.json found for slug '{slug}'"}

    claim = next((c for c in claims if c.get("id") == claim_id), None)
    if claim is None:
        return {"error": f"Claim '{claim_id}' not found in slug '{slug}'"}

    detail = {"claim": claim, "audit": None, "result": None, "verdict": None}

    audit = _read_json(slug, "audit.json")
    if audit:
        detail["audit"] = next((a for a in audit if a.get("id") == claim_id), None)

    results = _read_json(slug, "results.json")
    if results:
        detail["result"] = next((r for r in results if r.get("id") == claim_id), None)

    verdicts = _extract_verdicts(slug)
    detail["verdict"] = verdicts.get(claim_id)

    return detail


@mcp.tool()
def compare_audits(slug_a: str, slug_b: str) -> dict:
    """Compare two audits side-by-side: score differences, verdict changes, new/removed claims.

    Args:
        slug_a: First audit slug
        slug_b: Second audit slug
    """
    header_a = _parse_report_header(slug_a)
    header_b = _parse_report_header(slug_b)

    audit_a = _read_json(slug_a, "audit.json")
    audit_b = _read_json(slug_b, "audit.json")

    if audit_a is None:
        return {"error": f"No audit.json found for slug '{slug_a}'"}
    if audit_b is None:
        return {"error": f"No audit.json found for slug '{slug_b}'"}

    verdicts_a = _extract_verdicts(slug_a)
    verdicts_b = _extract_verdicts(slug_b)

    scores_a = {e["id"]: e.get("confidence_score", 0) for e in audit_a}
    scores_b = {e["id"]: e.get("confidence_score", 0) for e in audit_b}

    ids_a = set(scores_a.keys())
    ids_b = set(scores_b.keys())

    common = ids_a & ids_b
    score_diffs = []
    for cid in sorted(common):
        diff = scores_b[cid] - scores_a[cid]
        score_diffs.append({
            "id": cid,
            "score_a": scores_a[cid],
            "score_b": scores_b[cid],
            "diff": diff,
            "verdict_a": verdicts_a.get(cid),
            "verdict_b": verdicts_b.get(cid),
        })

    return {
        "audit_a": header_a,
        "audit_b": header_b,
        "only_in_a": sorted(ids_a - ids_b),
        "only_in_b": sorted(ids_b - ids_a),
        "common_claims": len(common),
        "score_changes": score_diffs,
    }


if __name__ == "__main__":
    mcp.run()
