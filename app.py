from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, traceback
from groq import Groq

app = Flask(__name__, template_folder='templates')
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# MODELOS ACTUALES SEPT 2026 - GROQ APAGÓ LLAMA-4
MODELO_TEXTO = "llama-3.1-8b-instant" # gratis, rápido
MODELO_VISION = "meta-llama/llama-4-scout-17b-16e-instruct" # probamos scout primero
MODELO_VISION_RESPALDO = "qwen/qwen3-32b" # si scout falla, usa qwen

def limpiar(t): return re.sub(r'\*\*(.*?)\*\*', r'\1', t).strip()

def prompt_por_nivel(nivel):
    prompts = {
        "primaria": "Explica como para niño de 10 años, con palabras muy fáciles, ejemplos con dibujitos, y muy corto.",
        "secundaria": "Explica como para secundaria, claro, paso a paso, sin palabras difíciles.",
        "preparatoria": "Explica como para prepa, con un poco más de análisis y términos técnicos pero claro.",
        "universidad": "Explica como para universidad, con análisis profundo, fuentes, crítica y estructura formal."
    }
    return prompts.get(nivel, prompts["secundaria"])

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
        data = request.get_json(force=True)
        mensaje = data.get("message","")
        historial = data.get("history",[])
        imagen = data.get("image")
        nivel = data.get("nivel","secundaria")

        estilo = prompt_por_nivel(nivel)
        system = f"Eres IA Maestra creada por J Carlos Double R. Nivel actual: {nivel}. {estilo} Si hay imagen, léela completa."

        msgs = [{"role":"system","content":system}]
        for m in historial[-4:]:
            if isinstance(m, dict): msgs.append(m)

        if imagen:
            msgs.append({"role":"user","content":[
                {"type":"text","text": mensaje},
                {"type":"image_url","image_url":{"url": imagen}}
            ]})
            modelo = MODELO_VISION
        else:
            msgs.append({"role":"user","content": mensaje})
            modelo = MODELO_TEXTO

        try:
            resp = client.chat.completions.create(model=modelo, messages=msgs, temperature=0.4, max_tokens=600)
        except Exception as e:
            # Si scout no existe en tu cuenta, usa qwen automáticamente
            print(f"Modelo {modelo} falló, probando respaldo: {e}")
            resp = client.chat.completions.create(model=MODELO_VISION_RESPALDO, messages=msgs, temperature=0.4, max_tokens=600)

        return jsonify({"reply": limpiar(resp.choices[0].message.content)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"reply": f"Error: {e}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))