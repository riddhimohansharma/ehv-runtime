# Ethical Hyper-Velocity (EHV) Governance Framework

[![arXiv](https://img.shields.io/badge/arXiv-under_review-B31B1B.svg)](https://arxiv.org/abs/2605.17909)
[![Stability: Alpha](https://img.shields.io/badge/stability-alpha-orange.svg)](#)

> A Provably Deterministic
> Governance-Aware JIT Compiler Architecture for Agentic Systems

**Author:** Riddhi Mohan Sharma
**Affiliation:** Independent Researcher, AI Governance &
Healthcare Informatics | Columbia University EPM
**Website:** [riddhimohan.com](https://www.riddhimohan.com)

---

## 📄 Paper

"Ethical Hyper-Velocity (EHV): A Provably Deterministic Governance-Aware JIT Compiler Architecture for Agentic Systems"

- arXiv: [arXiv:2605.17909 \[cs.AI\]](https://arxiv.org/abs/2605.17909) (or `arXiv:2605.17909v1 [cs.AI]` for this version)
- DOI: [10.48550/arXiv.2605.17909](https://doi.org/10.48550/arXiv.2605.17909)
- Blog: [riddhimohan.com/blog/ethical-hyper-velocity-ehv-governance-framework](https://www.riddhimohan.com/blog/ethical-hyper-velocity-ehv-governance-framework)

---

## 🔑 Key Contributions

- **SMFD** — Sub-millisecond Formal Determinism: GL → 0
  asymptotically, bounded by O(1) TEE attestation overhead
- **Policy Enforcement Invariant** — G(a,C) ∈ {PERMIT, DENY,
  ESCALATE} via hardware-rooted cryptographic attestation
- **CRDT Join-Semilattice** — Monotonic Byzantine Fault
  Tolerant policy sync via K-of-N threshold signatures
- **Tiered FSDM** — Fail-Safe Degraded Mode across 3
  clinical severity tiers (NIST SP 800-53 SI-17 aligned)
- **Velocity-Ethics Co-Production** — ∂V/∂I ≥ 0, a sign
  reversal from all existing framework assumptions

---

## 📐 TLA+ Formal Specification

The core safety guarantees of the EHV architecture are formally specified in TLA+:
- **Specification File**: [`EHV.tla`](EHV.tla) (and [`EHV.cfg`](EHV.cfg))
- **Model Checking**: Evaluated using the TLC Model Checker to a depth of 8, exploring 1,738 states (324 distinct states found) with 0 safety or liveness violations.
- **Safety Invariant**: Enforces that no unsafe agentic action can reach a `PERMIT` state under any asynchronous scheduler, network partition, or concurrent update interleaving.

---

## 🏗️ Repository Structure

This repository provides the reference proof-of-concept Python runtime implementing the EHV JIT-PEP enforcement pipeline:

- **[`ehv/`](ehv/)**: Reference implementation packages.
  - **[`ehv/compiler/engine.py`](ehv/compiler/engine.py)**: The JIT Policy Enforcement Point (PEP) decorator enforcer.
  - **[`ehv/sync/store.py`](ehv/sync/store.py)**: Conflict-free Replicated Data Type (CRDT) policy store using physical/logical timestamps.
  - **[`ehv/enclave/enclave.py`](ehv/enclave/enclave.py)**: Simulated Trusted Execution Environment (TEE) for attestation caching.
- **[`examples/`](examples/)**: Clinical dosage validation case studies and latency benchmarks.
- **[`tests/`](tests/)**: Exhaustive pytest unit test suite confirming SMFD, epoch attestation, and fail-closed partition semantics.
- **[`EHV.tla`](EHV.tla)**: TLA+ formal specification of the EHV state machine.

---

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/riddhimohansharma/ehv-runtime.git
cd ehv-runtime
```

### 2. Run the Clinical Dosage Case Study
See how EHV rejects a toxic dosage recommendation in **< 10 microseconds** immediately following a policy update.
```bash
python examples/clinical_dosage.py
```

### 3. Verify Performance (SMFD)
Run the 10,000 iteration benchmark to prove the sub-millisecond enforcement speed.
```bash
python examples/latency_bench.py
```

---

## 📂 Repository Roadmap

- [x] **Enforcement Pattern**: Decorator-based PEP + LWW Policy Store.
- [x] **Formal Verification**: TLA+ specification verified with TLC to depth 8 (0 violations, 324 distinct states) under a bounded configuration.
- [ ] **Multi-Node CRDT**: Distributed policy sync with partition testing.
- [ ] **Hardware Root**: Integration with Intel TDX / AMD SEV-SNP.
- [ ] **ASEL**: Action Schema Extraction Layer for natural language parsing.
- [ ] **LLM Integration**: PEP wrapping a real inference pipeline.

---

## 📚 Research & References

- arXiv Preprint: [arXiv:2605.17909](https://arxiv.org/abs/2605.17909)
- **[Verification Report](REPORT.md)**: View the latest empirical benchmarks.
- **[TLA+ Specification](EHV.tla)**: Inspect the formal safety proofs.
- **[Limitations & Scoping](LIMITATIONS.md)**: Detailed breakdown of PoC vs. full architecture.

---

## 📊 GL Reduction Model

| Architecture | GL | Reduction |
|---|---|---|
| ISO 42001 PDCA | ~2×10⁹ ms | Baseline |
| NIST AI RMF | ~3×10⁸ ms | ~85% |
| EHV Transitional | <60,000 ms | ~99.997% |
| EHV Full (TLA+) | O(1) bounded | ~100% |

---

## 📜 Citation

```bibtex
@misc{sharma2026ehv,
  title={Ethical Hyper-Velocity (EHV): A Provably Deterministic
         Governance-Aware JIT Compiler Architecture for Agentic Systems},
  author={Sharma, Riddhi Mohan},
  year={2026},
  eprint={2605.17909},
  archivePrefix={arXiv},
  primaryClass={cs.AI},
  doi={10.48550/arXiv.2605.17909},
  url={https://arxiv.org/abs/2605.17909}
}
```

---

## 🔖 License

CC BY 4.0 — You may share and adapt with attribution.

---
*Developed by Riddhi Mohan Sharma | [riddhimohan.com](https://riddhimohan.com)*
