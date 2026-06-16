# Current Audit

Date: 2026-06-15

## Summary

BioAcoustic is a coherent early BACL prototype. It has a working local architecture, but it should be presented as a research prototype and evidence-integrity direction, not production cryptography.

## What Is Real

- Clean-room BACL core unit tests pass.
- BACL Core Evidence Gate V0 passes 7/7 checks.
- Canonical evidence manifests produce stable digests.
- Signed authority is valid once and replay-locked after use.
- Missing, invalid, unknown, revoked, or replayed authority safe-holds or locks.
- Append-only ledger verification detects tampered manifests.
- Python AES-GCM demo runs successfully.
- Tampered ciphertext fails authentication.
- Rust edge node compiles with `cargo check`.
- Local coordinator stores waiting nodes and fusion events in SQLite.
- Dashboard polls coordinator status and renders network/fusion state.
- Edge-node logic includes low-entropy detection and fallback behavior.

## Verification Run

Commands run:

```powershell
python -m unittest discover -s .\tests -v
python .\tools\run_bacl_core_gate.py
python -m py_compile .\crypto_core\encryption_logic.py .\crypto_core\server.py .\edge_node\simulate_node_b.py
python .\crypto_core\encryption_logic.py
cd .\edge_node
cargo check
```

Result:

- BACL core tests: PASS, 6/6
- BACL core evidence gate: PASS, 7/7
- Python compile: PASS
- AES-GCM round trip: PASS
- Tamper authentication failure: PASS
- Rust `cargo check`: PASS
- Credential scan: no obvious API keys or tokens found

## Strongest Architecture Elements

- canonical manifest / digest discipline;
- fail-closed authority semantics;
- replay and revoked-key blocking;
- tamper-evident ledger verification;
- local/offline first shape;
- environmental entropy observation;
- cross-node pairing concept;
- authenticated encryption primitive;
- dashboard observability;
- path toward evidence-chain packaging.

## Highest Risks

1. **Cryptographic overclaim risk**  
   XORing two public or semi-public hashes and hashing the result is not enough for production key derivation.

2. **Entropy-source risk**  
   Microphone-derived data can be silent, replayed, compressed, spoofed, or dominated by device artifacts.

3. **Transport/authentication risk**  
   The Flask API accepts node hashes over unauthenticated HTTP in the local prototype.

4. **Repo hygiene risk**  
   Installer binaries and large demo videos do not belong in source control. They were removed from the clean-room pass.

5. **Evidence-custody gap**  
   The project does not yet contain a formal evidence manifest, detached signature, verification CLI, or chain-of-custody event model.

## Recommended Next Build

1. Add a formal manifest schema.
2. Add signed event records.
3. Add key registry and revocation list.
4. Add replay/spoof/low-entropy test fixtures.
5. Replace prototype key fusion with a clearly labeled KDF experiment.
6. Add an evidence-bundle verifier CLI.
7. Keep audio entropy as supplemental input, not sole authority.

## RTI-Safe Position

BioAcoustic/BACL is a supporting security and evidence-integrity asset. Its current value is not a claim of unbreakable natural-sound encryption. Its current value is a direction for fail-closed authority, tamper-evident provenance, local/offline evidence handling, and experimental entropy-source modeling.
