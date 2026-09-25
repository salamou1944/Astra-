from dataclasses import dataclass

@dataclass(frozen=True)
class Bar:
    t: int
    close: float

def backtest_signals(bars, signals, fee=0.0005, slip=0.0002):
    if len(bars) != len(signals): raise ValueError("signals length must match bars")
    equity=1.0; pos=0; peak=1.0; maxdd=0.0; trades=0
    for i,b in enumerate(bars):
        if i: equity *= 1 + pos*(b.close/bars[i-1].close-1)
        target=max(0,min(1,int(signals[i])))
        if target != pos:
            equity *= max(0,1-abs(target-pos)*(fee+slip)); trades+=1; pos=target
        peak=max(peak,equity); maxdd=max(maxdd,1-equity/peak)
    return {"return_pct":round((equity-1)*100,6),"max_drawdown_pct":round(maxdd*100,6),"trades":trades}
