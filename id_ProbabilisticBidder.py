import random

class BiddingAgent1:
    def __init__(self):
        self.base_divisor = 2.5
        self.exploration_rate = 0.1 # Probability of exploring
        self.exploration_factor = 0.2 # How much to vary the bid during exploration
        self.id_str = "id_ProbabilisticBidder"

    def get_bid(self, num_of_agents, P, q, v):
        bid = v / self.base_divisor

        # Introduce exploration
        if random.random() < self.exploration_rate:
            # Randomly increase or decrease the bid slightly
            deviation = (random.random() * 2 - 1) * self.exploration_factor * bid
            bid += deviation
        
        return max(bid, 1e-3)

    def notify_outcome(self, reward, payment, position):
        # This agent doesn't adapt its bidding strategy based on outcome directly in notify_outcome,
        # but rather relies on the built-in exploration to find better performing bids over time.
        # More advanced versions could adjust base_divisor based on long-term performance.
        pass

    def get_id(self):
        return self.id_str