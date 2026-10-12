---
ckb_doc: "operations"
title: "Operations"
audience: "engineers, SRE, on-call"
diataxis: "how-to"
source_commit: "26289dcca127c0dbe18e2cbba0fc4b205110441e"
branch: "main"
generator: "codebase-kb-engine 0.9.4"
ckb_version: "0.2"
confidence_scope: "doc"
confidence:
  confirmed: 13
  inferred: 2
  unknown: 0
freshness_cmd: "git diff --quiet 26289dcca127c0dbe18e2cbba0fc4b205110441e HEAD -- . ':(exclude).ckb'"
---
# Operations

## Build

The package is built with setuptools (pyproject.toml:1, pyproject.toml:3) [C]. It targets Python 3.10 or later (pyproject.toml:13) [C]. The core has no dependencies. The optional `bench` extra adds pandas and matplotlib (pyproject.toml:22, pyproject.toml:25) [C]. The exact build and publish commands are not recorded in the repo [?].

## Run locally

Make targets (Makefile:1) [C]:

- `make demo` runs examples/clinical_dosage.py and examples/latency_bench.py (Makefile:6) [C].
- `make gcd_demo` runs examples/gcd_dosage.py (Makefile:10) [C].
- `make bench` runs bench/sev_snp_benchmark.py and bench/measure_enforcement.py with `PYTHONPATH=.`. Outputs go to `bench/output` (Makefile:18, bench/measure_enforcement.py:87) [C].
- The red-team example is run with `python examples/anthropic_redteam.py` and needs `ANTHROPIC_API_KEY` in the environment (examples/anthropic_redteam.py:94) [C].

## Test

- Unit tests: `make unit_test` runs `PYTHONPATH=. pytest tests/` (Makefile:3) [C]. The suite covers engine, gbom, enclave, sync store, gcd, identity, oscal and vclock (tests/test_engine.py:1) [C].
- Experiments: `make test` runs the CRDT, epoch-staleness and GBOM-audit scripts (Makefile:13) [C].
- `make all` chains every target (Makefile:22) [C].
- Formal check: EHV.tla with EHV.cfg is for TLC. The invocation is not documented (EHV.cfg:1) [?].

## Deploy and environments

Not applicable — this is a library with no deployable service or environment definitions, and no CI or IaC was found [?]. Distribution is by package name `ehv-runtime` (pyproject.toml:6) [C]. The publish process is unobserved [?].

## Observability

- The GBOM log is the audit trail. It is hash-chained, can be verified with `verify_chain`, and is exported as OSCAL JSON to a file (ehv/compiler/gbom.py:125, experiments/gbom_audit.py:38) [C].
- The benchmarks write latency CSVs, plots and summaries (bench/measure_enforcement.py:117) [C].
- No metrics, tracing or logging endpoints were found [?].

## Alerts and failure modes

- Invalid or unreachable epoch attestation: every action is denied and a `GovernanceError` is raised (ehv/compiler/engine.py:131) [C].
- Falsy constraint: DENY. A constraint exception is logged as ESCALATE and re-raised (ehv/compiler/engine.py:141) [C].
- Stale or partitioned epoch: the example expects rejection once the 60s epoch has expired (examples/anthropic_redteam.py:234) [I].
- Expired or revoked SVID is invalid (ehv/identity/workload.py:43) [C].
- No alerting integration exists [?].

## Rollback

Not applicable — there is no deployed service. Roll back by pinning the previous package version (the current one is 0.3.0) [?] (pyproject.toml:7) [C]. Enclave shared memory (`ehv_enclave_mem`) is a local file artifact that can be removed (ehv/enclave/enclave.py:20) [I].
