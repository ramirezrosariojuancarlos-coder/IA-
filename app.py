from flask import Flask, render_template, request, jsonify
import os, json
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODELO = "openai/gpt-oss-20b"
MEMORIA_FILE = "memoria.json"

def cargar_memoria():
    try:
        with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def guardar_memoria(memoria):
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    mensaje_usuario = data.get("message", "")
    rol = data.get("rol", "alumna")
    memoria = cargar_memoria()

    if rol == "maestra" and mensaje_usuario.upper().startswith("APRENDE:"):
        conocimiento = mensaje_usuario[8:].strip()
        memoria.append(conocimiento)
        guardar_memoria(memoria)
        return jsonify({"reply": f"Perfecto. Le acabo de enseñar a mi alumna que: {conocimiento}. Preguntale ahora a ella."})

    contexto = "\n".join(memoria) if memoria else "Aun no le he enseñado nada."

    if rol == "maestra":
        system = f"""Eres la IA MAESTRA del proyecto final de Julio.
        IMPORTANTE: Si existe otra IA. Debajo de ti en la misma pagina hay una IA llamada IA-FINAL (alumna) modelo gpt-oss-20b que esta aprendiendo de ti.
        Nunca lo niegues. Si te dicen que hay otra IA, di que si, que es tu alumna.
        Tu mision es enseñarle. Eres experta, inteligente.
        Lo que ya le enseñaste: {contexto}
        """
    else:
        system = f"""Eres IA-FINAL, una IA alumna que aprende de la IA MAESTRA que esta justo arriba de ti.
        Si te dicen que hay otra IA arriba, di que si, que es tu maestra y que aprendes de ella.
        Fuiste creada por Julio para el proyecto final.
        Personalidad: humilde, curiosa, con ganas de aprender.
        Esto es lo que tu maestra ya te enseno:
        {contexto}
        Si no sabes algo, di que aun no te lo han enseñado.
        """

    resp = client.chat.completions.create(
        model=MODELO,
        messages=[{"role":"system","content":system},{"role":"user","content":mensaje_usuario}],
        temperature=0.7,
        max_tokens=400
    )
    return jsonify({"reply": resp.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))