import math, random

# ---------- פרמטרים גלובליים ----------
MIN_BID     = 1e-3
EPS         = 1e-4     # בוסט מיקרוסקופי לנצח את הרץ-אפ
ALPHA       = 0.05     # EMA smoothing
MIN_MARGIN  = 0.03     # דרישת רווח ≥ 3 % מהמחיר האומד
EXPLORE_P   = 0.02     # 2 % סיכוי ביד אקראי עדין

# ---------- חישובי EV ----------
def ev_list(P, q, v):
    """EV לכל סלוט: CTR·q·v"""
    return [p * q * v for p in P]

# ---------- גלאי מחיר ----------
class RunnerPriceEMA:
    """אומדן מחיר (runner-up) לכל סלוט באמצעות EMA."""
    def __init__(self):
        self.mean = None
        self.var  = 0.0
        self.n    = 0

    def update(self, price):
        self.n += 1
        if self.mean is None:
            self.mean = price
            self.var  = 0.0
        else:
            d        = price - self.mean
            self.mean += ALPHA * d
            self.var   = (1-ALPHA) * self.var + ALPHA * d * d

    def est(self):
        if self.mean is None:
            return 2.0                 # כל עוד אין מידע—ניחוש שמרני
        return self.mean + math.sqrt(self.var / max(self.n, 1))  # mean + 1σ
