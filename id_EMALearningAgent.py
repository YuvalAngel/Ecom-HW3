# --- Runner-up sniper 3.0 ----------------------------------------------
import random
MIN_BID = 1e-3
EPS     = 1e-4           # minimal bump above runner-up

def _evs(P, q, v):
    return [p * q * v for p in P]

class BiddingAgent1:
    """
    Wins slot-0 at (runner+ε)/q iff margin ≥ 3 %.
    Otherwise bids 4 %·EV — enough to register but rarely win.
    """
    def __init__(self):
        self.buffer    = 0.03      # 3 % profit threshold
        self.low_ratio = 0.04      # token bid = 4 % of top-EV

    def get_bid(self, n, P, q, v):
        evs    = sorted(_evs(P, q, v), reverse=True)
        top, runner = evs[0], (evs[1] if len(evs) > 1 else evs[0] * 0.7)

        if top - runner >= self.buffer * runner:
            bid = (runner + EPS) / q
        else:
            bid = self.low_ratio * top
        return max(bid, MIN_BID)

    def notify_outcome(self, r, p, pos): pass
    def get_id(self):               return "id_EMALearningAgent"
