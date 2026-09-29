from flask import Flask, request, jsonify, send_from_directory
import os
from groq import Groq

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# --- TU API KEY ---
# Pon tu key aquí o mejor ponla en Render como variable de entorno GROQ_API_KEY
client = Groq(api_key=os.environ.get("GROQ_API_KEY", "gsk_TU_API_KEY_AQUI"))

MODELO = "llama-3.3-70b-versatile" # El más inteligente y rápido gratis

@app.route('/')
def home():
    return send_from_directory(TEMPLATES_DIR, 'index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory(TEMPLATES_DIR, 'manifest.json')

@app.route('/sw.js')
def sw():
    return send_from_directory(TEMPLATES_DIR, 'sw.js')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    user_msg = data.get('message','')

    try:
        completion = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Eres IA Maestra, una maestra mexicana muy amable, paciente y divertida. Explicas todo fácil, con ejemplos paso a paso, usas emojis. Si te preguntan de Excel das los códigos listos para copiar y pegar. Si te preguntan de cualquier materia, enseñas muy claro."},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = f"Uy, hubo un error con la API: {str(e)}. Revisa que tu API KEY de Groq esté bien puesta en Render."

    return jsonify({"reply": reply})

@app.route('/<path:path>')
def any_file(path):
    full_path = os.path.join(TEMPLATES_DIR, path)
    if os.path.isfile(full_path):
        return send_from_directory(TEMPLATES_DIR, path)
    return send_from_directory(TEMPLATES_DIR, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)