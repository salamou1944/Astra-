import unittest,os
from astra.execution.gates import GateState
from astra.execution.kraken import KrakenConfig,KrakenSpot,KrakenError
from astra.risk import RiskGuardian
class SafetyTests(unittest.TestCase):
 def test_all_gates_required(self):
  self.assertFalse(GateState(True,True,True,True,True,True,True,False).authorize())
  self.assertTrue(GateState(True,True,True,True,True,True,True,True).authorize())
 def test_default_off(self):
  os.environ.pop("ASTRA_LIVE_TRADING",None); self.assertFalse(KrakenConfig.from_env().live_enabled)
 def test_live_missing_credentials_blocked(self):
  with self.assertRaises(KrakenError): KrakenSpot(KrakenConfig(live_enabled=True))
 def test_risk_halts(self):
  r=RiskGuardian(); r.reset(100); self.assertTrue(r.observe(91)["halted"])
if __name__=="__main__":unittest.main()
