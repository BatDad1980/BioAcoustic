from flask import Flask, request, jsonify
from flask_cors import CORS
from encryption_logic import generate_bio_key, encrypt_data
import time
import sqlite3
import string

app = Flask(__name__)
CORS(app)

DB_FILE = "constellation.db"
HEX_CHARS = set(string.hexdigits)


def is_sha3_hex(value):
    return isinstance(value, str) and len(value) == 64 and all(ch in HEX_CHARS for ch in value)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS waiting_nodes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, node_id TEXT, region TEXT, node_hash TEXT, timestamp REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS fusions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  node_1 TEXT, region_1 TEXT, 
                  node_2 TEXT, region_2 TEXT, 
                  proof_preview TEXT, timestamp REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/v1/node/hash', methods=['POST'])
def receive_node_hash():
    data = request.json
    node_id = data.get('node_id')
    node_hash = data.get('node_hash')
    region = data.get('region', 'Unknown_Region')
    
    if not node_id or not node_hash:
        return jsonify({"error": "Missing node_id or node_hash"}), 400

    if not is_sha3_hex(node_hash):
        return jsonify({"error": "node_hash must be a 64-character hex digest"}), 400
        
    print(f"\n[+] [Region: {region}] Received Hash from {node_id}: {node_hash[:16]}...")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Check if there is already a node waiting from a DIFFERENT region
    c.execute("SELECT id, node_id, region, node_hash FROM waiting_nodes WHERE region != ? LIMIT 1", (region,))
    partner = c.fetchone()
    
    if partner:
        fusion_id, fusion_partner_id, partner_region, partner_hash = partner
        
        # Remove partner from waiting pool
        c.execute("DELETE FROM waiting_nodes WHERE id = ?", (fusion_id,))
        
        print(f"\n[*] CONSTELLATION PROTOCOL TRIGGERED!")
        print(f"[*] Synchronizing {node_id} ({region}) with {fusion_partner_id} ({partner_region})...")
        
        # 1. XOR Fusion
        master_key = generate_bio_key(node_hash, partner_hash)
        print("[*] Demo key material derived via prototype hash fusion.")
        
        # 2. Encrypt dummy data
        payload = encrypt_data("Constellation Protocol Sequence Complete", master_key)
        proof_preview = payload['ciphertext'][:16]
        print(f"[*] Secured payload proof preview: {proof_preview}...")
        
        # Log fusion to DB
        timestamp = time.time()
        c.execute('''INSERT INTO fusions 
                     (node_1, region_1, node_2, region_2, proof_preview, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (node_id, region, fusion_partner_id, partner_region, proof_preview, timestamp))
        conn.commit()
        conn.close()

        return jsonify({
            "status": "Fusion successful",
            "partner_node": fusion_partner_id,
            "partner_region": partner_region
        }), 200
    else:
        # Insert
        c.execute('''INSERT INTO waiting_nodes (node_id, region, node_hash, timestamp)
                     VALUES (?, ?, ?, ?)''', (node_id, region, node_hash, time.time()))
        conn.commit()
        conn.close()
        
        print(f"[*] {node_id} added to waiting pool. Awaiting cross-region partner...")
        return jsonify({"status": "Waiting for fusion partner"}), 202

@app.route('/api/v1/network/status', methods=['GET'])
def network_status():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute("SELECT node_id, region, node_hash, timestamp FROM waiting_nodes")
    waiting_nodes = c.fetchall()
    
    c.execute("SELECT DISTINCT region FROM waiting_nodes")
    regions = [r[0] for r in c.fetchall()]
    
    nodes_info = []
    for nid, reg, hsh, ts in waiting_nodes:
        nodes_info.append({
            "id": nid,
            "region": reg,
            "hash_preview": hsh[:12],
            "waiting_since": ts
        })
        
    c.execute("SELECT node_1, region_1, node_2, region_2, proof_preview, timestamp FROM fusions ORDER BY timestamp DESC LIMIT 20")
    recent_fusions = []
    for row in c.fetchall():
        recent_fusions.append({
            "node_1": row[0],
            "region_1": row[1],
            "node_2": row[2],
            "region_2": row[3],
            "proof_preview": row[4],
            "timestamp": row[5]
        })
        
    conn.close()
        
    return jsonify({
        "waiting_nodes": len(waiting_nodes),
        "active_regions": regions,
        "nodes": nodes_info,
        "recent_fusions": recent_fusions
    }), 200

if __name__ == '__main__':
    print("--- BACL Crypto Core Server Initialized (SQLite) ---")
    print("--- Constellation Manager Online ---")
    print("Listening for Edge Node Hashes on port 5000...")
    app.run(host='0.0.0.0', port=5000)
