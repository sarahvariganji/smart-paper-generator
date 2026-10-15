# Paperwright — Smart Question Paper Generator (Maths)
   - Built by Sarah Variganji for the Evalvia internship assignment.
   - Live demo: https://smart-paper-generator-1.onrender.com

A Python (Flask) tool that builds a Maths question paper from a teacher's blueprint and shows how closely it matched.

## Architecture
```
Teacher enters requirements (browser form: marks, difficulty, topics, types)
        │  POST /api/generate
        ▼
engine/generator.py   Python generation engine: selects questions
        ▼
engine/validator.py   Validates + explains every unmet constraint
        ▼
Paper + breakdown     Swap one question (/api/swap), export (/api/export → .docx, or print to PDF)
```
- `engine/` — all logic, no web code, so it is unit-tested on its own (`tests/`).
- `app.py` — thin Flask API; `static/index.html` — the form and paper view.
- `data/questions.json` — tagged bank (topic × type × difficulty), 48 questions.

## Run locally
```
pip install -r requirements.txt
python app.py            # open http://127.0.0.1:5000
pytest                   # run the tests
```

## Approach: pure logic, no AI model
Marks arithmetic must be exact and repeatable; an LLM can't reliably make 40 marks fit three overlapping percentage splits. So selection is deterministic optimisation over a curated, tagged bank. An LLM is better used to *draft new bank questions* for a teacher to review.
- Assumption: question-type percentages are treated as percent of marks. Because questions are whole units (a Long answer is 5 marks), the result can land a few points off target, and the breakdown shows this.

1. **Type mix first:** percentages → marks → question counts (MCQ 1, Short 3, Long 5) with a greedy largest-deficit fill, so total marks are exact. (Assumption: type % means % of *marks*.)
2. **Topic + difficulty:** randomised hill-climb with restarts, swapping within a type, minimising `Σ|topic marks − target| + Σ|difficulty marks − target|`.
3. **Real-paper feel:** Sections A/B/C, grouped by topic, easy → hard, continuous numbering, marks and time shown.

## When constraints don't fit
The validator never lets this fail silently. Percentages not summing to 100 are scaled and reported. Infeasible blueprints return the *closest* paper; every bucket more than 5 points off gets a plain-language reason (bank too small vs traded off against another constraint). Bad input returns a clear 400 error. Try the "impossible blueprint" button.

## Swap
`/api/swap` replaces one question with the unused same-type question that keeps the whole blueprint closest (same topic and difficulty preferred), and says so if it had to compromise.

## Deploy (Render)
Push to GitHub → Render → New Web Service → build `pip install -r requirements.txt`, start `gunicorn app:app`.

## Where it falls short / next steps
- Small bank (48), Maths only; no LaTeX rendering.
- Hill-climb isn't guaranteed optimal; an ILP/CP solver (e.g. OR-Tools) would be.
- No sub-topics, marking scheme, question-locking or "avoid last paper's questions".
- Next: CSV bank upload, LLM-assisted bank growth with human review.

## Proud of / still weak
- **Proud of:** the honest conflict handling: a paper plus an explanation, never a silent miss.
- **Weak:** bank size limits variety, so heavy skews hit limits quickly.
