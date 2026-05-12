import pytest
from ehv.compiler.gbom import GBOMLog

def test_gbom_chain_integrity():
    log = GBOMLog()
    
    log.append("action1", "{}", "hash1", "PERMIT", True)
    log.append("action2", "{}", "hash2", "DENY", True)
    
    assert log.verify_chain() is True
    
    # Tamper with the log
    log.entries[0].enforcement_result = "TAMPERED"
    assert log.verify_chain() is False
