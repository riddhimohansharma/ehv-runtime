import time
import csv
from pathlib import Path
from ehv.compiler.engine import EHVEngine, GovernanceError
from ehv.compiler.gbom import GBOMLog
from ehv.enclave.enclave import Enclave
from ehv.sync.store import PolicyStore

def run_actual_benchmarks():
    # Setup fresh components (simulate_latency=False to measure purely execution/policy overhead)
    store = PolicyStore(node_id="bench")
    enclave = Enclave(memory_name="bench_enclave_mem", simulate_latency=False)
    gbom = GBOMLog()
    engine = EHVEngine(epoch_duration=3600, policy_store=store, enclave=enclave, gbom_log=gbom)

    store.update("limit", 10.0)

    # 1. PERMIT scenario
    def constraint_permit(policies, val):
        return val <= policies.get("limit", 0)

    @engine.enforce(constraint_permit)
    def action_permit(val):
        return val

    # Warmup
    action_permit(5.0)

    permit_times = []
    for _ in range(10000):
        t0 = time.perf_counter()
        action_permit(5.0)
        t1 = time.perf_counter()
        permit_times.append((t1 - t0) * 1000.0) # convert to ms

    # 2. DENY scenario
    def constraint_deny(policies, val):
        return val <= policies.get("limit", 0)

    @engine.enforce(constraint_deny)
    def action_deny(val):
        return val

    # Warmup
    try:
        action_deny(12.0)
    except GovernanceError:
        pass

    deny_times = []
    for _ in range(10000):
        t0 = time.perf_counter()
        try:
            action_deny(12.0)
        except GovernanceError:
            pass
        t1 = time.perf_counter()
        deny_times.append((t1 - t0) * 1000.0)

    # 3. ESCALATE scenario
    def constraint_escalate(policies, val):
        raise ValueError("Escalation triggered")

    @engine.enforce(constraint_escalate)
    def action_escalate(val):
        return val

    # Warmup
    try:
        action_escalate(5.0)
    except ValueError:
        pass

    escalate_times = []
    for _ in range(10000):
        t0 = time.perf_counter()
        try:
            action_escalate(5.0)
        except ValueError:
            pass
        t1 = time.perf_counter()
        escalate_times.append((t1 - t0) * 1000.0)

    enclave.cleanup()

    # Calculate statistics
    out = Path(__file__).parent / 'output'
    out.mkdir(exist_ok=True)
    
    csv_path = out / 'actual_enforcement_latency.csv'
    
    print("--- Actual Python PEP Enforcement Latency (ms) ---")
    
    results = []
    for name, times in [("PERMIT", permit_times), ("DENY", deny_times), ("ESCALATE", escalate_times)]:
        times_sorted = sorted(times)
        n = len(times_sorted)
        mean_val = sum(times_sorted) / n
        min_val = times_sorted[0]
        max_val = times_sorted[-1]
        median_val = times_sorted[int(n * 0.5)]
        p95_val = times_sorted[int(n * 0.95)]
        p99_val = times_sorted[int(n * 0.99)]
        
        results.append({
            "scenario": name,
            "mean_ms": round(mean_val, 6),
            "median_ms": round(median_val, 6),
            "p95_ms": round(p95_val, 6),
            "p99_ms": round(p99_val, 6),
            "min_ms": round(min_val, 6),
            "max_ms": round(max_val, 6)
        })
        
        print(f"{name}: Mean={mean_val:.6f}ms, Median={median_val:.6f}ms, P95={p95_val:.6f}ms, P99={p99_val:.6f}ms")

    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["scenario", "mean_ms", "median_ms", "p95_ms", "p99_ms", "min_ms", "max_ms"])
        writer.writeheader()
        writer.writerows(results)

if __name__ == '__main__':
    run_actual_benchmarks()
