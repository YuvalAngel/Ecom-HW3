# --- ROI balancer with moving threshold --------------------------------
import random
MIN_BID = 1e-3
EPS     = 1e-4

class BiddingAgent1:
    """
    Maintains EMA of realised ROI; if ROI ≥ 0.45 bids at runner-up+ε,
    else bids 4 %·EV.  fallback decays 0.20→0.04.
    """
    def __init__(self):
        self.roi_ema   = 1.0
        self.alpha     = 0.05
        self.min_roi   = 0.45
        self.fallback  = 0.20
        self.fall_min  = 0.04
        self.decay     = 0.9994
        self.id_str    = "id_RunnerUpROIBalancer"

    def get_bid(self, n, P, q, v):
        evs = sorted([p*q*v for p in P], reverse=True)
        top, runner = evs[0], (evs[1] if len(evs) > 1 else evs[0]*0.7)
        low = max(self.fallback * q * v, self.fall_min * q * v, MIN_BID)

        if self.roi_ema >= self.min_roi:
            bid = max((runner + EPS)/q, low)
        else:
            bid = low

        self.fallback = max(self.fallback * self.decay, self.fall_min)
        return bid

    def notify_outcome(self, r, p, pos):
        if p > 0:
            roi = r / p
            self.roi_ema = (1 - self.alpha) * self.roi_ema + self.alpha * roi

    def get_id(self): return self.id_str
