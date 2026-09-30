from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, traceback, requests
from groq import Groq

app = Flask(__name__, template_folder='templates')
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

# MODELOS VIVOS HOY - VERIFICADO 29/SEP/2026
GROQ_TEXTO = "openai/gpt-oss-20b" # reemplazo oficial de llama-3.1
GROQ_VISION = "qwen/qwen3.6-27b" # único vision vivo en Groq según docs
OPENROUTER_VISION = "meta-llama/llama-4-maverick:free" # respaldo gratis

def prompt_nivel(nivel):
    return {
        "primaria": "Eres para PRIMARIA: palabras de niño 10 años, muy corto, con emojis, ejemplo super simple.",
        "secundaria": "Eres para SECUNDARIA: claro, paso a paso, sin tecnicismos.",
        "prepa": "Eres para PREPA: explica con análisis, causas, analogía y ejemplo de preparatoria.",
        "universidad": "Eres para UNIVERSIDAD: análisis profundo, formal, con argumentos, referencias y conclusión crítica."
    }.get(nivel, "secundaria")

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

        system = f"Eres IA Maestra de J Carlos Double R. Nivel: {nivel.upper()}. {prompt_nivel(nivel)} Si hay imagen, transcribe TODO lo que dice y luego resuelve según el nivel."

        messages = [{"role":"system","content":system}] + hist

        if img:
            messages.append({"role":"user","content":[
                {"type":"text","text": msg or "Lee la imagen y resuelve según el nivel"},
                {"type":"image_url","image_url":{"url": img}}
            ]})
            # 1. Intenta Groq vision vivo
            try:
                r = groq.chat.completions.create(model=GROQ_VISION, messages=messages, max_tokens=700, temperature=0.4)
                return jsonify({"reply": re.sub(r'\*\*','', r.choices[0].message.content)})
            except Exception as e:
                print("Groq vision falló:", e)
                if not OPENROUTER_KEY:
                    return jsonify({"reply": f"Groq vision en preview limitado. Pon OPENROUTER_API_KEY para respaldo. Error: {e}"})

            # 2. Fallback OpenRouter free vision
            ro = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type":"application/json"},
                json={"model": OPENROUTER_VISION, "messages": messages, "max_tokens":700}, timeout=40)
            ro.raise_for_status()
            txt = ro.json()["choices"][0]["message"]["content"]
            return jsonify({"reply": re.sub(r'\*\*','', txt)})
        else:
            messages.append({"role":"user","content": msg})
            r = groq.chat.completions.create(model=GROQ_TEXTO, messages=messages, max_tokens=700, temperature=0.4)
            return jsonify({"reply": re.sub(r'\*\*','', r.choices[0].message.content)})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"reply": f"Error: {e}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))