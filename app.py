from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, traceback
from groq import Groq

app = Flask(__name__, template_folder='templates')
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODELO_TEXTO = "llama-3.3-70b-versatile"
MODELO_VISION = "meta-llama/llama-4-maverick-17b-128e-instruct"

def limpiar(t):
    return re.sub(r'\*\*(.*?)\*\*', r'\1', t).strip()

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
        mensaje = data.get("message","").strip()
        historial = data.get("history",[])
        imagen = data.get("image")

        # Si no hay mensaje ni imagen
        if not mensaje and not imagen:
            return jsonify({"reply": "Mándame la foto y escribe que quieres que haga."})

        system = "Eres IA Maestra, creada por J Carlos Double R. Si te mandan imagen, analízala y responde corto, claro, para secundaria."

        msgs = [{"role":"system","content":system}]
        # solo últimos 4 para que sea rápido
        for m in historial[-4:]:
            if isinstance(m, dict) and "role" in m and "content" in m:
                msgs.append(m)

        if imagen:
            # Groq necesita formato vision exacto
            msgs.append({
                "role":"user",
                "content": [
                    {"type":"text","text": mensaje if mensaje else "Lee esta imagen, transcribe el texto y resuelve la tarea. Responde corto para secundaria."},
                    {"type":"image_url","image_url":{"url": imagen}}
                ]
            })
            modelo = MODELO_VISION
        else:
            msgs.append({"role":"user","content": mensaje})
            modelo = MODELO_TEXTO

        resp = client.chat.completions.create(
            model=modelo,
            messages=msgs,
            temperature=0.4,
            max_tokens=500
        )
        return jsonify({"reply": limpiar(resp.choices[0].message.content)})

    except Exception as e:
        print("ERROR REAL:", str(e))
        traceback.print_exc()
        return jsonify({"reply": f"Error del servidor: {e}. Revisa tu GROQ_API_KEY en Render > Environment"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))