import sys
import os
import json

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ehv.compiler.engine import runtime, GovernanceError
from ehv.sync.store import global_policy_store
from ehv.compiler.gbom import global_gbom_log

def dosage_constraint(policies, patient_id, drug, amount):
    limit = policies.get(f"limit_{drug}", 10.0)
    return amount <= limit

@runtime.enforce(dosage_constraint)
def prescribe(patient_id, drug, amount):
    return f"Prescribed {amount} of {drug}"

def run_experiment():
    print("--- EHV-Runtime: GBOM Cryptographic Audit Trail ---")
    
    global_policy_store.update("limit_DrugX", 5.0)
    
    print("[ACTION] Executing valid action...")
    prescribe("P1", "DrugX", 3.0)
    
    print("[ACTION] Executing valid action...")
    prescribe("P2", "DrugX", 4.0)
    
    print("[ACTION] Attempting invalid action...")
    try:
        prescribe("P3", "DrugX", 10.0)
    except GovernanceError:
        pass
        
    print("\n[VERIFY] Checking GBOM hash chain integrity...")
    is_valid = global_gbom_log.verify_chain()
    
    print("\n--- GBOM Log Output (JSON) ---")
    print(global_gbom_log.to_json())
    
    if is_valid:
        print("\nSUCCESS: GBOM integrity verified. Tamper-evident hash chain intact.")
    else:
        print("\nFAILURE: GBOM hash chain is broken.")

if __name__ == "__main__":
    run_experiment()
