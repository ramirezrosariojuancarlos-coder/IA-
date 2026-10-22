from flask import Flask
import os
app = Flask(__name__)

HTML = """
<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CEREBRO REAL V6 - FINAL</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
body{margin:0;background:#070710;color:#7df9ff;font-family:'Press Start 2P';}
h1{font-size:10px;text-align:center;padding:10px} .sub{font-size:5px;text-align:center;color:#666;margin-bottom:6px}
canvas{image-rendering:pixelated;width:100%} #wrap{display:flex;justify-content:center;background:#05050f;border:2px solid #222}
.controls{max-width:1150px;margin:0 auto;padding:8px;display:grid;grid-template-columns:1fr 1fr;gap:8px}
@media(max-width:800px){.controls{grid-template-columns:1fr}} .card{border:2px solid #1e2a5a;background:#0a0e22;padding:8px}
.card h2{font-size:7px;color:#fff;margin:0 0 6px} input,textarea{width:100%;background:#000;border:1px solid #7df9ff;color:#7df9ff;padding:5px;font-family:monospace;font-size:9px;box-sizing:border-box;margin-top:4px}
button{width:100%;background:#000;border:2px solid #7df9ff;color:#7df9ff;padding:8px;font-family:'Press Start 2P';font-size:5px;cursor:pointer;margin-top:5px}
button:hover{background:#7df9ff;color:#000} button.o{border-color:#ffaa00;color:#ffaa00} button.g{border-color:#5aff8a;color:#5aff8a} button.r{border-color:#ff4444;color:#ff4444}
.result{font-size:6px;color:#fff;background:#000;padding:5px;margin-top:5px;white-space:pre-wrap;border-left:2px solid #7df9ff}
.neurona-edit{border:1px dashed #333;padding:4px;margin-top:4px;background:#000}
.neurona-edit b{font-size:5px;color:#ffaa00}
</style></head><body>
<h1>MI CEREBRO REAL V6 - TU CONTROL TOTAL</h1><div class="sub">ERROR = APRENDIZAJE | SESGO = PERSONALIDAD | PESO = MEMORIA | COLUMNA = CAPA</div>
<div id="wrap"><canvas id="c" width="700" height="420"></canvas></div>
<div class="controls">
<div class="card"><h2>01. ARQUITECTURA QUE CRECE Y SE PUEDE PODAR</h2>
Capas <input id="capas" value="3" type="number"> Neur x capa <input id="neur" value="7" type="number">
<button onclick="crear(true)">CREAR DESDE CERO</button>
<button class="g" onclick="crear(false)">AGREGAR CAPA CONSERVANDO</button>
<button class="r" onclick="borrarColumna(1)">BORRAR COLUMNA 1</button>
<button class="r" onclick="borrarColumna(2)">BORRAR COLUMNA 2</button>
<button class="r" onclick="borrarColumna(3)">BORRAR COLUMNA 3</button>
<button class="r" onclick="borrarColumna(4)">BORRAR COLUMNA 4</button>
<div id="info" class="result">Cerebro: sin crear</div></div>

<div class="card"><h2>02. ENTRENAR - ERROR REAL</h2>
<textarea id="train" rows="5">0,0,0,0,0 -> 0,0,1
1,0,0,0,0 -> 1,0,0
0,0,0,0,1 -> 0,1,0
1,1,0,0,0 -> 1,1,0</textarea>
LR <input id="lr" value="0.1" step="0.02"> EP <input id="ep" value="400">
<button class="o" onclick="entrenar()">ENTRENAR AHORA</button>
<div id="log" class="result">Log: Error ideal 0.02-0.08. Si llega a 0.0001 esta memorizando.</div>
<canvas id="chart" width="320" height="80" style="background:#000;border:1px solid #333;margin-top:4px"></canvas>
</div>

<div class="card"><h2>03. PROBAR + DESCARGAR</h2><div id="sliders"></div><button onclick="probar()">PROBAR</button><div id="out" class="result"></div>
<button class="g" onclick="descargar()">DESCARGAR mi_cerebro_real.json</button>
<button onclick="podar()">PODAR PESOS DEBILES (&lt;0.15)</button>
</div>

<div class="card"><h2>04. EDITAR SESGO Y PESOS A MANO</h2>
<div style="font-size:5px;color:#888">Sesgo = que tan facil se enoja. Peso = que tanto recuerda.</div>
<div id="listaNeuronas"></div>
</div></div>

<script>
const ctx=document.getElementById('c').getContext('2d'), chart=document.getElementById('chart').getContext('2d');
let cerebro=JSON.parse(localStorage.getItem('cerebro_v6'))||{capas:[{n:5,pesos:[]}]}; 
let entradas=[0.84,0.55,0.54,0.75,0.59];
let historialError=[];
function save(){localStorage.setItem('cerebro_v6',JSON.stringify(cerebro)); render();}
function sig(x){if(x>15)return 1; if(x<-15)return 0; return 1/(1+Math.exp(-x))} function dsig(y){return y*(1-y)}
function crear(desdeCero){
  let nC=parseInt(document.getElementById('capas').value), nN=parseInt(document.getElementById('neur').value);
  if(desdeCero){ let capas=[{n:5,pesos:[]}]; for(let c=0;c<nC;c++){ let prev=c==0?5:nN, pesos=[]; for(let i=0;i<nN;i++){ let w=[]; for(let j=0;j<prev;j++) w.push((Math.random()*2-1)*0.6); pesos.push({w,b:(Math.random()*2-1)*0.5,val:0}) } capas.push({n:nN,pesos}) } cerebro={capas}; }
  else{ let prevN=cerebro.capas[cerebro.capas.length-1].n, pesos=[]; for(let i=0;i<nN;i++){ let w=[]; for(let j=0;j<prevN;j++) w.push((Math.random()*2-1)*0.3); pesos.push({w,b:0,val:0}) } cerebro.capas.push({n:nN,pesos}); }
  save(); crearSliders(); probar();
}
function borrarColumna(num){
  if(cerebro.capas.length <= 2){ alert("No puedes borrar, quedaria vacio"); return; }
  if(num >= cerebro.capas.length){ alert("Esa columna no existe"); return; }
  if(!confirm("¿BORRAR COLUMNA "+num+" entera?")) return;
  cerebro.capas.splice(num,1);
  for(let c=num;c<cerebro.capas.length;c++){
    let prevN=cerebro.capas[c-1].n;
    for(let neu of cerebro.capas[c].pesos){
      if(neu.w.length > prevN) neu.w = neu.w.slice(0, prevN);
      if(neu.w.length < prevN) while(neu.w.length < prevN) neu.w.push((Math.random()*2-1)*0.2);
    }
  }
  save(); probar();
}
function crearSliders(){ let c=document.getElementById('sliders'); c.innerHTML=''; for(let i=0;i<5;i++) c.innerHTML+=`ENT ${i+1}: <input type="range" min="0" max="1" step="0.01" value="${entradas[i]}" oninput="entradas[${i}]=parseFloat(this.value); probar()">`; }
function forward(inp){ let act=[...inp]; for(let c=1;c<cerebro.capas.length;c++){ let next=[]; for(let neu of cerebro.capas[c].pesos){ let s=neu.b; for(let k=0;k<act.length;k++) s+=act[k]*(neu.w[k]||0); neu.val=sig(s); next.push(neu.val) } act=next } return act }
function entrenar(){
  let lineas=document.getElementById('train').value.trim().split('\\n'), datos=[];
  for(let l of lineas){ if(!l.includes('->'))continue; let [a,b]=l.split('->'); datos.push({i:a.split(',').map(Number), o:b.split(',').map(Number)}) }
  let lr=parseFloat(document.getElementById('lr').value), ep=parseInt(document.getElementById('ep').value);
  historialError=[]; let log=document.getElementById('log');
  for(let e=0;e<ep;e++){ let errT=0; for(let d of datos){ let acts=[d.i]; let act=[...d.i]; for(let c=1;c<cerebro.capas.length;c++){ let nxt=[]; for(let neu of cerebro.capas[c].pesos){ let s=neu.b; for(let k=0;k<act.length;k++) s+=act[k]*neu.w[k]; neu.val=sig(s); nxt.push(neu.val) } acts.push([...nxt]); act=nxt } let deltas={}; let last=cerebro.capas.length-1; let dOut=[]; for(let i=0;i<cerebro.capas[last].pesos.length;i++){ let tgt=d.o[i]||0, out=acts[last][i]||0, err=tgt-out; errT+=err*err; dOut.push(err*dsig(out)) } deltas[last]=dOut; for(let c=last-1;c>=1;c--){ let cur=[]; for(let i=0;i<cerebro.capas[c].pesos.length;i++){ let err=0; for(let j=0;j<cerebro.capas[c+1].pesos.length;j++) err+=deltas[c+1][j]*cerebro.capas[c+1].pesos[j].w[i]; cur.push(err*dsig(acts[c][i])) } deltas[c]=cur } for(let c=1;c<cerebro.capas.length;c++) for(let i=0;i<cerebro.capas[c].pesos.length;i++){ for(let k=0;k<cerebro.capas[c].pesos[i].w.length;k++){ let ch=lr*deltas[c][i]*acts[c-1][k]; if(ch>0.5)ch=0.5; if(ch<-0.5)ch=-0.5; cerebro.capas[c].pesos[i].w[k]+=ch; if(cerebro.capas[c].pesos[i].w[k]>5)cerebro.capas[c].pesos[i].w[k]=5; if(cerebro.capas[c].pesos[i].w[k]<-5)cerebro.capas[c].pesos[i].w[k]=-5; } let chB=lr*deltas[c][i]; if(chB>0.5)chB=0.5; if(chB<-0.5)chB=-0.5; cerebro.capas[c].pesos[i].b+=chB; } } historialError.push(errT); if(e%50==0) log.innerText=`Epoca ${e}/${ep} Error: ${errT.toFixed(4)}`; } 
  log.innerText=`FINAL Error ${historialError[historialError.length-1].toFixed(5)} Ideal 0.02-0.08. Si <0.001 esta memorizando.`;
  save(); dibujarChart(); probar();
}
function dibujarChart(){ chart.fillStyle='#000'; chart.fillRect(0,0,320,80); chart.strokeStyle='#ffaa00'; chart.beginPath(); let max=Math.max(...historialError,1); for(let i=0;i<historialError.length;i++){ let x=i/historialError.length*320, y=80-(historialError[i]/max*70)-5; if(i==0)chart.moveTo(x,y); else chart.lineTo(x,y) } chart.stroke(); }
function probar(){ if(!cerebro.capas||cerebro.capas.length<2)return; let sal=forward(entradas); document.getElementById('out').innerText=`ENT: [${entradas.map(v=>v.toFixed(2))}]\\nSAL: [${sal.map(v=>v.toFixed(3)).join(', ')}]\\nMAX ${(Math.max(...sal)*100).toFixed(1)}%`; renderLista(); dibujar(); }
function renderLista(){
  let cont=document.getElementById('listaNeuronas'); cont.innerHTML='';
  for(let c=1;c<cerebro.capas.length;c++){
    cont.innerHTML+=`<div style="color:#fff;font-size:6px;margin-top:6px">CAPA ${c} - ${cerebro.capas[c].n} neuronas</div>`;
    cerebro.capas[c].pesos.forEach((neu,idx)=>{
      cont.innerHTML+=`<div class="neurona-edit"><b>N ${c}-${idx} Sesgo:</b><input value="${neu.b.toFixed(3)}" onchange="cambiarSesgo(${c},${idx},this.value)" type="number" step="0.1"><b>Pesos:</b><input value="${neu.w.map(v=>v.toFixed(2)).join(',')}" onchange="cambiarPesos(${c},${idx},this.value)"><div style="font-size:5px">Val: ${neu.val.toFixed(3)}</div></div>`;
    });
  }
  document.getElementById('info').innerText=`Capas: ${cerebro.capas.length-1} | Neuronas: ${cerebro.capas.slice(1).reduce((a,b)=>a+b.n,0)} | Editable: SI`;
}
function cambiarSesgo(c,i,v){ cerebro.capas[c].pesos[i].b=parseFloat(v); save(); probar(); }
function cambiarPesos(c,i,v){ cerebro.capas[c].pesos[i].w=v.split(',').map(Number); save(); probar(); }
function podar(){ let umbral=0.15, c=0; for(let cc=1;cc<cerebro.capas.length;cc++) for(let neu of cerebro.capas[cc].pesos) for(let k=0;k<neu.w.length;k++) if(Math.abs(neu.w[k])<umbral){ neu.w[k]=0; c++; } save(); alert("Podados "+c+" pesos debiles"); probar(); }
function descargar(){ let blob=new Blob([JSON.stringify(cerebro,null,2)],{type:'application/json'}); let a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='mi_cerebro_real.json'; a.click(); }
function dibujar(){ ctx.fillStyle='#070710'; ctx.fillRect(0,0,700,420); if(!cerebro.capas||cerebro.capas.length<1)return; let xs=[]; for(let i=0;i<cerebro.capas.length;i++) xs.push(40+i*(620/(cerebro.capas.length-1||1))); for(let c=1;c<cerebro.capas.length;c++){ let prevX=xs[c-1], curX=xs[c], prevN=cerebro.capas[c-1].n, curN=cerebro.capas[c].n; for(let i=0;i<curN;i++) for(let j=0;j<prevN;j++){ let peso=cerebro.capas[c].pesos[i]?.w[j]||0; if(Math.abs(peso)<0.12) continue; ctx.strokeStyle=peso>0?`rgba(255,170,0,${Math.min(1,Math.abs(peso))})`:`rgba(125,249,255,${Math.min(1,Math.abs(peso)*0.7)})`; let y1=20+j*(360/prevN)+10, y2=20+i*(360/curN)+10; ctx.beginPath(); ctx.moveTo(prevX,y1); ctx.lineTo(curX,y2); ctx.lineWidth=Math.abs(peso)*2.5; ctx.stroke(); } } for(let c=0;c<cerebro.capas.length;c++){ let x=xs[c], n=cerebro.capas[c].n; for(let i=0;i<n;i++){ let y=20+i*(360/n)+10, val=c==0?(entradas[i]||0):(cerebro.capas[c].pesos[i]?.val||0); ctx.fillStyle=c==0?`rgba(40,50,120,${0.5+val*0.5})`:`rgba(10,${30+val*100},${60+val*150},1)`; ctx.beginPath(); ctx.arc(x,y,c==0?13:8,0,Math.PI*2); ctx.fill(); ctx.strokeStyle=c==0?'#3340aa':'#7df9ff'; ctx.lineWidth=1; ctx.stroke(); } } }
crearSliders(); probar(); setInterval(dibujar,600);
</script></body></html>
"""
@app.route("/")
def index(): return HTML
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
