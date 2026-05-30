"""
Grammar-Constrained Decoding (GCD): Logits Masker
v2 Primary Enforcement Path — replaces ASEL
"""

from typing import Dict, List
from .dfa import DFA, DEAD_STATE

class LogitsMasker:
    """
    LogitsMasker handles token-level logits masking against a compiled DFA.
    """
    def __init__(self, dfa: DFA):
        self.dfa = dfa

    def mask(self, logits: Dict[str, float], prefix: List[str]) -> Dict[str, float]:
        """
        Masks the given logits based on the token prefix and the DFA.
        Sets illegal transition tokens to -inf.
        """
        return mask_logits(logits, prefix, self.dfa)

def mask_logits(logits: Dict[str, float], prefix: List[str], dfa: DFA) -> Dict[str, float]:
    """
    Masks the given logits dictionary to set non-allowed token values to -inf.
    """
    masked = dict(logits)
    state = dfa.start
    for t in prefix:
        state = dfa.transition(state, t)
        if state == DEAD_STATE:
            # If state is dead/invalid, all tokens are blocked (set to -inf)
            for token in masked:
                masked[token] = -float("inf")
            return masked

    allowed = dfa.allowed_tokens(state)
    for token in list(masked.keys()):
        if token not in allowed:
            masked[token] = -float("inf")
    return masked
