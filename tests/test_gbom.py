import pytest
from ehv.compiler.gbom import GBOMLog


class TestGBOMChain:
    def test_chain_integrity(self):
        log = GBOMLog()
        log.append("a1", "{}", "h1", 1, "PERMIT", True)
        log.append("a2", "{}", "h2", 1, "DENY", True)
        assert log.verify_chain() is True

    def test_tamper_detection(self):
        log = GBOMLog()
        log.append("a1", "{}", "h1", 1, "PERMIT", True)
        log.append("a2", "{}", "h2", 1, "DENY", True)
        log.entries[0].enforcement_result = "TAMPERED"
        assert log.verify_chain() is False

    def test_empty_chain(self):
        log = GBOMLog()
        assert log.verify_chain() is True

    def test_epoch_id_recorded(self):
        log = GBOMLog()
        log.append("a1", "{}", "h1", 42, "PERMIT", True)
        assert log.entries[0].epoch_id == 42

    def test_json_roundtrip(self):
        import json
        log = GBOMLog()
        log.append("a1", "{}", "h1", 1, "PERMIT", True)
        parsed = json.loads(log.to_json())
        assert len(parsed) == 1
        assert parsed[0]["epoch_id"] == 1
        assert parsed[0]["enforcement_result"] == "PERMIT"
