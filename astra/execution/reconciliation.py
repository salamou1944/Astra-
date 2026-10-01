"""Fail-closed reconciliation for Kraken Spot execution.

No local state is treated as authoritative. Exchange responses are the source of
truth for order state, and mismatches block further live execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ReconciliationResult:
    ok: bool
    reason: str
    order_id: str | None = None
    status: str | None = None
    executed_volume: Decimal = Decimal("0")
    remaining_volume: Decimal = Decimal("0")


class KrakenReconciler:
    TERMINAL = {"closed", "canceled", "expired", "rejected"}

    def __init__(self, broker):
        self.broker = broker

    def order(self, txid: str, *, expected_volume: Decimal | None = None) -> ReconciliationResult:
        if not txid:
            return ReconciliationResult(False, "missing_exchange_order_id")

        result = self.broker.query_orders(txid)
        orders = result.get("orders") or {}
        raw = orders.get(txid)

        # Kraken may return a single key even when the requested identifier is
        # represented in a normalized form. Never accept an unrelated order.
        if raw is None and len(orders) == 1:
            candidate_id, candidate = next(iter(orders.items()))
            if candidate_id == txid:
                raw = candidate

        if not isinstance(raw, dict):
            return ReconciliationResult(False, "exchange_order_not_found", txid)

        status = str(raw.get("status", "")).lower()
        if not status:
            return ReconciliationResult(False, "exchange_order_status_missing", txid)

        try:
            executed = Decimal(str(raw.get("vol_exec", "0")))
            remaining = Decimal(str(raw.get("vol", "0"))) - executed
        except Exception:
            return ReconciliationResult(False, "invalid_exchange_volume", txid)

        if executed < 0 or remaining < 0:
            return ReconciliationResult(False, "invalid_exchange_volume", txid, status)

        if expected_volume is not None and executed > Decimal(str(expected_volume)):
            return ReconciliationResult(False, "executed_volume_exceeds_intent", txid, status, executed, remaining)

        if status not in self.TERMINAL:
            return ReconciliationResult(True, "order_open", txid, status, executed, remaining)

        return ReconciliationResult(True, "order_reconciled", txid, status, executed, remaining)

    def open_orders_snapshot(self):
        result = self.broker.open_orders()
        orders = result.get("open") or {}
        if not isinstance(orders, dict):
            raise RuntimeError("invalid_open_orders_response")
        return orders
