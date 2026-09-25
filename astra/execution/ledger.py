from dataclasses import dataclass
import hashlib,json

@dataclass(frozen=True)
class OrderIntent:
    intent_id:str; symbol:str; side:str; quantity:str; strategy_id:str; signal_timestamp:str
    @staticmethod
    def create(*,symbol,side,quantity,strategy_id,signal_timestamp):
        d={"symbol":symbol.upper(),"side":side.lower(),"quantity":str(quantity),"strategy_id":strategy_id,"signal_timestamp":signal_timestamp}
        return OrderIntent("intent-"+hashlib.sha256(json.dumps(d,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24],**d)

class ExecutionLedger:
    def __init__(self): self.ids=set(); self.events=[]
    def register(self,intent):
        if intent.intent_id in self.ids:return False
        self.ids.add(intent.intent_id); self.events.append({"type":"intent_created","id":intent.intent_id}); return True
