"""Canonical evidence manifests for BACL.

The manifest layer is intentionally boring: stable JSON, stable hashes, and
explicit metadata. This makes evidence bundles easier to verify later.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any


def canonical_json(payload: dict[str, Any]) -> str:
    """Return a stable JSON representation for hashing and signing."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def manifest_digest(payload: dict[str, Any]) -> str:
    """Return a SHA-256 digest of the canonical payload."""
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EvidenceManifest:
    """A bounded, reviewable evidence event manifest."""

    manifest_id: str
    asset_id: str
    event_type: str
    created_utc: str
    actor: str
    source_digest: str
    payload_digest: str
    parent_event_digest: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def digest(self) -> str:
        return manifest_digest(self.to_payload())

