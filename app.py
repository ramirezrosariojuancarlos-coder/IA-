from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)

# Aquí le das su personalidad y conocimiento
CEREBRO = {
    "hola": "¡Hola! Soy tu IA-Final, ya estoy viva en Render ✅ ¿En qué te ayudo?",
    "quien eres": "Soy IA-Final, tu servidor desplegado en Render, creada por ti hoy.",
    "que puedes hacer": "Puedo responder preguntas, recordar cosas, darte ideas, ayudarte con código, tareas y lo que me programes.",
}

HTML = """
<html><head><meta name='viewport' content='width=device-width,initial-scale=1'>
<style>
body{font-family:sans-serif;background:#0a0a0a;color:#fff;text-align:center;padding:20px}
#chat{background:#1a1a1a;border-radius:15px;padding:15px;max-width:500px;margin:20px auto;text-align:left;height:300px;overflow-y:auto}
.msg{margin:8px 0;padding:10px;border-radius:10px}
.user{background:#00ff88;color:#000;text-align:right}
.bot{background:#333}
input{padding:14px;width:70%;border-radius:12px;border:none}
button{padding:14px 18px;border-radius:12px;border:none;background:#00ff88;font-weight:bold}
</style></head><body>
<h2>🧠 IA-FINAL CON CEREBRO</h2>
<div id='chat'><div class='msg bot'>Hola, ya tengo más cerebro. Pregúntame algo.</div></div>
<input id='q' placeholder='Escribe aquí...'><button onclick='enviar()'>Enviar</button>
<script>
function enviar(){
 let q=document.getElementById('q').value;
 if(!q) return;
 let chat=document.getElementById('chat');
 chat.innerHTML+="<div class='msg user'>"+q+"</div>";
 fetch('/cerebro?q='+encodeURIComponent(q))
 .then(r=>r.json())
 .then(d=>{
   chat.innerHTML+="<div class='msg bot'>"+d.respuesta+"</div>";
   chat.scrollTop=chat.scrollHeight;
 });
 document.getElementById('q').value='';
}
</script>
</body></html>
"""

@app.route('/')
def home():
    return HTML

@app.route('/cerebro')
def cerebro():
    q = request.args.get('q','').lower()
    
    # 1. Busca en su memoria interna
    for palabra, respuesta in CEREBRO.items():
        if palabra in q:
            return jsonify({"respuesta": respuesta})

    # 2. Respuestas inteligentes según lo que preguntes
    if "hora" in q:
        return jsonify({"respuesta": f"Son las {datetime.datetime.now().strftime('%H:%M')} horas. Tu servidor está corriendo bien."})
    if "codigo" in q or "python" in q:
        return jsonify({"respuesta": "Puedo ayudarte a programar. Dime qué quieres que haga tu app y te doy el código listo para pegar."})
    if "render" in q:
        return jsonify({"respuesta": "Estoy desplegada en Render, región Oregon, con Python 3 y estoy en estado Deployed ✅"})

    # 3. Si no sabe, responde genérico pero inteligente
    return jsonify({"respuesta": f"Entendí que me dices: '{q}'. Ya estoy aprendiendo. Si quieres que sea aún más inteligente, conéctame a la API de OpenAI y tendré cerebro de ChatGPT."})

@app.route('/status')
def status():
    return jsonify({"status":"IA ACTIVA", "cerebro":"V2", "hora": str(datetime.datetime.now())})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
