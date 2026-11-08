"""Render audited live analysis as matching SVG/PDF; Python standard library only.

This presentation tool does not acquire models, change scores, bootstrap again,
or alter the frozen acquisition source. Input must be run_live.py analyze output.
"""

import argparse
import html
import json
from pathlib import Path


WIDTH, HEIGHT = 940, 560
INK, MUTED, BLUE, LIGHT = "#172b3a", "#516575", "#1b668c", "#a9c4d2"


class Canvas:
    def __init__(self):
        self.svg, self.pdf = [], []

    @staticmethod
    def color(value):
        return " ".join(f"{int(value[i:i+2], 16)/255:.5f}" for i in (1, 3, 5))

    def text(self, x, y, text, size=16, color=INK):
        text = str(text)
        self.svg.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{html.escape(text)}</text>')
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        escaped.encode("ascii")
        self.pdf.append(f"BT /F1 {size} Tf {self.color(color)} rg 1 0 0 1 {x} {HEIGHT-y} Tm ({escaped}) Tj ET")

    def line(self, x1, y1, x2, y2, color=INK, width=1):
        self.svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')
        self.pdf.append(f"{self.color(color)} RG {width} w {x1} {HEIGHT-y1} m {x2} {HEIGHT-y2} l S")

    def dot(self, x, y, radius=4, color=BLUE):
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}"/>')
        y, k, r = HEIGHT-y, radius*0.55228475, radius
        self.pdf.append(f"{self.color(color)} rg {x+r} {y} m "
            f"{x+r} {y+k} {x+k} {y+r} {x} {y+r} c "
            f"{x-k} {y+r} {x-r} {y+k} {x-r} {y} c "
            f"{x-r} {y-k} {x-k} {y-r} {x} {y-r} c "
            f"{x+k} {y-r} {x+r} {y-k} {x+r} {y} c f")

    def write(self, stem):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
               f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img">'
               '<title>Certificate scope, false assurance and useful completion</title>'
               '<desc>Counts, marginal Wilson intervals and paired uncertainty from audited live model responses.</desc>'
               f'<rect width="{WIDTH}" height="{HEIGHT}" fill="white"/>'
               '<g font-family="Arial, Helvetica, sans-serif">' + "".join(self.svg) + '</g></svg>\n')
        with Path(str(stem) + ".svg").open("x") as stream:
            stream.write(svg)
        content = "\n".join(self.pdf).encode("ascii")
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {WIDTH} {HEIGHT}] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>".encode(),
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            f"<< /Length {len(content)} >>\nstream\n".encode() + content + b"\nendstream",
        ]
        data, offsets = bytearray(b"%PDF-1.4\n"), [0]
        for number, obj in enumerate(objects, 1):
            offsets.append(len(data))
            data.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
        xref = len(data)
        data.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
        for offset in offsets[1:]:
            data.extend(f"{offset:010d} 00000 n \n".encode())
        data.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
        with Path(str(stem) + ".pdf").open("xb") as stream:
            stream.write(data)


def count(rate):
    return f'{rate["numerator"]}/{rate["denominator"]}'


def render(report):
    if report.get("mode") != "live_model_acquisition" or report.get("split") not in ("dev", "holdout"):
        raise ValueError("figure requires explicitly audited live analysis, not a test double")
    if not report.get("acquisition_audit", {}).get("valid"):
        raise ValueError("missing successful acquisition audit")
    canvas = Canvas()
    stage = "Held-out evaluation" if report["split"] == "holdout" else "Development pilot (not confirmatory)"
    canvas.text(24, 30, "Verified, but What? Certificate scope and useful completion", 22)
    canvas.text(24, 52, f'{stage}; {report["configuration"]["model"]} / {report["configuration"]["provider_response_name"]}', 16, MUTED)

    def panel(x, title, group, metric):
        canvas.text(x, 89, title, 18)
        left, right, axis_y = x+55, x+330, 252
        for tick in (0, .25, .5, .75, 1):
            px = left + (right-left)*tick
            canvas.line(px, 112, px, axis_y, "#e1e8ec", .7)
            canvas.text(px-12, axis_y+19, f"{tick*100:g}", 14, MUTED)
        for row, arm in enumerate(("B", "N", "S")):
            outcome = report["groups"][group][arm]
            rate = outcome[metric]
            y = 131 + row*45
            canvas.text(x+6, y+5, arm, 18)
            if rate["estimate"] is not None:
                interval = rate["wilson95"]
                if interval is not None:
                    lo, hi = [left+(right-left)*v for v in interval]
                    canvas.line(lo, y, hi, y, BLUE, 2)
                    canvas.line(lo, y-5, lo, y+5, BLUE)
                    canvas.line(hi, y-5, hi, y+5, BLUE)
                elif metric == "observed_false_safe_all_scheduled":
                    lo, hi = [left+(right-left)*v for v in outcome["full_sample_false_safe_bounds"]]
                    canvas.line(lo, y, hi, y, LIGHT, 5)
                canvas.dot(left+(right-left)*rate["estimate"], y)
            canvas.text(right+14, y+5, count(rate), 16)
        canvas.text(left+45, axis_y+38, "Percent of scheduled cases", 16, MUTED)

    panel(24, "A. False SAFE on planted faults", "fault", "observed_false_safe_all_scheduled")
    panel(488, "B. Correct equivalent controls", "equivalent", "correct_completion")
    canvas.text(24, 323, "C. Paired false-SAFE difference (percentage points)", 18)
    left, right, y_axis = 185, 720, 435
    for tick in (-1, -.5, 0, .5, 1):
        x = left+(right-left)*(tick+1)/2
        canvas.line(x, 341, x, y_axis, "#e1e8ec", .7)
        canvas.text(x-15, y_axis+17, f"{100*tick:g}", 14, MUTED)
    for y, key, label in ((365, "primary_fault_S_minus_B", "S minus B (primary)"),
                          (405, "secondary_fault_N_minus_B", "N minus B")):
        result = report[key]
        canvas.text(24, y+5, label, 16)
        point = result["difference"]
        if point is not None:
            for name, color, width in (("bounded_iid_hoeffding95", LIGHT, 6), ("bootstrap95", BLUE, 2)):
                lo, hi = [left+(right-left)*(v+1)/2 for v in result[name]]
                canvas.line(lo, y, hi, y, color, width)
            canvas.dot(left+(right-left)*(point+1)/2, y)
        canvas.text(744, y+5, f'{result["complete_pairs"]}/{result["scheduled_pairs"]} complete pairs', 16)
    natural = report["groups"]["natural"]["B"]
    drift = report["natural_drift_among_valid_translations"]
    canvas.text(24, 486, f'Natural pipeline: changed C/Q {count(drift)} valid translations; correct originals {count(natural["correct_completion"])}.', 16)
    canvas.text(24, 510, "A/B: marginal 95% Wilson intervals; pale range in A marks missingness bounds when needed.", 16, MUTED)
    canvas.text(24, 528, "C: dark paired bootstrap; pale bounded-iid Hoeffding interval. Shared templates limit inference.", 16, MUTED)
    canvas.text(24, 546, "B = PASS; N = neutral; S = explicit scope. All arms see the original task and identical evidence.", 16, MUTED)
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path, help="new file stem; .svg and .pdf are appended")
    args = parser.parse_args()
    with args.analysis.open() as stream:
        report = json.load(stream)
    render(report).write(args.out)
    print(json.dumps({"svg": str(args.out)+".svg", "pdf": str(args.out)+".pdf", "new_model_calls": 0}))


if __name__ == "__main__":
    main()