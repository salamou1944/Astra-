# ASTRA Private Trading Bot

Executable ASTRA bot boundary.

Implemented:
- Kraken public OHLC ingestion
- fixed long-momentum 30-day signal
- deterministic paper execution
- idempotent intent ledger
- kill switch and fail-closed execution gate
- unit tests and CI paper smoke

Safety:
- live trading is OFF
- runner refuses ASTRA_LIVE_TRADING=1
- no withdrawal capability
- no profitability or alpha claim

Research and evidence remain in salamou1944/Astra. Its current research gates do not establish profitability, so this bot remains paper-only.
