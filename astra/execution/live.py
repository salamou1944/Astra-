"""Evidence-gated live execution orchestration.

This module does not enable live trading by itself. Callers must explicitly
provide a fully-authorized gate and human approval. The default environment
still keeps live execution disabled.
"""
from __future__ import annotations

from decimal import Decimal

from .ledger import ExecutionLedger, OrderIntent
from .reconciliation import KrakenReconciler


class LiveExecutionError(RuntimeError):
    pass


class LiveExecutionService:
    def __init__(self, broker, gate, ledger: ExecutionLedger | None = None):
        self.broker = broker
        self.gate = gate
        self.ledger = ledger or ExecutionLedger()
        self.reconciler = KrakenReconciler(broker)

    def submit(self, *, symbol, side, quantity, strategy_id, signal_timestamp, human_approval=False):
        if not human_approval:
            raise LiveExecutionError("explicit human approval is required")

        if not self.gate.authorize():
            raise LiveExecutionError("live execution gate denied")

        intent = OrderIntent.create(
            symbol=symbol,
            side=side,
            quantity=str(quantity),
            strategy_id=strategy_id,
            signal_timestamp=signal_timestamp,
        )
        if not self.ledger.register(intent):
            raise LiveExecutionError("duplicate_order_intent")

        response = self.broker.submit_if_authorized(
            self.gate,
            pair=symbol,
            side=side,
            volume=Decimal(str(quantity)),
        )
        if not response.get("submitted"):
            raise LiveExecutionError(f"exchange_submission_blocked:{response.get('mode')}")

        result = response.get("result") or {}
        txids = result.get("txid") or []
        if len(txids) != 1 or not txids[0]:
            raise LiveExecutionError("exchange_order_id_missing_or_ambiguous")

        txid = str(txids[0])
        reconciliation = self.reconciler.order(txid, expected_volume=Decimal(str(quantity)))
        if not reconciliation.ok:
            raise LiveExecutionError(f"reconciliation_failed:{reconciliation.reason}")

        self.ledger.events.append({
            "type": "exchange_order_submitted",
            "intent_id": intent.intent_id,
            "exchange_order_id": txid,
            "status": reconciliation.status,
            "executed_volume": str(reconciliation.executed_volume),
        })
        return {
            "intent_id": intent.intent_id,
            "exchange_order_id": txid,
            "status": reconciliation.status,
            "executed_volume": str(reconciliation.executed_volume),
            "remaining_volume": str(reconciliation.remaining_volume),
        }
