import json
import hashlib
import time
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class GBOMEntry:
    """A single Governance Bill of Materials cryptographic receipt.
    
    Per the paper (Section VII.B), each GBOM entry binds a decision to:
    1. The specific policy version (policy_hash)
    2. The TEE attestation epoch (epoch_id)
    3. The enforcement outcome (enforcement_result)
    """
    timestamp: float
    action_name: str
    action_args: str
    policy_hash: str
    epoch_id: int
    enforcement_result: str   # PERMIT | DENY | ESCALATE
    attestation_valid: bool
    prev_hash: str
    
    def get_hash(self) -> str:
        """Computes the SHA-256 hash of this entry."""
        data = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

class GBOMLog:
    """
    Append-only tamper-evident log for the Governance Bill of Materials.
    Provides a cryptographic audit trail for agent actions.
    """
    GENESIS_HASH = "0" * 64

    def __init__(self):
        self.entries: list[GBOMEntry] = []
        self._latest_hash = self.GENESIS_HASH

    def append(self, action_name: str, action_args: str, policy_hash: str,
               epoch_id: int, enforcement_result: str, attestation_valid: bool):
        entry = GBOMEntry(
            timestamp=time.time(),
            action_name=action_name,
            action_args=action_args,
            policy_hash=policy_hash,
            epoch_id=epoch_id,
            enforcement_result=enforcement_result,
            attestation_valid=attestation_valid,
            prev_hash=self._latest_hash
        )
        self.entries.append(entry)
        self._latest_hash = entry.get_hash()

    def verify_chain(self) -> bool:
        """Verifies the integrity of the hash chain."""
        expected_prev = self.GENESIS_HASH
        for entry in self.entries:
            if entry.prev_hash != expected_prev:
                return False
            expected_prev = entry.get_hash()
        return True

    def to_json(self) -> str:
        return json.dumps([asdict(e) for e in self.entries], indent=2)

# Global GBOM log for the runtime
global_gbom_log = GBOMLog()
