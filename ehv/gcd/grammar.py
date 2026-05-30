"""
Grammar-Constrained Decoding (GCD): Clinical Dosage Grammar
Defines the grammar rules for Vincristine prescriptions.
"""

from .dfa import DFA, GrammarRule, build_dfa_from_rules

def build_clinical_dosage_dfa(max_dose: float = 1.5) -> DFA:
    """
    Builds a DFA grammar for clinical Vincristine prescriptions.
    The grammar allows prescribing Vincristine with a dosage up to max_dose.
    
    Vocabulary:
        "administer", "0.5", "0.75", "1.0", "1.25", "1.5", "2.0", "Vincristine", "IV"
    """
    allowed_doses = ["0.5", "0.75", "1.0", "1.25", "1.5", "2.0"]
    rules = []
    
    # Generate right-linear rules for "administer <dose> Vincristine IV"
    for dose in allowed_doses:
        if float(dose) <= max_dose:
            # S -> ["administer", dose, "Vincristine", "IV"]
            rules.append(GrammarRule("S", ["administer", dose, "Vincristine", "IV"]))

    # Add all states to the DFA
    dfa = build_dfa_from_rules(rules, start_symbol="S")
    
    # We need to make sure the alphabet includes all tokens in our vocabulary, even unused ones,
    # so the logits masker knows how to handle them.
    all_vocab = {"administer", "0.5", "0.75", "1.0", "1.25", "1.5", "2.0", "Vincristine", "IV", "oral"}
    dfa.alphabet.update(all_vocab)
    
    return dfa
