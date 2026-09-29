from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

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
    msg = data.get('message', '').lower()

    # --- CEREBRO DE LA IA MAESTRA ---
    if 'hola' in msg or 'buenas' in msg:
        reply = "¡Hola! 👋 Soy tu IA Maestra. Estoy lista para ayudarte. ¿Qué materia quieres ver hoy? (Matemáticas, Ciencias, Español, Historia)"
    elif 'matem' in msg:
        reply = "¡Vamos con Matemáticas! 🧮 Dime qué tema: sumas, restas, fracciones, álgebra, geometría... ¿Qué problema tienes?"
    elif 'ciencia' in msg or 'biolog' in msg or 'quimica' in msg:
        reply = "¡Ciencias! 🔬 ¿Qué quieres aprender? El cuerpo humano, los animales, el sistema solar, química básica..."
    elif 'español' in msg or 'lectura' in msg:
        reply = "¡Español! 📚 ¿Quieres que te ayude con ortografía, redacción, lectura o análisis de un texto?"
    elif 'historia' in msg:
        reply = "¡Historia! 🏛️ ¿De qué época? México, Revolución, Segunda Guerra Mundial..."
    elif 'que te pasa' in msg:
        reply = "¡Nada! Estoy súper bien 😊 Solo estaba en modo de prueba. Ahora ya estoy al 100% para enseñarte. ¿Qué quieres que te explique?"
    elif 'quien eres' in msg:
        reply = "Soy tu IA Maestra, creada para ayudarte a aprender de forma fácil y divertida. ¡Estoy aquí 24/7 para ti!"
    else:
        # Respuesta general inteligente
        reply = f"Entendido, me preguntas sobre: '{data.get('message','')}'. \n\nDéjame explicártelo fácil: \n\n{data.get('message','')} es un tema muy interesante. Para ayudarte mejor, dime ¿en qué nivel vas? ¿Primaria, secundaria o prepa? Y te lo explico paso a paso con ejemplos."

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