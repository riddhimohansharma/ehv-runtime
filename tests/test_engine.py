import pytest
from ehv.compiler.engine import EHVEngine, GovernanceError
from ehv.compiler.gbom import GBOMLog
from ehv.enclave.enclave import Enclave
from ehv.sync.store import PolicyStore


def _make_engine():
    """Creates a fresh, isolated engine for testing (no shared state)."""
    store = PolicyStore(node_id="test")
    enclave = Enclave(memory_name="test_engine_mem", simulate_latency=False)
    gbom = GBOMLog()
    engine = EHVEngine(
        epoch_duration=60, policy_store=store,
        enclave=enclave, gbom_log=gbom)
    return engine, store, enclave, gbom


class TestEnforcementCycle:
    """Tests the full PERMIT / DENY / ESCALATE cycle."""

    def test_permit_safe_action(self):
        engine, store, enclave, gbom = _make_engine()
        try:
            store.update("limit", 10.0)

            def constraint(policies, dose):
                return dose <= policies.get("limit", 0)

            @engine.enforce(constraint)
            def prescribe(dose):
                return f"ok:{dose}"

            result = prescribe(5.0)
            assert result == "ok:5.0"
            assert gbom.entries[-1].enforcement_result == "PERMIT"
        finally:
            enclave.cleanup()

    def test_deny_unsafe_action(self):
        engine, store, enclave, gbom = _make_engine()
        try:
            store.update("limit", 2.0)

            def constraint(policies, dose):
                return dose <= policies.get("limit", 0)

            @engine.enforce(constraint)
            def prescribe(dose):
                return f"ok:{dose}"

            with pytest.raises(GovernanceError):
                prescribe(5.0)
            assert gbom.entries[-1].enforcement_result == "DENY"
        finally:
            enclave.cleanup()

    def test_escalate_on_exception(self):
        engine, store, enclave, gbom = _make_engine()
        try:
            store.update("limit", 5.0)

            def constraint(policies, dose):
                raise ValueError("Ambiguous clinical case")

            @engine.enforce(constraint)
            def prescribe(dose):
                return f"ok:{dose}"

            with pytest.raises(ValueError):
                prescribe(3.0)
            assert gbom.entries[-1].enforcement_result == "ESCALATE"
        finally:
            enclave.cleanup()


class TestFailSafe:
    """Tests TLA+ fail-safe: epochValid=FALSE → DENY all."""

    def test_deny_on_invalid_epoch(self):
        engine, store, enclave, gbom = _make_engine()
        try:
            store.update("limit", 10.0)

            def constraint(policies, dose):
                return True  # Would normally permit

            @engine.enforce(constraint)
            def prescribe(dose):
                return "ok"

            # First call succeeds (triggers attestation)
            prescribe(1.0)
            assert gbom.entries[-1].enforcement_result == "PERMIT"

            # Invalidate epoch (simulates network partition)
            engine.invalidate_epoch()

            # Now ALL actions must be DENIED regardless of constraint
            with pytest.raises(GovernanceError, match="fail-closed partition"):
                prescribe(1.0)
            assert gbom.entries[-1].enforcement_result == "DENY"
            assert gbom.entries[-1].attestation_valid is False
        finally:
            enclave.cleanup()


class TestEmergencyReset:
    """Tests EMERGENCY_EPOCH_RESET signal."""

    def test_emergency_reset_forces_reattestation(self):
        engine, store, enclave, gbom = _make_engine()
        try:
            store.update("limit", 10.0)

            def constraint(policies, dose):
                return dose <= policies.get("limit", 0)

            @engine.enforce(constraint)
            def prescribe(dose):
                return "ok"

            prescribe(5.0)  # Triggers attestation
            store.update("limit", 2.0)  # Critical update

            # Without reset, the old epoch hash is cached,
            # so 5.0 might still pass. Force reset:
            engine.emergency_epoch_reset()

            with pytest.raises(GovernanceError):
                prescribe(5.0)
        finally:
            enclave.cleanup()


class TestGBOMEpochId:
    """Tests that GBOM entries contain correct epoch_id."""

    def test_epoch_id_in_gbom(self):
        engine, store, enclave, gbom = _make_engine()
        try:
            store.update("limit", 10.0)

            def constraint(policies):
                return True

            @engine.enforce(constraint)
            def action():
                return "ok"

            action()
            assert gbom.entries[0].epoch_id >= 1
        finally:
            enclave.cleanup()
