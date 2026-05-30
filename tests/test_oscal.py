import os
import pytest
from ehv.compiler.gbom import GBOMLog

def test_to_oscal_structure():
    log = GBOMLog()
    log.append("prescribe", '{"dose": 1.0}', "hash123", 1, "PERMIT", True, "sevsnp:measurement")
    
    oscal_dict = log.to_oscal()
    assert isinstance(oscal_dict, dict)
    assert "assessment-results" in oscal_dict

def test_oscal_has_required_fields():
    log = GBOMLog()
    log.append("prescribe", '{"dose": 1.0}', "hash123", 1, "PERMIT", True, "sevsnp:measurement")
    
    oscal_dict = log.to_oscal()
    # Check both root and nested formats for robust verification
    assert "uuid" in oscal_dict
    assert "metadata" in oscal_dict
    assert "results" in oscal_dict

    nested = oscal_dict["assessment-results"]
    assert "uuid" in nested
    assert "metadata" in nested
    assert "results" in nested

def test_oscal_entry_has_props():
    log = GBOMLog()
    log.append("prescribe", '{"dose": 1.0}', "hash123", 1, "PERMIT", True, "sevsnp:measurement")
    
    oscal_dict = log.to_oscal()
    results = oscal_dict["results"]
    assert len(results) == 1
    
    props = {p["name"]: p["value"] for p in results[0]["props"]}
    assert props["policy_version"] == "hash123"
    assert props["tee_measurement"] == "sevsnp:measurement"
    assert props["enforcement"] == "PERMIT"
    assert props["epoch_id"] == "1"

def test_export_oscal_writes_file(tmp_path):
    log = GBOMLog()
    log.append("prescribe", '{"dose": 1.0}', "hash123", 1, "PERMIT", True, "sevsnp:measurement")
    
    out_file = tmp_path / "oscal_gbom.json"
    log.export_oscal(str(out_file))
    
    assert os.path.exists(out_file)
    with open(out_file) as f:
        import json
        data = json.load(f)
        assert "assessment-results" in data

def test_oscal_status_mapping():
    log = GBOMLog()
    log.append("prescribe_permit", "{}", "hash1", 1, "PERMIT", True)
    log.append("prescribe_deny", "{}", "hash1", 1, "DENY", True)
    log.append("prescribe_escalate", "{}", "hash1", 1, "ESCALATE", True)
    
    oscal_dict = log.to_oscal()
    results = oscal_dict["results"]
    
    assert results[0]["status"] == "pass"
    assert results[1]["status"] == "fail"
    assert results[2]["status"] == "fail"
