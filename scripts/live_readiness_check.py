"""Technical readiness check; it never enables live trading."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from astra.execution.gates import GateState
from astra.execution.kraken import KrakenConfig,KrakenSpot
def main():
    cfg=KrakenConfig.from_env()
    assert not cfg.live_enabled
    KrakenSpot(cfg)
    state=GateState(True,False,True,True,True,True,False,False)
    assert not state.authorize()
    print({"technical_components":"READY","live_authorization":False,"strategy_valid":False,"human_approval":False,"live_enabled":False,"withdrawal_api":False})
if __name__=="__main__": main()
