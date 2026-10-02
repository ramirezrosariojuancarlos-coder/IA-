from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, traceback
from groq import Groq

app = Flask(__name__, template_folder='templates')
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# MODELOS QUE SI EXISTEN EN GROQ HOY - OCT 2026
MODELO_1 = "llama-3.1-8b-instant"
MODELO_2 = "llama-3.3-70b-versatile"
MODELO_3 = "gemma2-9b-it"

def limpiar(t):
    t = re.sub(r'\*\*(.*?)\*\*', r'\1', t)
    t = re.sub(r'##+\s*', '', t)
    t = re.sub(r'\|\s*\|+', ' ', t)
    t = re.sub(r'---.*', '', t)
    return t.strip()

def prompt_por_nivel(nivel):
    base = "Responde CORTO, directo, como chat de WhatsApp. Máximo 3 frases si es pregunta simple. No hagas tablas ni pongas ##. Solo si el usuario dice 'explícame a fondo' te extiendes."
    extras = {
        "primaria": " Primaria: palabras de niño de 10 años, muy fácil.",
        "secundaria": " Secundaria: claro y rápido.",
        "preparatoria": " Prepa: un poco más de detalle pero corto.",
        "universidad": " Universidad: conciso pero inteligente. Si es 'sabes debatir?' responde solo 'Sí, dime el tema y empezamos'."
    }
    return base + extras.get(nivel, "")

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
        nivel = data.get("nivel","secundaria")
        # Ignoramos imagen si Groq no deja visión, para no dar 404
        estilo = prompt_por_nivel(nivel)
        system = f"Eres IA Maestra de J Carlos. {estilo}"

        msgs = [{"role":"system","content":system}]
        for m in historial[-4:]:
            if isinstance(m, dict): msgs.append(m)
        msgs.append({"role":"user","content": mensaje + " Responde corto."})

        # Intento 1, 2, 3 - el que funcione
        modelos = [MODELO_1, MODELO_2, MODELO_3]
        respuesta = None
        ultimo_error = ""
        for mod in modelos:
            try:
                r = client.chat.completions.create(model=mod, messages=msgs, temperature=0.5, max_tokens=250)
                respuesta = r.choices[0].message.content
                break
            except Exception as e:
                ultimo_error = str(e)
                continue

        if not respuesta:
            return jsonify({"reply": f"No se pudo conectar: {ultimo_error[:100]}. Revisa tu GROQ_API_KEY en Render."})

        return jsonify({"reply": limpiar(respuesta)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"reply": f"Error: {e}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
