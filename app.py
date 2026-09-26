import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>IA Final</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;background:#111;color:#fff;display:flex;flex-direction:column;align-items:center;padding:20px}
#chat{width:90%;max-width:600px;height:400px;background:#222;overflow-y:auto;padding:10px;border-radius:10px;display:flex;flex-direction:column}
.msg{margin:8px 0;padding:10px 12px;border-radius:12px;max-width:80%;word-wrap:break-word}
.user{background:#0b93f6;align-self:flex-end}
.bot{background:#333;align-self:flex-start}
#inputArea{margin-top:15px;display:flex;width:90%;max-width:600px}
input{flex:1;padding:12px;border-radius:8px;border:none}
button{margin-left:8px;padding:12px 15px;border:none;border-radius:8px;background:#0b93f6;color:white;font-weight:bold}
</style>
</head>
<body>
<h2>IA Final - Chat con cerebro</h2>
<div id="chat"></div>
<div id="inputArea">
<input id="txt" placeholder="Escribe algo..." onkeypress="if(event.key==='Enter')send()">
<button onclick="send()">Enviar</button>
</div>
<script>
async function send(){
 let t=document.getElementById('txt').value;
 if(!t) return;
 let chat=document.getElementById('chat');
 chat.innerHTML+=`<div class='msg user'>${t}</div>`;
 document.getElementById('txt').value='';
 chat.scrollTop=chat.scrollHeight;
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

    if not os.environ.get("GROQ_API_KEY"):
        return jsonify({"reply": "Falta poner la GROQ_API_KEY en Render > Environment"})

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_msg}]
        )
        reply = resp.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run()