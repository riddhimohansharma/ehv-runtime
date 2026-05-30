"""
Vector Clock Implementation for Causal CRDT Ordering
v2 clock-skew mitigation — replaces physical timestamps (T7 mitigation)
"""

from __future__ import annotations
from typing import Dict, Any

class VectorClock:
    """
    A Vector Clock tracking causal relationships in a distributed system.
    """
    def __init__(self, clock_dict: Dict[str, int] = None):
        self.clocks = dict(clock_dict) if clock_dict else {}

    def increment(self, node_id: str) -> None:
        """Increments the clock component for the local node."""
        self.clocks[node_id] = self.clocks.get(node_id, 0) + 1

    def merge(self, other: VectorClock) -> VectorClock:
        """Merges this clock with another clock by taking the pointwise maximum."""
        merged_dict = dict(self.clocks)
        for node, val in other.clocks.items():
            merged_dict[node] = max(merged_dict.get(node, 0), val)
        return VectorClock(merged_dict)

    def happens_before(self, other: VectorClock) -> bool:
        """
        Returns True if this clock causally happens before the other clock.
        A happens-before B (A < B) if:
          - A[node] <= B[node] for all nodes
          - A[node] < B[node] for at least one node
        """
        all_nodes = set(self.clocks.keys()).union(other.clocks.keys())
        less_or_equal = True
        strictly_less = False
        
        for node in all_nodes:
            self_val = self.clocks.get(node, 0)
            other_val = other.clocks.get(node, 0)
            if self_val > other_val:
                less_or_equal = False
                break
            if self_val < other_val:
                strictly_less = True
                
        return less_or_equal and strictly_less

    def is_concurrent(self, other: VectorClock) -> bool:
        """
        Returns True if this clock and the other clock are concurrent
        (neither happens before the other, and they are not equal).
        """
        if self.clocks == other.clocks:
            return False
        return not self.happens_before(other) and not other.happens_before(self)

    def to_dict(self) -> Dict[str, int]:
        """Returns the dictionary representation of the vector clock."""
        return dict(self.clocks)

    def copy(self) -> VectorClock:
        """Returns a copy of this vector clock."""
        return VectorClock(self.clocks)

    def __repr__(self) -> str:
        return f"VectorClock({self.clocks})"
