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


if __name__ == "__main__":
    mcp.run()
