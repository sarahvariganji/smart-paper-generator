"""Question bank + shared constants."""
import json
from pathlib import Path

MK = {"M": 1, "S": 3, "L": 5}                       # marks per question type
GROUPS = {"d": "EMH", "t": "AGT", "y": "MSL"}       # difficulty, topic, type
LABEL = {"d": "Difficulty", "t": "Topic", "y": "Question type"}
NAMES = {"E": "Easy", "M": "Medium", "H": "Hard", "A": "Algebra", "G": "Geometry", "T": "Trigonometry"}
TYPE_NAMES = {"M": "MCQ", "S": "Short answer", "L": "Long answer"}
SECTIONS = [("M", "Section A — Multiple choice (1 mark each)"),
            ("S", "Section B — Short answer (3 marks each)"),
            ("L", "Section C — Long answer (5 marks each)")]

BANK = json.loads((Path(__file__).parent.parent / "data" / "questions.json").read_text(encoding="utf-8"))
BY_ID = {q["id"]: q for q in BANK}
BY_TYPE = {y: [q["id"] for q in BANK if q["y"] == y] for y in MK}

def name(g, k):
    return TYPE_NAMES[k] if g == "y" else NAMES[k]
