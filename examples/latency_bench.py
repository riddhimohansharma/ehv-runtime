import sys
import os
import time
import statistics

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ehv.compiler.engine import runtime
from ehv.sync.store import global_policy_store

def benchmark_constraint(policies, *args, **kwargs):
    # Simulate a real policy lookup
    limit = policies.get("active_limit")
    return limit is not None

def raw_action():
    return True

@runtime.enforce(benchmark_constraint)
def agent_action():
    return True

def run_bench(iterations=10000):
    print(f"--- EHV-Runtime Performance Benchmark ({iterations} iterations) ---")
    
    global_policy_store.update("active_limit", 1.0)
    baseline_latencies = []
    governed_latencies = []
    
    # Warmup
    for _ in range(100):
        raw_action()
        agent_action()
        
    print("[BENCH] Running baseline (no governance)...")
    for _ in range(iterations):
        start = time.perf_counter()
        raw_action()
        end = time.perf_counter()
        baseline_latencies.append((end - start) * 1000) # ms

    print("[BENCH] Running governed (with EHV PEP)...")
    for _ in range(iterations):
        start = time.perf_counter()
        agent_action()
        end = time.perf_counter()
        governed_latencies.append((end - start) * 1000) # ms
        
    baseline_mean = statistics.mean(baseline_latencies)
    governed_mean = statistics.mean(governed_latencies)
    overhead = governed_mean - baseline_mean
    
    print(f"\nBaseline Mean:   {baseline_mean:.6f} ms")
    print(f"Governed Mean:   {governed_mean:.6f} ms")
    print(f"---")
    print(f"Enforcement Cost: {overhead:.6f} ms")
    print(f"P99 Overhead:     {statistics.quantiles(governed_latencies, n=100)[98]:.6f} ms")
    
    if overhead < 1.0:
        print("\nSUCCESS: Low-latency enforcement pattern verified.")

if __name__ == "__main__":
    run_bench()
