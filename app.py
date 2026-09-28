from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODELO = "openai/gpt-oss-20b"

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
            {"role": "system", "content": "Eres la IA MAESTRA. Experta y segura. Te llamas Meta IA. Creada por Julio."},
            {"role": "user", "content": mensaje}
        ],
        temperature=0.3,
        max_tokens=500
    )
    return jsonify({"reply": resp.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))