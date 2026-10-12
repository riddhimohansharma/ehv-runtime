---
ckb_doc: "security-and-data"
title: "Security and data"
audience: "security, compliance, engineers"
diataxis: "reference"
source_commit: "26289dcca127c0dbe18e2cbba0fc4b205110441e"
branch: "main"
generator: "codebase-kb-engine 0.9.4"
ckb_version: "0.2"
confidence_scope: "doc"
confidence:
  confirmed: 16
  inferred: 4
  unknown: 0
freshness_cmd: "git diff --quiet 26289dcca127c0dbe18e2cbba0fc4b205110441e HEAD -- . ':(exclude).ckb'"
---
# Security and Data

## Trust boundaries

- Agent or LLM output to PEP. Decorated functions only run if the epoch is valid and the constraint passes (ehv/compiler/engine.py:113, ehv/compiler/engine.py:131) [C].
- PEP to enclave. Attestation and the epoch hash are held in a simulated enclave backed by shared memory (ehv/enclave/enclave.py:20, ehv/enclave/enclave.py:47) [C].
- PEP to policy store. Policies come from a CRDT store with last-writer-wins merging, so peers are trusted to supply honest timestamps (ehv/sync/store.py:28) [I].
- Process to outside. Only the red-team example calls out, to api.anthropic.com (examples/anthropic_redteam.py:97) [I].
- Decoding boundary. Grammar-constrained decoding masks tokens outside the dosage grammar (ehv/gcd/grammar.py:21) [C].

## AuthN/AuthZ model

- Workload identity is a SPIFFE SVID stub. An SVID is valid only if not revoked and within its TTL (default 3600s) (ehv/identity/workload.py:43) [C].
- Authorization is policy-based. The decision is PERMIT, DENY or ESCALATE, with fail-closed behaviour on an invalid epoch (ehv/compiler/engine.py:131, EHV.tla:77) [C].
- Safety invariant in the formal model: no unsafe action is PERMITted (EHV.tla:46) [C].
- No user authentication or network authz exists, because there is no server [C].

## Data classification

| Data | Class | Where | Source |
|---|---|---|---|
| Policies | internal | PolicyStore, in memory | ehv/sync/store.py:28 [C] |
| Enclave state | sensitive | shared memory file `ehv_enclave_mem` | ehv/enclave/enclave.py:20 [C] |
| GBOM audit log | audit | OSCAL JSON export | ehv/compiler/gbom.py:125 [C] |
| Benchmark output | public | bench/output | bench/measure_enforcement.py:87 [C] |
| Clinical dosage examples | synthetic, possible PHI-like domain | examples | examples/clinical_dosage.py:11 [I] |

No real PHI or PII was observed [?].

## Secrets inventory

| Name | Kind | Source | Referenced at |
|---|---|---|---|
| ANTHROPIC_API_KEY | API key | env var | examples/anthropic_redteam.py:94 [C] |
| Enclave secret_key (simulated root key) | hardcoded key | source code | ehv/enclave/enclave.py:24 [C] |

## Security findings

- **high [C]:** A hardcoded simulated enclave root key is in source (ehv/enclave/enclave.py:24) [C]. Anyone with the source can forge attestation, so it must never be used as a real trust anchor.
- **medium [I]:** The enclave state sits in a shared-memory file that other local processes may read or write, depending on file permissions (ehv/enclave/enclave.py:20) [I].
- **medium [I]:** The LWW store accepts any higher timestamp, so a peer with a skewed clock or a hostile peer can overwrite policy (ehv/sync/store.py:28) [I].
- **low [I]:** Stale-epoch windows during a partition can permit actions under old policy until re-attestation (experiments/epoch_staleness.py:141) [I].
- **low [?]:** The SVID stub is not validated against a real SPIRE agent (ehv/identity/workload.py:25) [?].

## Compliance notes

- The GBOM exports OSCAL, which fits NIST-style control documentation (ehv/compiler/gbom.py:125) [I].
- The tamper-evident hash chain supports audit use, but it has no external anchor or signature check observed (experiments/gbom_audit.py:38) [?].
- Clinical examples (Vincristine) are demonstrations and not validated for clinical use (examples/clinical_dosage.py:11) [I].
- The repo is MIT licensed (pyproject.toml:17) [C].
