import unittest
from decimal import Decimal
from astra.execution.live import LiveExecutionError, LiveExecutionService
from astra.execution.reconciliation import KrakenReconciler


class FakeGate:
    def __init__(self, allowed=True):
        self.allowed = allowed

    def authorize(self):
        return self.allowed


class FakeBroker:
    def __init__(self, txid="OID-1"):
        self.txid = txid

    def submit_if_authorized(self, gate, **order):
        if not gate.authorize():
            return {"submitted": False, "mode": "LIVE_BLOCKED"}
        return {"submitted": True, "mode": "LIVE_SPOT", "result": {"txid": [self.txid]}}

    def query_orders(self, txid):
        return {"orders": {txid: {"status": "closed", "vol": "0.001", "vol_exec": "0.001"}}}

    def open_orders(self):
        return {"open": {}}


class LiveExecutionTests(unittest.TestCase):
    def test_human_approval_required(self):
        service = LiveExecutionService(FakeBroker(), FakeGate())
        with self.assertRaisesRegex(LiveExecutionError, "human approval"):
            service.submit(
                symbol="XBTUSD", side="buy", quantity=Decimal("0.001"),
                strategy_id="test", signal_timestamp="2026-01-01T00:00:00+00:00",
                human_approval=False,
            )

    def test_gate_required(self):
        service = LiveExecutionService(FakeBroker(), FakeGate(False))
        with self.assertRaisesRegex(LiveExecutionError, "gate denied"):
            service.submit(
                symbol="XBTUSD", side="buy", quantity=Decimal("0.001"),
                strategy_id="test", signal_timestamp="2026-01-01T00:00:00+00:00",
                human_approval=True,
            )

    def test_duplicate_intent_blocked(self):
        service = LiveExecutionService(FakeBroker(), FakeGate())
        kwargs = dict(
            symbol="XBTUSD", side="buy", quantity=Decimal("0.001"),
            strategy_id="test", signal_timestamp="2026-01-01T00:00:00+00:00",
            human_approval=True,
        )
        first = service.submit(**kwargs)
        self.assertEqual(first["exchange_order_id"], "OID-1")
        with self.assertRaisesRegex(LiveExecutionError, "duplicate"):
            service.submit(**kwargs)

    def test_reconciliation_uses_exchange_truth(self):
        reconciler = KrakenReconciler(FakeBroker())
        result = reconciler.order("OID-1", expected_volume=Decimal("0.001"))
        self.assertTrue(result.ok)
        self.assertEqual(result.status, "closed")
        self.assertEqual(result.executed_volume, Decimal("0.001"))


if __name__ == "__main__":
    unittest.main()
