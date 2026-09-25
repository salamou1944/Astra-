# ASTRA Operational Readiness

The executable bot boundary is hardened for production-style paper operation.

Implemented:
- Kraken public market-data ingestion
- deterministic strategy boundary
- paper execution with costs
- idempotent intent tracking
- risk limits and automatic halt
- Kraken authenticated adapter behind fail-closed authorization
- reconciliation and kill-switch gates
- explicit human-approval gate
- no withdrawal capability
- CI tests and paper smoke verification

Live authorization remains deliberately false. The research repository salamou1944/Astra currently records failed research/robustness gates and profitability/alpha as UNVERIFIED. Therefore no technical implementation may represent the system as proven profitable or live-ready.

The required live transition is evidence-gated: DATA_VALID, STRATEGY_VALID, RISK_VALID, EXECUTION_VALID, RECONCILIATION_VALID, KILL_SWITCH_VALID, explicit HUMAN_APPROVAL, and LIVE_ENABLED must all be true. No gate is inferred automatically.
