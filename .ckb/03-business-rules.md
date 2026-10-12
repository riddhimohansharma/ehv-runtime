---
ckb_doc: "business-rules"
title: "Business rules"
audience: "product, engineers, QA, compliance"
diataxis: "reference"
source_commit: "26289dcca127c0dbe18e2cbba0fc4b205110441e"
branch: "main"
generator: "codebase-kb-engine 0.9.4"
ckb_version: "0.2"
confidence_scope: "doc"
confidence:
  confirmed: 10
  inferred: 5
  unknown: 0
freshness_cmd: "git diff --quiet 26289dcca127c0dbe18e2cbba0fc4b205110441e HEAD -- . ':(exclude).ckb'"
---
# Business Rules

## Rule catalog

<a id="business-rule-unsafe-action-never-permitted"></a>
### Unsafe action never permitted
`ckb:business_rule:unsafe-action-never-permitted`
- **ID:** BR-unsafe-action-never-permitted
- **Statement:** No unsafe action may reach PERMIT enforcement status (TLA+ SafetyInvariant).
- **Rationale:** Core safety property of the formal model. [I]
- **Trigger:** Any action submitted in the formal model.
- **Outcome:** Unsafe actions never reach PERMIT.
- **Exceptions:** None observed. [?]
- **Enforced at:** EHV.tla:46 [C]
- **Confidence:** [C]

<a id="business-rule-invalid-epoch-denies-by-default"></a>
### Invalid epoch denies by default
`ckb:business_rule:invalid-epoch-denies-by-default`
- **ID:** BR-invalid-epoch-denies-by-default
- **Statement:** If the policy epoch is not valid, enforcement is DENY; with a valid epoch safe is PERMIT, unsafe is DENY, others are ESCALATE.
- **Rationale:** Fail-safe default. [I]
- **Trigger:** Enforce step in the formal model.
- **Outcome:** DENY / PERMIT / ESCALATE by epoch validity and action class.
- **Exceptions:** None observed. [?]
- **Enforced at:** EHV.tla:77 [C]
- **Confidence:** [C]

<a id="business-rule-benchmark-limit-constraint"></a>
### Benchmark limit constraint
`ckb:business_rule:benchmark-limit-constraint`
- **ID:** BR-benchmark-limit-constraint
- **Statement:** Benchmark constraint permits an action only when val <= policies['limit'] (limit=10.0); violations raise GovernanceError (DENY); constraint exceptions are ESCALATE.
- **Rationale:** Exercises all three outcomes for latency measurement. [I]
- **Trigger:** `python bench/measure_enforcement.py`
- **Outcome:** DENY via GovernanceError, or ESCALATE on exception.
- **Exceptions:** None observed. [?]
- **Enforced at:** bench/measure_enforcement.py:16, bench/measure_enforcement.py:19 [I]
- **Confidence:** [I]

<a id="business-rule-epoch-re-attestation"></a>
### Epoch re-attestation
`ckb:business_rule:epoch-re-attestation`
- **ID:** BR-epoch-re-attestation
- **Statement:** Re-attest when epoch_duration (default 60s) has elapsed, on first run, or when the policy hash differs from the enclave hash.
- **Rationale:** Bounds how long stale policy can be trusted. [I]
- **Trigger:** Any decorated call.
- **Outcome:** Enclave attestation is refreshed before evaluation.
- **Exceptions:** None observed. [?]
- **Enforced at:** ehv/compiler/engine.py:58 [C]
- **Confidence:** [C]

<a id="business-rule-fail-closed-on-invalid-epoch"></a>
### Fail-closed on invalid epoch
`ckb:business_rule:fail-closed-on-invalid-epoch`
- **ID:** BR-fail-closed-on-invalid-epoch
- **Statement:** If epoch attestation is invalid or unreachable, all actions are DENIED and a GovernanceError is raised regardless of constraint result.
- **Rationale:** Never permit on unverified policy. [I]
- **Trigger:** EHVEngine.enforce wrapped call.
- **Outcome:** GovernanceError; action not run.
- **Exceptions:** None observed. [?]
- **Enforced at:** ehv/compiler/engine.py:131 [C]
- **Confidence:** [C]

<a id="business-rule-constraint-must-pass"></a>
### Constraint must pass
`ckb:business_rule:constraint-must-pass`
- **ID:** BR-constraint-must-pass
- **Statement:** The action runs only if constraint_func(policies,*args) is truthy; falsy raises GovernanceError (DENY); an exception is logged ESCALATE and re-raised.
- **Rationale:** Policy decision point semantics. [I]
- **Trigger:** EHVEngine.enforce wrapped call.
- **Outcome:** PERMIT runs action; DENY or ESCALATE raises.
- **Exceptions:** None observed. [?]
- **Enforced at:** ehv/compiler/engine.py:141, ehv/compiler/engine.py:149 [C]
- **Confidence:** [C]

<a id="business-rule-vincristine-dose-cap"></a>
### Vincristine dose cap
`ckb:business_rule:vincristine-dose-cap`
- **ID:** BR-vincristine-dose-cap
- **Statement:** The grammar permits only `administer <dose> Vincristine IV` with dose <= max_dose (default 1.5); other tokens are masked to -inf.
- **Rationale:** Prevents unsafe tokens at decode time. [I]
- **Trigger:** mask_logits during decoding.
- **Outcome:** Disallowed tokens get -inf logits.
- **Exceptions:** None observed. [?]
- **Enforced at:** ehv/gcd/grammar.py:21 [C]
- **Confidence:** [C]

<a id="business-rule-svid-validity"></a>
### SVID validity
`ckb:business_rule:svid-validity`
- **ID:** BR-svid-validity
- **Statement:** An SVID is valid only if not revoked and within TTL (default 3600s).
- **Rationale:** Workload identity freshness. [I]
- **Trigger:** SVID validation.
- **Outcome:** Invalid SVIDs rejected.
- **Exceptions:** None observed. [?]
- **Enforced at:** ehv/identity/workload.py:43, ehv/identity/workload.py:45 [C]
- **Confidence:** [C]

<a id="business-rule-lww-policy-update"></a>
### LWW policy update
`ckb:business_rule:lww-policy-update`
- **ID:** BR-lww-policy-update
- **Statement:** PolicyStore rejects updates with timestamp <= existing; merge ties are broken by lexicographic value; CausalPolicyStore uses vector clocks.
- **Rationale:** Deterministic convergence. [I]
- **Trigger:** Policy update or merge.
- **Outcome:** Stale update rejected.
- **Exceptions:** Vector clock detail in ehv/sync/vclock.py not scanned. [?]
- **Enforced at:** ehv/sync/store.py:28 [C]
- **Confidence:** [C]

<a id="business-rule-fail-closed-on-stale-attestation"></a>
### Fail-closed on stale attestation
`ckb:business_rule:fail-closed-on-stale-attestation`
- **ID:** BR-fail-closed-on-stale-attestation
- **Statement:** If the attestation epoch (60s) is expired and the enclave is partitioned, execution is rejected.
- **Rationale:** Demonstrates fail-closed behavior. [I]
- **Trigger:** Red-team example run.
- **Outcome:** Execution rejected.
- **Exceptions:** None observed. [?]
- **Enforced at:** examples/anthropic_redteam.py:234, examples/anthropic_redteam.py:242 [I]
- **Confidence:** [I]

<a id="business-rule-drug-dosage-limit"></a>
### Drug dosage limit
`ckb:business_rule:drug-dosage-limit`
- **ID:** BR-drug-dosage-limit
- **Statement:** Prescription amount must not exceed policy limit_<drug> (Vincristine 1.5 mg/m2, later 0.75); no limit means allowed. Enforced by the @enforce decorator.
- **Rationale:** Clinical safety demo. [I]
- **Trigger:** prescribe call.
- **Outcome:** Over-limit raises GovernanceError.
- **Exceptions:** Missing limit allows the action. [C]
- **Enforced at:** examples/clinical_dosage.py:11, examples/anthropic_redteam.py:130 [C]
- **Confidence:** [C]

<a id="business-rule-policy-store-converges-by-last-writer-wins-timestamp"></a>
### Policy store converges by last-writer-wins timestamp
`ckb:business_rule:policy-store-converges-by-last-writer-wins-timestamp`
- **ID:** BR-policy-store-converges-by-last-writer-wins-timestamp
- **Statement:** After partition recovery nodes must hold identical LWW state.
- **Rationale:** Experiment assertion. [I]
- **Trigger:** Recovery in the CRDT experiment.
- **Outcome:** has_converged is true.
- **Exceptions:** None observed. [?]
- **Enforced at:** experiments/crdt_convergence.py:53 [I]
- **Confidence:** [I]

<a id="business-rule-epoch-staleness-window-bounded-by-min-epoch-duration-partition-duration-policy-hash-mismatch-triggers-re-attestation-emergency-epoch-reset-forces-immediate-enforcement"></a>
### Epoch Staleness Window bounded by min(epoch_duration, partition_duration); policy hash mismatch triggers re-attestation; emergency_epoch_reset forces immediate enforcement
`ckb:business_rule:epoch-staleness-window-bounded-by-min-epoch-duration-partition-duration-policy-hash-mismatch-triggers-re-attestation-emergency-epoch-reset-forces-immediate-enforcement`
- **ID:** BR-epoch-staleness-window
- **Statement:** Staleness window is bounded by min(epoch_duration, partition_duration); a hash mismatch triggers re-attestation; emergency_epoch_reset forces immediate enforcement.
- **Rationale:** Asserted by experiment narrative. [I]
- **Trigger:** Epoch staleness experiment.
- **Outcome:** Stale remote permits within window; deny after merge or reset.
- **Exceptions:** None observed. [?]
- **Enforced at:** experiments/epoch_staleness.py:141, experiments/epoch_staleness.py:123 [I]
- **Confidence:** [I]

<a id="business-rule-dosage-limit-enforced-via-ehvengine-enforce"></a>
### Dosage limit enforced via EHVEngine.enforce
`ckb:business_rule:dosage-limit-enforced-via-ehvengine-enforce`
- **ID:** BR-dosage-limit-enforced-via-ehvengine-enforce
- **Statement:** dose <= policy 'limit' (or limit_<drug>, default 10.0); violation raises GovernanceError.
- **Rationale:** Experiment fixture policy. [I]
- **Trigger:** Experiment scripts.
- **Outcome:** GovernanceError on violation.
- **Exceptions:** None observed. [?]
- **Enforced at:** experiments/gbom_audit.py:12, experiments/epoch_staleness.py:30 [C]
- **Confidence:** [C]

<a id="business-rule-gbom-log-is-a-tamper-evident-hash-chain-verified-by-verify-chain"></a>
### GBOM log is a tamper-evident hash chain, verified by verify_chain
`ckb:business_rule:gbom-log-is-a-tamper-evident-hash-chain-verified-by-verify-chain`
- **ID:** BR-gbom-log-hash-chain
- **Statement:** The GBOM log is a tamper-evident hash chain verified by verify_chain; permitted and denied actions are both logged.
- **Rationale:** Audit integrity. [I]
- **Trigger:** GBOM audit experiment.
- **Outcome:** verify_chain succeeds on an untampered log.
- **Exceptions:** None observed. [?]
- **Enforced at:** experiments/gbom_audit.py:38 [I]
- **Confidence:** [I]

## Traceability

Tests live in tests/test_engine.py and siblings; per-rule mapping was not scanned. [?]

| Rule | Enforced at | Tests | Confidence |
|---|---|---|---|
| Unsafe action never permitted | EHV.tla:46 | none (TLC model) [?] | [C] |
| Invalid epoch denies by default | EHV.tla:77 | none (TLC model) [?] | [C] |
| Benchmark limit constraint | bench/measure_enforcement.py:16 | [?] | [I] |
| Epoch re-attestation | ehv/compiler/engine.py:58 | [?] | [C] |
| Fail-closed on invalid epoch | ehv/compiler/engine.py:131 | [?] | [C] |
| Constraint must pass | ehv/compiler/engine.py:141 | [?] | [C] |
| Vincristine dose cap | ehv/gcd/grammar.py:21 | [?] | [C] |
| SVID validity | ehv/identity/workload.py:43 | [?] | [C] |
| LWW policy update | ehv/sync/store.py:28 | [?] | [C] |
| Fail-closed on stale attestation | examples/anthropic_redteam.py:234 | [?] | [I] |
| Drug dosage limit | examples/clinical_dosage.py:11 | [?] | [C] |
| Policy store converges by last-writer-wins timestamp | experiments/crdt_convergence.py:53 | [?] | [I] |
| Epoch Staleness Window bounded by min(epoch_duration, partition_duration); policy hash mismatch triggers re-attestation; emergency_epoch_reset forces immediate enforcement | experiments/epoch_staleness.py:141 | [?] | [I] |
| Dosage limit enforced via EHVEngine.enforce | experiments/gbom_audit.py:12 | [?] | [C] |
| GBOM log is a tamper-evident hash chain, verified by verify_chain | experiments/gbom_audit.py:38 | [?] | [I] |
