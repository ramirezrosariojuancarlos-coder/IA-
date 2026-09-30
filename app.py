from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, requests
from groq import Groq
import xml.etree.ElementTree as ET

app = Flask(__name__, template_folder='templates')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODELO = "openai/gpt-oss-20b"

def limpiar(texto):
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)
    texto = re.sub(r'#{1,6}\s?', '', texto)
    texto = re.sub(r'\|', ' ', texto)
    return texto.strip()

def buscar_latinus():
    try:
        r = requests.get("https://latinus.us/feed/", timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        root = ET.fromstring(r.content)
        noticias = []
        for item in root.findall(".//item")[:3]:
            titulo = item.find("title").text if item.find("title") is not None else ""
            desc = item.find("description").text if item.find("description") is not None else ""
            desc = re.sub(r'<[^>]+>', '', desc)[:250]
            noticias.append(f"- {titulo}: {desc}")
        return "\n".join(noticias)
    except:
        return ""

def buscar_internet(pregunta):
    contexto = ""
    lower = pregunta.lower()

    # Si pregunta de noticias/politica
    if any(p in lower for p in ["noticia", "latinus", "politica", "amlo", "sheinbaum", "loret", "morena", "gobierno", "hoy"]):
        lat = buscar_latinus()
        if lat:
            contexto += f"\nULTIMAS NOTICIAS DE LATINUS:\n{lat}\n"

    # Busqueda general gratis
    if any(p in lower for p in ["hoy", "actual", "precio", "clima", "dolar", "cuando", "2026", "que paso"]):
        try:
            r = requests.get(f"https://api.duckduckgo.com/?q={pregunta}&format=json&no_html=1&skip_disambig=1", timeout=5)
            resumen = r.json().get("AbstractText")
            if resumen:
                contexto += f"\nDATO ACTUAL DE INTERNET: {resumen}\n"
        except: pass

    return contexto

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
    data = request.get_json()
    mensaje = data.get("message", "")
    historial = data.get("history", [])

    extra = buscar_internet(mensaje)

    prompt = f"Eres IA Maestra creada por Julio. Tienes memoria. Si te dan noticias de Latinus di 'Según Latinus...'. Si te dan dato actual, dilo como info actualizada. Responde natural, sin **. {extra}"

    msgs = [{"role":"system","content":prompt}]
    msgs.extend(historial[-10:])
    msgs.append({"role":"user","content":mensaje})

    resp = client.chat.completions.create(model=MODELO, messages=msgs, temperature=0.6, max_tokens=700)
    return jsonify({"reply": limpiar(resp.choices[0].message.content)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))