"""
Grammar-Constrained Decoding: Deterministic Finite Automaton (DFA)

Implements the DFA engine described in the EHV v2 paper (Appendix A).
Compiles policy-constrained action grammars into a DFA, then provides
O(1) token-level allowed-set queries for logits masking.

Architecture Note:
    This is a *pattern demonstration* against a synthetic vocabulary.
    It does not hook into a real LLM tokenizer. Production deployment
    would map subword tokens to DFA transitions via an adapter layer.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# Sentinel for invalid/dead state
DEAD_STATE = "__DEAD__"


@dataclass
class DFA:
    """
    A Deterministic Finite Automaton for grammar-constrained token generation.

    Attributes:
        states: Set of state names.
        alphabet: Set of valid tokens (vocabulary subset).
        transitions: Mapping of (state, token) → next_state.
        start: The initial state.
        accept: Set of accepting (terminal) states.
    """
    states: set[str]
    alphabet: set[str]
    transitions: dict[tuple[str, str], str]
    start: str
    accept: set[str]

    def transition(self, state: str, token: str) -> str:
        """
        Returns the next state for a given (state, token) pair.
        Returns DEAD_STATE if no valid transition exists.
        """
        if state == DEAD_STATE:
            return DEAD_STATE
        return self.transitions.get((state, token), DEAD_STATE)

    def allowed_tokens(self, state: str) -> set[str]:
        """
        Returns the set of tokens that have valid transitions from the
        given state. This is the core query used by the logits masker.

        O(|alphabet|) in the worst case, but typically much smaller
        because only a subset of tokens are valid at each state.
        """
        if state == DEAD_STATE:
            return set()
        return {
            token for token in self.alphabet
            if (state, token) in self.transitions
            and self.transitions[(state, token)] != DEAD_STATE
        }

    def is_accepting(self, state: str) -> bool:
        """Returns True if the state is an accepting (terminal) state."""
        return state in self.accept

    def trace(self, tokens: list[str]) -> list[str]:
        """
        Traces a token sequence through the DFA, returning the full
        state path. Useful for debugging and GBOM logging.
        """
        path = [self.start]
        state = self.start
        for token in tokens:
            state = self.transition(state, token)
            path.append(state)
        return path

    def accepts(self, tokens: list[str]) -> bool:
        """Returns True if the token sequence reaches an accepting state."""
        state = self.start
        for token in tokens:
            state = self.transition(state, token)
            if state == DEAD_STATE:
                return False
        return self.is_accepting(state)


@dataclass
class GrammarRule:
    """A simple production rule: nonterminal → sequence of symbols."""
    nonterminal: str
    production: list[str]


def build_dfa_from_rules(
    rules: list[GrammarRule],
    start_symbol: str = "S"
) -> DFA:
    """
    Builds a DFA from a list of grammar rules using direct state construction.

    This is a simplified compiler for regular grammars (right-linear).
    Each rule A → t1 t2 ... tn creates a chain of states with transitions
    on each terminal symbol. Multiple rules for the same nonterminal create
    branching paths from that nonterminal's state.

    For the EHV PoC, this is sufficient to demonstrate the GCD pattern.
    Production systems would use a full CFG→NFA→DFA subset construction.
    """
    states: set[str] = set()
    transitions: dict[tuple[str, str], str] = {}
    alphabet: set[str] = set()
    accept: set[str] = set()

    for rule in rules:
        current_state = rule.nonterminal
        states.add(current_state)

        for i, symbol in enumerate(rule.production):
            alphabet.add(symbol)
            # Create intermediate state names
            if i < len(rule.production) - 1:
                next_state = f"{rule.nonterminal}__{i + 1}"
            else:
                # Final symbol leads to an accept state
                next_state = f"{rule.nonterminal}__ACCEPT"
                accept.add(next_state)

            states.add(next_state)
            transitions[(current_state, symbol)] = next_state
            current_state = next_state

    return DFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start=start_symbol,
        accept=accept,
    )
