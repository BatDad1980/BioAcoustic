# Security Boundary

## Purpose

This document defines what the BioAcoustic / BACL prototype currently demonstrates and what it does not claim.

## Demonstrated Today

The repository demonstrates:

- canonical evidence manifests;
- stable manifest digests;
- local prototype signed-authority checks;
- fail-closed handling for missing, invalid, unknown, revoked, or replayed authority;
- append-only ledger events;
- tamper-evident ledger verification;
- local edge-node entropy capture shape;
- Shannon entropy estimation over audio sample bytes;
- hash generation from local entropy material;
- coordinator-side pairing of node hashes from different regions;
- demonstration key-material derivation from two node hashes;
- AES-256-GCM authenticated encryption;
- authentication failure when ciphertext is altered;
- local dashboard visibility into node pairing and fusion events.

## Not Demonstrated

The repository does not demonstrate:

- production key management;
- certified randomness or NIST-approved entropy conditioning;
- secure enrollment of trusted devices;
- hardware-backed attestation;
- replay/spoof resistance;
- secure transport between edge nodes and coordinator;
- authenticated node identity;
- court-certified evidence custody;
- production-grade cryptographic protocol design.

## Bioacoustic Entropy Boundary

Audio-derived entropy is treated as experimental supplemental input.

It must not be treated as sole signing authority or sole key authority. Production design would need:

- formal entropy-source characterization;
- spoofing and replay tests;
- silence and low-entropy failure handling;
- private secret material outside public telemetry;
- a standard KDF such as HKDF with proper salt and context labels;
- secure device identity and transport authentication;
- external cryptographic review.

## Buyer-Safe Language

Use:

- prototype entropy-source modeling;
- authenticated encryption demo;
- tamper-evident workflow direction;
- fail-closed authority boundary;
- chain-of-custody architecture concept;
- security research prototype.

Avoid:

- unbreakable;
- impossible to hack;
- guaranteed;
- military-grade;
- court-certified;
- production cryptography;
- nature-derived keys are inherently secure.

## Current Best Commercial Fit

BioAcoustic/BACL is strongest today as supporting infrastructure for:

- evidence integrity;
- chain-of-custody workflows;
- field evidence capture;
- secure local/offline systems;
- HQA authority gates;
- Forensic Audio evidence packaging;
- HPPW replay packet integrity.
