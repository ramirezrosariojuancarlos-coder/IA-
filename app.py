from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import re
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODELO = "openai/gpt-oss-20b"

def limpiar(texto):
    # Quita todo el markdown feo
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto) # **negrita**
    texto = re.sub(r'#{1,6}\s?', '', texto) # ## titulos
    texto = re.sub(r'\|', ' ', texto) # tablas |
    texto = re.sub(r'---', '', texto)
    texto = re.sub(r'```.*?```', '', texto, flags=re.DOTALL)
    texto = re.sub(r'`', '', texto)
    texto = re.sub(r'\*', '', texto)
    return texto.strip()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/manifest.json")
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route("/sw.js")
def sw():
    return send_from_directory('.', 'sw.js')

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    mensaje = data.get("message", "")
    resp = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": "Eres la IA MAESTRA. Creada por Julio. REGLA OBLIGATORIA: Responde siempre en texto plano, limpio, sin markdown. Prohibido usar **, ##, *, |, ---, tablas, negritas, codigos. Usa solo texto normal, parrafos cortos y listas simples con guion - si es necesario. Respuestas cortas, claras y directas."},
            {"role": "user", "content": mensaje}
        ],
        temperature=0.5,
        max_tokens=250
    )
    texto_limpio = limpiar(resp.choices[0].message.content)
    return jsonify({"reply": texto_limpio})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))