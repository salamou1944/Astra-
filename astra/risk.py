from dataclasses import dataclass
import math

@dataclass(frozen=True)
class RiskLimits:
    max_position: float=1.0
    max_daily_loss: float=0.02
    max_drawdown: float=0.08

class RiskGuardian:
    def __init__(self, limits=RiskLimits()):
        self.limits=limits; self.day_start=1.0; self.peak=1.0; self.halted=False; self.reason=None
    def reset_day(self,equity):
        self.day_start=float(equity); self.peak=float(equity); self.halted=False; self.reason=None
    def observe(self,equity):
        equity=float(equity)
        if not math.isfinite(equity) or equity < 0: raise ValueError("invalid equity")
        self.peak=max(self.peak,equity)
        daily=(self.day_start-equity)/self.day_start if self.day_start else 0
        dd=(self.peak-equity)/self.peak if self.peak else 0
        if daily >= self.limits.max_daily_loss: self.halted=True; self.reason="daily_loss_limit"
        if dd >= self.limits.max_drawdown: self.halted=True; self.reason="max_drawdown_limit"
        return {"halted":self.halted,"reason":self.reason,"daily_loss":daily,"drawdown":dd}
    def authorize(self,target):
        if self.halted:return 0.0
        return max(-self.limits.max_position,min(self.limits.max_position,float(target)))
