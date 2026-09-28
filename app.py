from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import re
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODELO = "openai/gpt-oss-20b"

def limpiar(texto):
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)
    texto = re.sub(r'#{1,6}\s?', '', texto)
    texto = re.sub(r'\|', ' ', texto)
    texto = re.sub(r'---', '', texto)
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

    # Si el usuario pregunta por tus instrucciones, no las muestres
    if "que significa" in mensaje.lower() and len(mensaje) < 30:
        # Evita que repita el prompt
        pass

    resp = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": "Eres IA MAESTRA, creada por Julio. Eres una profesora experta, clara y directa. Tu regla principal es ser BREVE. Responde siempre en maximo 4 lineas cortas. Ve directo al punto, sin analogias infantiles, sin decir 'imagina que', sin cuentos. Usa lenguaje academico pero sencillo, nivel secundaria/prepa. No uses **, ##, *, |, ---. Si el tema necesita mas detalle, da 3 puntos clave numerados y al final pregunta: ¿Quieres que profundice en algun punto?"},
            {"role": "user", "content": mensaje}
        ],
        temperature=0.5,
        max_tokens=5000
    )
    texto_limpio = limpiar(resp.choices[0].message.content)
    return jsonify({"reply": texto_limpio})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))