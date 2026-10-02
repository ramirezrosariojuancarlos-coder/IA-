from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, traceback
from groq import Groq

app = Flask(__name__, template_folder='templates')
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# MODELOS VIVOS VERIFICADOS 29/SEP/2026
TEXTO = "openai/gpt-oss-20b"
VISION = "qwen/qwen3.8-27b"

def prompt_nivel(n):
    return {
        "primaria": "PRIMARIA: como niño de 10 años, muy corto, emojis.",
        "secundaria": "SECUNDARIA: claro y paso a paso como alumno de secundaria.",
        "prepa": "PREPA: con análisis y ejemplo.",
        "universidad": "UNIVERSIDAD: profundo y formal."
    }.get(n.lower(), "SECUNDARIA")

@app.route("/")
def index(): return render_template("index.html")
@app.route("/manifest.json")
def manifest(): return send_from_directory(TEMPLATES_DIR, 'manifest.json')
@app.route("/sw.js")
def sw(): return send_from_directory(TEMPLATES_DIR, 'sw.js')
@app.route("/icon-192.png")
def icon192(): return send_from_directory(TEMPLATES_DIR, 'icon-192.png')
@app.route("/icon-512.png")
def icon512(): return send_from_directory(TEMPLATES_DIR, 'icon-512.png')

@app.route("/chat", methods=["POST"])
def chat():
    try:
        d = request.get_json(force=True)
        msg = d.get("message","")
        hist = d.get("history",[])[-4:]
        img = d.get("image")
        nivel = d.get("nivel","secundaria")

        system = f"Eres IA Maestra de J Carlos. Nivel {nivel}: {prompt_nivel(nivel)} Si hay imagen, transcríbela completa."
        messages = [{"role":"system","content":system}] + [m for m in hist if isinstance(m, dict)]

        modelo = VISION if img else TEXTO

        if img:
            messages.append({"role":"user","content":[
                {"type":"text","text": msg or f"Lee la imagen nivel {nivel}"},
                {"type":"image_url","image_url":{"url": img}}
            ]})
        else:
            messages.append({"role":"user","content": msg})

        r = client.chat.completions.create(model=modelo, messages=messages, max_tokens=800, temperature=0.4)
        txt = re.sub(r'\*\*','', r.choices[0].message.content)
        return jsonify({"reply": txt})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"reply": f"Error: {e}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
