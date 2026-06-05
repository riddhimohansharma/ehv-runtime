# EHV Empirical Verification Report

**Date**: 2026-05-30
**Artifact Version**: v2.0.0
**Environment**: macOS (aarch64), Python 3.12, AMD SEV-SNP (Modelled)

## 📋 Executive Summary
This report documents the empirical verification of **Sub-millisecond Formal Constraints (SMFD)** using the EHV reference implementation. The results confirm that token-level Grammar-Constrained Decoding (GCD) logits masking and policy enforcement add negligible overhead while ensuring 100% compliance.

## 🔬 Experiment 1: Clinical Safety Invariant (GCD)
**Scenario**: Pediatric Oncology Vincristine Dosage (FDA PCCP Update).
The JIT compiler applies a compiled DFA grammar to restrict token generation.

| Event | Action / Input Sequence | Outcome | Latency (GL) |
|:---|:---|:---|:---|
| Baseline | Prescribe 1.0 mg/m2 (Limit: 1.5) | **PERMIT** | ~0.016 ms |
| Policy Update | Limit changed to 0.75 mg/m2 | **SYNCED** | < 1s (Causal CRDT) |
| Post-Update | Generate "1.5" (Unsafe) | **MASKED** | Token logit set to $-\infty$ |
| Post-Update | Prescribe 1.0 mg/m2 | **DENIED** | **~0.015 ms** |

**Conclusion**: The safety invariant was enforced at the token level before sampling and validated at the JIT PEP wrapper. Non-compliant actions were unreachable in the verified bounded model.

## 📊 Experiment 2: Enforcement Overhead (10,000 Iterations)
Measured execution overhead of the JIT PEP decorator using `bench/measure_enforcement.py`.

| Metric | PERMIT | DENY | ESCALATE |
|:---|:---|:---|:---|
| **Mean** | 0.0153 ms | 0.0161 ms | 0.0173 ms |
| **Median** | 0.0145 ms | 0.0153 ms | 0.0160 ms |
| **P95** | 0.0181 ms | 0.0192 ms | 0.0218 ms |
| **P99** | 0.0275 ms | 0.0271 ms | 0.0323 ms |

**Threshold**: < 1.000 ms  
**Status**: **PASSED** (Actual PEP overhead is < 0.035 ms in all percentiles).

## 🚀 Experiment 3: SEV-SNP Simulated Pipeline Performance
Modeled end-to-end token generation performance under five workload scenarios (using `bench/sev_snp_benchmark.py`).

| Scenario | Description | Baseline | GCD Mask | Attestation | Update | Total Latency | Throughput |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **W1** | Safe Permit | 0.375 ms | 0.115 ms | 0.157 ms | 0.019 ms | **0.666 ms** | 1501.24 tok/s |
| **W2** | Unsafe Deny | 0.362 ms | 0.118 ms | 0.196 ms | 0.021 ms | **0.697 ms** | 1434.43 tok/s |
| **W3** | Escalate | 0.400 ms | 0.133 ms | 0.206 ms | 0.031 ms | **0.769 ms** | 1300.12 tok/s |
| **W4** | Policy Update | 0.348 ms | 0.160 ms | 0.250 ms | 0.042 ms | **0.800 ms** | 1249.49 tok/s |
| **W5** | Partition | 0.348 ms | 0.138 ms | 0.260 ms | 0.048 ms | **0.793 ms** | 1260.60 tok/s |

- **Mean Total Latency**: 0.7452 ms
- **P95 Total Latency**: 0.7989 ms
- **Mean Throughput**: 1349.18 tokens/sec

### Visual Performance Analysis
Here are the simulated latency and throughput profiles across all five workload scenarios:

![Latency Projections](bench/output/latency_plot.png)
![Throughput Projections](bench/output/throughput_plot.png)

## 🧠 Formal Methods Alignment
The execution path observed in these experiments aligns 100% with the **TLA+ model checking results** (1,738 states generated, 324 distinct states found, 0 violations at depth 8). The `EHV.tla` specification correctly predicted the "Deny-on-Update" behavior observed in the Clinical Safety experiment.

---
*Verified by EHV Governance Engine | Riddhi Mohan Sharma*
