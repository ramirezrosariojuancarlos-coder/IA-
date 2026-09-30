<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IA Maestra</title>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#1a1a2e">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box} body{font-family:Arial,sans-serif;background:#f0f2f5;height:100vh;display:flex;flex-direction:column}
.topbar{display:flex;justify-content:space-between;align-items:center;padding:12px 15px;background:#1a1a2e;color:white;z-index:10}
  #menu-btn,#dots-btn{font-size:26px;background:none;border:none;color:white;cursor:pointer;padding:5px}
.topbar h1{font-size:18px}
.side-menu{position:fixed;top:0;left:-280px;width:260px;height:100%;background:#16213e;padding-top:70px;transition:0.3s ease;z-index:1001;display:flex;flex-direction:column}
.side-menu.open{left:0}
.side-menu a{display:flex;align-items:center;gap:14px;padding:16px 20px;color:#ddd;text-decoration:none;border-bottom:1px solid #2a2a4a}
.dots-menu{position:fixed;top:50px;right:10px;width:200px;background:white;border-radius:10px;box-shadow:0 4px 15px rgba(0,0,0,0.2);display:none;flex-direction:column;z-index:1002;overflow:hidden}
.dots-menu.open{display:flex}
.dots-menu a{display:flex;align-items:center;gap:10px;padding:12px 15px;color:#333;text-decoration:none;font-size:14px}
  #overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:1000}
  #overlay.show{display:block}
  #chat-container{flex:1;overflow-y:auto;padding:15px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:10px 14px;border-radius:15px;line-height:1.4;word-wrap:break-word;font-size:15px}
.user{align-self:flex-end;background:#0f3460;color:white;border-bottom-right-radius:3px}
.bot{align-self:flex-start;background:white;color:#333;border-bottom-left-radius:3px;box-shadow:0 1px 2px rgba(0,0,0,0.1)}
.msg img{max-width:100%;border-radius:10px;margin-top:8px}
  #input-area{display:flex;padding:10px;background:white;border-top:1px solid #ddd;align-items:center;gap:8px}
  #user-input{flex:1;padding:12px;border:1px solid #ddd;border-radius:25px;outline:none}
  #send-btn{padding:0 20px;height:42px;border:none;background:#0f3460;color:white;border-radius:25px;cursor:pointer}
  #cam-btn{background:none;border:none;font-size:24px;cursor:pointer}
  #preview{display:none;padding:8px;background:white;border-top:1px solid #eee;align-items:center;gap:10px}
  #preview img{max-height:100px;border-radius:8px}
.materia-btn{margin:4px;padding:8px 12px;border-radius:20px;border:1px solid #0f3460;background:white;cursor:pointer}
</style>
</head>
<body>
<div class="topbar">
  <button id="menu-btn">☰</button><h1>IA Maestra</h1><button id="dots-btn">⋮</button>
  <div id="dots-menu" class="dots-menu">
    <a href="#" onclick="copyLast(); closeDots()"><span class="material-icons">content_copy</span> Copiar</a>
    <a href="#" onclick="shareLast(); closeDots()"><span class="material-icons">share</span> Compartir</a>
    <a href="#" onclick="deleteLast(); closeDots()"><span class="material-icons">delete</span> Borrar</a>
  </div>
</div>
<div id="side-menu" class="side-menu">
  <a href="#" onclick="closeMenu(); location.reload();"><span class="material-icons">home</span> Inicio</a>
  <a href="#" onclick="showMaterias()"><span class="material-icons">menu_book</span> Materias</a>
  <a href="#" onclick="clearChat(); closeMenu();"><span class="material-icons">history</span> Borrar Historial</a>
  <a href="#" onclick="showAcerca()"><span class="material-icons">info</span> Acerca de</a>
</div>
<div id="overlay" onclick="closeMenu(); closeDots();"></div>
<div id="chat-container"></div>
<div id="preview"><img id="preview-img"><button onclick="quitarImagen()" style="padding:5px 10px;background:#ff4444;color:white;border:none;border-radius:6px;">X</button><span style="font-size:11px">Comprimida lista</span></div>
<div id="input-area">
  <input type="file" id="file-input" accept="image/*" style="display:none">
  <button id="cam-btn" onclick="document.getElementById('file-input').click()">📷</button>
  <input type="text" id="user-input" placeholder="Escribe o envía imagen...">
  <button id="send-btn">Enviar</button>
</div>
<script>
const menuBtn=document.getElementById('menu-btn'), sideMenu=document.getElementById('side-menu'), overlay=document.getElementById('overlay'), dotsBtn=document.getElementById('dots-btn'), dotsMenu=document.getElementById('dots-menu'), chatContainer=document.getElementById('chat-container'), userInput=document.getElementById('user-input'), sendBtn=document.getElementById('send-btn'), fileInput=document.getElementById('file-input');
let historial=JSON.parse(localStorage.getItem("memoria_ia")||"[]"); let imagenBase64=null;
function pintarChat(){ chatContainer.innerHTML=""; if(!historial.length){ chatContainer.innerHTML='<div class="msg bot">¡Hola! Soy IA Maestra 📷 Ya leo imágenes rápido.</div>'; } else { historial.forEach(m=>{ const d=document.createElement("div"); d.className="msg "+(m.role==="user"?"user":"bot"); d.textContent=m.content; chatContainer.appendChild(d); }); } chatContainer.scrollTop=chatContainer.scrollHeight; } pintarChat();
// COMPRESOR RÁPIDO
fileInput.onchange=(e)=>{ const file=e.target.files[0]; if(!file) return; const img=new Image(); img.onload=()=>{ const canvas=document.createElement('canvas'); const MAX=800; let w=img.width,h=img.height; if(w>h){ if(w>MAX){h*=MAX/w; w=MAX;}} else { if(h>MAX){w*=MAX/h; h=MAX;}} canvas.width=w; canvas.height=h; canvas.getContext('2d').drawImage(img,0,0,w,h); imagenBase64=canvas.toDataURL('image/jpeg',0.7); document.getElementById('preview-img').src=imagenBase64; document.getElementById('preview').style.display='flex'; }; img.src=URL.createObjectURL(file); };
function quitarImagen(){ imagenBase64=null; document.getElementById('preview').style.display='none'; fileInput.value=''; }
menuBtn.onclick=()=>{ sideMenu.classList.add('open'); overlay.classList.add('show'); }
function closeMenu(){ sideMenu.classList.remove('open'); overlay.classList.remove('show'); }
function clearChat(){ if(confirm("¿Borrar memoria?")){ historial=[]; localStorage.removeItem("memoria_ia"); pintarChat(); } }
dotsBtn.onclick=(e)=>{ e.stopPropagation(); dotsMenu.classList.toggle('open'); }
function closeDots(){ dotsMenu.classList.remove('open'); } document.addEventListener('click',()=>closeDots());
function copyLast(){ const b=historial.filter(m=>m.role==='assistant'); if(b.length){ navigator.clipboard.writeText(b.slice(-1)[0].content); alert('Copiado'); } }
function deleteLast(){ if(historial.length){ historial.pop(); historial.pop(); localStorage.setItem("memoria_ia",JSON.stringify(historial)); pintarChat(); } }
function shareLast(){ const b=historial.filter(m=>m.role==='assistant'); if(b.length){ const t=b.slice(-1)[0].content; if(navigator.share) navigator.share({title:'IA Maestra',text:t}); else {navigator.clipboard.writeText(t); alert('Copiado');} } }
function showMaterias(){ closeMenu(); const d=document.createElement("div"); d.className="msg bot"; d.innerHTML=`<b>Elige:</b><br><button class="materia-btn" onclick="askMateria('Matemáticas')">Matemáticas</button><button class="materia-btn" onclick="askMateria('Español')">Español</button><button class="materia-btn" onclick="askMateria('Ciencias')">Ciencias</button>`; chatContainer.appendChild(d); }
function askMateria(m){ userInput.value=`Quiero aprender ${m}`; sendMessage(); }
function showAcerca(){ closeMenu(); const d=document.createElement("div"); d.className="msg bot"; d.innerHTML=`<b>IA Maestra v2.1 Rápida</b><br>Creado por <b>J Carlos Double R</b><br>Coyuca, Gro. 2026<br>Visión rápida + tiempo real`; chatContainer.appendChild(d); chatContainer.scrollTop=chatContainer.scrollHeight; }
async function sendMessage(){
  const text=userInput.value.trim(); if(!text &&!imagenBase64) return;
  let html=text; if(imagenBase64) html+=`<br><img src="${imagenBase64}">`;
  const du=document.createElement("div"); du.className="msg user"; du.innerHTML=html||"📷"; chatContainer.appendChild(du);
  const msgB=text||"Explica que ves en esta imagen, breve para secundaria."; const imgB=imagenBase64;
  userInput.value=''; quitarImagen(); chatContainer.scrollTop=chatContainer.scrollHeight;
  const typing=document.createElement('div'); typing.className='msg bot'; typing.textContent='Analizando...'; chatContainer.appendChild(typing);
  try{
    const res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msgB,history:historial.slice(-6),image:imgB})});
    const data=await res.json(); typing.textContent=data.reply;
    historial.push({role:"user",content:msgB+(imgB?" [img]":"")}); historial.push({role:"assistant",content:data.reply});
    if(historial.length>20) historial=historial.slice(-20); localStorage.setItem("memoria_ia",JSON.stringify(historial));
  }catch{ typing.textContent='Error conexión'; } chatContainer.scrollTop=chatContainer.scrollHeight;
}
sendBtn.onclick=sendMessage; userInput.addEventListener('keypress',e=>{ if(e.key==='Enter') sendMessage(); });
</script>
</body>
</html>