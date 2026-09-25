from __future__ import annotations
import json,os
from datetime import datetime,timezone
from decimal import Decimal
from urllib.request import Request,urlopen
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from astra.core import Bar
from astra.strategies import long_momentum
from astra.execution.paper import PaperBroker
from astra.execution.safety import KillSwitch,ExecutionGate
from astra.execution.ledger import OrderIntent,ExecutionLedger

URL="https://api.kraken.com/0/public/OHLC"; PAIR="XBTUSD"; WINDOW=30

def fetch_ohlc():
    req=Request(f"{URL}?pair={PAIR}&interval=1440",headers={"User-Agent":"ASTRA-private-bot/1.0"})
    with urlopen(req,timeout=15) as r: p=json.loads(r.read().decode())
    if p.get("error"): raise RuntimeError("; ".join(map(str,p["error"])))
    key=next(k for k in p["result"] if k!="last"); rows=p["result"][key]
    bars=[Bar(int(x[0]),float(x[4])) for x in rows]
    if len(bars)<WINDOW+2: raise RuntimeError("insufficient market data")
    return bars

def run_once(previous_signal=0,quantity=Decimal("0.001"),bars=None):
    bars=bars or fetch_ohlc(); sig=int(long_momentum(bars,WINDOW,0)[-1]); last=bars[-1]
    broker=PaperBroker(); ledger=ExecutionLedger(); kill=KillSwitch(); gate=ExecutionGate(kill)
    intent=None; order=None
    if sig!=previous_signal and sig==1:
        intent=OrderIntent.create(symbol=PAIR,side="buy",quantity=str(quantity),strategy_id="long_momentum_w30_t0",signal_timestamp=datetime.fromtimestamp(last.t,tz=timezone.utc).isoformat())
        if ledger.register(intent):
            order=broker.submit(symbol=PAIR,side="buy",quantity=quantity); broker.advance(symbol=PAIR,market_price=last.close)
    live=gate.authorize(data_valid=True,strategy_valid=False,risk_valid=True,execution_valid=True,reconciliation_valid=True,human_approval=False,live_enabled=False)
    if live: raise AssertionError("live authorization must remain impossible")
    return {"mode":"PAPER","pair":PAIR,"observed_bars":len(bars),"last_price":str(last.close),"signal":sig,"intent_id":intent.intent_id if intent else None,"order_id":order.order_id if order else None,"order_status":order.status.value if order else None,"paper_position":str(broker.positions.get(PAIR,Decimal("0"))),"paper_cash":str(broker.cash),"live_order_submitted":False,"kill_switch_halted":kill.halted}

def main():
    if os.getenv("ASTRA_LIVE_TRADING","0")=="1": raise SystemExit("ASTRA bot refuses live mode")
    d=run_once(previous_signal=int(os.getenv("ASTRA_PREVIOUS_SIGNAL","0")))
    p=Path("evidence/astra_bot_snapshot.json"); p.parent.mkdir(exist_ok=True); p.write_text(json.dumps(d,indent=2)+"\n"); print(json.dumps(d,indent=2))

if __name__=="__main__": main()
