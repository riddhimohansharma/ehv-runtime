---
ckb_doc: "reference"
title: "Generated reference"
audience: "engineers, tooling"
diataxis: "reference"
source_commit: "26289dcca127c0dbe18e2cbba0fc4b205110441e"
branch: "main"
generator: "codebase-kb-engine 0.9.4"
ckb_version: "0.2"
confidence_scope: "global"
confidence:
  confirmed: 61
  inferred: 24
  unknown: 0
freshness_cmd: "git diff --quiet 26289dcca127c0dbe18e2cbba0fc4b205110441e HEAD -- . ':(exclude).ckb'"
---
# Generated reference

Generated from `ckb.json` by `scripts/reference.sh`. Do not edit by hand. Tags: [C] confirmed, [I] inferred, [?] unknown.

## Interfaces

| ID | Kind | Role | Detail | Service | Name | Conf | Source |
|---|---|---|---|---|---|---|---|
| `interface:cli:provides:{"name":"run_actual_benchmarks"}` | cli | provides | {"name":"run_actual_benchmarks"} | - | measure_enforcement.py | [C] | bench/measure_enforcement.py:122 |
| `interface:cli:provides:{"name":"sev_snp_benchmark"}` | cli | provides | {"name":"sev_snp_benchmark"} | - | sev_snp_benchmark.py | [I] | bench/sev_snp_benchmark.py:1 |
| `interface:http:consumes:api.anthropic.com:POST:/v1/messages` | http | consumes | POST /v1/messages @api.anthropic.com | - | Anthropic Messages API (messages.create) | [I] | examples/anthropic_redteam.py:97 (+1) |
| `interface:library:provides:{"name":"ehv.compiler.engine.EHVEngine.enforce"}` | library | provides | {"name":"ehv.compiler.engine.EHVEngine.enforce"} | - | EHVEngine.enforce decorator | [C] | ehv/compiler/engine.py:113 |
| `interface:library:provides:{"name":"ehv.gcd.masker.mask_logits"}` | library | provides | {"name":"ehv.gcd.masker.mask_logits"} | - | mask_logits | [C] | ehv/gcd/masker.py:23 |
| `interface:library:provides:{"name":"ehv.identity.workload.SVIDManager"}` | library | provides | {"name":"ehv.identity.workload.SVIDManager"} | - | SVIDManager | [C] | ehv/identity/workload.py:25 |

## Dependencies

| purl | manifest_path | scope | version_constraint | resolved_version | source | Conf | Cited at |
|---|---|---|---|---|---|---|---|
| `pkg:pypi/matplotlib` | pyproject.toml | optional | * | - | registry | [C] | pyproject.toml:25 |
| `pkg:pypi/pandas` | pyproject.toml | optional | * | - | registry | [C] | pyproject.toml:25 |

## Artifacts

| purl | Kind | Version | manifest_path | Name | Conf | Source |
|---|---|---|---|---|---|---|
| `pkg:pypi/ehv-runtime` | package | 0.3.0 | pyproject.toml | ehv-runtime | [C] | pyproject.toml:6 (+1) |

## Services

_None recorded._

## Datastores

| ID | Engine | Instance key | Schema | Table | Access | Conf | Source |
|---|---|---|---|---|---|---|---|
| `datastore:filesystem:_:bench-output` | filesystem | - | - | - | write | [C] | bench/measure_enforcement.py:87 (+1) |
| `datastore:filesystem:_:ehv-enclave-mem` | filesystem | - | - | - | readwrite | [C] | ehv/enclave/enclave.py:20 |
| `datastore:filesystem:_:oscal-gbom-export-file` | filesystem | - | - | - | write | [C] | ehv/compiler/gbom.py:125 |

## Config keys

| Name | Source | is_secret | Conf | Referenced at |
|---|---|---|---|---|
| `ANTHROPIC_API_KEY` | env | true | [C] | examples/anthropic_redteam.py:94 |
| `Enclavesecret_key(hardcodedsimulatedrootkeyatenclave.py:24)` | other | true | [C] | ehv/enclave/enclave.py:24 |

## External services

| Domain | Vendor | Category | Conf | Source |
|---|---|---|---|---|
| `api.anthropic.com` | Anthropic | llm | [I] | examples/anthropic_redteam.py:97 |

## API specs

_None recorded._

## Relations

| From | Kind | To | Conf | Source |
|---|---|---|---|---|
| `component:.` | builds | `artifact:pkg:pypi/ehv-runtime` | [C] | pyproject.toml:6 |
| `component:.` | enforces | `business_rule:invalid-epoch-denies-by-default` | [I] | EHV.tla:77 |
| `component:.` | enforces | `business_rule:unsafe-action-never-permitted` | [I] | EHV.tla:46 |
| `component:bench` | enforces | `business_rule:benchmark-limit-constraint` | [I] | bench/measure_enforcement.py:22 |
| `component:bench` | provides | `interface:cli:provides:{"name":"run_actual_benchmarks"}` | [C] | bench/measure_enforcement.py:122 |
| `component:bench` | provides | `interface:cli:provides:{"name":"sev_snp_benchmark"}` | [I] | bench/sev_snp_benchmark.py:1 |
| `component:bench` | writes | `datastore:filesystem:_:bench-output` | [C] | bench/measure_enforcement.py:117 |
| `component:ehv` | contains | `component:ehv/compiler` | [I] | ehv/compiler/engine.py:1 |
| `component:ehv` | contains | `component:ehv/enclave` | [I] | ehv/enclave/enclave.py:1 |
| `component:ehv` | contains | `component:ehv/gcd` | [I] | ehv/gcd/dfa.py:1 |
| `component:ehv` | contains | `component:ehv/identity` | [I] | ehv/identity/workload.py:1 |
| `component:ehv` | contains | `component:ehv/sync` | [I] | ehv/sync/store.py:1 |
| `component:ehv/compiler` | enforces | `business_rule:constraint-must-pass` | [C] | ehv/compiler/engine.py:149 |
| `component:ehv/compiler` | enforces | `business_rule:epoch-re-attestation` | [C] | ehv/compiler/engine.py:58 |
| `component:ehv/compiler` | enforces | `business_rule:fail-closed-on-invalid-epoch` | [C] | ehv/compiler/engine.py:131 |
| `component:ehv/compiler` | imports | `component:ehv/enclave` | [C] | ehv/compiler/engine.py:6 |
| `component:ehv/compiler` | imports | `component:ehv/sync` | [C] | ehv/compiler/engine.py:5 |
| `component:ehv/compiler` | provides | `interface:library:provides:{"name":"ehv.compiler.engine.EHVEngine.enforce"}` | [C] | ehv/compiler/engine.py:113 |
| `component:ehv/compiler` | writes | `datastore:filesystem:_:oscal-gbom-export-file` | [C] | ehv/compiler/gbom.py:127 |
| `component:ehv/enclave` | configured_by | `config:other:Enclavesecret_key(hardcodedsimulatedrootkeyatenclave.py:24)` | [C] | ehv/enclave/enclave.py:24 |
| `component:ehv/enclave` | reads | `datastore:filesystem:_:ehv-enclave-mem` | [C] | ehv/enclave/enclave.py:70 |
| `component:ehv/enclave` | writes | `datastore:filesystem:_:ehv-enclave-mem` | [C] | ehv/enclave/enclave.py:47 |
| `component:ehv/gcd` | enforces | `business_rule:vincristine-dose-cap` | [C] | ehv/gcd/grammar.py:21 |
| `component:ehv/gcd` | provides | `interface:library:provides:{"name":"ehv.gcd.masker.mask_logits"}` | [C] | ehv/gcd/masker.py:23 |
| `component:ehv/identity` | enforces | `business_rule:svid-validity` | [C] | ehv/identity/workload.py:45 |
| `component:ehv/identity` | provides | `interface:library:provides:{"name":"ehv.identity.workload.SVIDManager"}` | [C] | ehv/identity/workload.py:25 |
| `component:ehv/sync` | enforces | `business_rule:lww-policy-update` | [C] | ehv/sync/store.py:28 |
| `component:examples` | configured_by | `config:env:ANTHROPIC_API_KEY` | [C] | examples/anthropic_redteam.py:94 |
| `component:examples` | consumes | `interface:http:consumes:api.anthropic.com:POST:/v1/messages` | [I] | examples/anthropic_redteam.py:157 |
| `component:examples` | enforces | `business_rule:drug-dosage-limit` | [C] | examples/clinical_dosage.py:21 |
| `component:examples` | enforces | `business_rule:fail-closed-on-stale-attestation` | [I] | examples/anthropic_redteam.py:242 |
| `component:examples` | uses_external | `external:api.anthropic.com` | [I] | examples/anthropic_redteam.py:97 |
| `component:root` | builds | `artifact:pkg:pypi/ehv-runtime` | [I] | pyproject.toml:5 |
| `component:root` | depends_on | `dependency:pkg:pypi/matplotlib@pyproject.toml` | [C] | pyproject.toml:25 |
| `component:root` | depends_on | `dependency:pkg:pypi/pandas@pyproject.toml` | [C] | pyproject.toml:25 |

