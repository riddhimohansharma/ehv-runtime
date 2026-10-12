---
ckb_doc: "decisions"
title: "Decisions"
audience: "architects, tech leads"
diataxis: "explanation"
source_commit: "26289dcca127c0dbe18e2cbba0fc4b205110441e"
branch: "main"
generator: "codebase-kb-engine 0.9.4"
ckb_version: "0.2"
confidence_scope: "doc"
confidence:
  confirmed: 14
  inferred: 4
  unknown: 0
freshness_cmd: "git diff --quiet 26289dcca127c0dbe18e2cbba0fc4b205110441e HEAD -- . ':(exclude).ckb'"
---
# Decisions

## Decision log

### ADR-stdlib-only-core: Zero runtime dependencies
- **Status:** observed
- **Context:** The runtime must be easy to embed and audit.
- **Decision:** The core depends only on the Python standard library. pandas and matplotlib are an optional `bench` extra.
- **Consequences:** The core is small and low-risk for supply chain. Benchmarks need an extra install.
- **Evidence:** pyproject.toml:21, pyproject.toml:25 [C]
- **Confidence:** [C]

### ADR-fail-closed-enforcement: Deny by default on invalid epoch
- **Status:** inferred
- **Context:** An agent action must not run when attestation cannot be trusted.
- **Decision:** An invalid or unreachable epoch denies all actions and raises `GovernanceError`. A constraint exception is logged as ESCALATE.
- **Consequences:** Availability suffers during partitions, in exchange for safety. The same is stated in the TLA+ model.
- **Evidence:** ehv/compiler/engine.py:131, ehv/compiler/engine.py:141, EHV.tla:77 [C]
- **Confidence:** [C]

### ADR-simulated-enclave: Simulate the TEE in software
- **Status:** inferred
- **Context:** Real SEV-SNP hardware is unavailable for a research prototype.
- **Decision:** The enclave is simulated with shared memory and a hardcoded key. SEV-SNP latency is projected synthetically.
- **Consequences:** The design can be exercised anywhere, but trust claims are not hardware-backed. Rationale is not documented in code [?].
- **Evidence:** ehv/enclave/enclave.py:8, ehv/enclave/enclave.py:24, bench/sev_snp_benchmark.py:25 [I]
- **Confidence:** [I]

### ADR-crdt-lww-policy-store: Replicate policy with a last-writer-wins CRDT
- **Status:** inferred
- **Context:** Policy must converge across partitioned nodes.
- **Decision:** PolicyStore rejects updates with a timestamp at or below the current one and breaks ties lexicographically. A vector-clock `CausalPolicyStore` also exists.
- **Consequences:** Convergence is simple, but it relies on trustworthy clocks.
- **Evidence:** ehv/sync/store.py:28, experiments/crdt_convergence.py:53 [I]
- **Confidence:** [I]

### ADR-epoch-reattestation: Time-boxed epochs with hash-mismatch re-attestation
- **Status:** inferred
- **Context:** Cached attestation can go stale.
- **Decision:** Re-attest after 60s by default, on the first run, or when the policy hash differs from the enclave hash.
- **Consequences:** A bounded staleness window exists during partitions.
- **Evidence:** ehv/compiler/engine.py:58, experiments/epoch_staleness.py:141 [C]
- **Confidence:** [C]

### ADR-hash-chained-gbom: Tamper-evident hash-chained audit log
- **Status:** inferred
- **Context:** Decisions, including denials, need an auditable trail.
- **Decision:** The GBOM log chains entries by hash, verifies them with `verify_chain`, and exports OSCAL.
- **Consequences:** Edits are detectable, but the log has no external anchor [?].
- **Evidence:** ehv/compiler/gbom.py:125, experiments/gbom_audit.py:38 [I]
- **Confidence:** [I]

### ADR-grammar-constrained-decoding: Enforce dosage at decode time
- **Status:** inferred
- **Context:** Unsafe output should be impossible to generate, not only blocked afterwards.
- **Decision:** A DFA grammar admits only `administer <dose> Vincristine IV` with dose at or below the maximum, and other tokens are masked to -inf.
- **Consequences:** The constraint is domain-specific and the grammar must be written per policy.
- **Evidence:** ehv/gcd/grammar.py:21, ehv/gcd/masker.py:23 [C]
- **Confidence:** [C]

### ADR-formal-tla-spec: Specify safety in TLA+
- **Status:** inferred
- **Context:** The enforcement logic should satisfy a checkable invariant.
- **Decision:** EHV.tla models actions and a SafetyInvariant, checked with TLC via EHV.cfg.
- **Consequences:** The proof covers the model only, and no conformance link to the Python code was observed [?].
- **Evidence:** EHV.tla:46, EHV.tla:70, EHV.cfg:1 [I]
- **Confidence:** [I]

## Existing ADRs

Not applicable — no docs/adr directory or RFCs were found. docs/ARCHITECTURE.md is an architecture description and was not scanned in depth [?].
