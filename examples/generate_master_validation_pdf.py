from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        if abs(value) >= 100:
            return f"{value:,.2f}"
        return f"{value:.4f}"
    if isinstance(value, list):
        return ", ".join(fmt(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)


def pct(value: Any) -> str:
    try:
        return f"{float(value) * 100:.2f}%"
    except Exception:
        return "-"


def fit_value(value: Any) -> str:
    try:
        value = float(value)
        if value >= 999000:
            return "no decay fit"
        return f"{value:,.2f}"
    except Exception:
        return "-"


def wilson_bounds(successes: int, total: int) -> tuple[float, float] | None:
    if total <= 0 or successes < 0 or successes > total:
        return None
    z = 1.959963984540054
    p_hat = successes / total
    denom = 1.0 + (z * z / total)
    center = (p_hat + (z * z) / (2.0 * total)) / denom
    margin = z * math.sqrt((p_hat * (1.0 - p_hat) / total) + (z * z) / (4.0 * total * total)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def short_hash(value: Any, n: int = 16) -> str:
    value = str(value or "")
    return value[:n] + ("..." if len(value) > n else "")


def p(text: str, style) -> Paragraph:
    return Paragraph(str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), style)


def table(data: list[list[Any]], widths: list[float] | None = None) -> Table:
    tbl = Table([[fmt(cell) for cell in row] for row in data], colWidths=widths, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("LEADING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return tbl


def add_kv(story: list[Any], title: str, payload: dict[str, Any], keys: list[str], styles) -> None:
    story.append(p(title, styles["Heading3"]))
    rows = [["Field", "Value"]]
    for key in keys:
        if key in payload:
            rows.append([key, payload.get(key)])
    story.append(table(rows, [2.2 * inch, 7.0 * inch]))
    story.append(Spacer(1, 0.10 * inch))


def campaign_sections(root: Path, story: list[Any], styles) -> None:
    campaign_files = [
        ("Accepted vs Rejected Quality Split", "accepted_vs_rejected.json"),
        ("Delay-Ramp Degradation Detection - Inconclusive", "delay_ramp.json"),
        ("Readout Mitigation Repeat", "readout_mitigation_repeat.json"),
        ("Probe Then Commit", "adaptive_probe_then_commit.json"),
        ("Adaptive Backend Selector", "adaptive_backend_selector.json"),
        ("Adaptive Layout Selector", "adaptive_layout_selector.json"),
        ("Adaptive Mitigation Selector", "adaptive_mitigation_selector.json"),
        ("Adaptive Coherence Controller - No Decay Fit", "adaptive_coherence_controller.json"),
        ("Dynamical Decoupling Insertion", "dynamical_decoupling_insertion.json"),
        ("Dynamic Circuit Governance", "dynamic_circuit_governance.json"),
        ("Calibration Campaign", "calibration_campaign.json"),
        ("Pulse-Level Controls", "pulse_level_controls.json"),
    ]
    story.append(p("Detailed Backend Campaign Results", styles["Heading2"]))
    for title, name in campaign_files:
        path = root / name
        if not path.exists():
            continue
        payload = load_json(path)
        story.append(p(title, styles["Heading3"]))
        add_kv(
            story,
            "Run Metadata",
            payload,
            [
                "source",
                "backend",
                "real",
                "status",
                "claim_boundary",
                "selected_backend",
                "selected_sequence",
                "selected_arm",
                "total_shots",
                "mean_raw_ghz",
                "mean_mitigated_ghz",
                "mean_delta",
                "std_delta",
                "success_condition_met",
            ],
            styles,
        )
        if name == "delay_ramp.json":
            story.append(p("Interpretation: this run is preserved as a negative/inconclusive result. The tested delay path did not produce monotonic degradation, so it should not be used as degradation-detection proof.", styles["BodyText"]))
        if name == "adaptive_coherence_controller.json":
            story.append(p("Interpretation: the controller emitted a capped sentinel because the returned outputs did not expose a meaningful decay curve. Treat this as no valid T_eff fit, not as a physical lifetime estimate.", styles["BodyText"]))

        if "acceptance_summary" in payload:
            rows = [["Group", "Count", "Mean GHZ", "Min", "Max", "q_conf mean", "Wilson 95 low", "Wilson 95 high"]]
            for row in payload["acceptance_summary"]:
                ci = row.get("ghz_wilson_95") or {}
                rows.append([
                    row.get("group"),
                    row.get("count"),
                    pct(row.get("mean_ghz")),
                    pct(row.get("min_ghz")),
                    pct(row.get("max_ghz")),
                    row.get("q_conf_mean"),
                    pct(ci.get("low")),
                    pct(ci.get("high")),
                ])
            story.append(table(rows))
            story.append(Spacer(1, 0.1 * inch))

        if "records" in payload:
            rows = [["#", "Job", "Backend", "Shots", "GHZ", "q_conf", "Gate", "Gov", "Latency s"]]
            for i, record in enumerate(payload["records"], 1):
                rows.append([
                    record.get("batch", i),
                    short_hash(record.get("job_id"), 18),
                    record.get("backend"),
                    record.get("shots") or record.get("total_shots"),
                    pct(record.get("ghz_population") or record.get("raw_ghz_population")),
                    record.get("q_conf") or record.get("aegis_raw_q_conf"),
                    record.get("continuity_gate_passed") if "continuity_gate_passed" in record else record.get("aegis_raw_continuity_gate_passed"),
                    record.get("governance_states") or record.get("aegis_raw_governance_states"),
                    record.get("round_trip_seconds"),
                ])
            story.append(table(rows))
            story.append(Spacer(1, 0.1 * inch))

        if "probes" in payload:
            rows = [["Backend", "Job", "Shots", "GHZ", "q_conf", "Score", "Gate", "Error"]]
            for record in payload["probes"]:
                rows.append([
                    record.get("requested_backend") or record.get("backend"),
                    short_hash(record.get("job_id"), 18),
                    record.get("shots"),
                    pct(record.get("ghz_population")),
                    record.get("q_conf"),
                    record.get("selector_score"),
                    record.get("continuity_gate_passed"),
                    record.get("error"),
                ])
            story.append(table(rows))
            story.append(Spacer(1, 0.1 * inch))

        if "committed_run" in payload:
            r = payload["committed_run"]
            rows = [["Backend", "Job", "Shots", "GHZ", "q_conf", "Gate", ".QOM bits", "Merkle"]]
            rows.append([
                r.get("requested_backend") or r.get("backend"),
                short_hash(r.get("job_id"), 18),
                r.get("shots"),
                pct(r.get("ghz_population")),
                r.get("q_conf"),
                r.get("continuity_gate_passed"),
                r.get("qom_compact_payload_bits"),
                short_hash(r.get("merkle_root")),
            ])
            story.append(table(rows))
            story.append(Spacer(1, 0.1 * inch))

        if "comparison" in payload:
            c = payload["comparison"]
            rows = [["Job", "Raw GHZ", "Mitigated GHZ", "Delta", "Aegis q_conf", "Aegis Gate", ".QOM bits"]]
            rows.append([
                short_hash(c.get("job_id"), 18),
                pct(c.get("raw_ghz_population")),
                pct(c.get("mitigated_ghz_population")),
                pct(c.get("mitigation_delta")),
                c.get("aegis_raw_q_conf"),
                c.get("aegis_raw_continuity_gate_passed"),
                c.get("qom_compact_payload_bits"),
            ])
            story.append(table(rows))
            if "decision" in payload:
                d = payload["decision"]
                story.append(table([["Selected Policy", "Reason", "Uplift", "Overhead"], [d.get("selected_policy"), d.get("selection_reason"), pct(d.get("uplift")), pct(d.get("mitigation_overhead"))]]))
            story.append(Spacer(1, 0.1 * inch))

        if "arms" in payload:
            rows = [["Arm/Sequence", "Status", "Job", "Shots", "Survival/GHZ", "Wilson 95%", "Fit t_eff", "Gate"]]
            for arm in payload["arms"]:
                fit = arm.get("fit") or {}
                records = arm.get("records") or []
                if records:
                    for rec in records:
                        rows.append([
                            arm.get("arm") or arm.get("sequence"),
                            arm.get("status"),
                            short_hash(rec.get("job_id"), 18),
                            rec.get("shots"),
                            pct(rec.get("ghz_population")),
                            "",
                            fit_value(fit.get("t_eff_ms")),
                            rec.get("continuity_gate_passed"),
                        ])
                else:
                    ci = arm.get("survival_wilson_95") or {}
                    if not ci and arm.get("survival") is not None and arm.get("shots"):
                        bounds = wilson_bounds(round(float(arm["survival"]) * int(arm["shots"])), int(arm["shots"]))
                        if bounds:
                            ci = {"low": bounds[0], "high": bounds[1]}
                    rows.append([
                        arm.get("arm") or arm.get("sequence"),
                        arm.get("status"),
                        short_hash(arm.get("job_id"), 18),
                        arm.get("shots"),
                        pct(arm.get("survival")),
                        f"{pct(ci.get('low'))} - {pct(ci.get('high'))}" if ci else "",
                        fit_value(fit.get("t_eff_ms")),
                        None,
                    ])
            story.append(table(rows))
            story.append(Spacer(1, 0.1 * inch))

        if "counts" in payload:
            story.append(table([["Counts"], [json.dumps(payload["counts"], sort_keys=True)]]))
            story.append(Spacer(1, 0.1 * inch))

        story.append(Spacer(1, 0.15 * inch))


def sanitized_artifact_sections(root: Path, story: list[Any], styles) -> None:
    raw_dir = root / "docs" / "validation" / "raw_counts_sanitized"
    artifacts = sorted(raw_dir.glob("*.json"))
    story.append(PageBreak())
    story.append(p("Complete Sanitized Validation Vault", styles["Heading2"]))
    story.append(p(f"This appendix lists every sanitized validation artifact currently represented in the public-safe vault: {len(artifacts)} artifacts.", styles["BodyText"]))
    rows = [["Artifact", "Source", "Backend", "Job", "Shots", "GHZ/Raw", "Mitigated/Survival", "Gate/Status", ".QOM", "Merkle"]]
    for path in artifacts:
        payload = load_json(path)
        status = payload.get("status")
        if payload.get("success_condition_met") is not None:
            status = f"success={payload.get('success_condition_met')}"
        rows.append([
            path.name,
            payload.get("source"),
            payload.get("backend") or payload.get("selected_backend"),
            short_hash(payload.get("job_id"), 14),
            payload.get("shots"),
            pct(payload.get("ghz_population") or payload.get("raw_ghz_population")),
            pct(payload.get("mitigated_ghz_population") if payload.get("mitigated_ghz_population") is not None else payload.get("selected_survival")),
            status,
            payload.get("qom_compact_payload_bits"),
            short_hash(payload.get("merkle_root"), 12),
        ])
    story.append(table(rows))


def summary_sections(root: Path, story: list[Any], styles) -> None:
    story.append(p("Executive Rollup", styles["Heading2"]))
    campaign_report = root / "docs" / "validation" / "AEGIS_Adaptive_IBM_Backend_Campaign_2026-05-29.md"
    if campaign_report.exists():
        story.append(p("Source campaign report: docs/validation/AEGIS_Adaptive_IBM_Backend_Campaign_2026-05-29.md", styles["BodyText"]))
    for title, rel in [
        ("Efficiency Summary", "docs/validation/efficiency_summary.json"),
        ("Blind Holdout Summary", "docs/validation/blind_holdout.json"),
        ("Ablation Summary", "docs/validation/ablation_workflow.json"),
    ]:
        path = root / rel
        if path.exists():
            payload = load_json(path)
            story.append(p(title, styles["Heading3"]))
            if "standard_efficiency" in payload:
                e = payload["standard_efficiency"]
                story.append(table([["Artifacts", "Tracked Shots", "Accepted", "Rerun Rate", "Shots / Accepted"], [payload.get("artifact_count"), payload.get("total_tracked_shots"), e.get("accepted_results"), pct(e.get("rerun_rate")), e.get("shots_per_accepted_result")]]))
            elif "holdout_efficiency" in payload:
                h = payload["holdout_efficiency"]
                t = payload["train_efficiency"]
                story.append(table([["Split", "Artifacts", "Accepted", "Rerun Rate", "Shots / Accepted"], ["holdout", payload.get("holdout_count"), h.get("accepted_results"), pct(h.get("rerun_rate")), h.get("shots_per_accepted_result")], ["train", payload.get("train_count"), t.get("accepted_results"), pct(t.get("rerun_rate")), t.get("shots_per_accepted_result")]]))
            elif "modes" in payload:
                rows = [["Mode", "Accepted", "Rerun Rate", "Shots / Accepted", "Accepted Target Quality", "Governed Score"]]
                for mode, values in payload["modes"].items():
                    rows.append([mode, values.get("accepted_results"), pct(values.get("rerun_rate")), values.get("shots_per_accepted_result"), pct(values.get("accepted_target_quality_mean")), values.get("governed_quality_score_mean")])
                story.append(table(rows))
                story.append(p("Ablation quality fields are split: accepted target quality is GHZ/count-derived, while governed score is a stricter software score. They should not be read as one interchangeable metric.", styles["BodyText"]))
            story.append(Spacer(1, 0.12 * inch))


def build_pdf(output: Path) -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER, fontSize=20, leading=24))
    styles["Heading2"].fontSize = 13
    styles["Heading3"].fontSize = 10
    styles["BodyText"].fontSize = 8
    styles["BodyText"].leading = 10

    story: list[Any] = []
    story.append(p("AEGIS Master IBM Quantum Validation Report", styles["TitleCenter"]))
    story.append(p(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} local time", styles["BodyText"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(p("Claim Boundary", styles["Heading2"]))
    story.append(
        p(
            "This report covers real IBM Quantum returned-output ingestion, classical governance, adaptive workload selection, mitigation selection, .QOM serialization, Merkle lineage, and hardware-feature harness behavior. It does not claim intrinsic device noise suppression, intrinsic T1/T2 improvement, or real-time pulse-level control over public IBM backends.",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 0.2 * inch))
    summary_sections(ROOT, story, styles)
    story.append(PageBreak())
    campaign_sections(ROOT, story, styles)
    sanitized_artifact_sections(ROOT, story, styles)

    doc = SimpleDocTemplate(
        str(output),
        pagesize=landscape(letter),
        rightMargin=0.35 * inch,
        leftMargin=0.35 * inch,
        topMargin=0.35 * inch,
        bottomMargin=0.35 * inch,
        title="AEGIS Master IBM Quantum Validation Report",
    )
    doc.build(story)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate master PDF for all AEGIS IBM validation results.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build_pdf(args.output)
    print(json.dumps({"pdf": str(args.output), "bytes": args.output.stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
