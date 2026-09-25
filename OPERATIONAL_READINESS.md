# ASTRA Operational Readiness

The executable bot boundary is hardened for production-style paper operation and contains a fail-closed path for future Kraken Spot live execution.

Implemented:
- Kraken public market-data ingestion
- deterministic strategy boundary
- paper execution with costs
- idempotent intent tracking
- risk limits and automatic halt
- authenticated Kraken adapter for account/order operations
- exchange-truth order reconciliation
- live execution orchestration behind authorization gates
- explicit human-approval gate
- no withdrawal capability
- CI tests and paper smoke verification

Live authorization remains deliberately false. The research repository salamou1944/Astra records research/robustness and profitability gates that must be proven independently before live operation is considered.

Required live transition:
DATA_VALID, STRATEGY_VALID, RISK_VALID, EXECUTION_VALID, RECONCILIATION_VALID, KILL_SWITCH_VALID, explicit HUMAN_APPROVAL, and LIVE_ENABLED must all be true.

Additional execution invariants:
- one deterministic intent maps to at most one exchange submission
- a successful submission must contain exactly one exchange order ID
- exchange order state, not local state, is authoritative for reconciliation
- executed volume may not exceed the requested intent
- withdrawal endpoints are absent
- default configuration keeps live execution disabled

This repository does not claim profitability, alpha, or live readiness merely because the Kraken adapter exists.
