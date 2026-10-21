from flask import Flask, render_template, request, jsonify
import psycopg2
import json
import os

app = Flask(__name__)

# PEGA AQUI TU URL DE POSTGRES
DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql://usuario:password@localhost:5432/tu_db"

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def get_cerebro():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT data FROM cerebro WHERE user_id='julio' LIMIT 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return row[0]
    return {"neuronas": []}

def save_cerebro(data):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE cerebro SET data=%s, updated_at=NOW() WHERE user_id='julio'", (json.dumps(data),))
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def lab():
    return render_template("laboratorio.html")

@app.route("/api/cerebro", methods=["GET"])
def api_get():
    return jsonify(get_cerebro())

@app.route("/api/cerebro", methods=["POST"])
def api_save():
    data = request.get_json()
    save_cerebro(data)
    return jsonify({"ok": True, "data": data})

@app.route("/api/cerebro/borrar", methods=["POST"])
def api_borrar():
    save_cerebro({"neuronas": []})
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
