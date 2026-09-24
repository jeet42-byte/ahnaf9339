"""Per-student view: each course's sessional mark next to the final GPA, with a short reading of the shift."""
import re
from pathlib import Path

import shift

S = shift.S
LABEL = ["501", "502", "506", "507", "508"]


def reading(s):
    d, mv = round(s["delta"], 2), s["move"]
    best = LABEL[max(range(5), key=lambda i: s["marks"][i])]
    worst = LABEL[min(range(5), key=lambda i: s["marks"][i])]
    if d > 0:
        finals = "Finals beat sessional form"
    elif d == 0:
        finals = "Finals matched sessional form exactly"
    elif d >= -0.10:
        finals = "Finals held up well (small slip)"
    elif d >= -0.25:
        finals = "Typical slip in finals"
    else:
        finals = "Finals well below sessional form"
    if mv >= 5:
        rank = f"big climb ({s['srank']}→{s['frank']})"
    elif mv > 0:
        rank = f"edged up ({s['srank']}→{s['frank']})"
    elif mv == 0:
        rank = f"held rank {s['frank']}"
    elif mv > -5:
        rank = f"slipped ({s['srank']}→{s['frank']})"
    else:
        rank = f"big drop ({s['srank']}→{s['frank']})"
    t0, t1 = shift.stier(s["sess"]), shift.tier(s["gpa"])
    tier = f"; Tier {t0}→{t1}" if t0 != t1 else ""
    return f"{finals}; {rank}{tier}. Best sessional {best}, weakest {worst}."


def key(s):
    return re.sub(r"^(Md\.|Mohammad|Miah Md\.)\s*", "", s["name"]).lower()


out = ["# Sessional marks vs final GPA — by student", "",
       "Students listed alphabetically (ignoring \"Md.\"/\"Mohammad\"). Sessional marks are out of 50 per course; "
       "total out of 250. Implied GPA = what the sessional % alone would earn. Δ = final − implied.", "",
       "| Name | 501 | 502 | 506 | 507 | 508 | Total | Sess. rank | Implied GPA | Final GPA | Final rank | Move | Δ | Reading |",
       "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for s in sorted(S, key=key):
    n = f"**{s['name']}**" if s["roll"] == 24 else s["name"]
    mv = f"▲{s['move']}" if s["move"] > 0 else f"▼{-s['move']}" if s["move"] < 0 else "—"
    out.append(f"| {n} | " + " | ".join(f"{m:g}" for m in s["marks"]) +
               f" | {s['sess']:g} | {s['srank']} | {s['implied']:.2f} | {s['gpa']:.2f} | {s['frank']} | {mv} | "
               f"{s['delta']:+.2f} | {reading(s)} |")
Path(__file__).with_name("BY_STUDENT.md").write_text("\n".join(out) + "\n", encoding="utf-8")
