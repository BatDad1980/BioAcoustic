"""Clean-room BACL evidence-integrity core.

This package contains local prototype primitives for canonical manifests,
signed event records, fail-closed authority decisions, and append-only ledger
verification. It is not production cryptography.
"""

from .authority import AuthorityDecision, KeyRegistry, evaluate_authority
from .ledger import EvidenceLedger, LedgerVerification
from .manifest import EvidenceManifest, canonical_json, manifest_digest

__all__ = [
    "AuthorityDecision",
    "EvidenceLedger",
    "EvidenceManifest",
    "KeyRegistry",
    "LedgerVerification",
    "canonical_json",
    "evaluate_authority",
    "manifest_digest",
]
