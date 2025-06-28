import random

class BiddingAgent1:
    def __init__(self):
        # Start at v/3, similar to the strong dummy agent
        self.divisor = 3.0
        # Aggressively increase divisor if profitable (bid less)
        self.learning_rate_good_utility = 0.02
        # Cautiously decrease divisor if not profitable (bid more)
        self.learning_rate_bad_utility = 0.005 # Much smaller than before
        self.min_divisor = 1.1 # Don't bid more than v/1.1
        self.max_divisor = 10.0 # Can be very conservative, bidding v/10
        self.id_str = "id_ConservativeAdaptiveFraction"

    def get_bid(self, num_of_agents, P, q, v):
        bid = v / self.divisor
        return max(bid, 1e-3)

    def notify_outcome(self, reward, payment, position):
        utility = reward - payment

        if utility > 0:
            # If profitable, try to be even more conservative, assuming we can maintain utility
            self.divisor = min(self.divisor + self.learning_rate_good_utility, self.max_divisor)
        else: # utility <= 0 or did not win
            # If not profitable, slightly increase aggression (decrease divisor)
            self.divisor = max(self.divisor - self.learning_rate_bad_utility, self.min_divisor)
        
        # If we didn't get any position, it means our bid was too low
        # This is a strong signal to increase aggression a bit more directly.
        if position == -1:
            self.divisor = max(self.divisor - (self.learning_rate_bad_utility * 2), self.min_divisor)
        
        # Ensure the divisor doesn't fluctuate too wildly at the extremes
        self.divisor = max(self.min_divisor, min(self.divisor, self.max_divisor))

    def get_id(self): return self.id_str