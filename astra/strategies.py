def long_momentum(bars, window=30, threshold=0.0):
    closes=[b.close for b in bars]; out=[]
    for i,p in enumerate(closes):
        out.append(0 if i < window else int(p/closes[i-window]-1 > threshold/100))
    return out
