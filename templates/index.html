<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>IA de J Carlos - WhatsApp</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{height:100vh;display:flex;flex-direction:column;font-family:'Segoe UI',Helvetica,Arial,sans-serif;background:#111b21}
#header{height:59px;background:#202c33;display:flex;align-items:center;padding:0 16px;gap:12px;color:#fff;z-index:10}
#header img{width:40px;height:40px;border-radius:50%;background:#00a884;display:flex;align-items:center;justify-content:center}
#header b{font-size:16px} #header span{font-size:13px;color:#8696a0;display:block}
#chat{flex:1;background:#0b141a;background-image:url("https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png");background-blend-mode:overlay;background-color:#e5ddd5;overflow-y:auto;padding:12px 8px 20px 8px;display:flex;flex-direction:column;gap:2px}
.msg{max-width:78%;padding:6px 7px 20px 9px;border-radius:7.5px;font-size:14.2px;line-height:19.2px;position:relative;box-shadow:0 1px 0.5px rgba(0,0,0,0.13);word-wrap:break-word;white-space:pre-wrap}
.user{background:#d9fdd3;align-self:flex-end;border-top-right-radius:0;margin-left:auto;color:#111b21}
.bot{background:#fff;align-self:flex-start;border-top-left-radius:0;margin-right:auto;color:#111b21}
.time{position:absolute;bottom:3px;right:6px;font-size:11px;color:#667781;display:flex;gap:3px;align-items:center}
.user .time{color:#53bdeb}
#inputArea{height:62px;background:#202c33;display:flex;align-items:center;padding:5px 10px;gap:8px}
#inputArea input{flex:1;height:42px;border-radius:21px;border:none;padding:0 18px;font-size:15px;outline:none;background:#2a3942;color:#fff}
#inputArea input::placeholder{color:#8696a0}
#send{width:45px;height:45px;background:#00a884;border:none;border-radius:50%;color:#fff;font-size:20px;display:flex;align-items:center;justify-content:center;cursor:pointer}
#send:active{transform:scale(0.92)}
</style>
</head>
<body>
<div id="header">
<div style="width:40px;height:40px;border-radius:50%;background:#00a884;display:flex;align-items:center;justify-content:center;font-size:22px">🤖</div>
<div><b>IA de J Carlos</b><span>en línea</span></div>
</div>

<div id="chat">
<div class="msg bot">Hola J Carlos 👋 Soy tu IA. ¿En qué te ayudo hoy?<span class="time">10:24 ✓✓</span></div>
</div>

<div id="inputArea">
<input id="text" placeholder="Escribe un mensaje" autocomplete="off">
<button id="send">➤</button>
</div>

<script>
const chat=document.getElementById('chat'),input=document.getElementById('text'),btn=document.getElementById('send');
function addMsg(t,type){
let d=document.createElement('div');d.className='msg '+type;
let hora=new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
d.innerHTML=t+'<span class="time">'+hora+(type=='user'?' ✓✓':'')+'</span>';
chat.appendChild(d);chat.scrollTop=chat.scrollHeight;
}
async function send(){
let q=input.value.trim();if(!q)return;addMsg(q,'user');input.value='';
try{
let r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:q})});
let data=await r.json();addMsg(data.reply||data.message||'Error en IA','bot');
}catch{
// MODO DEMO si no hay backend - responde local
setTimeout(()=>{addMsg('Recibí: "'+q+'" - Aquí va la respuesta de tu IA real cuando conectes el backend.','bot')},600);
}
}
btn.onclick=send;input.addEventListener('keydown',e=>{if(e.key==='Enter')send()});
</script>
</body>
</html>
