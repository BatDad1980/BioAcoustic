import requests
import hashlib
import time

def simulate_node_b():
    print("--- Simulating Node B (Geographically Distant) ---")
    server_url = "http://127.0.0.1:5000/api/v1/node/hash"
    
    # Simulate a hash derived from a different biome (e.g., Marine Biome)
    # We use a dummy hash here just to trigger the API
    mock_audio_data = b"marine_biome_waves_crashing_100ms"
    node_b_hash = hashlib.sha3_256(mock_audio_data).hexdigest()
    
    print(f"[*] Generated Marine Biome Hash: {node_b_hash[:16]}...")
    
    payload = {
        "node_id": "Node_B_Marine_01",
        "region": "Atlantic_Coast",
        "node_hash": node_b_hash
    }
    
    print("    -> Transmitting to Crypto Core API...")
    try:
        response = requests.post(server_url, json=payload)
        if response.status_code == 200:
            print("    -> SUCCESS: Constellation Fusion Triggered!")
            print("       Check the Python Server terminal to see the cryptography happen!")
        elif response.status_code == 202:
            print("    -> SUCCESS: Node B added to Waiting Pool.")
            print("       Waiting for a node from a different region to arrive...")
        else:
            print(f"    -> FAILED: Status Code {response.status_code}")
    except Exception as e:
        print(f"    -> ERROR: {e}")

if __name__ == "__main__":
    simulate_node_b()
