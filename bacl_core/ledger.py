"""Tamper-evident event ledger for BACL prototype evidence records."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .authority import KeyRegistry, evaluate_authority
from .manifest import EvidenceManifest, canonical_json, manifest_digest


@dataclass(frozen=True)
class LedgerEvent:
    sequence: int
    manifest: dict
    manifest_digest: str
    previous_event_digest: str | None
    key_id: str
    signature: str
    event_digest: str


@dataclass(frozen=True)
class LedgerVerification:
    ok: bool
    checked_events: int
    failure_reason: str | None = None


class EvidenceLedger:
    """Append-only evidence ledger with local signature verification."""

    def __init__(self, registry: KeyRegistry) -> None:
        self.registry = registry
        self._events: list[LedgerEvent] = []

    @property
    def events(self) -> list[LedgerEvent]:
        return list(self._events)

    def append(self, manifest: EvidenceManifest, key_id: str, signature: str) -> LedgerEvent:
        payload = manifest.to_payload()
        decision = evaluate_authority(payload, signature, key_id, self.registry)
        if decision.decision != "AUTHORIZED":
            raise PermissionError(decision.reason)

        previous_digest = self._events[-1].event_digest if self._events else None
        event_payload = {
            "sequence": len(self._events) + 1,
            "manifest": payload,
            "manifest_digest": manifest.digest,
            "previous_event_digest": previous_digest,
            "key_id": key_id,
            "signature": signature,
        }
        event_digest = manifest_digest(event_payload)
        event = LedgerEvent(event_digest=event_digest, **event_payload)
        self._events.append(event)
        return event

    def export_jsonl(self) -> str:
        return "\n".join(canonical_json(asdict(event)) for event in self._events)


def verify_ledger(events: list[LedgerEvent]) -> LedgerVerification:
    previous_digest: str | None = None

    for index, event in enumerate(events, start=1):
        if event.sequence != index:
            return LedgerVerification(False, index - 1, "SEQUENCE_GAP")

        if event.previous_event_digest != previous_digest:
            return LedgerVerification(False, index - 1, "CHAIN_LINK_MISMATCH")

        if manifest_digest(event.manifest) != event.manifest_digest:
            return LedgerVerification(False, index - 1, "MANIFEST_DIGEST_MISMATCH")

        event_payload = {
            "sequence": event.sequence,
            "manifest": event.manifest,
            "manifest_digest": event.manifest_digest,
            "previous_event_digest": event.previous_event_digest,
            "key_id": event.key_id,
            "signature": event.signature,
        }
        if manifest_digest(event_payload) != event.event_digest:
            return LedgerVerification(False, index - 1, "EVENT_DIGEST_MISMATCH")

        previous_digest = event.event_digest

    return LedgerVerification(True, len(events))

