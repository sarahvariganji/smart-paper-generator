"""Stage 2 — the generation engine: picks questions to match the blueprint."""
import random
from .bank import BY_ID, BY_TYPE, GROUPS, LABEL, MK
from .validator import report

def parse(req):
    """Validate input and convert percentages to target marks per bucket."""
    total = int(req.get("total", 40))
    if not 5 <= total <= 100:
        raise ValueError("Total marks must be between 5 and 100.")
    notes, targets = [], {}
    for g, keys in GROUPS.items():
        vals = {k: float(req.get(g, {}).get(k, 0)) for k in keys}
        if any(v < 0 for v in vals.values()):
            raise ValueError("Percentages cannot be negative.")
        s = sum(vals.values())
        if s == 0:
            vals, s = {k: 1.0 for k in keys}, float(len(keys))
            notes.append(["w", f"{LABEL[g]}: nothing was entered, so it was split evenly."])
        elif round(s) != 100:
            notes.append(["i", f"{LABEL[g]} percentages added up to {s:g}%, so they were scaled to 100%."])
        targets[g] = {k: vals[k] / s * total for k in keys}
    return total, targets, notes

def type_counts(total, targets):
    """Fill the type mix first (greedy, largest marks-deficit) so total marks are exact."""
    c, cur = {y: 0 for y in MK}, 0
    while True:
        best, gap = None, -1e9
        for y in MK:
            if c[y] >= len(BY_TYPE[y]) or cur + MK[y] > total:
                continue
            d = targets["y"][y] - c[y] * MK[y]
            if d > gap:
                best, gap = y, d
        if best is None:
            return c
        c[best] += 1
        cur += MK[best]

def cost(ids, targets):
    """Total absolute deviation (in marks) from topic and difficulty targets."""
    m = {"t": {}, "d": {}}
    for i in ids:
        q = BY_ID[i]
        for g in m:
            m[g][q[g]] = m[g].get(q[g], 0) + MK[q["y"]]
    return sum(abs(m[g].get(k, 0) - v) for g in m for k, v in targets[g].items())

def solve(counts, targets, rng, restarts=10, iters=2500):
    """Randomised hill-climb. Swaps stay within a type, so total marks never change."""
    best, best_c = [], float("inf")
    for _ in range(restarts):
        sel = [i for y, n in counts.items() for i in rng.sample(BY_TYPE[y], n)]
        cur = cost(sel, targets)
        for _ in range(iters if sel else 0):
            p = rng.randrange(len(sel))
            cand = rng.choice(BY_TYPE[BY_ID[sel[p]]["y"]])
            if cand in sel:
                continue
            t = sel[:p] + [cand] + sel[p + 1:]
            c = cost(t, targets)
            if c <= cur:
                sel, cur = t, c
        if cur < best_c:
            best, best_c = sel, cur
    return best

def _sort(ids):
    key = lambda i: ("MSL".index(BY_ID[i]["y"]), "AGT".index(BY_ID[i]["t"]), "EMH".index(BY_ID[i]["d"]))
    return sorted(ids, key=key)

def generate(req, seed=None):
    total, targets, notes = parse(req)
    ids = _sort(solve(type_counts(total, targets), targets, random.Random(seed)))
    return report(ids, total, targets, notes, req)

def swap(req, ids, index, seed=None):
    """Replace one question with the unused same-type question that keeps the blueprint closest."""
    total, targets, notes = parse(req)
    ids = list(ids)
    if not 0 <= index < len(ids):
        raise ValueError("Question index out of range.")
    old, used = BY_ID[ids[index]], set(ids)
    scored = []
    for n in BY_TYPE[old["y"]]:
        if n in used:
            continue
        q = BY_ID[n]
        s = cost(ids[:index] + [n] + ids[index + 1:], targets) + (q["t"] != old["t"]) * .01 + (q["d"] != old["d"]) * .005
        scored.append((s, n))
    if not scored:
        notes.append(["w", "No unused question of this type is left in the bank to swap in."])
        return report(ids, total, targets, notes, req)
    best = min(s for s, _ in scored)
    new = random.Random(seed).choice([n for s, n in scored if abs(s - best) < 1e-9])
    ids[index] = new
    q = BY_ID[new]
    if (q["t"], q["d"]) == (old["t"], old["d"]):
        notes.append(["i", "Swapped for another question of the same topic and difficulty."])
    else:
        notes.append(["w", "No unused question of the same topic and difficulty was left, so the closest fit that keeps the blueprint was used."])
    return report(ids, total, targets, notes, req)
