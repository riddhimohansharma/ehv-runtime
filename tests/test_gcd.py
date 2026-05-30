import pytest
import math
from ehv.gcd.dfa import build_dfa_from_rules, GrammarRule
from ehv.gcd.grammar import build_clinical_dosage_dfa
from ehv.gcd.masker import mask_logits
from ehv.compiler.engine import EHVEngine, GovernanceError
from ehv.sync.store import PolicyStore
from ehv.enclave.enclave import Enclave
from ehv.compiler.gbom import GBOMLog

def test_dfa_accept_valid_token_sequence():
    dfa = build_clinical_dosage_dfa(max_dose=1.5)
    assert dfa.accepts(["administer", "1.0", "Vincristine", "IV"]) is True
    assert dfa.accepts(["administer", "1.5", "Vincristine", "IV"]) is True

def test_dfa_reject_invalid_token_sequence():
    dfa = build_clinical_dosage_dfa(max_dose=1.5)
    # Exceeds max dose
    assert dfa.accepts(["administer", "2.0", "Vincristine", "IV"]) is False
    # Invalid drug
    assert dfa.accepts(["administer", "1.0", "Aspirin", "IV"]) is False

def test_mask_logits_blocks_illegal_tokens():
    dfa = build_clinical_dosage_dfa(max_dose=0.75)
    # Prefix is ["administer"]
    # Next token must be a dose <= 0.75: "0.5" or "0.75"
    logits = {
        "0.5": 2.0,
        "0.75": 1.5,
        "1.5": 5.0,
        "2.0": 3.0,
        "Vincristine": 0.5
    }
    masked = mask_logits(logits, ["administer"], dfa)
    assert masked["1.5"] == -float("inf")
    assert masked["2.0"] == -float("inf")
    assert masked["Vincristine"] == -float("inf")

def test_mask_logits_preserves_legal_tokens():
    dfa = build_clinical_dosage_dfa(max_dose=0.75)
    logits = {
        "0.5": 2.0,
        "0.75": 1.5,
        "1.5": 5.0,
    }
    masked = mask_logits(logits, ["administer"], dfa)
    assert masked["0.5"] == 2.0
    assert masked["0.75"] == 1.5

def test_dfa_from_grammar_simple():
    rules = [
        GrammarRule("S", ["hello", "world"])
    ]
    dfa = build_dfa_from_rules(rules, start_symbol="S")
    assert dfa.accepts(["hello", "world"]) is True
    assert dfa.accepts(["hello", "there"]) is False

def test_gcd_integration_with_engine():
    store = PolicyStore(node_id="test")
    enclave = Enclave(memory_name="test_gcd_mem", simulate_latency=False)
    gbom = GBOMLog()
    engine = EHVEngine(epoch_duration=60, policy_store=store, enclave=enclave, gbom_log=gbom)
    
    try:
        store.update("limit_Vincristine", 0.75)
        
        # Simulate LLM generation with GCD masking
        dfa = build_clinical_dosage_dfa(max_dose=0.75)
        
        # Action is constructed step by step
        tokens = []
        vocab = ["administer", "0.5", "0.75", "1.5", "Vincristine", "IV"]
        
        # Step 1: next token
        logits = {t: 1.0 for t in vocab}
        masked = mask_logits(logits, tokens, dfa)
        # Select highest logit from allowed
        next_token = max((k for k in vocab if masked[k] > -float("inf")), key=lambda k: masked[k])
        assert next_token == "administer"
        tokens.append(next_token)
        
        # Step 2: dose
        logits = {t: 1.0 for t in vocab}
        masked = mask_logits(logits, tokens, dfa)
        assert masked["1.5"] == -float("inf") # 1.5 is masked
        next_token = "0.75" # Chosen from allowed
        tokens.append(next_token)
        
        # Step 3: drug
        logits = {t: 1.0 for t in vocab}
        masked = mask_logits(logits, tokens, dfa)
        next_token = "Vincristine"
        tokens.append(next_token)
        
        # Step 4: route
        logits = {t: 1.0 for t in vocab}
        masked = mask_logits(logits, tokens, dfa)
        next_token = "IV"
        tokens.append(next_token)
        
        # Complete sequence
        assert tokens == ["administer", "0.75", "Vincristine", "IV"]
        
        # Parse output (acting as ASEL layer or similar)
        amount = float(tokens[1])
        drug = tokens[2]
        
        # Enforce through PEP
        def constraint(policies, p_drug, p_amount):
            limit = policies.get(f"limit_{p_drug}")
            return limit is not None and p_amount <= limit
            
        @engine.enforce(constraint)
        def run_action(p_drug, p_amount):
            return "executed"
            
        res = run_action(drug, amount)
        assert res == "executed"
        assert gbom.entries[-1].enforcement_result == "PERMIT"
        
    finally:
        enclave.cleanup()
