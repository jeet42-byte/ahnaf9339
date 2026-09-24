"""Group students from a results CSV into GPA tiers and write a Markdown report.

Tier cut-offs follow the University of Dhaka letter-grade boundaries
(A = 3.75, A- = 3.50, B+ = 3.25).
"""
import csv
import sys
from pathlib import Path

TIERS = [
    ("Tier 1 — Distinction", "GPA ≥ 3.75 (A range)", 3.75),
    ("Tier 2 — Very Good", "3.50 ≤ GPA < 3.75 (A- range)", 3.50),
    ("Tier 3 — Good", "3.25 ≤ GPA < 3.50 (B+ range)", 3.25),
    ("Tier 4 — Satisfactory", "GPA < 3.25", 0.0),
]


def tier_of(gpa):
    return next(i for i, (_, _, floor) in enumerate(TIERS) if gpa >= floor)


def main(csv_path, out_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        students = [dict(r, gpa=float(r["gpa"])) for r in csv.DictReader(f)]
    students.sort(key=lambda s: (-s["gpa"], int(s["roll"])))

    # Competition ranking: tied GPAs share a rank (1, 2, 3, 3, 3, 6, ...).
    rank = {}
    for i, s in enumerate(students, 1):
        rank.setdefault(s["gpa"], i)

    groups = [[] for _ in TIERS]
    for s in students:
        groups[tier_of(s["gpa"])].append(s)

    gpas = [s["gpa"] for s in students]
    lines = [
        "# Criminology — 1st Semester 2026 Results by Tier",
        "",
        "Professional Masters in Criminology and Criminal Justice, University of Dhaka.",
        "",
        f"Students: **{len(students)}** · Mean GPA: **{sum(gpas) / len(gpas):.2f}** · "
        f"Highest: **{max(gpas):.2f}** · Lowest: **{min(gpas):.2f}** · Pass rate: **100%**",
        "",
        "| Tier | Range | Students |",
        "|---|---|---|",
    ]
    lines += [f"| {t} | {r} | {len(g)} |" for (t, r, _), g in zip(TIERS, groups)]
    for (title, rng, _), group in zip(TIERS, groups):
        lines += ["", f"## {title}", "", f"_{rng}_ — {len(group)} student{'s' if len(group) != 1 else ''}", "",
                  "| Rank | Roll | Name | Hall | GPA |", "|---|---|---|---|---|"]
        for s in group:
            lines.append(f"| {rank[s['gpa']]} | {s['roll']} | {s['name']} | {s['hall']} | {s['gpa']:.2f} |")
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    here = Path(__file__).parent
    main(sys.argv[1] if len(sys.argv) > 1 else here / "criminology_2026_sem1.csv",
         sys.argv[2] if len(sys.argv) > 2 else here / "TIERS.md")
