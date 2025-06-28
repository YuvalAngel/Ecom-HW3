import random

class BiddingAgent1:
    def __init__(self):
        self.base_divisor = 2.5 # Retain the successful base from your id_ProbabilisticBidder
        self.exploration_rate = 0.1 # Keep exploration, it seems beneficial
        self.exploration_factor = 0.2 # Keep exploration factor
        
        # New: A stricter cap on the bid relative to v
        self.max_bid_ratio_of_v = 0.9 # Never bid more than 90% of your value 'v'
        
        # New: A very subtle, almost negligible, long-term adjustment to the divisor
        self.long_term_alpha = 0.000001 # Extremely small learning rate
        self.long_term_min_divisor = 2.0 # Don't go below v/2.0
        self.long_term_max_divisor = 3.5 # Don't go above v/3.5
        
        self.id_str = "id_ProbabilisticCapped"

    def get_bid(self, num_of_agents, P, q, v):
        bid = v / self.base_divisor

        # Introduce exploration (from your original ProbabilisticBidder)
        if random.random() < self.exploration_rate:
            deviation = (random.random() * 2 - 1) * self.exploration_factor * bid
            bid += deviation
        
        # Critical Safety Cap 1: Never bid more than max_bid_ratio_of_v * v
        bid = min(bid, v * self.max_bid_ratio_of_v)

        # Critical Safety Cap 2: Ensure the effective bid (bid*q) does not exceed
        # your potential max value if you win the top spot (v * P[0]).
        # This is a strong upper bound to prevent overpaying for positions.
        # Handle cases where P or q might be zero.
        max_effective_value = v * P[0] if len(P) > 0 else v # If no P[0], use v as fallback
        
        if q > 1e-6: # Avoid division by zero
            # Max bid should not exceed what you'd pay for the top spot to break even on 'v'
            bid_based_on_max_effective_value = max_effective_value / q
            bid = min(bid, bid_based_on_max_effective_value)
        
        return max(bid, 1e-3) # Ensure bid is never zero or negative

    def notify_outcome(self, reward, payment, position):
        utility = reward - payment

        # Apply an extremely subtle, long-term adaptation to the base_divisor
        # This is an attempt to slightly nudge the base_divisor over millions of rounds,
        # without rapid fluctuations.
        if utility > 0:
            # If profitable, very, very slightly increase divisor (make bids smaller)
            self.base_divisor = min(self.base_divisor + self.long_term_alpha, self.long_term_max_divisor)
        else: # Utility is zero or negative
            if position == -1: # Did not win any position
                # Very, very slightly decrease divisor (make bids larger)
                self.base_divisor = max(self.base_divisor - self.long_term_alpha * 2, self.long_term_min_divisor)
            else: # Won, but broke even or lost money
                # Slightly increase divisor to avoid future unprofitable wins
                self.base_divisor = min(self.base_divisor + self.long_term_alpha * 3, self.long_term_max_divisor)

        # Ensure base_divisor stays within long-term bounds
        self.base_divisor = max(self.long_term_min_divisor, min(self.base_divisor, self.long_term_max_divisor))
    def get_id(self): return self.id_str