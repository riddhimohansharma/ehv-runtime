# EHV-Runtime: Scope & Limitations

> This document explicitly scopes what the EHV-Runtime **does** and **does not** implement relative to the full EHV architecture described in the paper (arXiv preprint, under review).

## What This Repository Is

EHV-Runtime is a **proof-of-concept** demonstrating the EHV enforcement pattern: decorator-based policy enforcement with CRDT-inspired policy synchronization. It validates the **control flow** of the Governance-Aware JIT architecture.

## Implementation Status

| Paper Pillar | Claim | Runtime Status | Notes |
|:---|:---|:---|:---|
| **Pillar 1: CRDT Policy Sync** | distributed causal policy synchronization | ✅ **Implemented** | `CausalPolicyStore` using vector clocks to enforce causal consistency and prevent NTP hijacking (mitigating Threat T7). |
| **Pillar 2: TEE Attestation Caching** | Hardware-rooted TEE with epoch-based attestation | ⚠️ **Simulated** | Attestation reports mock TEE measurements. Successfully enforces strict fail-closed partition semantics: when a partition outlasts the epoch duration $|E_k|$, the PEP transitions to a `Safe Halt State` denying all actions (simulated via `invalidate_epoch()`). |
| **Pillar 3: PEP in JIT** | Token-generation layer enforcement inside TEE | ✅ **Implemented** | `LogitsMasker` DFA engine implements token-level logits masking (Appendix A). Replaces ASEL as primary enforcement path. |
| **Identity Model** | SPIFFE workload identity + SVID | ⚠️ **Stub** | `WorkloadIdentity` and `SVIDManager` provide structured workload provenance. |
| **GBOM** | Cryptographic audit receipt per decision | ✅ **Implemented** | `GBOMLog` logs decisions with Merkle roots, TEE measurements, and exports in standard NIST OSCAL v1.1.2 JSON. |
| **Formal Verification** | Prove non-compliance is unreachable | ⚠️ **Bounded Only** | Verified via TLA+ to depth 8 (324 distinct states) under a bounded, small-scope configuration. Unbounded verification via inductive invariants (TLAPS) is a future target. |

## Threat Model & Mitigations

| Threat ID | Description | v2 Status / Mitigation |
|:---|:---|:---|
| **T2 - StackWarp Zen 1-5** | CPU stack state leaked via interrupt timing. | Requires AMD guest firmware update schedule (operational control). |
| **T7 - Clock-Skew / NTP Poisoning** | Attacker poisons LWW CRDT state via physical clocks. | **Mitigated**: `CausalPolicyStore` uses vector clocks to establish partial causal ordering, removing physical clock dependencies. |

## Benchmark Interpretation

The SEV-SNP benchmark harness (`bench/sev_snp_benchmark.py`) models expected performance on confidential hardware based on published literature. The overhead of actual PEP verification was measured using `bench/measure_enforcement.py` and is verified to execute in **~15 microseconds** (excluding simulated TEE enter/exit and network latency).

## Future Work

- [ ] Multi-node network partition testing on distributed nodes.
- [ ] Integration with physical Intel TDX / AMD SEV-SNP enclaves.
- [ ] Direct binding to a real LLM tokenizer adapter (vLLM / Hugging Face).
- [ ] TLAPS proof generation for unbounded state space verification.

---
*This document ensures transparency for reviewers and users of the EHV-Runtime artifact.*
