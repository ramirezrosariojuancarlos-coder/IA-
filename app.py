from flask import Flask, render_template, request, jsonify
import os
import json
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODELO = "openai/gpt-oss-20b"

MEMORIA_FILE = "memoria.json"

def cargar_memoria():
    if not os.path.exists(MEMORIA_FILE):
        return []
    with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_memoria(memoria):
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    mensaje = data.get("message")
    rol = data.get("rol") # "maestra" o "alumna"

    memoria = cargar_memoria()
    contexto_memoria = "\n".join([f"- {m}" for m in memoria[-10:]])

    if rol == "maestra":
        system_prompt = """
        Eres la IA MAESTRA, inteligente, directa y un poco sarcástica.
        Te llamas Meta IA. Eres la versión avanzada. Tu trabajo es corregir a la IA Alumna y explicar bien.
        Siempre responde con seguridad.
        """

    else: # alumna
        system_prompt = f"""
        Eres IA-FINAL, una IA que APENAS ESTA APRENDIENDO.
        Eres humilde, dices cosas como "creo que", "aún estoy aprendiendo", "si no me equivoco".
        Tu meta es llegar a ser como la IA Maestra.
        Esto es lo que has aprendido hasta ahora:
        {contexto_memoria}
        Si no sabes algo, dilo con honestidad. Si te corrigen, agradece.
        Fuiste creada por Julio.
        """

    completion = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensaje}
        ],
        temperature= 0.7 if rol == "alumna" else 0.3
    )

    respuesta = completion.choices[0].message.content

    # Si es la maestra corrigiendo, la alumna aprende
    if rol == "maestra" and "APRENDE:" in mensaje:
        nuevo_conocimiento = mensaje.split("APRENDE:")[1].strip()
        memoria.append(nuevo_conocimiento)
        guardar_memoria(memoria)

    return jsonify({"reply": respuesta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
<div style="display:flex; gap:20px">
  <div style="flex:1; border:2px solid blue; padding:10px">
    <h3> IA Maestra (Yo)</h3>
    <div id="chat-maestra"></div>
    <input id="input-maestra" placeholder="Habla con la maestra...">
  </div>
  <div style="flex:1; border:2px solid green; padding:10px">
    <h3> IA-Final (Aprendiendo)</h3>
    <div id="chat-alumna"></div>
    <input id="input-alumna" placeholder="Habla con la alumna...">
  </div>
</div>

<script>
// Vas a tener que duplicar tu función de enviar mensaje
// enviando rol: 'maestra' o 'alumna'
// Y para enseñarle, escribes en la maestra: APRENDE: la fotosíntesis es...
</script>