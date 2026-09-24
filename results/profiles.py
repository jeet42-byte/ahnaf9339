"""Descriptive profile for every student: sessionals per course, final GPA and how the result shifted."""
import re
from pathlib import Path
from statistics import pstdev

import shift

S = shift.S
C = ["501", "502", "506", "507", "508"]
N = len(S)

course_rank = [shift.comp_rank([s["marks"][i] for s in S]) for i in range(5)]
for j, s in enumerate(S):
    s["cranks"] = [course_rank[i][j] for i in range(5)]
climb_order = sorted(S, key=lambda s: (-s["move"], -round(s["delta"], 2), s["frank"]))
for i, s in enumerate(climb_order, 1):
    s["cpos"] = i


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def sgn(x):
    return f"{x:+.2f}".replace("-", "−")


def finals_text(d):
    d = round(d, 2)
    if d > 0:
        return f"finals went **better** than the sessionals (Δ {sgn(d)}), the only student in the class to do so"
    if d == 0:
        return "finals matched the sessionals exactly (Δ 0.00)"
    if d >= -0.10:
        return f"finals held up well, a small slip of {sgn(d)} against a class average of −0.17"
    if d >= -0.25:
        return f"finals slipped by {sgn(d)}, roughly in line with the class average of −0.17"
    return f"finals fell well short of the sessionals ({sgn(d)}), one of the larger drops in the class"


def verdict(s):
    d, mv, fr = round(s["delta"], 2), s["move"], s["frank"]
    if s["srank"] <= 5 and fr <= 3:
        return "A top student on both measures who carried sessional form straight into the finals."
    if mv >= 10:
        return "One of the standout climbers: a middling sessional record turned into a much stronger final result."
    if mv >= 5:
        return "Finished clearly higher than the sessionals suggested, mainly by losing less ground in the finals than peers."
    if mv <= -10:
        return "The sharpest reversal in the class: good sessional marks that did not carry into the final exams."
    if mv <= -5:
        return "Sessional promise did not fully carry over; the finals cost several places."
    if d == 0 and fr >= 30:
        return "Sessionals and finals told the same story; improving the sessional base is the clearest route up."
    if abs(mv) <= 2:
        return "A stable result: the final standing closely mirrors the sessional standing."
    return "A modest shift; the final standing is broadly in line with the sessionals."


def profile(s):
    marks = " · ".join(f"{c}: {m:g} ({ordinal(r)})" for c, m, r in zip(C, s["marks"], s["cranks"]))
    bi = min(range(5), key=lambda i: (s["cranks"][i], -s["marks"][i]))
    wi = max(range(5), key=lambda i: (s["cranks"][i], -s["marks"][i]))
    spread = pstdev(s["cranks"])
    shape = ("very consistent across courses" if spread < 4 else
             "fairly consistent across courses" if spread < 8 else
             f"an uneven profile, ranging from {ordinal(min(s['cranks']))} to {ordinal(max(s['cranks']))}")
    t0, t1 = shift.stier(s["sess"]), shift.tier(s["gpa"])
    tier = f"Tier {t0} → Tier {t1}" if t0 != t1 else f"stayed in Tier {t1}"
    mv = s["move"]
    pl = lambda n: f"{n} place" + ("s" if n != 1 else "")
    move = (f"climbed **{pl(mv)}** ({ordinal(s['srank'])} → {ordinal(s['frank'])})" if mv > 0 else
            f"dropped **{pl(-mv)}** ({ordinal(s['srank'])} → {ordinal(s['frank'])})" if mv < 0 else
            f"held rank **{ordinal(s['frank'])}**")
    up = sum(r > s["frank"] for r in s["cranks"])
    down = sum(r < s["frank"] for r in s["cranks"])
    name = s["name"] + (" ⭐" if s["roll"] == 24 else "")
    return "\n".join([
        f"### {name}",
        f"*Roll {s['roll']} · {s['hall']}*", "",
        f"- **Sessionals:** {marks}",
        f"- **Sessional total:** {s['sess']:g}/250, {ordinal(s['srank'])} of {N}. Strongest in MCCJ {C[bi]}, "
        f"weakest in MCCJ {C[wi]}; {shape}.",
        f"- **Final GPA:** {s['gpa']:.2f}, {ordinal(s['frank'])} of {N} ({tier}).",
        f"- **Shift:** {move}; {finals_text(s['delta'])}. {ordinal(s['cpos'])} on the climbers list.",
        f"- **By course:** final rank was better than the course sessional rank in {up} of 5 courses"
        + (f", worse in {down}" if down else "") + (f", level in {5 - up - down}." if 5 - up - down else "."),
        f"- **Verdict:** {verdict(s)}", ""])


def key(s):
    return re.sub(r"^(Md\.|Mohammad|Miah Md\.)\s*", "", s["name"]).lower()


out = ["# Student profiles — sessionals vs final GPA", "",
       f"Descriptive analysis for all {N} students, alphabetical (ignoring \"Md.\"/\"Mohammad\"). "
       "Course ranks are out of 39; Δ = final GPA − the GPA the sessionals alone would earn "
       "(class average −0.17).", ""]
out += [profile(s) for s in sorted(S, key=key)]
Path(__file__).with_name("PROFILES.md").write_text("\n".join(out), encoding="utf-8")
