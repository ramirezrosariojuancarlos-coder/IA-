from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, traceback
from groq import Groq

app = Flask(__name__, template_folder='templates')
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# UNICO MODELO VIVO EN GROQ SEP 2026 CON VISION - VERIFICADO
MODELO_VIVO = "qwen/qwen3.6-27b" # preview pero funciona gratis 30 RPM

def limpiar(t):
    return re.sub(r'\*\*(.*?)\*\*', r'\1', t).strip()

def prompt_nivel(nivel):
    return {
        "primaria": "PRIMARIA: explica como a niño de 10 años, muy corto, con emojis.",
        "secundaria": "SECUNDARIA: claro, paso a paso, sin palabras difíciles, como alumno de secundaria.",
        "prepa": "PREPA: explica con análisis y ejemplo de prepa.",
        "universidad": "UNIVERSIDAD: análisis profundo y formal."
    }.get(nivel.lower(), "SECUNDARIA")

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

        system = f"Eres IA Maestra de J Carlos Double R. Nivel actual: {nivel}. {prompt_nivel(nivel)} Si hay imagen, léela completa y resuelve."

        messages = [{"role":"system","content":system}]
        for m in hist:
            if isinstance(m, dict) and "role" in m:
                messages.append(m)

        if img:
            messages.append({"role":"user","content":[
                {"type":"text","text": msg or "Lee esta imagen y resuelve según el nivel "+nivel},
                {"type":"image_url","image_url":{"url": img}}
            ]})
        else:
            messages.append({"role":"user","content": msg})

        resp = client.chat.completions.create(
            model=MODELO_VIVO,
            messages=messages,
            temperature=0.4,
            max_tokens=800
        )
        return jsonify({"reply": limpiar(resp.choices[0].message.content)})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"reply": f"Error Groq: {e}. Verifica que tu GROQ_API_KEY sigue activa y que el modelo {MODELO_VIVO} está en tu plan free."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))