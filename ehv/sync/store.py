import time
import json
from threading import Lock

class PolicyStore:
    """
    Pillar 1: CRDT-Based Policy Store (LWW-Element-Set)
    Simulates monotonic policy convergence across nodes.
    """
    def __init__(self):
        self._policies = {} # key -> (value, timestamp)
        self._lock = Lock()

    def update(self, key, value):
        """Monotonic update via LWW (Last-Writer-Wins)"""
        with self._lock:
            ts = time.time()
            self._policies[key] = (value, ts)
            return ts

    def get(self, key):
        with self._lock:
            item = self._policies.get(key)
            return item[0] if item else None

    def get_all(self):
        with self._lock:
            return {k: v[0] for k, v in self._policies.items()}

    def get_hash(self):
        """Pillar 2: Policy Hash for Epoch Attestation"""
        state_str = json.dumps(self.get_all(), sort_keys=True)
        import hashlib
        return hashlib.sha256(state_str.encode()).hexdigest()

# Singleton for the runtime
global_policy_store = PolicyStore()
