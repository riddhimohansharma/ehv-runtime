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
We use a **Last-Writer-Wins Element-Set (LWW-Element-Set)**. Every policy update is timestamped. This ensures that even in distributed environments with network partitions, all nodes eventually converge on the most recent policy version.

## 3. Sub-millisecond Formal Determinism (SMFD)
To avoid the overhead of a remote attestation check (which can exceed 200ms), EHV implements **Epoch-based Attestation Caching**.
- **Epoch Verification**: Once per epoch (e.g., 60s), the system performs a full hardware attestation and computes a hash of the current policy state.
- **Hot-Path Verification**: For every inference call within the epoch, the system performs a local O(1) hash comparison.

## 4. Formal Verification (TLA+)
The architecture is verified using the **TLA+** specification language. The model checker (TLC) was used to verify a bounded configuration (generating 1,738 states and finding 324 distinct states at a state graph depth of 8) across network partitions and concurrent updates, verifying that the safety invariant $I_g$ holds in all cases.

---
*Back to [README.md](../README.md)*
