from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/sw.js')
def sw():
    return send_from_directory('.', 'sw.js')

@app.route('/chat', methods=['POST'])
def chat(): 
    data = request.get_json()
    msg = data.get('message', '') if data else ''
    reply = f"Me preguntaste: {msg}. ¡Vamos a aprender juntos!"
    return jsonify({"reply": reply})

# Esto evita el Not Found para cualquier otro archivo
@app.route('/<path:path>')
def serve_any(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    else:
        return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)