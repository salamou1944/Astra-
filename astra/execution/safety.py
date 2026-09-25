from dataclasses import dataclass

@dataclass
class KillSwitch:
    halted: bool=False
    reason: str|None=None
    def trip(self,reason): self.halted=True; self.reason=str(reason)
    def authorize(self): return not self.halted

class ExecutionGate:
    def __init__(self,kill_switch): self.kill_switch=kill_switch
    def authorize(self,*,data_valid,strategy_valid,risk_valid,execution_valid,reconciliation_valid,human_approval,live_enabled):
        return bool(live_enabled and data_valid and strategy_valid and risk_valid and execution_valid and reconciliation_valid and human_approval and self.kill_switch.authorize())
