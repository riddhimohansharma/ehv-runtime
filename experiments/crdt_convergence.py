import sys
import os
import time

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ehv.sync.store import PolicyStore
from ehv.sync.network import global_network

def run_experiment():
    print("--- EHV-Runtime: CRDT Convergence Experiment ---")
    
    # 1. Initialize Nodes
    node_a = PolicyStore(node_id="Hospital_A")
    node_b = PolicyStore(node_id="Hospital_B")
    
    global_network.register_node(node_a)
    global_network.register_node(node_b)
    
    print("[INIT] Registered Node A and Node B")
    
    # 2. Simulate Partition
    global_network.partition()
    
    # 3. Independent Updates during Partition
    print("[UPDATE] Node A sets Vincristine_limit = 1.0 (ts=100)")
    node_a.update("Vincristine_limit", 1.0, ts=100)
    
    print("[UPDATE] Node B sets Vincristine_limit = 0.75 (ts=110)")
    node_b.update("Vincristine_limit", 0.75, ts=110)
    
    print("[UPDATE] Node A sets Doxorubicin_limit = 30.0 (ts=105)")
    node_a.update("Doxorubicin_limit", 30.0, ts=105)
    
    # 4. Attempt Propagation (will be queued due to partition)
    global_network.propagate("Hospital_A", "Hospital_B")
    global_network.propagate("Hospital_B", "Hospital_A")
    
    print(f"\n[STATE] During Partition:")
    print(f"Node A: {node_a.get_all()}")
    print(f"Node B: {node_b.get_all()}")
    
    # 5. Network Recovery
    print("\n[EVENT] Network Recovery...")
    global_network.recover()
    
    print(f"\n[STATE] After Recovery:")
    print(f"Node A: {node_a.get_all()}")
    print(f"Node B: {node_b.get_all()}")
    
    # 6. Verify Convergence
    if node_a.has_converged(node_b):
        print("\nSUCCESS: CRDT Convergence verified. Nodes converged to identical LWW state after partition recovery.")
    else:
        print("\nFAILURE: Nodes did not converge.")

if __name__ == "__main__":
    run_experiment()
