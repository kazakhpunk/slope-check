# Slope Check Plugin — Project Conventions

## Core principles

- Skepticism by default: assume claims are inflated until signals suggest otherwise
- REFUTED requires positive contradicting evidence — low confidence alone is never enough to refute
- Never penalize a claim for missing external data; mark it UNVERIFIABLE, not REFUTED
- Always cite exact source location: file + line number, or URL + section heading
- Reproducibility Confidence is a score (0-100); verdict is a separate judgment derived from it
- No emojis anywhere in reports, agent output, or plugin scaffolding
- The --run flag requires explicit user confirmation before any code from a target repo is executed
- Reports are saved to ./slope-reports/ relative to where the plugin is invoked
- claims.json is read-only after claim-extractor completes; no downstream agent may modify it

## Agent communication

All agents communicate via files in slope-reports/{project-slug}/. Never pass data in memory between agents. Each agent reads its inputs, writes its outputs, and exits.

## Known patterns

The static-auditor MUST consult known-patterns.md before performing any web search. Matched patterns take precedence over generic red flag detection.

## Report tone

Reports are factual and cite specific evidence. Do not speculate beyond what the signals support. When uncertain, say so explicitly.
