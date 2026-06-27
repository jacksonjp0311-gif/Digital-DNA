from __future__ import annotations

from engine.cli import main
from engine.orchestrator.run_ddna import run_scan
from engine.reporting import render_html, render_markdown


def test_run_scan_can_return_record_without_writing():
    record = run_scan(write_artifact=False)

    assert "stability" in record
    assert abs(float(record["stability"]) - (float(record["retention"]) - float(record["drift"]))) < 1e-9


def test_report_renderers_include_core_metrics():
    record = run_scan(write_artifact=False)

    markdown = render_markdown(record)
    html = render_html(record)

    assert "Digital-DNA Structural Report" in markdown
    assert "Stability" in html
    assert "<!doctype html>" in html


def test_cli_gate_fails_when_threshold_is_impossible():
    assert main(["gate", "--min-stability", "2.0", "--format", "json"]) == 2
