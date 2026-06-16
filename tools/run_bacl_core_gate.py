"""Run the clean-room BACL core evidence gate.

This script writes a small markdown report proving the core local behaviors:
stable manifest digest, fresh signature authorization, replay blocking,
revocation lockout, ledger append, and tamper detection.
"""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bacl_core.authority import KeyRegistry, evaluate_authority, sign_payload
from bacl_core.ledger import EvidenceLedger, LedgerEvent, verify_ledger
from bacl_core.manifest import EvidenceManifest

REPORT_PATH = ROOT / "docs" / "BACL_CORE_EVIDENCE_GATE_V0.md"


def build_manifest(manifest_id: str = "BACL-MANIFEST-001") -> EvidenceManifest:
    return EvidenceManifest(
        manifest_id=manifest_id,
        asset_id="BACL_CORE_GATE",
        event_type="EVIDENCE_IMPORT",
        created_utc="2026-06-15T16:00:00Z",
        actor="clean_room_operator",
        source_digest="a" * 64,
        payload_digest="b" * 64,
        metadata={"mode": "local_core_gate", "live_authority": False},
    )


def run_gate() -> list[tuple[str, bool, str]]:
    key_material = b"local-gate-key-material-not-a-secret"
    registry = KeyRegistry()
    registry.register("reviewer-key-v0", key_material)

    manifest = build_manifest()
    payload = manifest.to_payload()
    signature = sign_payload(payload, key_material)

    first_decision = evaluate_authority(payload, signature, "reviewer-key-v0", registry)
    replay_decision = evaluate_authority(payload, signature, "reviewer-key-v0", registry)

    revoked_registry = KeyRegistry()
    revoked_registry.register("reviewer-key-v0", key_material)
    revoked_registry.revoke("reviewer-key-v0")
    revoked_decision = evaluate_authority(payload, signature, "reviewer-key-v0", revoked_registry)

    ledger_registry = KeyRegistry()
    ledger_registry.register("ledger-key-v0", key_material)
    ledger = EvidenceLedger(ledger_registry)
    ledger_signature = sign_payload(payload, key_material)
    event = ledger.append(manifest, "ledger-key-v0", ledger_signature)
    ledger_verification = verify_ledger(ledger.events)

    tampered_event = LedgerEvent(
        sequence=event.sequence,
        manifest={**event.manifest, "actor": "tampered_actor"},
        manifest_digest=event.manifest_digest,
        previous_event_digest=event.previous_event_digest,
        key_id=event.key_id,
        signature=event.signature,
        event_digest=event.event_digest,
    )
    tampered_verification = verify_ledger([tampered_event])

    checks = [
        ("stable_manifest_digest", manifest.digest == build_manifest().digest, f"Digest: `{manifest.digest[:16]}...`"),
        ("fresh_signature_authorized", first_decision.decision == "AUTHORIZED", first_decision.reason),
        ("signature_replay_locked", replay_decision.decision == "SKULL_LOCK", replay_decision.reason),
        ("revoked_key_locked", revoked_decision.decision == "SKULL_LOCK", revoked_decision.reason),
        ("ledger_append_verified", ledger_verification.ok, f"Checked events: `{ledger_verification.checked_events}`"),
        ("tampered_manifest_detected", not tampered_verification.ok and tampered_verification.failure_reason == "MANIFEST_DIGEST_MISMATCH", tampered_verification.failure_reason or ""),
        ("no_raw_fallback_allowed", all(not decision.raw_fallback_allowed for decision in [first_decision, replay_decision, revoked_decision]), "All authority decisions keep raw fallback disabled."),
    ]
    return checks


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# BACL Core Evidence Gate V0",
        "",
        "## Purpose",
        "",
        "This gate verifies the clean-room BACL core: canonical manifests, fail-closed authority decisions, replay blocking, revoked-key lockout, append-only ledger verification, and tamper detection.",
        "",
        "## Results",
        "",
        f"- Checks: `{len(checks)}`",
        f"- Passed: `{passed}`",
        f"- Failed: `{len(checks) - passed}`",
        "",
        "| Check | Status | Detail |",
        "|---|---:|---|",
    ]
    for name, ok, detail in checks:
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This gate validates local evidence-integrity behavior only. It does not provide production cryptography, certify entropy sources, authorize hardware, or replace external security review.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    checks = run_gate()
    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"BACL core evidence gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
