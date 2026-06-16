# BACL Core Evidence Gate V0

## Purpose

This gate verifies the clean-room BACL core: canonical manifests, fail-closed authority decisions, replay blocking, revoked-key lockout, append-only ledger verification, and tamper detection.

## Results

- Checks: `7`
- Passed: `7`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| stable_manifest_digest | PASS | Digest: `aa882fc35055864c...` |
| fresh_signature_authorized | PASS | FRESH_VALID_SIGNATURE |
| signature_replay_locked | PASS | SIGNATURE_REPLAY_OR_REUSE |
| revoked_key_locked | PASS | KEY_REVOKED |
| ledger_append_verified | PASS | Checked events: `1` |
| tampered_manifest_detected | PASS | MANIFEST_DIGEST_MISMATCH |
| no_raw_fallback_allowed | PASS | All authority decisions keep raw fallback disabled. |

## Boundary

This gate validates local evidence-integrity behavior only. It does not provide production cryptography, certify entropy sources, authorize hardware, or replace external security review.
