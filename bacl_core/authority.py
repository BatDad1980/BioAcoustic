"""Fail-closed authority checks for BACL prototype manifests.

This module uses HMAC-SHA256 as a local prototype signature primitive. It does
not claim to be a production signing system. The purpose is to prove authority
semantics: missing, stale, revoked, malformed, or replayed authority fails
closed.
"""

from __future__ import annotations

import hmac
import hashlib
from dataclasses import dataclass, field
from typing import Literal

from .manifest import canonical_json


Decision = Literal["AUTHORIZED", "SAFE_HOLD", "SKULL_LOCK"]


@dataclass(frozen=True)
class AuthorityDecision:
    decision: Decision
    reason: str
    raw_fallback_allowed: bool = False


@dataclass
class KeyRegistry:
    """Small in-memory key registry for local verification tests."""

    _keys: dict[str, bytes] = field(default_factory=dict)
    _revoked: set[str] = field(default_factory=set)
    _used_signatures: set[str] = field(default_factory=set)

    def register(self, key_id: str, key_material: bytes) -> None:
        self._keys[key_id] = key_material
        self._revoked.discard(key_id)

    def revoke(self, key_id: str) -> None:
        self._revoked.add(key_id)

    def key_for(self, key_id: str) -> bytes | None:
        return self._keys.get(key_id)

    def is_revoked(self, key_id: str) -> bool:
        return key_id in self._revoked

    def mark_used(self, signature: str) -> None:
        self._used_signatures.add(signature)

    def was_used(self, signature: str) -> bool:
        return signature in self._used_signatures


def sign_payload(payload: dict, key_material: bytes) -> str:
    body = canonical_json(payload).encode("utf-8")
    return hmac.new(key_material, body, hashlib.sha256).hexdigest()


def evaluate_authority(
    payload: dict,
    signature: str | None,
    key_id: str | None,
    registry: KeyRegistry,
    *,
    mark_used: bool = True,
) -> AuthorityDecision:
    """Evaluate a signed payload using fail-closed authority rules."""

    if not key_id:
        return AuthorityDecision("SAFE_HOLD", "MISSING_KEY_ID")

    key = registry.key_for(key_id)
    if key is None:
        return AuthorityDecision("SKULL_LOCK", "UNREGISTERED_KEY")

    if registry.is_revoked(key_id):
        return AuthorityDecision("SKULL_LOCK", "KEY_REVOKED")

    if not signature:
        return AuthorityDecision("SKULL_LOCK", "MISSING_SIGNATURE")

    if registry.was_used(signature):
        return AuthorityDecision("SKULL_LOCK", "SIGNATURE_REPLAY_OR_REUSE")

    expected = sign_payload(payload, key)
    if not hmac.compare_digest(signature, expected):
        return AuthorityDecision("SKULL_LOCK", "SIGNATURE_INVALID")

    if mark_used:
        registry.mark_used(signature)

    return AuthorityDecision("AUTHORIZED", "FRESH_VALID_SIGNATURE")

