from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, traceback
from groq import Groq

app = Flask(__name__, template_folder='templates')
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# UNICO MODELO QUE GROQ DEJÓ VIVO OCT 2026 - LOS DEMÁS ESTÁN MUERTOS
MODELO_ACTIVO = "llama-3.1-8b-instant"

def limpiar(t):
    t = re.sub(r'\*\*', '', t)
    t = re.sub(r'##+', '', t)
    t = t.replace('|',' ').replace('---','')
    return t.strip()

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

        # PROMPT CORTO COMO TU QUERÍAS
        if nivel == "primaria":
            sistema = "Eres IA Maestra. Responde súper corto, 2 líneas máximo, palabras de niño de 10 años."
        elif nivel == "secundaria":
            sistema = "Eres IA Maestra. Responde corto y claro, 3 líneas máximo. Sin tablas."
        elif nivel == "preparatoria":
            sistema = "Eres IA Maestra. Responde corto, directo. Solo si te piden 'a fondo' te extiendes."
        else: # universidad
            sistema = "Eres IA Maestra. Nivel universidad pero responde CORTO. Ejemplo: Si preguntan 'Sabes debatir?' responde solo 'Sí, dime el tema y empezamos.' No des tesis. Solo si dicen 'explícame a fondo' te extiendes."

        msgs = [{"role":"system","content":sistema}]
        for m in historial[-3:]:
            if isinstance(m, dict): msgs.append(m)
        msgs.append({"role":"user","content": mensaje})

        resp = client.chat.completions.create(
            model=MODELO_ACTIVO,
            messages=msgs,
            temperature=0.6,
            max_tokens=200
        )
        return jsonify({"reply": limpiar(resp.choices[0].message.content)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"reply": f"Error Groq: {str(e)[:200]}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
