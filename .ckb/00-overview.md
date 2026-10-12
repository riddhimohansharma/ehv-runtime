---
ckb_doc: "overview"
title: "Overview"
audience: "everyone: new engineers, product, leadership"
diataxis: "explanation"
source_commit: "26289dcca127c0dbe18e2cbba0fc4b205110441e"
branch: "main"
generator: "codebase-kb-engine 0.9.4"
ckb_version: "0.2"
confidence_scope: "doc"
confidence:
  confirmed: 19
  inferred: 0
  unknown: 0
freshness_cmd: "git diff --quiet 26289dcca127c0dbe18e2cbba0fc4b205110441e HEAD -- . ':(exclude).ckb'"
---
# EHV Runtime Overview

## Elevator pitch

ehv-runtime is a Python library (version 0.3.0) implementing Ethical Hyper-Velocity: a policy enforcement point that permits, denies or escalates agent actions, backed by a simulated enclave, CRDT policy sync, grammar-constrained decoding and a hash-chained audit log (pyproject.toml:6) [C]

## Executive summary

- Library package `ehv` with five modules: compiler, enclave, gcd, identity, sync (ehv/__init__.py:1) [C]
- Decorator `EHVEngine.enforce` fails closed when epoch attestation is invalid (ehv/compiler/engine.py:131) [C]
- A TLA+ model states the safety invariant that unsafe actions are never permitted (EHV.tla:46) [C]
- The enclave is simulated, with a hardcoded root key (ehv/enclave/enclave.py:24) [C]
- bench, examples and experiments are demo scripts; no servers or routes exist [I]

## Stakeholders and users

- Owner: Riddhi Mohan Sharma (pyproject.toml:6) [C]
- Agent developers embedding the decorator [I]
- Researchers using benchmarks and experiments [I]

## Quality goals

- Safety: fail-closed enforcement (ehv/compiler/engine.py:131) [C]
- Auditability: GBOM hash chain (ehv/compiler/gbom.py:125) [C]
- Convergence under partition (ehv/sync/store.py:28) [C]
- Low enforcement latency, measured by bench/measure_enforcement.py:122 [C]

## Glossary

| Term | Meaning | Source |
|---|---|---|
| PEP | Policy enforcement point, the enforce decorator | ehv/compiler/engine.py:113 [C] |
| GBOM | Governance bill of materials, hash-chained audit log | ehv/compiler/gbom.py:125 [C] |
| Epoch | Attestation window, default 60s | ehv/compiler/engine.py:58 [C] |
| SVID | SPIFFE workload identity document | ehv/identity/workload.py:25 [C] |
| GCD | Grammar-constrained decoding | ehv/gcd/masker.py:23 [C] |
| LWW | Last-writer-wins policy merge | ehv/sync/store.py:28 [C] |
| ESCALATE | Third outcome besides PERMIT and DENY | EHV.tla:77 [C] |

## Macro context

Part of the wider EHV project. It needs real TEE hardware (SEV-SNP latency is only synthetic, bench/sev_snp_benchmark.py:25) and an agent framework to call it. [I]

## How to read this KB

Legend: [C] confirmed in code, [I] inferred, [?] unknown.
- 01-technical-architecture.md: containers, components, data, config.
- 02-functional-workflows.md: end-to-end flows.
- 03-business-rules.md: rule catalog.
- 04-system-context-and-gaps.md: context, risks, open questions.
- 09-reference.md: generated tables of all entities.
