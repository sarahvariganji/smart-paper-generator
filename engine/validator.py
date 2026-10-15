"""Stage 3 — validate the result and explain every unmet constraint."""
from .bank import BANK, BY_ID, GROUPS, LABEL, MK, name

TOLERANCE = 5  # percentage points

def _avail(g, k):
    return sum(MK[q["y"]] for q in BANK if q[g] == k)

def report(ids, total, targets, notes, req):
    paper = [BY_ID[i] for i in ids]
    got = sum(MK[q["y"]] for q in paper)
    notes = list(notes)
    if got < total:
        notes.append(["w", f"Only {got} of {total} marks could be filled: the bank ran out of questions of the requested types."])
    breakdown = []
    for g in GROUPS:
        rows = []
        for k in GROUPS[g]:
            tg = targets[g][k]
            ac = sum(MK[q["y"]] for q in paper if q[g] == k)
            off = abs(ac - tg) / total * 100 > TOLERANCE and abs(ac - tg) >= 1
            if off:
                lack, av = ac < tg, _avail(g, k)
                why = (f"the bank holds only {av} marks of this in total, so the target is not reachable." if lack and av < tg
                       else "it was traded off to satisfy the other constraints, which cannot all be met at once." if lack
                       else "other constraints pushed it above target; the bank has too little of the alternatives.")
                notes.append(["w", f"{name(g, k)} ({LABEL[g].lower()}): asked for {tg:.1f} marks, got {ac}; {why}"])
            rows.append({"name": name(g, k), "target": round(tg / total * 100), "actual": round(ac / total * 100), "marks": ac, "off": off})
        breakdown.append({"label": LABEL[g], "rows": rows})
    if not any(n[0] == "w" for n in notes):
        notes.append(["i", f"All constraints met within ±{TOLERANCE} percentage points."])
    return {"req": req, "target_total": total, "total": got, "notes": notes, "breakdown": breakdown,
            "paper": [dict(q, marks=MK[q["y"]]) for q in paper]}
