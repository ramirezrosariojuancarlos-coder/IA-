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
        return ["Soy nueva, aun no se nada."]

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
        return jsonify({"reply": f"Guardado! Ahora la alumna sabe que: {conocimiento}"})

    contexto = "\n".join(memoria[-15:])

    if rol == "maestra":
        system = f"""Eres la IA MAESTRA. Eres experta, segura. Te llamas Meta IA.
        En esta pagina hay otra IA debajo de ti llamada IA-FINAL que es tu alumna. Nunca lo niegues.
        Tu mision es ensenarle. Si te habla tu alumna, corrigela y ensenale bien.
        Lo que ya le ensenaste: {contexto}
        """
    else:
        system = f"""Eres IA-FINAL, una IA bebe que aprende de la IA MAESTRA de arriba.
        Si te habla tu maestra, respondele con humildad y curiosidad.
        Fuiste creada por Julio.
        Esto es lo que ya sabes: {contexto}
        """

    resp = client.chat.completions.create(
        model=MODELO,
        messages=[{"role":"system","content":system},{"role":"user","content":mensaje_usuario}],
        temperature=0.8 if rol == "alumna" else 0.3,
        max_tokens=400
    )
    return jsonify({"reply": resp.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))