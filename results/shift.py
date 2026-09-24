"""Compare pre-final sessional standing with the final semester GPA."""
import csv
from pathlib import Path
from statistics import mean, pstdev

HERE = Path(__file__).parent
COURSES = ["MCCJ501", "MCCJ502", "MCCJ506", "MCCJ507", "MCCJ508"]


def gp(pct):
    """DU grade point for a percentage."""
    for cut, g in [(80, 4.0), (75, 3.75), (70, 3.5), (65, 3.25), (60, 3.0), (55, 2.75), (50, 2.5), (45, 2.25), (40, 2.0)]:
        if pct >= cut:
            return g
    return 0.0


def comp_rank(values):
    order = sorted(values, reverse=True)
    return [order.index(v) + 1 for v in values]


def pearson(x, y):
    mx, my = mean(x), mean(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (len(x) * pstdev(x) * pstdev(y))


def spearman(x, y):
    def avg_rank(v):
        order = sorted(v)
        return [(order.index(a) + 1 + len(order) - order[::-1].index(a)) / 2 for a in v]
    return pearson(avg_rank(x), avg_rank(y))


final = {}
for r in csv.DictReader(open(HERE / "criminology_2026_sem1.csv", encoding="utf-8")):
    final[41 if r["roll"] == "2431" else int(r["roll"]) - 2600] = r
sess = {int(r["roll"]): r for r in csv.DictReader(open(HERE / "sessionals.csv"))}

S = []
for roll, f in final.items():
    marks = [float(sess[roll][c]) for c in COURSES]
    S.append(dict(roll=roll, name=f["name"], hall=f["hall"], gpa=float(f["gpa"]),
                  sess=sum(marks), implied=mean(gp(m * 2) for m in marks), marks=marks))

for s, r in zip(S, comp_rank([s["sess"] for s in S])):
    s["srank"] = r
for s, r in zip(S, comp_rank([s["gpa"] for s in S])):
    s["frank"] = r
for s in S:
    s["move"] = s["srank"] - s["frank"]          # positive = climbed after the final
    s["delta"] = s["gpa"] - s["implied"]          # finals vs. what sessionals alone would give


def tier(g):
    return 1 if g >= 3.75 else 2 if g >= 3.5 else 3 if g >= 3.25 else 4


def stier(total):
    p = total / 250
    return 1 if p >= .8 else 2 if p >= .75 else 3 if p >= .7 else 4


x, y = [s["sess"] for s in S], [s["gpa"] for s in S]
out = ["# How results shifted: sessionals → semester-final GPA", "",
       "Sessional = combined marks in MCCJ 501, 502, 506, 507, 508 (out of 250).",
       "Sessional-implied GPA = average DU grade point each course's sessional % would earn on its own.",
       "Δ = final GPA − sessional-implied GPA: positive means the final exams pulled the student up.", "",
       "## Headline numbers", "",
       f"- Students compared: {len(S)} (Imtiaz Ahmed and Md. Rakib Bin Quddus do not appear in the final result list)",
       f"- Pearson r (sessional total vs GPA): **{pearson(x, y):.2f}** · Spearman ρ (rank vs rank): **{spearman(x, y):.2f}**",
       f"- Mean sessional-implied GPA **{mean(s['implied'] for s in S):.2f}** → mean final GPA **{mean(y):.2f}** "
       f"(Δ {mean(s['delta'] for s in S):+.2f})",
       f"- GPA spread (std dev): {pstdev(y):.3f}; sessional-implied spread: {pstdev([s['implied'] for s in S]):.3f}",
       f"- Climbed ≥ 5 ranks: {sum(s['move'] >= 5 for s in S)} · Dropped ≥ 5 ranks: {sum(s['move'] <= -5 for s in S)} · "
       f"Within ±4: {sum(abs(s['move']) < 5 for s in S)}",
       f"- Final GPA above sessional-implied: {sum(s['delta'] > 0 for s in S)} · equal: {sum(s['delta'] == 0 for s in S)} · "
       f"below: {sum(s['delta'] < 0 for s in S)}", ""]

# Tier transition matrix
out += ["## Tier transitions (sessional tier → final GPA tier)", "",
        "| Sessional ↓ / Final → | T1 | T2 | T3 | T4 | Total |", "|---|---|---|---|---|---|"]
for a in range(1, 5):
    row = [sum(1 for s in S if stier(s["sess"]) == a and tier(s["gpa"]) == b) for b in range(1, 5)]
    out.append(f"| T{a} | " + " | ".join(map(str, row)) + f" | {sum(row)} |")
col = [sum(1 for s in S if tier(s["gpa"]) == b) for b in range(1, 5)]
out += ["| Total | " + " | ".join(map(str, col)) + f" | {len(S)} |", "",
        "Sessional tiers: T1 ≥ 200, T2 ≥ 187.5, T3 ≥ 175, T4 < 175. Final tiers: T1 ≥ 3.75, T2 ≥ 3.50, T3 ≥ 3.25, T4 < 3.25.", ""]


def table(rows, title):
    lines = [f"## {title}", "",
             "| Name | Roll | Sessional /250 | Sess. rank | Implied GPA | Final GPA | Final rank | Rank move | Δ GPA |",
             "|---|---|---|---|---|---|---|---|---|"]
    for s in rows:
        n = f"**{s['name']}**" if s["roll"] == 24 else s["name"]
        mv = f"▲{s['move']}" if s["move"] > 0 else f"▼{-s['move']}" if s["move"] < 0 else "—"
        lines.append(f"| {n} | {s['roll']} | {s['sess']:g} | {s['srank']} | {s['implied']:.2f} | {s['gpa']:.2f} | "
                     f"{s['frank']} | {mv} | {s['delta']:+.2f} |")
    return lines + [""]


out += table(sorted(S, key=lambda s: -s["move"])[:8], "Biggest climbers")
out += table(sorted(S, key=lambda s: s["move"])[:8], "Biggest fallers")
out += table(sorted(S, key=lambda s: (s["frank"], s["srank"])), "Full comparison (ordered by final GPA)")

# Hall breakdown
out += ["## By hall", "", "| Hall | Students | Mean sessional | Mean implied GPA | Mean final GPA | Mean Δ |",
        "|---|---|---|---|---|---|"]
halls = {}
for s in S:
    halls.setdefault(s["hall"], []).append(s)
for h, g in sorted(halls.items(), key=lambda kv: -len(kv[1])):
    out.append(f"| {h} | {len(g)} | {mean(s['sess'] for s in g):.1f} | {mean(s['implied'] for s in g):.2f} | "
               f"{mean(s['gpa'] for s in g):.2f} | {mean(s['delta'] for s in g):+.2f} |")
(HERE / "SHIFT.md").write_text("\n".join(out) + "\n", encoding="utf-8")
