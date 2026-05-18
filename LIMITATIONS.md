# EHV-Runtime: Scope & Limitations

> This document explicitly scopes what the EHV-Runtime **does** and **does not** implement relative to the full EHV architecture described in the [paper](https://arxiv.org/abs/2605.xxxxx).

## What This Repository Is

EHV-Runtime is a **proof-of-concept** demonstrating the EHV enforcement pattern: decorator-based policy enforcement with CRDT-inspired policy synchronization. It validates the **control flow** of the Governance-Aware JIT architecture.

## Implementation Status

| Paper Pillar | Claim | Runtime Status | Notes |
|:---|:---|:---|:---|
| **Pillar 1: CRDT Policy Sync** | LWW-Element-Set with distributed multi-node convergence | ⚠️ **Partial** | Single-node `PolicyStore` with LWW timestamps. No multi-node distribution or network partition testing. |
| **Pillar 2: TEE Attestation Caching** | Hardware-rooted TEE with epoch-based attestation | ⚠️ **Simulated** | Epoch check via `time.time()` comparison. No real TEE (Intel SGX/TDX, AMD SEV-SNP) integration. |
| **Pillar 3: PEP in JIT** | Token-generation layer enforcement inside TEE | ⚠️ **Pattern Only** | Python decorator wrapping function calls. No JIT compilation, no token-level interception. |
| **ASEL** | Structured action extraction from LLM output | ❌ **Not Implemented** | Examples use pre-structured function arguments. |
| **GBOM** | Cryptographic audit receipt per decision | ❌ **Not Implemented** | Future work. |
| **Formal Verification** | Prove non-compliance is unreachable | ⚠️ **Bounded Only** | Verified via TLA+ to depth 8 (324 distinct states) under a bounded, small-scope configuration. Unbounded verification via inductive invariants (TLAPS) is a Phase 2 target. |

## Threat Model & Vulnerabilities

| Threat ID | Description | Phase 2 Mitigation |
|:---|:---|:---|
| **T7 - Clock-Skew / NTP Poisoning** | An attacker with root access on an edge node can forge future timestamps to poison the global policy state in the LWW CRDT. | Migration from physical timestamps to a cryptographically signed causal DAG (vector clocks). |

## Benchmark Interpretation

The latency numbers reported by `examples/latency_bench.py` measure **Python function-call overhead** of the enforcement decorator pattern. They demonstrate that the enforcement pattern adds negligible computational cost (~1μs). They do **not** constitute a measurement of governance enforcement latency in a production TEE or LLM inference pipeline.

Results vary by ±30% across runs due to OS scheduling jitter and thermal state.

## Future Work

- [ ] Multi-node CRDT with network partition simulation
- [ ] Integration with Intel TDX / AMD SEV-SNP for real TEE attestation
- [ ] Integration with a real LLM inference pipeline (e.g., vLLM, Ollama)
- [ ] ASEL implementation for clinical language parsing
- [ ] GBOM cryptographic receipt generation
- [ ] Concurrent multi-agent modeling and conflict testing

---
*This document ensures transparency for reviewers and users of the EHV-Runtime artifact.*
