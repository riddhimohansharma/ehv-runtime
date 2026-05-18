import atexit
import time
import functools
import json
from ..sync.store import PolicyStore, global_policy_store
from ..enclave.enclave import Enclave
from .gbom import global_gbom_log


class GovernanceError(Exception):
    """Raised when an agent action violates a policy invariant."""
    pass


class EHVEngine:
    """
    Pillar 3: The Policy Enforcement Point (PEP) in JIT
    
    Provides the governance-aware hook for agentic actions.
    Implements the TLA+ Enforce action: evaluates (action, constraints)
    and returns PERMIT | DENY | ESCALATE.
    
    Matches TLA+ behaviour:
      - epochValid=FALSE → DENY all (fail-safe, line 87-89 of EHV.tla)
      - epochValid=TRUE + UnsafeAction → DENY
      - epochValid=TRUE + SafeAction → PERMIT
      - constraint_func raises → ESCALATE
    """

    def __init__(self, epoch_duration=60, policy_store=None,
                 enclave=None, gbom_log=None):
        self.epoch_duration = epoch_duration
        self._last_attestation = 0
        self._epoch_hash = None
        self._epoch_id = 0
        self._epoch_valid = False  # Start invalid; first action triggers attestation

        # Dependency injection (MAJOR-2 fix)
        self.policy_store = policy_store or global_policy_store
        self.enclave = enclave or Enclave()
        self.gbom_log = gbom_log or global_gbom_log

    def _verify_epoch(self):
        """
        Pillar 2: Epoch-based Attestation Caching
        
        Returns (re_attested: bool, attestation_valid: bool)
        
        Per the paper:
          Verify(a) = O(1) if H_p^local == H_p^epoch
                    = Re-attest otherwise
        """
        now = time.time()
        local_hash = self.policy_store.get_hash()

        # Case 1: Epoch expired or first run → must re-attest
        if (now - self._last_attestation > self.epoch_duration
                or self._epoch_hash is None):
            # Attempt re-attestation
            success, valid = self._do_attestation(local_hash, now)
            if not success:
                # Network partition / cannot reach attestation broker.
                # Must explicitly fail-closed.
                self._epoch_valid = False
                return False, False
            return success, valid

        # Case 2: Epoch still valid → O(1) hot-path comparison
        if not self._epoch_valid:
            # Epoch was invalidated (e.g., network partition)
            # TLA+ line 87-89: deny by default
            return False, False

        is_valid = self.enclave.verify_epoch(local_hash)
        if not is_valid:
            # Hash mismatch → policy changed mid-epoch → force re-attestation
            return self._do_attestation(local_hash, now)

        return False, True  # Hot-path: no re-attestation needed, epoch valid

    def _do_attestation(self, policy_hash, now):
        """Performs remote attestation and updates epoch state."""
        try:
            report = self.enclave.attest(policy_hash)
            self._epoch_hash = report["policy_hash"]
            self._epoch_id = report["epoch_id"]
            self._last_attestation = now
            self._epoch_valid = report["attestation_status"] == "VALID"
            return True, self._epoch_valid
        except Exception:
            # Simulate failure to reach KBS (Key Broker Service)
            return False, False

    def emergency_epoch_reset(self):
        """
        EMERGENCY_EPOCH_RESET signal (Paper Section VI.D).
        Forces immediate re-attestation, reducing ESW to
        network propagation latency (<1s).
        """
        local_hash = self.policy_store.get_hash()
        self._do_attestation(local_hash, time.time())

    def invalidate_epoch(self):
        """
        Simulates epoch invalidation due to network partition.
        Matches TLA+ NetworkPartition action: epochValid' = FALSE
        """
        self._epoch_valid = False
        self.enclave.invalidate()

    def enforce(self, constraint_func):
        """
        Decorator for agentic actions.
        Implements G(a, C) ∈ {PERMIT, DENY, ESCALATE}
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                action_name = func.__name__
                action_args = json.dumps(
                    {"args": args, "kwargs": kwargs}, default=str)

                re_attested, attestation_valid = self._verify_epoch()
                policy_hash = self.policy_store.get_hash()

                # CRITICAL-1 fix: TLA+ fail-safe (line 87-89)
                # If epoch is invalid, DENY all actions regardless of constraint
                if not attestation_valid:
                    self.gbom_log.append(
                        action_name, action_args, policy_hash,
                        self._epoch_id, "DENY", False)
                    # Task 1: Strict Fail-Closed Partition Semantics
                    raise GovernanceError(
                        "DENIED: Epoch attestation invalid (fail-closed partition)")

                current_policies = self.policy_store.get_all()

                try:
                    result = constraint_func(current_policies, *args, **kwargs)
                except Exception as e:
                    self.gbom_log.append(
                        action_name, action_args, policy_hash,
                        self._epoch_id, "ESCALATE", attestation_valid)
                    raise

                if not result:
                    end_time = time.perf_counter()
                    gl = (end_time - start_time) * 1000
                    self.gbom_log.append(
                        action_name, action_args, policy_hash,
                        self._epoch_id, "DENY", attestation_valid)
                    raise GovernanceError(
                        f"DENIED by EHV Invariant (GL: {gl:.4f}ms)")

                res = func(*args, **kwargs)

                end_time = time.perf_counter()
                gl = (end_time - start_time) * 1000
                self.gbom_log.append(
                    action_name, action_args, policy_hash,
                    self._epoch_id, "PERMIT", attestation_valid)
                return res
            return wrapper
        return decorator

    def get_gbom(self):
        return self.gbom_log.to_json()


# Shared engine instance
runtime = EHVEngine()

atexit.register(runtime.enclave.cleanup)
