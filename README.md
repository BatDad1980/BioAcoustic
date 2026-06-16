# BioAcoustic / BACL Prototype

BioAcoustic is an early prototype lane for the Bio-Acoustic Cryptography Ledger (BACL).

The current repository contains two prototype lanes:

1. a clean-room BACL core for evidence integrity and authority failure behavior;
2. an experimental BioAcoustic constellation demo for entropy-source modeling.

The clean-room BACL core demonstrates:

- canonical evidence manifests;
- stable SHA-256 manifest digests;
- local prototype signed-authority checks;
- fail-closed handling for missing, unknown, revoked, invalid, or replayed authority;
- append-only evidence ledger records;
- ledger-chain tamper detection.

The BioAcoustic constellation demo demonstrates:

- Rust edge nodes collect microphone-derived sample data and estimate entropy.
- Edge nodes hash local entropy material into fixed-width node digests.
- A Python Flask coordinator pairs nodes from different regions.
- The coordinator derives demonstration key material from paired node hashes.
- AES-256-GCM is used to demonstrate authenticated encryption and tamper detection.
- A static dashboard visualizes waiting nodes and fusion events.

## Current Status

This repository is a research prototype, not production cryptography.

What is working:

- BACL core unit tests pass.
- Manifest hashing is stable.
- Signed authority is valid once and replay-locked after use.
- Missing, invalid, revoked, unknown, or replayed authority safe-holds or locks.
- Ledger verification detects tampered manifests.
- Python encryption helper compiles and runs.
- AES-GCM round trip succeeds.
- Tampered ciphertext fails authentication.
- Rust edge node passes `cargo check`.
- Coordinator API validates 64-character hex node hashes.
- Dashboard can poll the local coordinator status endpoint.

What is not claimed:

- no production-ready key management;
- no certified entropy source;
- no court-certified chain of custody;
- no "unbreakable" encryption;
- no hardware-backed root of trust;
- no external security audit.

## Repository Layout

```text
bacl_core/
  manifest.py            Canonical manifest payloads and stable digests.
  authority.py           Local prototype signing and fail-closed authority rules.
  ledger.py              Append-only event ledger and chain verification.

crypto_core/
  encryption_logic.py    Demo AES-GCM and key-material derivation helper.
  server.py              Flask coordinator for node pairing and fusion logs.

edge_node/
  src/main.rs            Rust microphone entropy edge-node prototype.
  simulate_node_b.py     Simple Python sender to trigger a second-region fusion.
  test_fusion.ps1        Local manual demo helper.

dashboard/
  index.html             Local dashboard shell.
  app.js                 Polls coordinator status.
  style.css              Dashboard styling.

docs/
  BACL Tech Spec Report.pdf
  BACL_CORE_EVIDENCE_GATE_V0.md

tests/
  test_bacl_core.py      Unit tests for manifests, authority, and ledger behavior.
```

## Quick Verification

From the repository root:

```powershell
python -m unittest discover -s .\tests -v
python .\tools\run_bacl_core_gate.py
python -m py_compile .\crypto_core\encryption_logic.py .\crypto_core\server.py .\edge_node\simulate_node_b.py
python .\crypto_core\encryption_logic.py
cd .\edge_node
cargo check
```

Expected behavior:

- BACL core tests pass.
- BACL core evidence gate writes `docs/BACL_CORE_EVIDENCE_GATE_V0.md`.
- Python files compile.
- Encryption demo decrypts the original message.
- Tampered ciphertext returns an authentication failure.
- Rust edge node type-checks.

## Local Demo

Terminal 1:

```powershell
cd .\crypto_core
python .\server.py
```

Terminal 2:

```powershell
cd .\edge_node
python .\simulate_node_b.py
cargo run
```

Then open:

```text
dashboard/index.html
```

## Security Boundary

BACL's strongest current evidence sits in the broader HQA authority-gate lane:

- fail-closed authority contracts;
- signed manifest review;
- key reuse blocking;
- malformed/unregistered/revoked authority lockouts;
- dry-run-only authorization for valid manifests.

This BioAcoustic repository is the experimental entropy-source lane. Audio-derived entropy should be treated as supplemental research material until measured, conditioned, mixed with private secret material, and externally reviewed.

See `docs/SECURITY_BOUNDARY.md` for the detailed claim boundary.
