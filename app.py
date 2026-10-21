from flask import Flask, request, jsonify
import os, json, psycopg2

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    if not DATABASE_URL: return None
    return psycopg2.connect(DATABASE_URL)

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RED NEURONAL</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
body{margin:0;background:#070710;color:#7df9ff;font-family:'Press Start 2P',monospace;overflow-x:hidden}
h1{font-size:18px;text-align:center;color:#7df9ff;text-shadow:0 0 10px #7df9ff;letter-spacing:2px;margin-top:20px}
.sub{font-size:10px;text-align:center;color:#888;margin-bottom:15px}
#canvasWrap{width:100%;display:flex;justify-content:center;background:#05050f;border-top:2px solid #1a1a3a;border-bottom:2px solid #1a1a3a}
canvas{image-rendering:pixelated;max-width:95vw}
.controls{max-width:700px;margin:15px auto;padding:10px;display:grid;grid-template-columns:1fr 1fr;gap:10px}
.card{border:2px solid #1e2a5a;background:#0a0e22;padding:12px}
.card h2{font-size:8px;color:#fff;margin:0 0 10px 0}
input{width:100%;background:#000;border:1px solid #7df9ff;color:#7df9ff;padding:6px;font-family:monospace;box-sizing:border-box;font-size:11px}
button{width:100%;background:#000;border:2px solid #7df9ff;color:#7df9ff;padding:10px;font-family:'Press Start 2P';font-size:8px;cursor:pointer;margin-top:8px}
button:hover{background:#7df9ff;color:#000;box-shadow:0 0 15px #7df9ff}
button.danger{border-color:#ff3b7f;color:#ff3b7f} button.danger:hover{background:#ff3b7f;color:#fff}
.result{font-size:9px;line-height:14px;color:#fff;background:#000;padding:8px;margin-top:8px;border-left:2px solid #7df9ff}
.sliders{display:flex;flex-direction:column;gap:6px}
</style>
</head>
<body>
<h1>RED NEURONAL</h1>
<div class="sub">CAPA -> CAPA -> CAPA</div>

<div id="canvasWrap"><canvas id="c" width="500" height="500"></canvas></div>

<div class="controls">
<div class="card">
<h2>01. CREAR RED</h2>
Capas: <input id="capas" value="3" type="number" min="2" max="4">
Neuronas por capa: <input id="neuronas" value="9">
<button onclick="crearRed()">CREAR / ALEATORIZAR</button>
<button onclick="guardarRed()" style="border-color:#5aff8a;color:#5aff8a">GUARDAR CEREBRO</button>
</div>

<div class="card">
<h2>02. PROBAR RED</h2>
<div class="sliders" id="sliders"></div>
<button onclick="probar()">PROBAR AHORA</button>
<div id="out" class="result">Salida: esperando...</div>
</div>

<div class="card">
<h2>03. CEREBRO GUARDADO</h2>
<pre id="json" style="font-size:7px;white-space:pre-wrap;color:#666;height:100px;overflow:auto"></pre>
<button class="danger" onclick="borrarTodo()">BORRAR TODO</button>
</div>

<div class="card">
<h2>04. COMO FUNCIONA</h2>
<div style="font-size:7px;line-height:12px;color:#888">
SUMA = Σ(peso*entrada)<br>
+ SESGO<br>
+ SIGMOID<br>
Marrón = peso +<br>
Morado = peso -
</div>
</div>
</div>

<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
let red = JSON.parse(localStorage.getItem('red_pixel_v2')) || null;
let entradas = [0.3,0.6,0.8,0.5,0.9];

function sigmoid(x){return 1/(1+Math.exp(-x))}

function crearRed(){
  let numCapas = parseInt(document.getElementById('capas').value);
  let nPerCapa = parseInt(document.getElementById('neuronas').value);
  let capas = [];
  // capa entrada = 5 como en tu foto
  capas.push({n:5, pesos:[]});
  for(let c=0;c<numCapas;c++){
    let prevN = c==0 ? 5 : capas[c].n;
    let pesos = [];
    for(let i=0;i<nPerCapa;i++){
      let w = [];
      for(let j=0;j<prevN;j++) w.push((Math.random()*2-1)*1.5);
      pesos.push({w, b:(Math.random()*2-1), val:0});
    }
    capas.push({n:nPerCapa, pesos});
  }
  red = {capas};
  localStorage.setItem('red_pixel_v2', JSON.stringify(red));
  crearSliders();
  dibujar();
  guardarEnServer();
}

function crearSliders(){
  let cont = document.getElementById('sliders');
  cont.innerHTML='';
  entradas.forEach((v,i)=>{
    cont.innerHTML+=`<div style="font-size:7px">ENTRADA ${i+1}: <input type="range" min="0" max="1" step="0.01" value="${v}" oninput="entradas[${i}]=parseFloat(this.value); probar()"></div>`;
  });
}

function forward(){
  if(!red) return [];
  let activacion = [...entradas];
  for(let c=1;c<red.capas.length;c++){
    let next = [];
    for(let neu of red.capas[c].pesos){
      let suma=neu.b;
      for(let k=0;k<activacion.length;k++) suma+= activacion[k]*neu.w[k];
      neu.val = sigmoid(suma);
      next.push(neu.val);
    }
    activacion = next;
  }
  return activacion;
}

function dibujar(){
  ctx.fillStyle='#070710'; ctx.fillRect(0,0,500,500);
  if(!red) return;
  let capasX = [];
  let totalCapas = red.capas.length;
  for(let i=0;i<totalCapas;i++) capasX.push(60 + i*(380/(totalCapas-1)));

  // dibujar conexiones primero
  for(let c=1;c<red.capas.length;c++){
    let prevX = capasX[c-1], curX = capasX[c];
    let prevN = red.capas[c-1].n, curN = red.capas[c].n;
    for(let i=0;i<curN;i++){
      for(let j=0;j<prevN;j++){
        let peso = red.capas[c].pesos[i] ? red.capas[c].pesos[i].w[j] : 0;
        ctx.strokeStyle = peso>0 ? `rgba(180,110,40,${Math.min(1,Math.abs(peso))})` : `rgba(140,80,255,${Math.min(1,Math.abs(peso))})`;
        ctx.lineWidth = 1;
        let y1 = 50 + j*(400/prevN) + 400/prevN/2;
        let y2 = 50 + i*(400/curN) + 400/curN/2;
        ctx.beginPath(); ctx.moveTo(prevX, y1); ctx.lineTo(curX, y2); ctx.stroke();
      }
    }
  }
  // dibujar neuronas
  for(let c=0;c<red.capas.length;c++){
    let x = capasX[c];
    let n = red.capas[c].n;
    for(let i=0;i<n;i++){
      let y = 50 + i*(400/n) + 400/n/2;
      let val = 0;
      if(c==0) val = entradas[i] || 0;
      else val = red.capas[c].pesos[i]?.val || 0;
      
      // circulo pixelado
      ctx.fillStyle = c==0 ? `rgba(40,50,120,${0.5+val*0.5})` : `rgba(10,${30+val*100},${60+val*150},1)`;
      ctx.beginPath(); ctx.arc(x,y, c==0?18:12,0,Math.PI*2); ctx.fill();
      ctx.strokeStyle = c==0 ? '#3340aa' : '#7df9ff';
      ctx.lineWidth = 2; ctx.stroke();
      // brillo segun activacion
      if(val>0.5){
        ctx.fillStyle = `rgba(125,249,255,${val*0.4})`;
        ctx.beginPath(); ctx.arc(x,y, c==0?22:16,0,Math.PI*2); ctx.fill();
      }
    }
  }
  document.getElementById('json').innerText = JSON.stringify(red,null,1).slice(0,800);
}

function probar(){
  let salida = forward();
  document.getElementById('out').innerHTML = `ENTRADA: [${entradas.map(v=>v.toFixed(2)).join(',')}]<br>SALIDA: [${salida.map(v=>v.toFixed(3)).join(', ')}]<br>MAX: ${(Math.max(...salida)*100).toFixed(1)}%`;
  dibujar();
}

async function guardarEnServer(){
  try{ await fetch('/api/cerebro',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(red)});}catch(e){}
}

async function guardarRed(){
  localStorage.setItem('red_pixel_v2', JSON.stringify(red));
  await guardarEnServer();
  alert('Red guardada! Ya no se borra.');
}

async function borrarTodo(){
  if(!confirm('Borrar toda la red?')) return;
  red=null; localStorage.removeItem('red_pixel_v2');
  try{ await fetch('/api/cerebro/borrar',{method:'POST'});}catch(e){}
  ctx.clearRect(0,0,500,500); crearSliders();
}

if(red){ crearSliders(); forward(); }
else{ crearRed(); }
dibujar();
setInterval(dibujar, 200);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return HTML

@app.route("/api/cerebro", methods=["POST"])
def save():
    try:
        data = request.get_json()
        if DATABASE_URL:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS cerebro (user_id TEXT PRIMARY KEY, data JSONB)")
            cur.execute("INSERT INTO cerebro VALUES ('julio', %s) ON CONFLICT (user_id) DO UPDATE SET data=%s", (json.dumps(data), json.dumps(data)))
            conn.commit(); cur.close(); conn.close()
    except Exception as e: print(e)
    return jsonify(ok=True)

@app.route("/api/cerebro/borrar", methods=["POST"])
def borrar():
    try:
        if DATABASE_URL:
            conn=get_conn(); cur=conn.cursor()
            cur.execute("UPDATE cerebro SET data='{\"capas\":[]}' WHERE user_id='julio'")
            conn.commit(); cur.close(); conn.close()
    except: pass
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
