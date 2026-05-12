import pytest
from ehv.enclave.enclave import Enclave


class TestAttestation:
    def test_attest_and_verify(self):
        enclave = Enclave(memory_name="test_attest", simulate_latency=False)
        try:
            report = enclave.attest("abc123")
            assert report["attestation_status"] == "VALID"
            assert report["policy_hash"] == "abc123"
            assert report["epoch_id"] == 1
            assert enclave.verify_epoch("abc123") is True
            assert enclave.verify_epoch("wrong") is False
        finally:
            enclave.cleanup()

    def test_epoch_id_increments(self):
        enclave = Enclave(memory_name="test_epoch_id", simulate_latency=False)
        try:
            r1 = enclave.attest("h1")
            r2 = enclave.attest("h2")
            assert r2["epoch_id"] == r1["epoch_id"] + 1
        finally:
            enclave.cleanup()

    def test_invalidate(self):
        enclave = Enclave(memory_name="test_invalidate", simulate_latency=False)
        try:
            enclave.attest("abc123")
            assert enclave.verify_epoch("abc123") is True
            enclave.invalidate()
            assert enclave.verify_epoch("abc123") is False
        finally:
            enclave.cleanup()


class TestSealing:
    def test_seal_unseal_roundtrip(self):
        enclave = Enclave(memory_name="test_seal", simulate_latency=False)
        try:
            data = {"secret": "clinical_key", "value": 42}
            sealed = enclave.seal(data)
            unsealed = enclave.unseal(sealed)
            assert unsealed == data
        finally:
            enclave.cleanup()

    def test_tamper_detection(self):
        enclave = Enclave(memory_name="test_tamper", simulate_latency=False)
        try:
            sealed = enclave.seal({"secret": "x"})
            tampered = sealed[:-1] + ("A" if sealed[-1] != "A" else "B")
            with pytest.raises(ValueError):
                enclave.unseal(tampered)
        finally:
            enclave.cleanup()
