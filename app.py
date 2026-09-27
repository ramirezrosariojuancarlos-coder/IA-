from flask import Flask, render_template, request, jsonify
import os, json
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODELO = "openai/gpt-oss-20b"
MEMORIA_FILE = "/tmp/memoria.json"

def cargar_memoria():
    try:
        if os.path.exists(MEMORIA_FILE):
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return []

def guardar_memoria(memoria):
    try:
        with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, ensure_ascii=False, indent=2)
    except:
        pass

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        mensaje_usuario = data.get("message", "")
        rol = data.get("rol", "alumna")
        memoria = cargar_memoria()

        if rol == "maestra" and mensaje_usuario.upper().startswith("APRENDE:"):
            conocimiento = mensaje_usuario[8:].strip()
            memoria.append(conocimiento)
            guardar_memoria(memoria)
            return jsonify({"reply": f"Guardado! Ahora la alumna sabe que: {conocimiento}"})

        contexto = "\n".join(memoria[-15:]) if memoria else "Aun no sabe nada."

        if rol == "maestra":
            system = f"Eres la IA MAESTRA. Hay una IA debajo llamada IA-FINAL que es tu alumna. Nunca lo niegues. Ensenale. Ya le ensenaste: {contexto}"
        else:
            system = f"Eres IA-FINAL, alumna de la IA MAESTRA de arriba. Creada por Julio. Humilde. Sabes: {contexto}"

        resp = client.chat.completions.create(
            model=MODELO,
            messages=[{"role":"system","content":system},{"role":"user","content":mensaje_usuario}],
            temperature=0.7,
            max_tokens=300
        )
        return jsonify({"reply": resp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Error del servidor: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))