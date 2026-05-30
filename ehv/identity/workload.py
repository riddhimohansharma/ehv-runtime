"""
Workload Identity Model (SPIFFE/SPIRE SVID Stub)
v2 identity validation model
"""

import time
from dataclasses import dataclass, field

@dataclass
class WorkloadIdentity:
    """
    SPIFFE Verifiable Identity Document (SVID) representation.
    """
    spiffe_id: str
    trust_domain: str
    ttl_seconds: int
    issued_at: float
    claims: dict = field(default_factory=dict)

    def is_expired(self, current_time: float = None) -> bool:
        """Returns True if the SVID is past its TTL."""
        now = current_time or time.time()
        return now > (self.issued_at + self.ttl_seconds)

class SVIDManager:
    """
    Simulated SPIFFE Workload API manager issuing and validating SVIDs.
    """
    def __init__(self):
        self.revoked_ids: set[str] = set()

    def issue_svid(self, workload_name: str, trust_domain: str = "ehv.example", ttl: int = 3600) -> WorkloadIdentity:
        """Issues a new WorkloadIdentity with a valid SPIFFE ID URI."""
        spiffe_id = f"spiffe://{trust_domain}/{workload_name}"
        return WorkloadIdentity(
            spiffe_id=spiffe_id,
            trust_domain=trust_domain,
            ttl_seconds=ttl,
            issued_at=time.time(),
            claims={"workload": workload_name}
        )

    def validate_svid(self, svid: WorkloadIdentity, current_time: float = None) -> bool:
        """Validates SVID expiration and revocation status."""
        if svid.spiffe_id in self.revoked_ids:
            return False
        return not svid.is_expired(current_time)

    def revoke_svid(self, spiffe_id: str) -> None:
        """Revokes a SPIFFE ID, adding it to the revocation list."""
        self.revoked_ids.add(spiffe_id)

    def is_revoked(self, spiffe_id: str) -> bool:
        """Checks if a SPIFFE ID is revoked."""
        return spiffe_id in self.revoked_ids
