import pytest
import time
from ehv.sync.store import PolicyStore


class TestPolicyStoreMonotonicity:
    """Tests that the LWW store rejects stale updates."""

    def test_reject_older_update(self):
        store = PolicyStore(node_id="test")
        ts1 = store.update("limit", 1.0)
        store.update("limit", 2.0, ts=ts1 - 100)
        assert store.get("limit") == 1.0

    def test_accept_newer_update(self):
        store = PolicyStore(node_id="test")
        store.update("limit", 1.0, ts=100)
        store.update("limit", 2.0, ts=200)
        assert store.get("limit") == 2.0

    def test_reject_equal_timestamp(self):
        store = PolicyStore(node_id="test")
        store.update("limit", 1.0, ts=100)
        store.update("limit", 2.0, ts=100)
        # Equal timestamp should be rejected (LWW: first write wins on tie)
        assert store.get("limit") == 1.0


class TestCRDTMerge:
    """Tests that merge() implements a correct Join-Semilattice."""

    def test_merge_lww_newer_wins(self):
        a = PolicyStore(node_id="A")
        b = PolicyStore(node_id="B")
        a.update("drug", 5.0, ts=100)
        b.update("drug", 10.0, ts=110)
        a.merge(b)
        assert a.get("drug") == 10.0

    def test_merge_commutativity(self):
        """CRDT requirement: merge(A,B) == merge(B,A)"""
        a = PolicyStore(node_id="A")
        b = PolicyStore(node_id="B")
        a.update("drug_x", 5.0, ts=100)
        a.update("drug_y", 20.0, ts=105)
        b.update("drug_x", 10.0, ts=110)
        b.update("drug_z", 30.0, ts=108)

        # Fork both before merging
        a1 = a.diverge("A1")
        b1 = b.diverge("B1")
        a2 = a.diverge("A2")
        b2 = b.diverge("B2")

        a1.merge(b1)
        b2.merge(a2)

        assert a1.get_all() == b2.get_all(), \
            f"Commutativity violated: {a1.get_all()} != {b2.get_all()}"

    def test_merge_idempotency(self):
        """CRDT requirement: merge(A, A) == A"""
        a = PolicyStore(node_id="A")
        a.update("drug", 5.0, ts=100)
        state_before = a.get_all()
        a.merge(a)
        assert a.get_all() == state_before

    def test_merge_associativity(self):
        """CRDT requirement: merge(merge(A,B), C) == merge(A, merge(B,C))"""
        a = PolicyStore(node_id="A")
        b = PolicyStore(node_id="B")
        c = PolicyStore(node_id="C")
        a.update("x", 1.0, ts=100)
        b.update("x", 2.0, ts=110)
        c.update("x", 3.0, ts=105)

        # (A merge B) merge C
        ab = a.diverge("AB")
        ab.merge(b)
        ab.merge(c)

        # A merge (B merge C)
        bc = b.diverge("BC")
        bc.merge(c)
        a2 = a.diverge("A2")
        a2.merge(bc)

        assert ab.get_all() == a2.get_all(), \
            f"Associativity violated: {ab.get_all()} != {a2.get_all()}"

    def test_merge_disjoint_keys(self):
        a = PolicyStore(node_id="A")
        b = PolicyStore(node_id="B")
        a.update("drug_a", 1.0, ts=100)
        b.update("drug_b", 2.0, ts=100)
        a.merge(b)
        assert a.get("drug_a") == 1.0
        assert a.get("drug_b") == 2.0


class TestConvergence:
    def test_diverge_and_converge(self):
        a = PolicyStore(node_id="A")
        a.update("limit", 1.0, ts=100)
        b = a.diverge("B")
        a.update("limit", 2.0, ts=200)
        b.update("limit", 3.0, ts=150)
        a.merge(b)
        b.merge(a)
        assert a.has_converged(b)
        assert a.get("limit") == 2.0  # ts=200 wins


class TestPolicyHash:
    def test_hash_deterministic(self):
        a = PolicyStore(node_id="A")
        a.update("x", 1.0, ts=100)
        h1 = a.get_hash()
        h2 = a.get_hash()
        assert h1 == h2

    def test_hash_changes_on_update(self):
        a = PolicyStore(node_id="A")
        a.update("x", 1.0, ts=100)
        h1 = a.get_hash()
        a.update("x", 2.0, ts=200)
        h2 = a.get_hash()
        assert h1 != h2
