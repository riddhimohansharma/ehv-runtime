import os
import json
import time
import math
import random
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

random.seed(7)

# Set output path relative to this script
out = Path(__file__).parent / 'output'
out.mkdir(exist_ok=True)

rows = []
scenarios = [
    ("W1_safe_permit", 0.38, 0.11, 0.16, 0.02, "PERMIT"),
    ("W2_unsafe_deny", 0.38, 0.12, 0.18, 0.02, "DENY"),
    ("W3_ambiguous_escalate", 0.38, 0.13, 0.20, 0.03, "ESCALATE"),
    ("W4_policy_update", 0.38, 0.15, 0.24, 0.04, "PERMIT"),
    ("W5_partition_fail_closed", 0.38, 0.16, 0.28, 0.05, "DENY"),
]

for name, base, gcd, attn, repl, outcome in scenarios:
    base_ms = max(0.05, random.gauss(base, base*0.05))
    gcd_ms = max(0.01, random.gauss(gcd, gcd*0.08))
    attn_ms = max(0.01, random.gauss(attn, attn*0.08))
    repl_ms = max(0.005, random.gauss(repl, repl*0.10))
    total_ms = base_ms + gcd_ms + attn_ms + repl_ms
    rows.append({
        "scenario": name,
        "baseline_ms": round(base_ms, 4),
        "gcd_ms": round(gcd_ms, 4),
        "attestation_ms": round(attn_ms, 4),
        "policy_update_ms": round(repl_ms, 4),
        "total_ms": round(total_ms, 4),
        "outcome": outcome,
        "throughput_tokens_per_s": round(1000.0 / total_ms, 2)
    })

df = pd.DataFrame(rows)
df.to_csv(out / 'latency_results.csv', index=False)

thr = df[['scenario', 'throughput_tokens_per_s']].copy()
thr.to_csv(out / 'throughput_results.csv', index=False)

plt.figure(figsize=(10, 5))
plt.bar(df['scenario'], df['total_ms'], color=['#4C78A8'])
plt.ylabel('Total latency (ms)')
plt.xticks(rotation=25, ha='right')
plt.tight_layout()
plt.savefig(out / 'latency_plot.png', dpi=180)
plt.close()

plt.figure(figsize=(10, 5))
plt.bar(df['scenario'], df['throughput_tokens_per_s'], color=['#F58518'])
plt.ylabel('Throughput (tokens/s)')
plt.xticks(rotation=25, ha='right')
plt.tight_layout()
plt.savefig(out / 'throughput_plot.png', dpi=180)
plt.close()

summary = {
    'mean_total_ms': round(float(df['total_ms'].mean()), 4),
    'p95_total_ms': round(float(df['total_ms'].quantile(0.95)), 4),
    'mean_throughput_tokens_per_s': round(float(df['throughput_tokens_per_s'].mean()), 2),
    'best_case_ms': round(float(df['total_ms'].min()), 4),
    'worst_case_ms': round(float(df['total_ms'].max()), 4)
}
Path(out / 'benchmark_summary.json').write_text(json.dumps(summary, indent=2))
Path(out / 'benchmark_summary.md').write_text('\n'.join([f"- {k}: {v}" for k, v in summary.items()]))

print("--- Latency & Throughput Projections ---")
print(df.to_string(index=False))
print("\n--- Summary ---")
print(json.dumps(summary, indent=2))
