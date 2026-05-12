import time
import functools
import json
from ..sync.store import global_policy_store
from ..enclave.enclave import Enclave
from .gbom import global_gbom_log

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
        self.enclave = Enclave()

    def _verify_epoch(self):
        """Pillar 2: Epoch-based Attestation Caching"""
        now = time.time()
        local_hash = global_policy_store.get_hash()
        
        # Check if we need to re-attest (epoch expired or first run)
        if now - self._last_attestation > self.epoch_duration or self._epoch_hash is None:
            report = self.enclave.attest(local_hash)
            self._epoch_hash = report["policy_hash"]
            self._last_attestation = now
            return True, report["attestation_status"] == "VALID"
        
        # Hot-path: O(1) comparison against enclave memory
        is_valid = self.enclave.verify_epoch(local_hash)
        if not is_valid:
            # Hash mismatch, force re-attestation
            report = self.enclave.attest(local_hash)
            self._epoch_hash = report["policy_hash"]
            self._last_attestation = now
            return True, report["attestation_status"] == "VALID"
            
        return False, True # Didn't re-attest, but valid

    def enforce(self, constraint_func):
        """
        Decorator for agentic actions.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                action_name = func.__name__
                action_args = json.dumps({"args": args, "kwargs": kwargs}, default=str)
                
                re_attested, attestation_valid = self._verify_epoch()
                current_policies = global_policy_store.get_all()
                policy_hash = global_policy_store.get_hash()
                
                try:
                    result = constraint_func(current_policies, *args, **kwargs)
                except Exception as e:
                    global_gbom_log.append(action_name, action_args, policy_hash, "ESCALATE", attestation_valid)
                    print(f"[ESCALATE] Human override required: {e}")
                    raise
                
                if not result:
                    end_time = time.perf_counter()
                    gl = (end_time - start_time) * 1000
                    global_gbom_log.append(action_name, action_args, policy_hash, "DENY", attestation_valid)
                    raise GovernanceError(f"DENIED by EHV Invariant (GL: {gl:.4f}ms)")
                
                res = func(*args, **kwargs)
                
                end_time = time.perf_counter()
                gl = (end_time - start_time) * 1000
                global_gbom_log.append(action_name, action_args, policy_hash, "PERMIT", attestation_valid)
                return res
            return wrapper
        return decorator

    def get_gbom(self):
        return global_gbom_log.to_json()

# Shared engine instance
runtime = EHVEngine()

import atexit
atexit.register(runtime.enclave.cleanup)
