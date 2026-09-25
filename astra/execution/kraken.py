"""Fail-closed Kraken Spot adapter. Withdrawal endpoints are intentionally absent."""
from __future__ import annotations
import base64,hashlib,hmac,json,os,time
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request,urlopen
@dataclass(frozen=True)
class KrakenConfig:
    api_key:str=""; api_secret:str=""; live_enabled:bool=False
    base_url:str="https://api.kraken.com"; timeout:float=10
    @classmethod
    def from_env(cls): return cls(os.getenv("ASTRA_KRAKEN_API_KEY",""),os.getenv("ASTRA_KRAKEN_API_SECRET",""),os.getenv("ASTRA_LIVE_TRADING","0")=="1")
class KrakenError(RuntimeError): pass
class KrakenSpot:
    def __init__(self,cfg):
        self.cfg=cfg
        if cfg.live_enabled and (not cfg.api_key or not cfg.api_secret): raise KrakenError("live execution requires API credentials")
    def _sig(self,path,nonce,payload):
        data=urlencode(payload); msg=path.encode()+hashlib.sha256((nonce+data).encode()).digest()
        return base64.b64encode(hmac.new(base64.b64decode(self.cfg.api_secret),msg,hashlib.sha512).digest()).decode()
    def _private(self,path,payload):
        if not self.cfg.live_enabled: raise KrakenError("live execution is OFF")
        nonce=str(time.time_ns()//1000000); body=dict(payload,nonce=nonce)
        req=Request(self.cfg.base_url+path,data=urlencode(body).encode(),method="POST",headers={"API-Key":self.cfg.api_key,"API-Sign":self._sig(path,nonce,body)})
        with urlopen(req,timeout=self.cfg.timeout) as r: out=json.loads(r.read().decode())
        if out.get("error"): raise KrakenError("; ".join(map(str,out["error"])))
        return out.get("result",{})
    def balance(self): return self._private("/0/private/Balance",{})
    def open_orders(self): return self._private("/0/private/OpenOrders",{})
    def query_orders(self,txid=None): return self._private("/0/private/QueryOrders",{} if txid is None else {"txid":txid})
    def cancel_order(self,txid): return self._private("/0/private/CancelOrder",{"txid":txid})
    def build_order(self,*,pair,side,volume,ordertype="market",price=None):
        if side not in {"buy","sell"} or float(volume)<=0: raise ValueError("invalid order")
        if ordertype not in {"market","limit"}: raise ValueError("invalid order type")
        if ordertype=="limit" and (price is None or float(price)<=0): raise ValueError("limit price required")
        d={"pair":pair,"type":side,"ordertype":ordertype,"volume":str(volume)}
        if price is not None:d["price"]=str(price)
        return d
    def submit_if_authorized(self,gate,**order):
        if not self.cfg.live_enabled:return {"submitted":False,"mode":"OFF"}
        if not gate.authorize():return {"submitted":False,"mode":"LIVE_BLOCKED"}
        return {"submitted":True,"mode":"LIVE_SPOT","result":self._private("/0/private/AddOrder",self.build_order(**order))}
