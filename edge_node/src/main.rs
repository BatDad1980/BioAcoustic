// BACL Edge Node ("The Ear", "The Nexus", and "Storm-Guard")
use sha3::{Digest, Keccak256};
use hex;
use reqwest::Client;
use serde::Serialize;
use std::time::Duration;
use tokio::time::sleep;
use std::collections::HashMap;
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use std::sync::{Arc, Mutex};
use anyhow::Result;

#[derive(Serialize)]
struct NodePayload {
    node_id: String,
    region: String,
    node_hash: String,
}

/// Storm-Guard: Calculates Shannon Entropy of the raw byte array
fn calculate_shannon_entropy(data: &[u8]) -> f64 {
    if data.is_empty() {
        return 0.0;
    }

    let mut frequency_map = HashMap::new();
    for &byte in data {
        *frequency_map.entry(byte).or_insert(0) += 1;
    }

    let len = data.len() as f64;
    let mut entropy = 0.0;

    for &count in frequency_map.values() {
        let p = count as f64 / len;
        entropy -= p * p.log2();
    }

    entropy
}

fn extract_entropy(audio_data: &[f32]) -> Vec<u8> {
    let mut raw_bytes = Vec::new();
    for &sample in audio_data {
        raw_bytes.extend_from_slice(&sample.to_le_bytes());
    }
    raw_bytes
}

fn generate_node_hash(entropy_bytes: &[u8]) -> String {
    let mut hasher = Keccak256::new();
    hasher.update(entropy_bytes);
    hex::encode(hasher.finalize())
}

fn setup_audio_stream(buffer: Arc<Mutex<Vec<f32>>>) -> Result<cpal::Stream> {
    let host = cpal::default_host();
    let device = host.default_input_device()
        .ok_or_else(|| anyhow::anyhow!("Failed to get default input device"))?;
        
    println!("[*] Audio Device Connected: {}", device.name().unwrap_or_default());
    
    let config = device.default_input_config()?;
    
    let err_fn = move |err| {
        eprintln!("an error occurred on stream: {}", err);
    };

    let stream = match config.sample_format() {
        cpal::SampleFormat::F32 => device.build_input_stream(
            &config.into(),
            move |data: &[f32], _: &cpal::InputCallbackInfo| {
                let mut buf = buffer.lock().unwrap();
                buf.extend_from_slice(data);
                // Keep buffer size manageable
                if buf.len() > 44100 * 2 {
                    let drain_len = buf.len() - 44100;
                    buf.drain(0..drain_len);
                }
            },
            err_fn,
            None,
        )?,
        _ => return Err(anyhow::anyhow!("Unsupported sample format")),
    };

    stream.play()?;
    Ok(stream)
}

#[tokio::main]
async fn main() -> Result<()> {
    println!("--- BACL Edge Node Initialized ---");
    println!("[*] Storm-Guard Watchdog Active. Minimum Entropy Threshold: 3.5 bits/byte");
    
    let audio_buffer = Arc::new(Mutex::new(Vec::new()));
    
    // Setup CPAL hardware stream
    let _stream = match setup_audio_stream(audio_buffer.clone()) {
        Ok(s) => {
            println!("[*] Hardware Microphone Online. Listening for biological entropy...");
            Some(s)
        },
        Err(e) => {
            println!("[!] Hardware Microphone Warning: {}. Defaulting to TRNG fallback loop.", e);
            None
        }
    };
    
    let node_id = "Node_A_Forest_01".to_string();
    let region = "Pacific_Northwest".to_string();
    let client = Client::new();
    let server_url = "http://127.0.0.1:5000/api/v1/node/hash";

    for cycle in 1..=5 {
        println!("\n------------------------------------------------");
        println!("[+] Starting Hardware Cycle {}...", cycle);
        
        // Wait to accumulate audio buffer
        sleep(Duration::from_secs(2)).await;
        
        let mut captured_audio: Vec<f32> = {
            let mut buf = audio_buffer.lock().unwrap();
            let data = buf.clone();
            buf.clear(); // clear after reading
            data
        };
        
        // If stream failed or mic is perfectly silent, this will be empty or 0s
        if captured_audio.is_empty() {
            captured_audio = vec![0.0; 100]; // Simulated zero-entropy flatline
        }

        let mut entropy_bytes = extract_entropy(&captured_audio);
        
        // 1. Storm-Guard Watchdog Check
        let current_entropy = calculate_shannon_entropy(&entropy_bytes);
        println!("    -> Measured Shannon Entropy: {:.3} bits/byte", current_entropy);

        if current_entropy < 3.5 {
            println!("    -> [WARNING] STORM-GUARD TRIGGERED! Entropy critically low (possible spoofing, silent mic, or hardware failure).");
            println!("    -> [FAIL-SAFE] Pivoting to Hardware TRNG Fallback...");
            
            // Generate raw entropy simulating a hardware TRNG
            let time_bytes = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().subsec_nanos().to_le_bytes();
            let mut hasher = Keccak256::new();
            hasher.update(&time_bytes);
            let mut trng_bytes = hasher.finalize().to_vec();
            
            // Duplicate to pad
            trng_bytes.extend(trng_bytes.clone());
            
            entropy_bytes = trng_bytes; // Swap out the bad audio entropy for the hardware entropy
            println!("    -> [FAIL-SAFE] New TRNG Entropy: {:.3} bits/byte", calculate_shannon_entropy(&entropy_bytes));
        } else {
            println!("    -> [STORM-GUARD] Signal Verified. Biological audio entropy is healthy.");
        }

        // 2. Hash and Transmit
        let node_hash = generate_node_hash(&entropy_bytes);
        println!("    -> Generated Hash: {}...", &node_hash[..16]);
        
        let payload = NodePayload {
            node_id: node_id.clone(),
            region: region.clone(),
            node_hash: node_hash,
        };

        match client.post(server_url).json(&payload).send().await {
            Ok(res) if res.status().is_success() => println!("    -> SUCCESS: Hash transmitted to Crypto Core."),
            Ok(res) if res.status() == 202 => println!("    -> SUCCESS: Added to waiting pool."),
            _ => println!("    -> FAILED: Could not transmit to API."),
        }
    }

    Ok(())
}
