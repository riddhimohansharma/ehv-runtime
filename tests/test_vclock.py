import pytest
from ehv.sync.vclock import VectorClock
from ehv.sync.store import CausalPolicyStore

def test_increment():
    vc = VectorClock()
    assert vc.to_dict() == {}
    vc.increment("node1")
    assert vc.to_dict() == {"node1": 1}
    vc.increment("node1")
    assert vc.to_dict() == {"node1": 2}
    vc.increment("node2")
    assert vc.to_dict() == {"node1": 2, "node2": 1}

def test_merge():
    vc1 = VectorClock({"node1": 1, "node2": 3})
    vc2 = VectorClock({"node2": 2, "node3": 4})
    merged = vc1.merge(vc2)
    assert merged.to_dict() == {"node1": 1, "node2": 3, "node3": 4}

def test_happens_before():
    vc1 = VectorClock({"node1": 1, "node2": 2})
    vc2 = VectorClock({"node1": 1, "node2": 3})
    assert vc1.happens_before(vc2) is True
    assert vc2.happens_before(vc1) is False

    # Equal clocks do not happen before
    assert vc1.happens_before(vc1) is False

    # Concurrent clocks
    vc3 = VectorClock({"node1": 2, "node2": 1})
    assert vc1.happens_before(vc3) is False
    assert vc3.happens_before(vc1) is False

def test_concurrent():
    vc1 = VectorClock({"node1": 1, "node2": 2})
    vc2 = VectorClock({"node2": 3}) # node1: 0, node2: 3
    # vc1 has node1: 1, node2: 2. vc2 has node1: 0, node2: 3.
    # vc1 has higher node1, vc2 has higher node2.
    assert vc1.is_concurrent(vc2) is True
    assert vc2.is_concurrent(vc1) is True

    vc3 = VectorClock({"node1": 1, "node2": 3})
    assert vc1.is_concurrent(vc3) is False # vc1 happens before vc3

def test_causal_policy_store_update():
    store = CausalPolicyStore(node_id="nodeA")
    vc1 = store.update("key1", "val1")
    assert vc1.to_dict() == {"nodeA": 1}
    assert store.get("key1") == "val1"

    # Subsequent update increments clock
    vc2 = store.update("key1", "val2")
    assert vc2.to_dict() == {"nodeA": 2}
    assert store.get("key1") == "val2"

def test_causal_policy_store_merge():
    storeA = CausalPolicyStore(node_id="nodeA")
    storeB = CausalPolicyStore(node_id="nodeB")

    storeA.update("limit", 1.5) # clock for storeA is {"nodeA": 1}
    storeB.update("limit", 0.75) # clock for storeB is {"nodeB": 1}

    # Merging B into A
    # Since clocks are concurrent, we resolve via lexicographic tie-breaker on value
    # str("1.5") vs str("0.75"). "1.5" > "0.75" lexicographically, so "1.5" wins.
    # Clock becomes {"nodeA": 1, "nodeB": 1}
    storeA.merge(storeB)
    assert storeA.get("limit") == 1.5
    
    # Merge A into B
    storeB.merge(storeA)
    assert storeB.get("limit") == 1.5

def test_causal_store_commutativity():
    # Merge(A, B) == Merge(B, A)
    storeA = CausalPolicyStore(node_id="nodeA")
    storeB = CausalPolicyStore(node_id="nodeB")

    storeA.update("limit", 1.5)
    storeB.update("limit", 0.75)

    storeA.merge(storeB)
    stateA = storeA.get_all()

    # Reset B and merge
    storeB_reset = CausalPolicyStore(node_id="nodeB")
    storeB_reset.update("limit", 0.75)
    
    storeA_reset = CausalPolicyStore(node_id="nodeA")
    storeA_reset.update("limit", 1.5)

    storeB_reset.merge(storeA_reset)
    stateB = storeB_reset.get_all()

    assert stateA == stateB

def test_causal_store_idempotency():
    # Merge(A, A) == A
    store = CausalPolicyStore(node_id="nodeA")
    store.update("limit", 1.5)
    
    state_before = store.get_all()
    store.merge(store)
    state_after = store.get_all()
    
    assert state_before == state_after

def test_clock_skew_resistance():
    storeA = CausalPolicyStore(node_id="nodeA")
    storeB = CausalPolicyStore(node_id="nodeB")

    # Local update on A
    vcA = storeA.update("limit", 1.5) # {"nodeA": 1}

    # B gets a forged physical update but we are using vector clocks
    # B does some local updates:
    vcB = storeB.update("limit", 0.75) # {"nodeB": 1}

    # Now storeA updates "limit" to 2.0 (causally after limit=1.5)
    vcA2 = storeA.update("limit", 2.0) # {"nodeA": 2}

    # If we merge B into A, vcB is concurrent with vcA2.
    # "2.0" vs "0.75". "2.0" > "0.75". "2.0" wins.
    storeA.merge(storeB)
    assert storeA.get("limit") == 2.0
