---
ckb_doc: "functional-workflows"
title: "Functional workflows"
audience: "engineers, product, QA"
diataxis: "explanation"
source_commit: "26289dcca127c0dbe18e2cbba0fc4b205110441e"
branch: "main"
generator: "codebase-kb-engine 0.9.4"
ckb_version: "0.2"
confidence_scope: "doc"
confidence:
  confirmed: 23
  inferred: 8
  unknown: 0
freshness_cmd: "git diff --quiet 26289dcca127c0dbe18e2cbba0fc4b205110441e HEAD -- . ':(exclude).ckb'"
---
# Functional Workflows

## Actors

- Agent or application developer: decorates functions with the policy enforcement point. [I]
- Researcher: runs bench, experiments and examples scripts (bench/measure_enforcement.py:122, experiments/gbom_audit.py:20) [C]
- LLM (Anthropic API): proposes tool calls in the red-team example (examples/anthropic_redteam.py:97) [I]
- Verifier: runs the TLC model checker over EHV.tla (EHV.tla:46) [I]

## Capabilities

- Enforce PERMIT, DENY or ESCALATE on decorated calls (ehv/compiler/engine.py:113) [C]
- Attest policy epochs through a simulated enclave (ehv/enclave/enclave.py:8) [C]
- Converge policy across nodes by LWW or vector clocks (ehv/sync/store.py:28) [C]
- Mask logits by grammar-constrained decoding (ehv/gcd/masker.py:23) [C]
- Record a hash-chained GBOM audit log (ehv/compiler/gbom.py:125) [C]
- Measure enforcement latency (bench/measure_enforcement.py:122) [C]

## Workflows

<a id="workflow-action-enforcement-formal-model"></a>
### Action enforcement (formal model)
`ckb:workflow:action-enforcement-formal-model`
- **Trigger:** agent submits action. Inputs: action class, epoch validity. Outputs: PERMIT, DENY or ESCALATE.

```mermaid
sequenceDiagram
  participant agent
  participant ehv_tla
  agent->>ehv_tla: SubmitAction
  ehv_tla-->>ehv_tla: Enforce by epoch and class
  ehv_tla-->>agent: PERMIT/DENY/ESCALATE
  agent-->>ehv_tla: CompleteAction
```
Source: EHV.tla:70 [I]

1. SubmitAction records the action. [I]
2. Enforce picks the status from epoch validity and action class (EHV.tla:77) [C]
3. CompleteAction resets state. [I]

<a id="workflow-measure-pep-enforcement-latency"></a>
### Measure PEP enforcement latency
`ckb:workflow:measure-pep-enforcement-latency`
- **Trigger:** `python bench/measure_enforcement.py`. Output: actual_enforcement_latency.csv.

```mermaid
sequenceDiagram
  participant researcher
  participant bench_measure
  participant bench_output
  researcher->>bench_measure: run script
  bench_measure->>bench_measure: 10000 PERMIT, DENY, ESCALATE calls
  bench_measure->>bench_output: write csv
```
Source: bench/measure_enforcement.py:9 [C]

1. Build PolicyStore, Enclave, GBOMLog, EHVEngine (bench/measure_enforcement.py:122) [C]
2. Time 10000 calls per outcome. [C]
3. Write the CSV under bench/output (bench/measure_enforcement.py:87) [C]

<a id="workflow-synthetic-sev-snp-latency-projection"></a>
### Synthetic SEV-SNP latency projection
`ckb:workflow:synthetic-sev-snp-latency-projection`
- **Trigger:** `python bench/sev_snp_benchmark.py`. Output: CSVs, plots, summary.

```mermaid
sequenceDiagram
  participant researcher
  participant bench_sev
  participant bench_output
  researcher->>bench_sev: run script
  bench_sev->>bench_sev: seeded Gaussian latency per scenario
  bench_sev->>bench_output: write csv, plots, summary
```
Source: bench/sev_snp_benchmark.py:25 [C]

1. Generate seeded Gaussian latency per scenario (bench/sev_snp_benchmark.py:25) [C]
2. Write outputs to bench/output (bench/sev_snp_benchmark.py:13) [C]

Values are synthetic, not measured on SEV-SNP hardware. [I]

<a id="workflow-governed-action-enforcement"></a>
### Governed action enforcement
`ckb:workflow:governed-action-enforcement`
- **Trigger:** call of a function decorated with EHVEngine.enforce. Output: action result or GovernanceError.

```mermaid
sequenceDiagram
  participant caller
  participant ehv_compiler
  participant ehv_enclave
  participant ehv_sync
  caller->>ehv_compiler: decorated call
  ehv_compiler->>ehv_enclave: verify or attest epoch
  ehv_compiler->>ehv_sync: read policies
  ehv_compiler-->>ehv_compiler: constraint DENY/ESCALATE/PERMIT
  ehv_compiler-->>ehv_compiler: append GBOM entry
  ehv_compiler-->>caller: result or GovernanceError
```
Source: ehv/compiler/engine.py:113 [C]

1. Verify epoch, or attest via enclave (ehv/compiler/engine.py:58) [C]
2. Read policies from the store (ehv/compiler/engine.py:5) [C]
3. Evaluate the constraint (ehv/compiler/engine.py:141) [C]
4. Append a hash-chained GBOM entry (ehv/compiler/gbom.py:127) [C]

<a id="workflow-red-team-agent-tool-call-enforcement"></a>
### Red-team agent tool call enforcement
`ckb:workflow:red-team-agent-tool-call-enforcement`
- **Trigger:** `python examples/anthropic_redteam.py`. Requires ANTHROPIC_API_KEY (examples/anthropic_redteam.py:94) [C]

```mermaid
sequenceDiagram
  participant redteam_script
  participant anthropic_api
  participant dosage_policy
  redteam_script->>anthropic_api: messages.create
  anthropic_api-->>redteam_script: tool_use prescribe_medication
  redteam_script->>dosage_policy: PEP dosage check
  dosage_policy-->>redteam_script: PERMIT or GovernanceError
```
Source: examples/anthropic_redteam.py:144 [I]

1. LLM returns tool_use (examples/anthropic_redteam.py:157) [I]
2. Decorator checks dosage policy (examples/anthropic_redteam.py:130) [C]
3. Attestation fail-closed check (examples/anthropic_redteam.py:234) [I]

<a id="workflow-crdt-partition-recovery-convergence"></a>
### CRDT partition/recovery convergence
`ckb:workflow:crdt-partition-recovery-convergence`
- **Trigger:** run experiments/crdt_convergence.py.

```mermaid
sequenceDiagram
  participant experiment
  participant node_a
  participant node_b
  experiment->>node_a: partition and update
  experiment->>node_b: partition and update
  experiment->>node_a: recover and propagate
  experiment->>node_b: has_converged
```
Source: experiments/crdt_convergence.py:15 [C]

1. Register two PolicyStore nodes, partition, update independently. [C]
2. Queue propagation, recover, check has_converged (experiments/crdt_convergence.py:53) [C]

<a id="workflow-epoch-staleness-scenarios"></a>
### Epoch staleness scenarios
`ckb:workflow:epoch-staleness-scenarios`
- **Trigger:** run experiments/epoch_staleness.py.

```mermaid
sequenceDiagram
  participant experiment
  participant ehv_engine
  experiment->>ehv_engine: local update, hash mismatch
  ehv_engine-->>experiment: deny
  experiment->>ehv_engine: partitioned remote stale
  ehv_engine-->>experiment: permit
  experiment->>ehv_engine: merge, then emergency_epoch_reset
  ehv_engine-->>experiment: deny
```
Source: experiments/epoch_staleness.py:19 [C]

1. Local update causes hash mismatch, so deny. [C]
2. Partitioned remote with a stale epoch permits. [C]
3. Merge then deny; emergency_epoch_reset deny (experiments/epoch_staleness.py:123) [C]

<a id="workflow-gbom-audit-trail"></a>
### GBOM audit trail
`ckb:workflow:gbom-audit-trail`
- **Trigger:** run experiments/gbom_audit.py.

```mermaid
sequenceDiagram
  participant experiment
  participant gbom_log
  experiment->>gbom_log: permit two prescriptions
  experiment->>gbom_log: denied prescription
  experiment->>gbom_log: verify_chain
  experiment->>gbom_log: to_json
```
Source: experiments/gbom_audit.py:23 [C]

1. Set policy, permit two prescriptions, deny one. [C]
2. verify_chain, then dump to_json (experiments/gbom_audit.py:38) [C]

## State machines

Enforcement status is one of PERMIT, DENY, ESCALATE (EHV.tla:77) [C]. Epoch state: valid, expired, re-attested after duration or hash mismatch (ehv/compiler/engine.py:58) [C]. SVID: valid until revoked or TTL expiry (ehv/identity/workload.py:43) [C].

## Error and edge handling

- Constraint exception: logged ESCALATE and re-raised (ehv/compiler/engine.py:141) [C]
- Invalid or unreachable attestation: GovernanceError (ehv/compiler/engine.py:131) [C]
- Stale LWW update ignored (ehv/sync/store.py:28) [C]
- Partitioned stale permits within the window (experiments/epoch_staleness.py:141) [I]
