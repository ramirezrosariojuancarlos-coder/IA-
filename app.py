from flask import Flask, request, jsonify
import psycopg2, json, os

app = Flask(__name__)

# PEGA AQUI TU URL DE POSTGRES DE RENDER/SUPABASE
DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql://user:pass@host/db"

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cerebro (
              user_id TEXT PRIMARY KEY,
              data JSONB NOT NULL
            );
        """)
        cur.execute("""
            INSERT INTO cerebro (user_id, data)
            VALUES ('julio', '{"neuronas":[]}'::jsonb)
            ON CONFLICT (user_id) DO NOTHING;
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("DB lista!")
    except Exception as e:
        print(f"DB aún no conectada: {e}")

init_db()

HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>NEURONA LAB</title>
<style>
body{background:#02020a;color:#00f5ff;font-family:monospace;padding:20px}
.card{border:1px solid #00f5ff55;padding:15px;border-radius:10px;margin-bottom:15px;background:#0a0f1e}
input{width:100%;padding:8px;background:#000;border:1px solid #00f5ff;color:#00f5ff;margin-top:5px}
button{padding:10px 15px;border:1px solid #00f5ff;background:transparent;color:#00f5ff;cursor:pointer;margin-top:10px}
button:hover{background:#00f5ff;color:#000}
</style></head><body>
<h1>NEURONA // LAB - PERSISTENTE</h1>
<div class="card">
<input id="nombre" value="Neurona A"><input id="pesos" value="0.3,0.6,0.8,0.5"><input id="sesgo" value="0.5" type="number">
<button onclick="guardar()">Guardar Neurona</button>
</div>
<div class="card">
<input id="entradas" value="0.3,0.6,0.8,0.5"><button onclick="probar()">Probar</button>
<div id="res"></div>
</div>
<div class="card"><h3>Tu Cerebro:</h3><pre id="cerebro"></pre><button onclick="borrar()">Borrar todo</button></div>
<script>
let cerebro={"neuronas":[]};
async function cargar(){
  try{let r=await fetch('/api/cerebro'); cerebro=await r.json();}catch(e){
    let b=localStorage.getItem('backup_cerebro'); if(b) cerebro=JSON.parse(b);
  }
  document.getElementById('cerebro').innerText=JSON.stringify(cerebro,null,2);
}
async function guardar(){
  let n={nombre:document.getElementById('nombre').value,pesos:document.getElementById('pesos').value.split(',').map(Number),sesgo:parseFloat(document.getElementById('sesgo').value),id:Date.now()};
  cerebro.neuronas.push(n);
  localStorage.setItem('backup_cerebro',JSON.stringify(cerebro));
  await fetch('/api/cerebro',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cerebro)});
  cargar();
}
async function borrar(){
  cerebro={"neuronas":[]}; localStorage.setItem('backup_cerebro',JSON.stringify(cerebro));
  await fetch('/api/cerebro/borrar',{method:'POST'}); cargar();
}
function probar(){
  let pesos=document.getElementById('pesos').value.split(',').map(Number);
  let ent=document.getElementById('entradas').value.split(',').map(Number);
  let sesgo=parseFloat(document.getElementById('sesgo').value);
  let suma=0; for(let i=0;i<pesos.length;i++) suma+=pesos[i]*ent[i];
  let total=suma+sesgo; let sig=1/(1+Math.exp(-total));
  document.getElementById('res').innerHTML=`SUMA=${suma.toFixed(3)} + SESGO ${sesgo} = ${total.toFixed(3)} -> sigmoid=${sig.toFixed(3)}`;
}
cargar();
</script></body></html>
"""

@app.route("/")
def index():
    return HTML

@app.route("/api/cerebro")
def api_get():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT data FROM cerebro WHERE user_id='julio'")
        row = cur.fetchone()
        cur.close(); conn.close()
        return jsonify(row[0] if row else {"neuronas":[]})
    except:
        return jsonify({"neuronas":[]})

@app.route("/api/cerebro", methods=["POST"])
def api_save():
    try:
        data = request.get_json()
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE cerebro SET data=%s WHERE user_id='julio'", (json.dumps(data),))
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        print(e)
    return jsonify({"ok":True})

@app.route("/api/cerebro/borrar", methods=["POST"])
def api_borrar():
    return api_save().__wrapped__ if False else api_save.__call__() if False else api_save() or jsonify({"ok":True})

# truco para borrar
@app.route("/api/cerebro/borrar", methods=["POST"])
def borrar_api():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE cerebro SET data='{\"neuronas\":[]}' WHERE user_id='julio'")
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"ok":True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
