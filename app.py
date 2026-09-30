from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, requests
from groq import Groq
import xml.etree.ElementTree as ET

# --- Iconos ---
try:
    from PIL import Image, ImageDraw
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    for size in [192, 512]:
        path = os.path.join(TEMPLATES_DIR, f'icon-{size}.png')
        if not os.path.exists(path):
            img = Image.new('RGB', (size, size), '#0f3460')
            d = ImageDraw.Draw(img)
            d.ellipse([size*0.2, size*0.2, size*0.8, size*0.8], fill='white')
            img.save(path)
except: pass

app = Flask(__name__, template_folder='templates')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
TAVILY_KEY = os.environ.get("TAVILY_API_KEY", "") # Ponla en Render si la sacas
MODELO = "openai/gpt-oss-20b"

def limpiar(texto):
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)
    texto = re.sub(r'#{1,6}\s?', '', texto)
    texto = re.sub(r'\|', ' ', texto)
    texto = re.sub(r'---', '', texto)
    return texto.strip()

def buscar_latinus(pregunta):
    # Si pregunta por noticias, politica, amlo, sheinbaum, latinus
    gatillos_noticia = ["noticia", "latinus", "politica", "gobierno", "morena", "amlo", "sheinbaum", "loret"]
    if not any(p in pregunta.lower() for p in gatillos_noticia):
        return ""
    try:
        # RSS de Latinus
        r = requests.get("https://latinus.us/feed/", timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        root = ET.fromstring(r.content)
        noticias = []
        for item in root.findall(".//item")[:3]: # 3 ultimas
            titulo = item.find("title").text if item.find("title") is not None else ""
            desc = item.find("description").text if item.find("description") is not None else ""
            # Limpia html
            desc = re.sub(r'<[^>]+>', '', desc)[:300]
            noticias.append(f"- {titulo}: {desc}")
        if noticias:
            return "\nNOTICIAS RECIENTES DE LATINUS (úsalas, cita a Latinus):\n" + "\n".join(noticias) + "\n"
    except Exception as e:
        print("Error Latinus:", e)
    return ""

def buscar_internet(pregunta):
    contexto = ""

    # 1. Latinus primero
    contexto += buscar_latinus(pregunta)

    # 2. Busqueda general
    gatillos = ["hoy", "actual", "precio", "clima", "quien gano", "cuando", "2025", "2026", "dolar", "presidente", "que paso"]
    if any(p in pregunta.lower() for p in gatillos) or contexto!= "":

        # Si tienes TAVILY_API_KEY es 10x mejor
        if TAVILY_KEY:
            try:
                r = requests.post("https://api.tavily.com/search",
                    json={"query": pregunta, "max_results": 3, "include_answer": True, "api_key": TAVILY_KEY}, timeout=10)
                data = r.json()
                if data.get("answer"):
                    contexto += f"\nINFO ACTUALIZADA DE INTERNET: {data['answer']}\n"
                for res in data.get("results", [])[:2]:
                    contexto += f"\nFuente: {res.get('content','')[:400]}\n"
            except: pass
        else:
            # Fallback gratis DuckDuckGo
            try:
                r = requests.get(f"https://api.duckduckgo.com/?q={pregunta}&format=json&no_html=1", timeout=5)
                data = r.json()
                resumen = data.get("AbstractText")
                if resumen:
                    contexto += f"\nINFO ACTUAL DE INTERNET: {resumen}\n"
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
    contexto_actual = buscar_internet(mensaje)

    mensajes_ia = [
        {"role": "system", "content": f"Eres IA Maestra, creada por Julio en Guerrero. Tienes memoria. Hablas español natural. Si te dan contexto, úsalo y di que es información actualizada. Si es de Latinus, di 'Según Latinus...'. Nunca uses ** ni #. {contexto_actual}"}
    ]
    mensajes_ia.extend(historial[-10:])
    mensajes_ia.append({"role": "user", "content": mensaje})

    resp = client.chat.completions.create(model=MODELO, messages=mensajes_ia, temperature=0.6, max_tokens=700)
    return jsonify({"reply": limpiar(resp.choices[0].message.content)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))