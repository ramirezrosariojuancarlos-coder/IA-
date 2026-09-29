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
    msg = data.get('message', '')
    return jsonify({"reply": f"Me dijiste: {msg}"})

@app.route('/<path:path>')
def any_file(path):
    full_path = os.path.join(TEMPLATES_DIR, path)
    if os.path.isfile(full_path):
        return send_from_directory(TEMPLATES_DIR, path)
    return send_from_directory(TEMPLATES_DIR, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)