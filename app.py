from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, json, math

app = Flask(__name__)

# --- CONFIG GROQ, no se cae si falta la key ---
try:
    from groq import Groq
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    MODELO = "openai/gpt-oss-20b"
except Exception as e:
    client = None
    print(f"Groq no configurado: {e}")

CEREBRO_FILE = "cerebro_custom.json"

def limpiar(texto):
    if not texto: return ""
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)
    texto = re.sub(r'#{1,6}\s?', '', texto)
    texto = re.sub(r'\|', ' ', texto)
    texto = re.sub(r'---', '', texto)
    texto = re.sub(r'`', '', texto)
    texto = re.sub(r'\*', '', texto)
    return texto.strip()

def cargar_cerebro():
    if not os.path.exists(CEREBRO_FILE):
        return {"neuronas": []}
    try:
        with open(CEREBRO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"neuronas": []}

def guardar_cerebro(data):
    with open(CEREBRO_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def activar(tipo, x):
    try:
        if tipo == "sigmoid": return 1 / (1 + math.exp(-x))
        if tipo == "relu": return max(0, x)
        if tipo == "tanh": return math.tanh(x)
    except: return 0
    return x

# --- PRIMOS GEMELOS ---
def get_twin_pair(n):
    limit = 10000
    while True:
        is_prime = bytearray(b'\x01') * (limit+3)
        is_prime[0:2] = b'\x00\x00'
        r = int(limit**0.5)+1
        for i in range(2, r):
            if is_prime[i]:
                is_prime[i*i:limit+3:i] = b'\x00' * (((limit+2 - i*i)//i)+1)
        twins = [(p, p+2) for p in range(3, limit) if is_prime[p] and is_prime[p+2]]
        if len(twins) >= n: return twins[n-1]
        limit *= 2

def extraer_numero(texto):
    m = re.search(r'\d+', texto)
    return int(m.group()) if m else None

# --- RUTAS ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/laboratorio")
def laboratorio():
    try:
        cerebro = cargar_cerebro()
        return render_template("laboratorio.html", cerebro=cerebro)
    except Exception as e:
        return f"<h1>Falta templates/laboratorio.html</h1><p>{e}</p><a href='/'>Volver al inicio</a>"

@app.route("/api/neurona", methods=["POST"])
def crear_neurona():
    data = request.get_json()
    cerebro = cargar_cerebro()
    nueva = {
        "nombre": data.get("nombre", f"Neurona {len(cerebro['neuronas'])+1}"),
        "pesos": data.get("pesos", [0.5, 0.5]),
        "sesgo": data.get("sesgo", 0),
        "curva": data.get("curva", "sigmoid")
    }
    cerebro["neuronas"].append(nueva)
    guardar_cerebro(cerebro)
    return jsonify({"ok": True, "cerebro": cerebro})

@app.route("/api/neurona/calcular", methods=["POST"])
def calcular_neurona():
    data = request.get_json()
    entradas = data.get("entradas", [])
    pesos = data.get("pesos", [])
    sesgo = data.get("sesgo", 0)
    curva = data.get("curva", "sigmoid")
    suma = sum(e * p for e, p in zip(entradas, pesos)) + sesgo
    salida = activar(curva, suma)
    return jsonify({"suma": suma, "salida": salida})

@app.route("/api/cerebro/borrar", methods=["POST"])
def borrar_cerebro():
    guardar_cerebro({"neuronas": []})
    return jsonify({"ok": True})

@app.route("/manifest.json")
def manifest(): 
    if os.path.exists("manifest.json"):
        return send_from_directory('.', 'manifest.json')
    return jsonify({})

@app.route("/sw.js")
def sw(): 
    if os.path.exists("sw.js"):
        return send_from_directory('.', 'sw.js')
    return "", 404

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    mensaje = data.get("message", "") or ""

    cerebro = cargar_cerebro()
    if "mi neurona" in mensaje.lower() and cerebro["neuronas"]:
        n = cerebro["neuronas"][-1]
        return jsonify({"reply": f"Usando tu última neurona '{n['nombre']}' con pesos {n['pesos']}, sesgo {n['sesgo']} y curva {n['curva']}. Dime los números de entrada y te calculo la salida como en el video."})

    if "gemelo" in mensaje.lower() or "par numero" in mensaje.lower() or "par número" in mensaje.lower():
        num = extraer_numero(mensaje)
        if num:
            par = get_twin_pair(num)
            return jsonify({"reply": f"El par número {num} de primos gemelos es: {par}"})

    if client is None:
        return jsonify({"reply": "Falta configurar GROQ_API_KEY en Render, pero tu laboratorio de neuronas si funciona. Ve a /laboratorio"})

    try:
        resp = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Eres IA Maestra, una asistente amable, clara y útil creada por Julio. Hablas español. Responde siempre natural, corta y limpia."},
                {"role": "user", "content": mensaje}
            ],
            temperature=0.5, max_tokens=500
        )
        return jsonify({"reply": limpiar(resp.choices[0].message.content)})
    except Exception as e:
        return jsonify({"reply": f"Error de Groq: {e}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
