# ASTRA Private Trading Bot

Executable ASTRA bot boundary.

Implemented:
- Kraken public OHLC ingestion
- fixed long-momentum 30-day signal
- deterministic paper execution
- idempotent intent ledger
- kill switch and fail-closed execution gate
- authenticated Kraken Spot adapter for Balance/OpenOrders/QueryOrders/CancelOrder/AddOrder
- exchange-truth reconciliation for live orders
- evidence-gated live execution orchestration
- explicit human approval requirement
- no withdrawal capability
- unit tests and CI paper smoke

Safety:
- live trading remains OFF by default
- the paper runner refuses live mode
- live execution cannot proceed unless every authorization gate passes
- exchange order IDs and execution state must be reconciled before success is recorded
- no profitability or alpha claim

Research and evidence remain in salamou1944/Astra. Its current research gates do not establish profitability, so this bot remains paper-only until those gates and the operational gates are independently proven.
