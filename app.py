
from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, requests
from groq import Groq
import xml.etree.ElementTree as ET

app = Flask(__name__, template_folder='templates')
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODELO_TEXTO = "openai/gpt-oss-20b"
MODELO_VISION = "meta-llama/llama-4-scout-17b-16e-instruct"

def limpiar(t):
    t = re.sub(r'\*\*(.*?)\*\*', r'\1', t)
    t = re.sub(r'#{1,6}\s?', '', t)
    return t.strip()

def leer_link(url):
    try:
        r = requests.get(f"https://cc.jina.ai/{url}", timeout=12, headers={"User-Agent":"Mozilla/5.0"})
        return r.text[:4000]
    except: return ""

def get_latinus():
    try:
        r = requests.get("https://latinus.us/feed/", timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        root = ET.fromstring(r.content)
        out=[]
        for item in root.findall(".//item")[:4]:
            t = item.find("title").text or ""
            d = re.sub(r'<[^>]+>', '', item.find("description").text or "")[:180]
            out.append(f"- {t}: {d}")
        return "\n".join(out)
    except: return ""

def inyectar_tiempo_real(pregunta):
    lower = pregunta.lower()
    contexto = ""
    urls = re.findall(r'(https?://\S+)', pregunta)
    for url in urls[:2]:
        c = leer_link(url)
        if c: contexto += f"\nWEB REAL {url}:\n{c[:3000]}\n"
    if any(x in lower for x in ["noticia", "latinus", "morena", "sheinbaum"]):
        contexto += f"\nNOTICIAS LATINUS HOY:\n{get_latinus()}\n"
    if "dolar" in lower or "dólar" in lower or "usd" in lower:
        try:
            r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=6).json()
            contexto += f"\nDolar hoy 1 USD = {r['rates']['MXN']:.4f} MXN\n"
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
    mensaje = data.get("message","")
    historial = data.get("history",[])
    imagen = data.get("image", None)
    extra = inyectar_tiempo_real(mensaje)
    system = f"Eres IA Maestra, creada por J Carlos Double R. Eres maestra que explica con imagenes. Datos reales: {extra}"

    msgs = [{"role":"system","content":system}]
    msgs.extend(historial[-8:])

    if imagen:
        msgs.append({
            "role":"user",
            "content": [
                {"type":"text","text": mensaje},
                {"type":"image_url","image_url":{"url": imagen}}
            ]
        })
        modelo_usar = MODELO_VISION
    else:
        msgs.append({"role":"user","content": mensaje})
        modelo_usar = MODELO_TEXTO

    resp = client.chat.completions.create(model=modelo_usar, messages=msgs, temperature=0.6, max_tokens=900)
    return jsonify({"reply": limpiar(resp.choices[0].message.content)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))