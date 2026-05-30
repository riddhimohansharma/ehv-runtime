import pytest
import time
from ehv.identity.workload import SVIDManager, WorkloadIdentity

def test_issue_svid():
    manager = SVIDManager()
    svid = manager.issue_svid("twin-001", trust_domain="ehv.example", ttl=3600)
    assert isinstance(svid, WorkloadIdentity)
    assert svid.spiffe_id == "spiffe://ehv.example/twin-001"
    assert svid.trust_domain == "ehv.example"
    assert svid.ttl_seconds == 3600
    assert svid.claims["workload"] == "twin-001"

def test_validate_svid_valid():
    manager = SVIDManager()
    svid = manager.issue_svid("twin-001")
    assert manager.validate_svid(svid) is True

def test_validate_svid_expired():
    manager = SVIDManager()
    # Issue SVID with short TTL
    svid = manager.issue_svid("twin-001", ttl=5)
    # Validate with a simulated future time past the TTL
    assert manager.validate_svid(svid, current_time=time.time() + 10) is False

def test_revoke_svid():
    manager = SVIDManager()
    svid = manager.issue_svid("twin-001")
    assert manager.validate_svid(svid) is True
    
    manager.revoke_svid(svid.spiffe_id)
    assert manager.is_revoked(svid.spiffe_id) is True
    assert manager.validate_svid(svid) is False

def test_spiffe_id_format():
    manager = SVIDManager()
    svid = manager.issue_svid("twin-002", trust_domain="hospital.org")
    assert svid.spiffe_id.startswith("spiffe://")
    assert svid.spiffe_id == "spiffe://hospital.org/twin-002"
