import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

# Cliente de OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>IA Final</title>
<style>
body{font-family:Arial;background:#111;color:#fff;display:flex;flex-direction:column;align-items:center;padding:20px}
#chat{width:90%;max-width:600px;height:400px;background:#222;overflow-y:auto;padding:10px;border-radius:10px}
.msg{margin:8px 0;padding:8px 12px;border-radius:8px}
.user{background:#0b93f6;align-self:flex-end}
.bot{background:#333}
#inputArea{margin-top:15px;display:flex;width:90%;max-width:600px}
input{flex:1;padding:10px;border-radius:8px;border:none}
button{margin-left:8px;padding:10px 15px;border:none;border-radius:8px;background:#0b93f6;color:white}
</style>
</head>
<body>
<h2>IA Final - Chat con cerebro</h2>
<div id="chat"></div>
<div id="inputArea">
<input id="txt" placeholder="Escribe algo...">
<button onclick="send()">Enviar</button>
</div>
<script>
async function send(){
 let t=document.getElementById('txt').value;
 if(!t) return;
 let chat=document.getElementById('chat');
 chat.innerHTML+=`<div class='msg user'>${t}</div>`;
 document.getElementById('txt').value='';
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
 let d=await r.json();
 chat.innerHTML+=`<div class='msg bot'>${d.reply}</div>`;
 chat.scrollTop=chat.scrollHeight;
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")

    if not os.environ.get("OPENAI_API_KEY"):
        return jsonify({"reply": "Falta poner la API KEY en Render > Environment"})

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_msg}]
        )
        reply = resp.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run()