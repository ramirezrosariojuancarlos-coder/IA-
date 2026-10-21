from flask import Flask, render_template, request, jsonify, send_from_directory
import os, re, json, math

app = Flask(__name__)

try:
    from groq import Groq
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    MODELO = "openai/gpt-oss-20b"
except:
    client = None

DATABASE_URL = os.environ.get("DATABASE_URL")
CEREBRO_FILE = "cerebro_custom.json"

def get_db_conn():
    if not DATABASE_URL: return None
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error DB: {e}")
        return None

def init_db():
    conn = get_db_conn()
    if not conn: return
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS neuronas (
            id SERIAL PRIMARY KEY,
            nombre TEXT,
            pesos TEXT,
            sesgo FLOAT,
            curva TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def cargar_cerebro():
    conn = get_db_conn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT nombre, pesos, sesgo, curva FROM neuronas ORDER BY id")
            rows = cur.fetchall()
            neuronas = []
            for nombre, pesos, sesgo, curva in rows:
                neuronas.append({
                    "nombre": nombre,
                    "pesos": json.loads(pesos),
                    "sesgo": sesgo,
                    "curva": curva
                })
            cur.close()
            conn.close()
            return {"neuronas": neuronas}
        except Exception as e:
            print(e)
    # Fallback archivo
    if os.path.exists(CEREBRO_FILE):
        try:
            with open(CEREBRO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {"neuronas": []}

def guardar_neurona_db(nombre, pesos, sesgo, curva):
    conn = get_db_conn()
    if conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO neuronas (nombre, pesos, sesgo, curva) VALUES (%s,%s,%s,%s)",
                    (nombre, json.dumps(pesos), sesgo, curva))
        conn.commit()
        cur.close()
        conn.close()
        return True
    else:
        # fallback archivo
        cerebro = cargar_cerebro()
        cerebro["neuronas"].append({"nombre":nombre,"pesos":pesos,"sesgo":sesgo,"curva":curva})
        with open(CEREBRO_FILE, 'w', encoding='utf-8') as f:
            json.dump(cerebro, f, ensure_ascii=False, indent=2)
        return False

def activar(tipo, x):
    try:
        if tipo == "sigmoid": return 1 / (1 + math.exp(-x))
        if tipo == "relu": return max(0, x)
        if tipo == "tanh": return math.tanh(x)
    except: return 0
    return x

def extraer_numero(texto):
    m = re.search(r'\d+', texto)
    return int(m.group()) if m else None

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

def limpiar(texto):
    if not texto: return ""
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)
    texto = re.sub(r'#{1,6}\s?', '', texto)
    texto = re.sub(r'\|', ' ', texto)
    return texto.strip()

@app.route("/")
def index(): return render_template("index.html")

@app.route("/laboratorio")
def laboratorio():
    init_db()
    cerebro = cargar_cerebro()
    return render_template("laboratorio.html", cerebro=cerebro)

@app.route("/api/neurona", methods=["POST"])
def crear_neurona():
    data = request.get_json()
    nombre = data.get("nombre", "Neurona")
    pesos = data.get("pesos", [0.5, 0.5])
    sesgo = data.get("sesgo", 0)
    curva = data.get("curva", "sigmoid")
    guardar_neurona_db(nombre, pesos, sesgo, curva)
    return jsonify({"ok": True, "cerebro": cargar_cerebro()})

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
    conn = get_db_conn()
    if conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM neuronas")
        conn.commit()
        cur.close()
        conn.close()
    else:
        if os.path.exists(CEREBRO_FILE):
            os.remove(CEREBRO_FILE)
    return jsonify({"ok": True})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    mensaje = data.get("message", "") or ""
    if "mi neurona" in mensaje.lower():
        cerebro = cargar_cerebro()
        if cerebro["neuronas"]:
            n = cerebro["neuronas"][-1]
            return jsonify({"reply": f"Usando tu neurona '{n['nombre']}' de tu base de datos permanente. Pesos {n['pesos']}, sesgo {n['sesgo']}"})
    if "gemelo" in mensaje.lower():
        num = extraer_numero(mensaje)
        if num:
            par = get_twin_pair(num)
            return jsonify({"reply": f"El par número {num} de primos gemelos es: {par}"})
    if client is None:
        return jsonify({"reply": "Falta GROQ_API_KEY pero tu cerebro permanente si funciona en /laboratorio"})
    resp = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": "Eres IA Maestra, asistente amable creada por Julio. Hablas español, corta y limpia."},
            {"role": "user", "content": mensaje}
        ],
        temperature=0.5, max_tokens=500
    )
    return jsonify({"reply": limpiar(resp.choices[0].message.content)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
