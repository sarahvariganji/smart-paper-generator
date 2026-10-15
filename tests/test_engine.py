import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import pytest
from engine import generate, swap

DEFAULT = {"total": 40, "d": {"E": 30, "M": 50, "H": 20}, "t": {"A": 40, "G": 30, "T": 30}, "y": {"M": 40, "S": 40, "L": 20}}
IMPOSSIBLE = {"total": 30, "d": {"E": 10, "M": 20, "H": 70}, "t": {"A": 80, "G": 10, "T": 10}, "y": {"M": 10, "S": 10, "L": 80}}

def test_total_marks_exact():
    for total in (20, 25, 40, 50, 60):
        assert generate(dict(DEFAULT, total=total))["total"] == total

def test_no_duplicate_questions():
    ids = [q["id"] for q in generate(DEFAULT)["paper"]]
    assert len(ids) == len(set(ids))

def test_default_close_to_targets():
    for g in generate(DEFAULT, seed=1)["breakdown"]:
        for row in g["rows"]:
            assert abs(row["actual"] - row["target"]) <= 10

def test_impossible_never_crashes_and_warns():
    r = generate(IMPOSSIBLE)
    assert r["total"] > 0 and any(n[0] == "w" for n in r["notes"])

def test_percentages_not_100_are_scaled_and_reported():
    r = generate(dict(DEFAULT, d={"E": 30, "M": 50, "H": 40}))
    assert any("scaled" in n[1] for n in r["notes"])

def test_bad_input_rejected():
    with pytest.raises(ValueError):
        generate(dict(DEFAULT, total=1000))

def test_swap_keeps_type_total_and_changes_question():
    r = generate(DEFAULT, seed=2)
    ids = [q["id"] for q in r["paper"]]
    s = swap(DEFAULT, ids, 3, seed=2)
    assert s["total"] == r["total"] and s["paper"][3]["y"] == r["paper"][3]["y"] and s["paper"][3]["id"] != ids[3]
