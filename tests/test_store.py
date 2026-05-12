import pytest
import time
from ehv.sync.store import PolicyStore

def test_store_monotonicity():
    store = PolicyStore(node_id="test")
    ts1 = store.update("limit", 1.0)
    
    # Simulate older update arriving late
    ts_old = ts1 - 100
    store.update("limit", 2.0, ts=ts_old)
    
    # Should still be 1.0 because 2.0 was older
    assert store.get("limit") == 1.0

def test_store_merge():
    node_a = PolicyStore(node_id="A")
    node_b = PolicyStore(node_id="B")
    
    node_a.update("drug_x", 5.0, ts=100)
    node_b.update("drug_x", 10.0, ts=110)
    
    node_a.merge(node_b)
    
    # LWW wins
    assert node_a.get("drug_x") == 10.0
