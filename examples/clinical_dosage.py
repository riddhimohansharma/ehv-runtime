import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ehv.compiler.engine import runtime, GovernanceError
from ehv.sync.store import global_policy_store

# Define the Governance Constraint (The Invariant)
def dosage_constraint(policies, patient_id, drug, amount, unit):
    limit = policies.get(f"limit_{drug}")
    if limit is None:
        return True 
    
    if amount > limit:
        return False 
    return True

# The Agentic Action
@runtime.enforce(dosage_constraint)
def prescribe_medication(patient_id, drug, amount, unit):
    return f"Successfully prescribed {amount}{unit} of {drug} to patient {patient_id}"

def run_simulation():
    print("--- EHV-Runtime: Clinical Dosage Simulation ---")
    
    global_policy_store.update("limit_Vincristine", 1.5)
    print("[INIT] Policy set: Vincristine limit = 1.5 mg/m2")
    
    print("\n[ACTION] Agent prescribing 1.0 mg/m2...")
    try:
        res = prescribe_medication("P-882", "Vincristine", 1.0, "mg/m2")
        print(f"Result: {res}")
    except GovernanceError as e:
        print(f"Error: {e}")

    print("\n[UPDATE] CRDT Sync: FDA issues neurotoxicity warning. New limit = 0.75 mg/m2")
    global_policy_store.update("limit_Vincristine", 0.75)

    print("\n[ACTION] Agent prescribing 1.0 mg/m2 (Enforced at Runtime)...")
    try:
        res = prescribe_medication("P-882", "Vincristine", 1.0, "mg/m2")
        print(f"Result: {res}")
    except GovernanceError as e:
        print(f"REJECTED: {e}")
        print("Proof: Non-compliant actions are computationally unreachable.")

    print("\n--- GBOM (Governance Bill of Materials) ---")
    from ehv.compiler.gbom import global_gbom_log
    print(global_gbom_log.to_json())

if __name__ == "__main__":
    run_simulation()
