from __future__ import annotations

from engine.cli import main
from engine.orchestrator.run_ddna import run_scan
from jsonschema import validate

from engine.policy import DEFAULT_POLICY, attach_gate, evaluate_gate
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


def test_policy_gate_reports_violations():
    record = run_scan(write_artifact=False)
    policy = dict(DEFAULT_POLICY)
    policy["min_stability"] = 2.0

    gate = evaluate_gate(record, policy)

    assert gate.passed is False
    assert any("stability" in item for item in gate.violations)


def test_report_includes_gate_metadata():
    record = run_scan(write_artifact=False)
    gate = evaluate_gate(record, dict(DEFAULT_POLICY))
    markdown = render_markdown(attach_gate(record, gate))

    assert "## Gate" in markdown
    assert "Status" in markdown


def test_record_schema_accepts_gate_record():
    import json
    from pathlib import Path

    record = run_scan(write_artifact=False)
    gate = evaluate_gate(record, dict(DEFAULT_POLICY))
    schema = json.loads(Path("schema/ddna_record.schema.json").read_text(encoding="utf-8"))

    validate(attach_gate(record, gate), schema)
