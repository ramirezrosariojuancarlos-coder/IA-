from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

HTML = """
<html><head><meta name='viewport' content='width=device-width,initial-scale=1'>
<style>
body{font-family:sans-serif;background:#0a0a0a;color:#fff;text-align:center;padding:20px}
#chat{background:#1a1a1a;border-radius:15px;padding:15px;max-width:500px;margin:20px auto;text-align:left;height:400px;overflow-y:auto}
.msg{margin:8px 0;padding:12px;border-radius:12px;line-height:1.4}
.user{background:#00ff88;color:#000;text-align:right}
.bot{background:#333}
input{padding:14px;width:68%;border-radius:12px;border:none}
button{padding:14px 18px;border-radius:12px;border:none;background:#00ff88;font-weight:bold}
</style></head>
<body>
<h2>🧠 IA-FINAL V3 - REAL</h2>
<div id='chat'><div class='msg bot'>Hola, ya tengo cerebro real de OpenAI. Pregúntame lo que quieras.</div></div>
<br>
<input id='q' placeholder='Escribe aquí...'><button onclick='enviar()'>Enviar</button>
<script>
function enviar(){
 let q=document.getElementById('q').value;
 if(!q) return;
 let chat=document.getElementById('chat');
 chat.innerHTML+="<div class='msg user'>"+q+"</div>";
 chat.scrollTop=chat.scrollHeight;
 document.getElementById('q').value='';
 fetch('/cerebro?q='+encodeURIComponent(q))
.then(r=>r.json())
.then(d=>{
   chat.innerHTML+="<div class='msg bot'>"+d.respuesta+"</div>";
   chat.scrollTop=chat.scrollHeight;
 });
}
</script>
</body></html>
"""

@app.route('/')
def home():
    return HTML

@app.route('/cerebro')
def cerebro():
    q = request.args.get('q','')
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"Eres IA-Final, la IA del usuario, útil, amigable, hablas español, eres muy inteligente."},
                {"role":"user","content": q}
            ]
        )
        return jsonify({"respuesta": resp.choices[0].message.content})
    except Exception as e:
        return jsonify({"respuesta": f"Error: {e}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)