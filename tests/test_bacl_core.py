import copy
import unittest

from bacl_core.authority import KeyRegistry, evaluate_authority, sign_payload
from bacl_core.ledger import EvidenceLedger, LedgerEvent, verify_ledger
from bacl_core.manifest import EvidenceManifest


def sample_manifest(manifest_id="M-001", parent_event_digest=None):
    return EvidenceManifest(
        manifest_id=manifest_id,
        asset_id="FOR_AUDIO_CASE_001",
        event_type="EVIDENCE_IMPORT",
        created_utc="2026-06-15T16:00:00Z",
        actor="lab_operator",
        source_digest="a" * 64,
        payload_digest="b" * 64,
        parent_event_digest=parent_event_digest,
        metadata={"file_name": "sample.wav", "case_id": "CASE-001"},
    )


class TestBACLCore(unittest.TestCase):
    def setUp(self):
        self.registry = KeyRegistry()
        self.registry.register("reviewer-key-1", b"local-test-key-material")

    def test_manifest_digest_is_stable(self):
        left = sample_manifest()
        right = sample_manifest()

        self.assertEqual(left.digest, right.digest)

    def test_valid_signature_authorizes_once(self):
        manifest = sample_manifest()
        payload = manifest.to_payload()
        signature = sign_payload(payload, b"local-test-key-material")

        first = evaluate_authority(payload, signature, "reviewer-key-1", self.registry)
        second = evaluate_authority(payload, signature, "reviewer-key-1", self.registry)

        self.assertEqual(first.decision, "AUTHORIZED")
        self.assertEqual(second.decision, "SKULL_LOCK")
        self.assertEqual(second.reason, "SIGNATURE_REPLAY_OR_REUSE")
        self.assertFalse(first.raw_fallback_allowed)
        self.assertFalse(second.raw_fallback_allowed)

    def test_failure_cases_fail_closed(self):
        manifest = sample_manifest()
        payload = manifest.to_payload()
        signature = sign_payload(payload, b"local-test-key-material")

        cases = [
            evaluate_authority(payload, signature, None, self.registry),
            evaluate_authority(payload, signature, "unknown-key", self.registry),
            evaluate_authority(payload, None, "reviewer-key-1", self.registry),
            evaluate_authority({**payload, "actor": "attacker"}, signature, "reviewer-key-1", self.registry),
        ]

        for decision in cases:
            self.assertIn(decision.decision, {"SAFE_HOLD", "SKULL_LOCK"})
            self.assertFalse(decision.raw_fallback_allowed)

    def test_revoked_key_locks(self):
        manifest = sample_manifest()
        payload = manifest.to_payload()
        signature = sign_payload(payload, b"local-test-key-material")
        self.registry.revoke("reviewer-key-1")

        decision = evaluate_authority(payload, signature, "reviewer-key-1", self.registry)

        self.assertEqual(decision.decision, "SKULL_LOCK")
        self.assertEqual(decision.reason, "KEY_REVOKED")

    def test_ledger_append_and_verify(self):
        ledger = EvidenceLedger(self.registry)
        manifest = sample_manifest()
        signature = sign_payload(manifest.to_payload(), b"local-test-key-material")

        event = ledger.append(manifest, "reviewer-key-1", signature)
        verification = verify_ledger(ledger.events)

        self.assertEqual(event.sequence, 1)
        self.assertTrue(verification.ok)
        self.assertEqual(verification.checked_events, 1)

    def test_ledger_detects_tampered_manifest(self):
        ledger = EvidenceLedger(self.registry)
        manifest = sample_manifest()
        signature = sign_payload(manifest.to_payload(), b"local-test-key-material")
        event = ledger.append(manifest, "reviewer-key-1", signature)

        tampered_manifest = copy.deepcopy(event.manifest)
        tampered_manifest["actor"] = "attacker"
        tampered_event = LedgerEvent(
            sequence=event.sequence,
            manifest=tampered_manifest,
            manifest_digest=event.manifest_digest,
            previous_event_digest=event.previous_event_digest,
            key_id=event.key_id,
            signature=event.signature,
            event_digest=event.event_digest,
        )

        verification = verify_ledger([tampered_event])

        self.assertFalse(verification.ok)
        self.assertEqual(verification.failure_reason, "MANIFEST_DIGEST_MISMATCH")


if __name__ == "__main__":
    unittest.main()
