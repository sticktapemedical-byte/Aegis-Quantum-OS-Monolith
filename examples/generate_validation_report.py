from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def bar(width: int, value: float) -> str:
    filled = max(0, min(width, int(round(width * value))))
    return "#" * filled + "." * (width - filled)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate lightweight validation CSV/Markdown/SVG report artifacts.")
    parser.add_argument("--artifacts", type=Path, default=Path("docs/validation/raw_counts_sanitized"))
    parser.add_argument("--outdir", type=Path, default=Path("docs/validation/reports"))
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    plot_dir = args.outdir / "plots"
    plot_dir.mkdir(exist_ok=True)
    rows = []
    for path in sorted(args.artifacts.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        rows.append({
            "artifact": path.name,
            "backend": record.get("backend", ""),
            "shots": record.get("shots", record.get("total_shots", "")),
            "ghz_population": record.get("ghz_population", record.get("raw_ghz_population", "")),
            "q_conf": record.get("q_conf", record.get("aegis_raw_q_conf", "")),
            "gate": record.get("continuity_gate_passed", record.get("aegis_raw_continuity_gate_passed", "")),
        })
    csv_path = args.outdir / "metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["artifact"])
        writer.writeheader()
        writer.writerows(rows)
    md_path = args.outdir / "validation_summary.md"
    lines = ["# AEGIS Validation Summary", "", "| Artifact | Backend | Shots | GHZ/Quality | q_conf | Gate |", "| --- | --- | ---: | ---: | ---: | --- |"]
    for row in rows:
        lines.append(f"| {row['artifact']} | {row['backend']} | {row['shots']} | {row['ghz_population']} | {row['q_conf']} | {row['gate']} |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    svg_lines = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="520">', '<rect width="100%" height="100%" fill="white"/>']
    y = 25
    for row in rows[:18]:
        try:
            value = float(row["ghz_population"])
        except Exception:
            value = 0.0
        svg_lines.append(f'<text x="10" y="{y}" font-size="11">{row["artifact"][:42]}</text>')
        svg_lines.append(f'<rect x="330" y="{y-10}" width="{int(500*value)}" height="12" fill="#2563eb"/>')
        svg_lines.append(f'<text x="840" y="{y}" font-size="11">{value:.3f} {bar(10, value)}</text>')
        y += 26
    svg_lines.append("</svg>")
    svg_path = plot_dir / "ghz_quality_bars.svg"
    svg_path.write_text("\n".join(svg_lines), encoding="utf-8")
    payload = {
        "source": "aegis_validation_report_generator",
        "rows": len(rows),
        "metrics_csv": str(csv_path),
        "summary_markdown": str(md_path),
        "plot_svg": str(svg_path),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
