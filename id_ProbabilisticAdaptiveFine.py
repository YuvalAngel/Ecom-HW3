import random

class BiddingAgent1:
    def __init__(self):
        self.base_divisor = 2.5 # Start slightly more aggressive than v/3
        self.exploration_rate = 0.05 # Reduced exploration frequency
        self.exploration_factor = 0.1 # Reduced exploration strength
        
        # Extremely small adaptation rates for 1 million rounds
        self.alpha_increase_divisor = 0.00005 # Make bids smaller (more conservative) on win
        self.alpha_decrease_divisor = 0.00015 # Make bids larger (more aggressive) on no win/loss
        
        self.min_divisor = 1.01 # Bids no more than v/1.01
        self.max_divisor = 5.0  # Bids no less than v/5
        
        self.id_str = "id_ProbabilisticAdaptiveFine"

    def get_bid(self, num_of_agents, P, q, v):
        base_bid = v / self.base_divisor

        # Introduce exploration
        if random.random() < self.exploration_rate:
            deviation = (random.random() * 2 - 1) * self.exploration_factor * base_bid
            bid = base_bid + deviation
        else:
            bid = base_bid
            
        # Ensure bid is always positive and does not exceed own value (v)
        return max(min(bid, v * 0.99), 1e-3)

    def notify_outcome(self, reward, payment, position):
        utility = reward - payment

        if utility > 0:
            # If profitable, very slowly increase divisor (make bid smaller)
            self.base_divisor = min(self.base_divisor + self.alpha_increase_divisor, self.max_divisor)
        else: # utility <= 0
            if position == -1: # Did not win any position
                # Very slowly decrease divisor (make bid larger)
                self.base_divisor = max(self.base_divisor - self.alpha_decrease_divisor * 1.5, self.min_divisor)
            else: # Won but broke even or lost money
                # Slightly increase divisor (make bid smaller) to avoid unprofitable wins
                self.base_divisor = min(self.base_divisor + self.alpha_increase_divisor * 0.5, self.max_divisor)
        
        # Ensure base_divisor stays within bounds
        self.base_divisor = max(self.min_divisor, min(self.base_divisor, self.max_divisor))

    def get_id(self):
        return self.id_str