Write-Host "Starting Fusion Test..."
python simulate_node_b.py
Start-Sleep -Seconds 3
cargo run
