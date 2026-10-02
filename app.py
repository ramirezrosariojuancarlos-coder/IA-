from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, traceback
from groq import Groq

app = Flask(__name__, template_folder='templates')
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODELO_TEXTO = "llama-3.1-8b-instant"
MODELO_VISION = "meta-llama/llama-4-scout-17b-16e-instruct"
MODELO_RESPALDO = "qwen/qwen3-32b"

def limpiar(t):
    t = re.sub(r'\*\*(.*?)\*\*', r'\1', t)
    t = re.sub(r'##+\s*', '', t)
    t = re.sub(r'\|\s*\|+', '', t)
    t = re.sub(r'---.*', '', t)
    return t.strip()

def prompt_por_nivel(nivel):
    base = "Responde CORTO y directo. Máximo 3 frases para preguntas simples. No des biblia si no te la piden. Si es tarea, da pasos cortos. Usa letra estilo WhatsApp, sin negritas excesivas ni tablas. Habla como amigo, no como libro."
    extras = {
        "primaria": " Nivel primaria: palabras muy fáciles, ejemplo corto, max 4 lineas.",
        "secundaria": " Nivel secundaria: claro y rápido, max 5 lineas.",
        "preparatoria": " Nivel prepa: un poco más de detalle pero sigue corto.",
        "universidad": " Nivel universidad: puedes ser un poco más profundo pero SIGUE SIENDO CORTO. Solo si te piden 'explícame a fondo' te extiendes."
    }
    return base + extras.get(nivel, extras["secundaria"])

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
        system = f"Eres IA Maestra creada por J Carlos Double R. {estilo}"

        msgs = [{"role":"system","content":system}]
        for m in historial[-4:]:
            if isinstance(m, dict): msgs.append(m)

        if imagen:
            msgs.append({"role":"user","content":[
                {"type":"text","text": mensaje + " (Responde corto)"},
                {"type":"image_url","image_url":{"url": imagen}}
            ]})
            modelo = MODELO_VISION
        else:
            msgs.append({"role":"user","content": mensaje + " Responde corto."})
            modelo = MODELO_TEXTO

        try:
            resp = client.chat.completions.create(model=modelo, messages=msgs, temperature=0.5, max_tokens=300)
        except Exception as e:
            print(f"Fallo {modelo}: {e}")
            resp = client.chat.completions.create(model=MODELO_RESPALDO, messages=msgs, temperature=0.5, max_tokens=300)

        return jsonify({"reply": limpiar(resp.choices[0].message.content)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"reply": f"Error: {e}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
