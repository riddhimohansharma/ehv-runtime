# EHV-Runtime Architecture

This document provides a technical deep-dive into the EHV-Runtime implementation.

## 1. The Policy Enforcement Point (PEP)
The PEP is implemented as a high-performance Python decorator that wraps agentic functions. It intercepts the call *before* the function logic executes, evaluates the active policy state, and either PERMITs or DENYs the action.

```python
@runtime.enforce(dosage_constraint)
def prescribe_medication(drug, amount):
    # This logic only runs if dosage_constraint returns True
    pass
```

## 2. Policy Synchronization (CRDT)
We use a **CausalPolicyStore** backed by **Vector Clocks**. Every policy update carries a vector clock rather than a physical timestamp. This ensures that even in distributed environments with network partitions, all nodes eventually converge on the most recent policy version while preserving causal ordering (mitigating clock skew vulnerabilities).

## 3. Sub-millisecond Formal Determinism (SMFD)
To avoid the overhead of a remote attestation check (which can exceed 200ms), EHV implements **Epoch-based Attestation Caching**.
- **Epoch Verification**: Once per epoch (e.g., 60s), the system performs a full hardware attestation and computes a hash of the current policy state.
- **Hot-Path Verification**: For every inference call within the epoch, the system performs a local O(1) hash comparison.

## 4. Formal Verification (TLA+)
The architecture is verified using the **TLA+** specification language. The model checker (TLC) was used to verify a bounded configuration (generating 1,738 states and finding 324 distinct states at a state graph depth of 8) across network partitions and concurrent updates, verifying that the safety invariant $I_g$ holds in all cases.

## 5. Grammar-Constrained Decoding (GCD)
GCD is the primary enforcement mechanism for LLM workloads. By compiling clinical governance constraints into a Deterministic Finite Automaton (DFA), GCD masks the output logits of the LLM before sampling occurs. This formally bounds the generation space, ensuring the model can only generate syntactically and semantically compliant actions (e.g., valid clinical dosages).

## 6. Workload Identity (SPIFFE)
The identity model aligns with the SPIFFE framework. Workloads are issued short-lived SVIDs (SPIFFE Verifiable Identity Documents) within a designated trust domain. This mitigates unauthorized escalation (T3) and spoofing by tying actions strictly to validated workload identities with bounded TTLs.

## 7. OSCAL GBOM Export
To support continuous compliance and automated audits, the runtime exports its Governance Bill of Materials (GBOM) in NIST OSCAL v1.1.2 format. This cryptographically binds the enforcement result, epoch ID, active policy version, and TEE attestation measurement into a machine-readable `assessment-results` artifact.

---
*Back to [README.md](../README.md)*
