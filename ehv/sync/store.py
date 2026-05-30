import time
import json
import hashlib
from threading import Lock
from .vclock import VectorClock

class PolicyStore:
    """
    Pillar 1: CRDT-Based Policy Store (LWW-Element-Set)
    Simulates monotonic policy convergence across nodes.

    WARNING (Threat T7): The current LWW CRDT relies on physical timestamps 
    (time.time()). In untrusted edge deployments, this is vulnerable to clock 
    skew and NTP poisoning. Phase 2 hardening will replace this with a directed 
    acyclic graph (DAG) of policy mutations using vector clocks or Lamport timestamps.
    """
    def __init__(self, node_id="default"):
        self.node_id = node_id
        self._policies = {} # key -> (value, timestamp)
        self._lock = Lock()

    def update(self, key, value, ts=None):
        """Monotonic update via LWW (Last-Writer-Wins)"""
        with self._lock:
            ts = ts or time.time()
            if key in self._policies:
                _, existing_ts = self._policies[key]
                if ts <= existing_ts:
                    return existing_ts # Reject older update
            self._policies[key] = (value, ts)
            return ts

    def get(self, key):
        with self._lock:
            item = self._policies.get(key)
            return item[0] if item else None

    def get_all(self):
        with self._lock:
            return {k: v[0] for k, v in self._policies.items()}

    def get_raw_state(self):
        """Returns the internal state including timestamps for merging."""
        with self._lock:
            return dict(self._policies)

    def merge(self, other_store):
        """Join-semilattice merge operation (Least Upper Bound)."""
        other_state = other_store.get_raw_state()
        with self._lock:
            for key, (val, ts) in other_state.items():
                if key not in self._policies:
                    self._policies[key] = (val, ts)
                else:
                    _, existing_ts = self._policies[key]
                    if ts > existing_ts:
                        self._policies[key] = (val, ts)
                    elif ts == existing_ts:
                        # Tie-breaker (lexicographic sort on value str for determinism)
                        existing_val = self._policies[key][0]
                        if str(val) > str(existing_val):
                            self._policies[key] = (val, ts)

    def diverge(self, new_node_id):
        """Simulates a network partition by forking the state."""
        new_store = PolicyStore(node_id=new_node_id)
        with self._lock:
            new_store._policies = dict(self._policies)
        return new_store

    def has_converged(self, other_store):
        """Checks if two nodes have converged to the exact same state."""
        return self.get_hash() == other_store.get_hash()

    def get_hash(self):
        """Pillar 2: Policy Hash for Epoch Attestation"""
        state_str = json.dumps(self.get_all(), sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()


class CausalPolicyStore(PolicyStore):
    """
    Pillar 1 Upgrade: Causal Policy Store using Vector Clocks
    Mitigates clock skew and NTP hijacking (Threat T7) by enforcing causal ordering.
    """
    def __init__(self, node_id="default"):
        super().__init__(node_id=node_id)
        self.vclock = VectorClock()

    def update(self, key, value, vclock=None):
        """Monotonic update via Causal Ordering (Vector Clocks)"""
        with self._lock:
            if vclock is None:
                self.vclock.increment(self.node_id)
                vc = self.vclock.copy()
            else:
                self.vclock = self.vclock.merge(vclock)
                vc = vclock.copy()

            if key in self._policies:
                existing_val, existing_vc = self._policies[key]
                if vc.happens_before(existing_vc):
                    return existing_vc  # Reject older update

                if vc.is_concurrent(existing_vc):
                    # Resolve concurrent updates using lexicographic tie-breaker on value
                    if str(value) > str(existing_val):
                        self._policies[key] = (value, vc.merge(existing_vc))
                    else:
                        self._policies[key] = (existing_val, existing_vc.merge(vc))
                    return self._policies[key][1]

            self._policies[key] = (value, vc)
            return vc

    def merge(self, other_store):
        """Join-semilattice merge operation using vector clocks."""
        other_state = other_store.get_raw_state()
        with self._lock:
            self.vclock = self.vclock.merge(other_store.vclock)
            for key, (val, vc) in other_state.items():
                if key not in self._policies:
                    self._policies[key] = (val, vc.copy())
                else:
                    existing_val, existing_vc = self._policies[key]
                    if vc.happens_before(existing_vc):
                        continue
                    elif existing_vc.happens_before(vc):
                        self._policies[key] = (val, vc.copy())
                    elif vc.is_concurrent(existing_vc):
                        if str(val) > str(existing_val):
                            self._policies[key] = (val, vc.merge(existing_vc))
                        else:
                            self._policies[key] = (existing_val, existing_vc.merge(vc))

    def diverge(self, new_node_id):
        """Simulates a network partition by forking the state."""
        new_store = CausalPolicyStore(node_id=new_node_id)
        with self._lock:
            new_store._policies = {k: (v[0], v[1].copy()) for k, v in self._policies.items()}
            new_store.vclock = self.vclock.copy()
        return new_store


# Singleton for the runtime's primary node
global_policy_store = PolicyStore(node_id="primary")

