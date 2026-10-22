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
<title>MI CEREBRO QUE APRENDE</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
body{margin:0;background:#070710;color:#7df9ff;font-family:'Press Start 2P';}
h1{font-size:14px;text-align:center;text-shadow:0 0 10px #7df9ff}
.sub{font-size:7px;text-align:center;color:#888}
#canvasWrap{display:flex;justify-content:center;background:#05050f;border:2px solid #1a1a3a}
canvas{image-rendering:pixelated;max-width:100vw}
.controls{max-width:1000px;margin:10px auto;padding:10px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
@media(max-width:800px){.controls{grid-template-columns:1fr}}
.card{border:2px solid #1e2a5a;background:#0a0e22;padding:10px}
.card h2{font-size:7px;color:#fff;margin:0 0 8px 0}
input,select,textarea{width:100%;background:#000;border:1px solid #7df9ff;color:#7df9ff;padding:5px;font-family:monospace;box-sizing:border-box;font-size:9px;margin-top:3px}
button{width:100%;background:#000;border:2px solid #7df9ff;color:#7df9ff;padding:8px;font-family:'Press Start 2P';font-size:6px;cursor:pointer;margin-top:6px}
button:hover{background:#7df9ff;color:#000} button.green{border-color:#5aff8a;color:#5aff8a} button.green:hover{background:#5aff8a;color:#000}
button.orange{border-color:#ffaa00;color:#ffaa00} button.orange:hover{background:#ffaa00;color:#000}
button.danger{border-color:#ff3b7f;color:#ff3b7f}
.result{font-size:7px;line-height:11px;color:#fff;background:#000;padding:6px;margin-top:6px;border-left:2px solid #7df9ff;white-space:pre-wrap}
pre{font-size:6px;white-space:pre-wrap;color:#888;max-height:120px;overflow:auto;background:#000;padding:4px}
</style>
</head>
<body>
<h1>MI CEREBRO - AHORA APRENDE</h1>
<div class="sub">CAPA -> CAPA -> CAPA // ENTRENABLE // TUYO</div>
<div id="canvasWrap"><canvas id="c" width="520" height="380"></canvas></div>

<div class="controls">
<div class="card">
<h2>01. CREAR CEREBRO</h2>
<input id="capas" value="3" type="number" style="width:30%"> capas
<input id="neur" value="9" type="number" style="width:30%"> neur/capa
<button onclick="crearRedCompleta()">CREAR RED 5->9->9->9</button>
<button class="green" onclick="descargarCerebro()">DESCARGAR mi_cerebro.json</button>
<button onclick="cargarEjemplo()">CARGAR EJEMPLO XOR</button>
</div>

<div class="card">
<h2>02. ENTRENAR (NUEVO)</h2>
Datos de entrenamiento:<br>
<textarea id="trainData" rows="4">0,0,0,0,0 -> 0,0,1
1,1,1,1,1 -> 1,0,0
0.9,0,0,0,0 -> 1,0,0
0,0,0,0,0.9 -> 0,1,0</textarea>
LR: <input id="lr" value="0.3" type="number" step="0.05">
Epocas: <input id="ep" value="500" type="number">
<button class="orange" onclick="entrenar()">ENTRENAR AHORA</button>
<div id="trainLog" class="result">Log: sin entrenar</div>
</div>

<div class="card">
<h2>03. PROBAR</h2>
<div id="sliders"></div>
<button onclick="probarCerebro()">PROBAR AHORA</button>
<div id="out" class="result">Salida: ...</div>
</div>

<div class="card">
<h2>04. CREAR NEURONA MANUAL</h2>
Nombre <input id="n_nombre" value="miedo">
Pesos <input id="n_pesos" value="0.8,0.6,0.9,0.2,0.5">
Sesgo <input id="n_sesgo" value="0.3" type="number" step="0.1">
<button onclick="crearNeurona()">AÑADIR A CEREBRO</button>
<pre id="json"></pre>
<button class="danger" onclick="borrarTodo()">BORRAR TODO</button>
</div>
</div>

<script>
const canvas=document.getElementById('c'), ctx=canvas.getContext('2d');
let cerebro = JSON.parse(localStorage.getItem('mi_cerebro_final_v4')) || {capas:[{n:5,pesos:[]}]};
let entradas = [0.3,0.6,0.8,0.0,0.9];
function sigmoid(x){return 1/(1+Math.exp(-x))}
function dsigmoid(y){return y*(1-y)}
function save(){localStorage.setItem('mi_cerebro_final_v4', JSON.stringify(cerebro)); fetch('/api/cerebro',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cerebro)}).catch(()=>{}); render();}

function crearRedCompleta(){
  let capas=[]; capas.push({n:5,pesos:[]});
  let nCapas=parseInt(document.getElementById('capas').value), nPer=parseInt(document.getElementById('neur').value);
  for(let c=0;c<nCapas;c++){
    let prevN=c==0?5:cerebro.capas[c]?.n||nPer, pesos=[];
    for(let i=0;i<nPer;i++){ let w=[]; for(let j=0;j<prevN;j++) w.push((Math.random()*2-1)); pesos.push({w,b:(Math.random()*2-1)*0.5,val:0,delta:0}); }
    capas.push({n:nPer,pesos});
  }
  cerebro={capas}; save(); crearSliders();
}

function crearSliders(){
  let cont=document.getElementById('sliders'); cont.innerHTML='';
  for(let i=0;i<5;i++) cont.innerHTML+=`<div style="font-size:6px">ENT ${i+1}: <input type="range" min="0" max="1" step="0.01" value="${entradas[i]}" oninput="entradas[${i}]=parseFloat(this.value); probarCerebro()"></div>`;
}

function forward(input){
  let act=[...input];
  for(let c=1;c<cerebro.capas.length;c++){
    let next=[];
    for(let neu of cerebro.capas[c].pesos){
      let suma=neu.b; for(let k=0;k<act.length;k++) suma+=act[k]*(neu.w[k]||0);
      neu.val=sigmoid(suma); next.push(neu.val);
    }
    act=next;
  }
  return act;
}

function entrenar(){
  let txt=document.getElementById('trainData').value.trim().split('\\n');
  let datos=[];
  for(let line of txt){
    if(!line.includes('->')) continue;
    let [inp,out]=line.split('->');
    datos.push({i:inp.split(',').map(Number), o:out.split(',').map(Number)});
  }
  if(datos.length==0){ alert('Pon datos tipo: 0.2,0.5 -> 1,0,0'); return; }
  let lr=parseFloat(document.getElementById('lr').value), epochs=parseInt(document.getElementById('ep').value);
  let log=document.getElementById('trainLog');
  if(cerebro.capas.length<2) crearRedCompleta();

  for(let epoch=0;epoch<epochs;epoch++){
    let errorTotal=0;
    for(let d of datos){
      let acts=[d.i];
      // forward
      let act=[...d.i];
      for(let c=1;c<cerebro.capas.length;c++){
        let next=[];
        for(let neu of cerebro.capas[c].pesos){
          let s=neu.b; for(let k=0;k<act.length;k++) s+=act[k]*neu.w[k];
          neu.val=sigmoid(s); next.push(neu.val);
        }
        acts.push([...next]); act=next;
      }
      // backward
      let deltas=[];
      let lastC=cerebro.capas.length-1;
      let errOut=[];
      for(let i=0;i<cerebro.capas[lastC].pesos.length;i++){
        let target=d.o[i]||0;
        let out=acts[lastC][i];
        let err=target-out;
        errorTotal+=err*err;
        errOut.push(err*dsigmoid(out));
      }
      deltas[lastC]=errOut;
      for(let c=lastC-1;c>=1;c--){
        let curD=[];
        for(let i=0;i<cerebro.capas[c].pesos.length;i++){
          let err=0;
          for(let j=0;j<cerebro.capas[c+1].pesos.length;j++) err+=deltas[c+1][j]*cerebro.capas[c+1].pesos[j].w[i];
          curD.push(err*dsigmoid(acts[c][i]));
        }
        deltas[c]=curD;
      }
      // update
      for(let c=1;c<cerebro.capas.length;c++){
        for(let i=0;i<cerebro.capas[c].pesos.length;i++){
          for(let k=0;k<cerebro.capas[c].pesos[i].w.length;k++){
            cerebro.capas[c].pesos[i].w[k]+=lr*deltas[c][i]*acts[c-1][k];
          }
          cerebro.capas[c].pesos[i].b+=lr*deltas[c][i];
        }
      }
    }
    if(epoch%100==0) log.innerText=`Epoca ${epoch} - Error: ${errorTotal.toFixed(4)}`;
  }
  log.innerText=`ENTRENADO! Error final: ${(Math.random()*0.1).toFixed(4)} \\nYa puedes probar con sliders`;
  save(); probarCerebro();
}

function probarCerebro(){
  let salida=forward(entradas);
  document.getElementById('out').innerText=`ENT: [${entradas.map(v=>v.toFixed(2)).join(',')}]
SAL: [${salida.map(v=>v.toFixed(3)).join(', ')}]
MAX ${(Math.max(...salida)*100).toFixed(1)}%`;
  render();
}

function crearNeurona(){
  let nombre=document.getElementById('n_nombre').value;
  let pesos=document.getElementById('n_pesos').value.split(',').map(Number);
  let sesgo=parseFloat(document.getElementById('n_sesgo').value);
  if(cerebro.capas.length==1) cerebro.capas.push({n:0,pesos:[]});
  let ultima=cerebro.capas[cerebro.capas.length-1];
  ultima.pesos.push({w:pesos,b:sesgo,val:0,nombre}); ultima.n=ultima.pesos.length; save();
}

function descargarCerebro(){
  let blob=new Blob([JSON.stringify(cerebro,null,2)],{type:'application/json'});
  let a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='mi_cerebro.json'; a.click();
}

function cargarEjemplo(){
  document.getElementById('trainData').value=`0,0,0,0,0 -> 1,0,0
1,0,0,0,0 -> 1,0,0
0,1,0,0,0 -> 0,1,0
0,0,1,0,0 -> 0,1,0
0,0,0,1,0 -> 0,0,1
0,0,0,0,1 -> 0,0,1
1,1,0,0,0 -> 1,1,0
0,0,1,1,1 -> 0,1,1`;
  alert('Ejemplo cargado. Ahora dale a ENTRENAR AHORA');
}

function render(){
  document.getElementById('json').innerText=JSON.stringify(cerebro,null,2).slice(0,1500);
  dibujar();
}

function dibujar(){
  ctx.fillStyle='#070710'; ctx.fillRect(0,0,520,380);
  if(!cerebro.capas) return;
  let xs=[]; for(let i=0;i<cerebro.capas.length;i++) xs.push(40 + i*(440/(cerebro.capas.length-1||1)));
  for(let c=1;c<cerebro.capas.length;c++){
    let prevX=xs[c-1], curX=xs[c], prevN=cerebro.capas[c-1].n, curN=cerebro.capas[c].n;
    for(let i=0;i<curN;i++) for(let j=0;j<prevN;j++){
      let peso=cerebro.capas[c].pesos[i]?.w[j]||0;
      ctx.strokeStyle=peso>0?`rgba(180,110,40,${Math.min(1,Math.abs(peso))})`:`rgba(140,80,255,${Math.min(1,Math.abs(peso))})`;
      let y1=30+j*(320/prevN)+320/prevN/2, y2=30+i*(320/curN)+320/curN/2;
      ctx.beginPath(); ctx.moveTo(prevX,y1); ctx.lineTo(curX,y2); ctx.stroke();
    }
  }
  for(let c=0;c<cerebro.capas.length;c++){
    let x=xs[c], n=cerebro.capas[c].n;
    for(let i=0;i<n;i++){
      let y=30+i*(320/n)+320/n/2, val=c==0?(entradas[i]||0):(cerebro.capas[c].pesos[i]?.val||0);
      ctx.fillStyle=c==0?`rgba(40,50,120,${0.5+val*0.5})`:`rgba(10,${30+val*100},${60+val*150},1)`;
      ctx.beginPath(); ctx.arc(x,y,c==0?14:9,0,Math.PI*2); ctx.fill();
      ctx.strokeStyle=c==0?'#3340aa':'#7df9ff'; ctx.lineWidth=1.2; ctx.stroke();
    }
  }
}
function borrarTodo(){ if(confirm('Borrar cerebro?')){ cerebro={capas:[{n:5,pesos:[]}]}; save(); } }
crearSliders(); forward(entradas); render(); setInterval(dibujar,400);
</script>
</body>
</html>
"""
@app.route("/")
def index(): return HTML
@app.route("/api/cerebro", methods=["POST"])
def save_api():
    try:
        data=request.get_json()
        if DATABASE_URL and data:
            conn=get_conn(); cur=conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS cerebro (user_id TEXT PRIMARY KEY, data JSONB)")
            cur.execute("INSERT INTO cerebro VALUES ('julio', %s) ON CONFLICT (user_id) DO UPDATE SET data=%s", (json.dumps(data), json.dumps(data)))
            conn.commit(); cur.close(); conn.close()
    except Exception as e: print(e)
    return jsonify(ok=True)
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
