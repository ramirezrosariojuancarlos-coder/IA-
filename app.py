from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, requests
from groq import Groq
import xml.etree.ElementTree as ET

app = Flask(__name__, template_folder='templates')
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODELO = "openai/gpt-oss-20b"

def limpiar(t):
    t = re.sub(r'\*\*(.*?)\*\*', r'\1', t)
    t = re.sub(r'#{1,6}\s?', '', t)
    return t.strip()

# --- LECTOR DE LINKS GRATIS QUE SI SIRVE ---
def leer_link(url):
    try:
        # jina.ai te convierte cualquier web en texto limpio gratis
        r = requests.get(f"https://cc.jina.ai/{url}", timeout=12, headers={"User-Agent":"Mozilla/5.0"})
        # Si falla, prueba con r.jina.ai
        if len(r.text) < 100:
            r = requests.get(f"https://r.jina.ai/http://{url.replace('https://','').replace('http://','')}", timeout=12)
        texto = r.text[:4000] # solo 4000 caracteres para no saturar
        return texto
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

    # 1. DETECTA LINKS
    urls = re.findall(r'(https?://\S+)', pregunta)
    for url in urls[:2]:
        contenido = leer_link(url)
        if contenido:
            contexto += f"\nCONTENIDO REAL DE LA WEB {url}:\n{contenido[:3000]}\n"

    # 2. NOTICIAS
    if any(x in lower for x in ["noticia", "latinus", "politica", "morena", "sheinbaum", "amlo"]):
        contexto += f"\nNOTICIAS LATINUS HOY:\n{get_latinus()}\n"

    # 3. DOLAR REAL
    if "dolar" in lower or "dólar" in lower or "usd" in lower:
        try:
            mxn = requests.get("https://open.er-api.com/v6/latest/USD", timeout=6).json()["rates"]["MXN"]
            contexto += f"\nDATO REAL: Dolar hoy 1 USD = {mxn:.2f} MXN\n"
        except: pass

    # 4. CLIMA
    if "clima" in lower:
        try:
            c = requests.get("https://wttr.in/Zihuatanejo?format=%C+%t", timeout=5).text
            contexto += f"\nDATO REAL: Clima Zihuatanejo ahora: {c}\n"
        except: pass

    # 5. CUALQUIER OTRA COSA ACTUAL - busca en Wikipedia que si tiene resumen bueno
    if any(x in lower for x in ["que es", "quien es", "cuando", "donde", "hoy", "actual"]):
        try:
            # Wikipedia gratis
            q = pregunta.replace(" ","%20")
            wiki = requests.get(f"https://es.wikipedia.org/api/rest_v1/page/summary/{q}", timeout=5).json()
            if wiki.get("extract"):
                contexto += f"\nDATO DE WIKIPEDIA: {wiki['extract'][:500]}\n"
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
    extra = inyectar_tiempo_real(mensaje)

    system = f"""Eres IA Maestra. Creada por Julio.
TIENES INTERNET. Te inyecto datos reales abajo, ÚSALOS y nunca digas que tu conocimiento corta en 2024.
Si te paso contenido de una web, resumelo. Si te paso dólar o clima, dilo como dato actual.
Datos reales inyectados: {extra}
"""

    msgs = [{"role":"system","content":system}]
    msgs.extend(historial[-10:])
    msgs.append({"role":"user","content":mensaje})

    resp = client.chat.completions.create(model=MODELO, messages=msgs, temperature=0.5, max_tokens=1000)
    return jsonify({"reply": limpiar(resp.choices[0].message.content)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))