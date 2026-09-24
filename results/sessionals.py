"""Tier the 1st-semester sessional marks (out of 50) for each course, plus a combined view."""
import csv
from pathlib import Path

HERE = Path(__file__).parent
COURSES = {
    "MCCJ501": "Introduction to Criminology",
    "MCCJ502": "Introduction to Policing",
    "MCCJ506": "Penology and Corrections",
    "MCCJ507": "Sessionals (course title not on sheet)",
    "MCCJ508": "Genocide and Crimes against Humanity",
}
# Percentage bands from the DU letter-grade scale (A+ 80%, A 75%, A- 70%).
TIERS = [("Tier 1 — A+", 0.80), ("Tier 2 — A", 0.75), ("Tier 3 — A-", 0.70), ("Tier 4 — below A-", 0.0)]
# Missed the midterm (and more) in every course, so their totals are not comparable.
INCOMPLETE = {13: "Imtiaz Ahmed", 30: "Md. Rakib Bin Quddus"}

names = {}
with open(HERE / "criminology_2026_sem1.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        n = 41 if r["roll"] == "2431" else int(r["roll"]) - 2600
        names[n] = r["name"]
names.update(INCOMPLETE)

with open(HERE / "sessionals.csv", encoding="utf-8") as f:
    rows = [{k: (float(v) if v else None) for k, v in r.items()} for r in csv.DictReader(f)]
for r in rows:
    r["roll"] = int(r["roll"])


def section(title, key, out_of):
    scored = sorted((r for r in rows if r["roll"] not in INCOMPLETE), key=lambda r: (-r[key], r["roll"]))
    rank = {}
    for i, r in enumerate(scored, 1):
        rank.setdefault(r[key], i)
    vals = [r[key] for r in scored]
    lines = [f"## {title}", "",
             f"Out of {out_of:g} · {len(vals)} students · mean **{sum(vals)/len(vals):.2f}** · "
             f"high **{max(vals):g}** · low **{min(vals):g}**", ""]
    buckets = [[] for _ in TIERS]
    for r in scored:
        buckets[next(i for i, (_, p) in enumerate(TIERS) if r[key] >= p * out_of)].append(r)
    for (label, p), b in zip(TIERS, buckets):
        rng = f"≥ {p*out_of:g}" if p else f"< {TIERS[-2][1]*out_of:g}"
        lines.append(f"**{label}** ({rng}) — {len(b)}")
        lines.append("")
        lines += [f"- {rank[r[key]]}. {names[r['roll']]} (roll {r['roll']}) — {r[key]:g}" for r in b] or ["- —"]
        lines.append("")
    inc = ", ".join(f"{names[r['roll']]} ({r[key]:g})" if r[key] is not None else f"{names[r['roll']]} (no marks)"
                    for r in rows if r["roll"] in INCOMPLETE)
    lines += [f"_Incomplete / absent, not tiered:_ {inc}", ""]
    return lines


for r in rows:
    r["ALL"] = sum(r[c] or 0 for c in COURSES)

out = ["# 1st Semester Sessional Marks by Tier — MCCJ 9th Batch", "",
       "Tiers use the DU grade bands as a share of the maximum: "
       "Tier 1 ≥ 80% (A+), Tier 2 75–79% (A), Tier 3 70–74% (A-), Tier 4 < 70%.", ""]
for code, name in COURSES.items():
    out += section(f"{code[:4]} {code[4:]} — {name}", code, 50)
out += section("Combined — all five courses", "ALL", 250)
(HERE / "SESSIONALS.md").write_text("\n".join(out), encoding="utf-8")
