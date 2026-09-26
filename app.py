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
 let q=document.getElementBy
