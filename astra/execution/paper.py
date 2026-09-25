from dataclasses import dataclass,field
from decimal import Decimal
from enum import Enum

class OrderStatus(str,Enum):
    ACCEPTED="accepted"; FILLED="filled"; REJECTED="rejected"

@dataclass
class PaperOrder:
    order_id:str; symbol:str; side:str; quantity:Decimal; status:OrderStatus=OrderStatus.ACCEPTED; filled:Decimal=Decimal("0")

@dataclass
class PaperBroker:
    cash:Decimal=Decimal("10000"); fee_rate:Decimal=Decimal("0.0005"); slippage_bps:Decimal=Decimal("2"); orders:dict=field(default_factory=dict); positions:dict=field(default_factory=dict); seq:int=0
    def submit(self,*,symbol,side,quantity):
        q=Decimal(str(quantity)); side=side.lower()
        if side!="buy" or q<=0: return PaperOrder("rejected",symbol,side,q,OrderStatus.REJECTED)
        self.seq+=1; o=PaperOrder(f"paper-{self.seq:08d}",symbol,side,q); self.orders[o.order_id]=o; return o
    def advance(self,*,symbol,market_price):
        px=Decimal(str(market_price)); changed=[]
        for o in self.orders.values():
            if o.status is not OrderStatus.ACCEPTED or o.symbol!=symbol: continue
            fp=px*(1+self.slippage_bps/Decimal("10000")); fee=o.quantity*fp*self.fee_rate
            if self.cash < o.quantity*fp+fee: o.status=OrderStatus.REJECTED; changed.append(o); continue
            self.cash-=o.quantity*fp+fee; self.positions[symbol]=self.positions.get(symbol,Decimal("0"))+o.quantity; o.filled=o.quantity; o.status=OrderStatus.FILLED; changed.append(o)
        return changed
