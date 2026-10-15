"""Flask API + static frontend.  Run:  python app.py"""
import io
from flask import Flask, jsonify, request, send_file, send_from_directory
from engine import generate, swap
from engine.export import to_docx

app = Flask(__name__, static_folder="static")

@app.get("/")
def home():
    return send_from_directory("static", "index.html")

def _safe(fn):
    try:
        return fn(request.get_json(force=True))
    except (KeyError, ValueError, TypeError) as e:
        return jsonify(error=str(e) or "Invalid request"), 400

@app.post("/api/generate")
def api_generate():
    return _safe(lambda b: jsonify(generate(b["req"])))

@app.post("/api/swap")
def api_swap():
    return _safe(lambda b: jsonify(swap(b["req"], b["ids"], int(b["index"]))))

@app.post("/api/export")
def api_export():
    def go(b):
        data = to_docx(b["ids"], bool(b.get("answers")))
        return send_file(io.BytesIO(data), as_attachment=True, download_name="question_paper.docx",
                         mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    return _safe(go)

if __name__ == "__main__":
    app.run(debug=True)
