<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IA Maestra - J Carlos Double R</title>
<link rel="manifest" href="/manifest.json">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0f0f0f;color:white;display:flex;flex-direction:column;height:100vh}
header{background:#1a1a1a;padding:15px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #333}
.logo{display:flex;align-items:center;gap:10px}
.logo img{width:35px;height:35px;border-radius:8px;background:white;object-fit:cover}
.logo h1{font-size:18px}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:15px}
.msg{max-width:80%;padding:12px 16px;border-radius:15px;line-height:1.4;font-size:15px}
.user{background:#2d5bff;align-self:flex-end;border-bottom-right-radius:4px}
.bot{background:#222;align-self:flex-start;border-bottom-left-radius:4px;border:1px solid #333}
.input-area{display:flex;padding:15px;background:#1a1a1a;border-top:1px solid #333;gap:10px}
.input-area input{flex:1;padding:12px 15px;border-radius:25px;border:none;background:#2a2a2a;color:white;outline:none}
.input-area button{padding:12px 20px;border-radius:25px;border:none;background:#2d5bff;color:white;font-weight:bold;cursor:pointer}
footer{text-align:center;padding:8px;font-size:12px;color:#666}
footer a{color:#888;text-decoration:none}
</style>
</head>
<body>
<header>
  <div class="logo">
    <!-- Si tienes logo.png ponlo en templates y cambia src -->
    <img src="/icon-192.png" alt="logo">
    <h1>IA Maestra</h1>
  </div>
  <div style="font-size:13px;color:#aaa;">J Carlos Double R</div>
</header>

<div id="chat">
  <div class="msg bot">Hola, soy IA Maestra. Creada por <b>J Carlos Double R</b>. ¿En qué te ayudo hoy? Puedo leer links, darte el dólar real y noticias de Latinus.</div>
</div>

<div class="input-area">
  <input type="text" id="input" placeholder="Escribe o pega un link..." onkeypress="if(event.key==='Enter') enviar()">
  <button onclick="enviar()">Enviar</button>
</div>

<footer>
  <a href="#" onclick="abrirAcerca()">Acerca de</a> • Creado por J Carlos Double R
</footer>

<!-- MODAL ACERCA DE -->
<div id="modalAcerca" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999;">
  <div style="background:#1e1e1e; max-width:380px; margin:20% auto; padding:30px; border-radius:20px; text-align:center; border:1px solid #333;">
    <img src="/icon-192.png" style="width:80px;height:80px;border-radius:15px;margin-bottom:15px;background:white;">
    <h2>IA Maestra</h2>
    <p style="color:#aaa; margin:10px 0;">v2.0 - Tiempo Real</p>
    <hr style="border:none; border-top:1px solid #333; margin:15px 0;">
    <p style="font-size:18px; font-weight:bold;">Creado por<br>J Carlos Double R</p>
    <p style="font-size:13px; color:#777; margin-top:10px;">Coyuca de Benítez, Gro. México<br>Proyecto Escolar 2026<br>Con acceso a internet real, lector de links y noticias Latinus</p>
    <button onclick="cerrarAcerca()" style="margin-top:20px; padding:10px 25px; border:none; background:white; color:black; border-radius:10px; font-weight:bold; cursor:pointer;">Cerrar</button>
  </div>
</div>

<script>
let historial = [];
function abrirAcerca(){ document.getElementById('modalAcerca').style.display='block'; }
function cerrarAcerca(){ document.getElementById('modalAcerca').style.display='none'; }

async function enviar(){
  let input = document.getElementById('input');
  let texto = input.value.trim();
  if(!texto) return;
  let chat = document.getElementById('chat');
  chat.innerHTML += `<div class="msg user">${texto}</div>`;
  input.value = '';
  chat.scrollTop = chat.scrollHeight;

  historial.push({role:"user", content:texto});

  let respDiv = document.createElement('div');
  respDiv.className = 'msg bot';
  respDiv.textContent = 'Buscando datos reales...';
  chat.appendChild(respDiv);
  chat.scrollTop = chat.scrollHeight;

  let res = await fetch('/chat',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:texto, history:historial})});
  let data = await res.json();
  respDiv.textContent = data.reply;
  historial.push({role:"assistant", content:data.reply});
  chat.scrollTop = chat.scrollHeight;
}
</script>
</body>
</html>