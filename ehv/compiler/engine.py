import time
import functools
from ..sync.store import global_policy_store

class GovernanceError(Exception):
    """Raised when an agent action violates a policy invariant."""
    pass

class EHVEngine:
    """
    Pillar 3: The Policy Enforcement Point (PEP) in JIT
    Provides the governance-aware hook for agentic actions.
    """
    def __init__(self, epoch_duration=60):
        self.epoch_duration = epoch_duration
        self._last_attestation = 0
        self._epoch_hash = None

    def _verify_epoch(self):
        """Pillar 2: Epoch-based Attestation Caching"""
        now = time.time()
        if now - self._last_attestation > self.epoch_duration:
            # Re-attest (simulate 200ms latency on miss)
            # time.sleep(0.2) 
            self._epoch_hash = global_policy_store.get_hash()
            self._last_attestation = now
            return True
        return True

    def enforce(self, constraint_func):
        """
        Decorator for agentic actions.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                
                self._verify_epoch()
                current_policies = global_policy_store.get_all()
                
                try:
                    result = constraint_func(current_policies, *args, **kwargs)
                except Exception as e:
                    print(f"[ESCALATE] Human override required: {e}")
                    raise
                
                if not result:
                    end_time = time.perf_counter()
                    gl = (end_time - start_time) * 1000
                    raise GovernanceError(f"DENIED by EHV Invariant (GL: {gl:.4f}ms)")
                
                res = func(*args, **kwargs)
                
                end_time = time.perf_counter()
                gl = (end_time - start_time) * 1000
                return res
            return wrapper
        return decorator

# Shared engine instance
runtime = EHVEngine()
