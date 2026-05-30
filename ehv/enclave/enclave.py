import time
import hashlib
import json
import base64
import hmac
from multiprocessing import shared_memory

class Enclave:
    """
    Simulates a Trusted Execution Environment (TEE) like Intel SGX / TDX.
    Uses Python's SharedMemory to simulate isolated enclave memory accessible
    by the PEP JIT compiler.
    
    Architecture Notes:
    - SharedMemory provides process-level isolation (simulates enclave memory)
    - attest() simulates remote attestation with 200ms round-trip
    - verify_epoch() provides O(1) hot-path hash comparison
    - seal()/unseal() simulate SGX sealing with HMAC authentication
    """
    def __init__(self, memory_name="ehv_enclave_mem", size=256,
                 simulate_latency=True):
        self.memory_name = memory_name
        self.size = size
        self.secret_key = b"simulate_hardware_root_key"
        self.simulate_latency = simulate_latency
        self._attestation_count = 0
        
        try:
            self.shm = shared_memory.SharedMemory(
                name=self.memory_name, create=True, size=self.size)
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=self.memory_name)

    def attest(self, policy_hash):
        """
        Simulates remote attestation (e.g. 200ms roundtrip).
        Writes the validated policy hash into the isolated shared memory buffer.
        Returns attestation report with status.
        """
        if self.simulate_latency:
            time.sleep(0.2)
        
        self._attestation_count += 1
        
        # Write hash to shared memory (padded to 64 bytes for SHA-256 hex)
        hash_bytes = policy_hash.encode('utf-8').ljust(64, b'\x00')
        self.shm.buf[:64] = hash_bytes
        
        return {
            "attestation_status": "VALID",
            "policy_hash": policy_hash,
            "epoch_id": self._attestation_count,
            "epoch_timestamp": time.time(),
            "hardware": "Simulated-TEE",
            "measurement": "sevsnp:mrenclave:def456f81d4fae7dec11d0a76500a0c9"
        }

    def invalidate(self):
        """
        Simulates epoch invalidation (e.g., due to network partition).
        Zeroes the shared memory buffer so verify_epoch() will fail.
        """
        self.shm.buf[:64] = b'\x00' * 64

    def verify_epoch(self, local_hash):
        """
        O(1) hot-path verification. Reads the validated hash from shared memory
        and compares it to the local hash.
        """
        enclave_hash_bytes = bytes(self.shm.buf[:64])
        enclave_hash = enclave_hash_bytes.rstrip(b'\x00').decode('utf-8')
        return local_hash == enclave_hash

    def seal(self, data):
        """Simulates SGX sealing (encrypting data for enclave-only access)."""
        data_bytes = json.dumps(data).encode('utf-8')
        tag = hmac.new(self.secret_key, data_bytes, hashlib.sha256).digest()
        sealed = base64.b64encode(tag + data_bytes).decode('utf-8')
        return sealed

    def unseal(self, sealed_data):
        """Simulates SGX unsealing."""
        try:
            raw = base64.b64decode(sealed_data.encode('utf-8'))
            tag, data_bytes = raw[:32], raw[32:]
            expected_tag = hmac.new(
                self.secret_key, data_bytes, hashlib.sha256).digest()
            if hmac.compare_digest(tag, expected_tag):
                return json.loads(data_bytes.decode('utf-8'))
            raise ValueError("Integrity check failed")
        except Exception:
            raise ValueError("Invalid sealed data")

    def cleanup(self):
        """Releases the shared memory buffer."""
        self.shm.close()
        try:
            self.shm.unlink()
        except FileNotFoundError:
            pass
