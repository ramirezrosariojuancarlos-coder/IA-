from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html><head><meta name='viewport' content='width=device-width,initial-scale=1'>
    <style>
    body{font-family:sans-serif;background:#111;color:#fff;text-align:center;padding:20px}
    #chat{background:#222;padding:15px;border-radius:15px;max-width:500px;margin:auto;height:400px;overflow-y:auto;text-align:left}
    .user{background:#00ff88;color:#000;padding:10px;border-radius:10px;margin:5px;text-align:right}
    .bot{background:#333;padding:10px;border-radius:10px;margin:5px}
    </style></head>
    <body>
    <h2>IA-FINAL con cerebro real</h2>
    <div id='chat'><div class='bot'>Hola! Ya tengo cerebro. Pregúntame algo.</div></div>
    <br><input id='q' style='padding:12px;width:60%;border-radius:10px;border:none' placeholder='Escribe...'>
    <button style='padding:12px;border-radius:10px;background:#00ff88;border:none;font-weight:bold' onclick='enviar()'>Enviar</button>
    <script>
    function enviar(){
      let q=document.getElementById('q').value;
      if(!q) return;
      let c=document.getElementById('chat');
      c.innerHTML+="<div class='user'>"+q+"</div>";
      document.getElementById('q').value='';
      fetch('/cerebro?q='+encodeURIComponent(q)).then(r=>r.json()).then(d=>{
        c.innerHTML+="<div class='bot'>"+d.respuesta+"</div>";
        c.scrollTop=c.scrollHeight;
      });
    }
    </script>
    </body></html>
    """

@app.route('/cerebro')
def cerebro():
    pregunta = request.args.get('q','Hola')
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":pre