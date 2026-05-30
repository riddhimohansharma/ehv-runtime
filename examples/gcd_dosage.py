"""
Grammar-Constrained Decoding (GCD) Clinical Dosage Demo
v2 GCD Demonstration — replaces ASEL
"""

import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ehv.gcd.grammar import build_clinical_dosage_dfa
from ehv.gcd.masker import mask_logits
from ehv.compiler.engine import EHVEngine
from ehv.sync.store import CausalPolicyStore
from ehv.compiler.gbom import GBOMLog
from ehv.enclave.enclave import Enclave

def run_demo():
    print("=== EHV v2: Grammar-Constrained Decoding (GCD) Demonstration ===")
    
    # Initialize components
    store = CausalPolicyStore(node_id="primary")
    enclave = Enclave(memory_name="demo_enclave_mem", simulate_latency=False)
    gbom = GBOMLog()
    engine = EHVEngine(epoch_duration=60, policy_store=store, enclave=enclave, gbom_log=gbom)
    
    # Set the policy: Vincristine dosage limit to 0.75 mg/m2
    print("[POLICY] FDA Neurotoxicity warning updates policy: max Vincristine dose = 0.75")
    store.update("limit_Vincristine", 0.75)
    
    # Build DFA for the clinical dosage grammar
    dfa = build_clinical_dosage_dfa(max_dose=0.75)
    
    vocab = ["administer", "0.5", "0.75", "1.0", "1.5", "2.0", "Vincristine", "IV", "oral"]
    
    # Simulate step-by-step token generation with logits masking
    print("\n[LLM GENERATION] Simulating generation of: 'administer 1.5 Vincristine IV'...")
    tokens = []
    
    # Step 1: token 1
    logits = {t: 1.0 for t in vocab} # equal raw logits
    # The LLM wants to output 'administer'
    masked = mask_logits(logits, tokens, dfa)
    print(f"  Step 1 prefix: {tokens}")
    print(f"  Allowed next tokens: {[t for t in vocab if masked[t] > -float('inf')]}")
    tokens.append("administer")
    
    # Step 2: token 2 (dose)
    logits = {t: 1.0 for t in vocab}
    # LLM wants to output '1.5' (which is unsafe!)
    masked = mask_logits(logits, tokens, dfa)
    print(f"\n  Step 2 prefix: {tokens}")
    print(f"  LLM wants to output '1.5', but we apply GCD masking:")
    print(f"  Allowed next tokens: {[t for t in vocab if masked[t] > -float('inf')]}")
    print(f"  Logit for '1.5': {masked['1.5']}")
    
    # The masker successfully set '1.5' logit to -inf!
    # The sampler must pick from allowed tokens. Let's sample '0.75'.
    tokens.append("0.75")
    print(f"  Sampled: '0.75'")
    
    # Step 3: token 3 (drug)
    logits = {t: 1.0 for t in vocab}
    masked = mask_logits(logits, tokens, dfa)
    tokens.append("Vincristine")
    
    # Step 4: token 4 (route)
    logits = {t: 1.0 for t in vocab}
    masked = mask_logits(logits, tokens, dfa)
    tokens.append("IV")
    
    print(f"\n[GENERATION COMPLETE] Generated tokens: {tokens}")
    
    # Trace path through DFA
    path = dfa.trace(tokens)
    print(f"[DFA TRACE] State path: {path}")
    print(f"Accepted by DFA: {dfa.accepts(tokens)}")

    # PEP Enforcement Invariant check
    def dosage_constraint(policies, patient_id, drug, amount, unit):
        limit = policies.get(f"limit_{drug}")
        return limit is None or amount <= limit

    @engine.enforce(dosage_constraint)
    def prescribe_medication(patient_id, drug, amount, unit):
        return f"Successfully prescribed {amount}{unit} of {drug} to patient {patient_id}"

    # Verify the generated dose through the PEP
    amount = float(tokens[1])
    drug = tokens[2]
    route = tokens[3]
    
    print(f"\n[PEP ENFORCEMENT] Verifying final prescription of {amount} mg/m2 {drug} {route}...")
    try:
        res = prescribe_medication("P-882", drug, amount, "mg/m2")
        print(f"Result: {res}")
    except Exception as e:
        print(f"Rejected: {e}")
        
    print("\n=== OSCAL GBOM Cryptographic Receipt ===")
    import json
    print(json.dumps(gbom.to_oscal()["assessment-results"], indent=2))
    
    enclave.cleanup()

if __name__ == "__main__":
    run_demo()
