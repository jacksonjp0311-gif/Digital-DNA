from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def render_markdown(record: dict[str, Any]) -> str:
    lines = [
        "# Digital-DNA Structural Report",
        "",
        f"**Stability:** `{float(record['stability']):.6f}`",
        f"**Retention:** `{float(record['retention']):.6f}`",
        f"**Drift:** `{float(record['drift']):.6f}`",
        "",
        "## Drift Channels",
        "",
        "| Channel | Value |",
        "| --- | ---: |",
        f"| Topology | {float(record['drift_topology']):.6f} |",
        f"| Dependency | {float(record['drift_dependency']):.6f} |",
        f"| Raw weighted drift | {float(record['drift_raw']):.6f} |",
        "",
        "## Weights",
        "",
        "| Weight | Value |",
        "| --- | ---: |",
    ]
    weights = record.get("weights", {})
    for key in sorted(weights):
        lines.append(f"| {key} | {float(weights[key]):.6f} |")
    lines.extend(
        [
            "",
            "## Invariant",
            "",
            "`stability = retention - clamp(weighted_drift, 0, 1)`",
            "",
            f"Timestamp: `{record.get('timestamp', '')}`",
        ]
    )
    return "\n".join(lines) + "\n"


def render_html(record: dict[str, Any]) -> str:
    markdown = render_markdown(record)
    status = "pass" if float(record["stability"]) >= 0 else "fail"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Digital-DNA Structural Report</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;max-width:980px;margin:32px auto;padding:0 20px;color:#17202a;line-height:1.5;}}
h1{{font-size:30px;margin:0 0 12px;letter-spacing:0;}}
.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0 24px;}}
.metric{{border:1px solid #d7dde5;border-radius:8px;background:#f7f9fc;padding:12px;}}
.label{{font-size:12px;color:#5b6472;text-transform:uppercase;font-weight:700;}}
.value{{font-size:22px;font-weight:700;margin-top:4px;}}
.pass{{color:#0f766e;}}.fail{{color:#b42318;}}
pre{{background:#101827;color:#e5e7eb;padding:16px;border-radius:8px;overflow:auto;}}
</style>
</head>
<body>
<h1>Digital-DNA Structural Report</h1>
<div class="summary">
<div class="metric"><div class="label">Stability</div><div class="value {status}">{float(record['stability']):.6f}</div></div>
<div class="metric"><div class="label">Retention</div><div class="value">{float(record['retention']):.6f}</div></div>
<div class="metric"><div class="label">Drift</div><div class="value">{float(record['drift']):.6f}</div></div>
</div>
<pre>{html.escape(markdown)}</pre>
</body>
</html>
"""


def load_record(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
