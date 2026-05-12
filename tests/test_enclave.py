import pytest
from ehv.enclave.enclave import Enclave

def test_enclave_attestation_and_verify():
    enclave = Enclave(memory_name="test_enclave_mem", size=256)
    
    try:
        policy_hash = "abc123hash"
        
        # Attest writes to shared memory
        report = enclave.attest(policy_hash)
        assert report["attestation_status"] == "VALID"
        assert report["policy_hash"] == policy_hash
        
        # Verify epoch reads from shared memory (should be True)
        assert enclave.verify_epoch(policy_hash) is True
        
        # Verify mismatch (should be False)
        assert enclave.verify_epoch("wronghash") is False
    finally:
        enclave.cleanup()

def test_enclave_sealing():
    enclave = Enclave(memory_name="test_enclave_seal", size=256)
    try:
        data = {"secret": "clinical_key"}
        sealed = enclave.seal(data)
        
        unsealed = enclave.unseal(sealed)
        assert unsealed["secret"] == "clinical_key"
        
        # Tamper test
        with pytest.raises(ValueError):
            enclave.unseal(sealed[:-1] + ("A" if sealed[-1] != "A" else "B"))
    finally:
        enclave.cleanup()
