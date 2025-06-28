import time
import random

import numpy as np
import pandas as pd
import CONSTANTS # Assuming this CONSTANTS module exists and defines necessary constants
from tqdm import tqdm

import os


NUM_SIMULATIONS = 5

# Your provided functions (cap_prob, get_agent_list, is_agent_valid, BookKeeping,
# sample_relevant_agents, get_timeout_agents, sample_variables, gsp, sample_rewards,
# and sequential_game) should be placed here or imported.
# For this example, I'm assuming they are accessible in the same scope or imported.

# --- Start of your provided code (assuming it's all in one file for simplicity) ---

def cap_prob(p):
    if p > 1.0:
        return 0.999
    elif p < 0.00001:
        return 0.00001
    else:
        return p


def get_agent_list(is_agent2 = False):
    file_list = [f.rstrip(".py") for f in os.listdir('.') if (os.path.isfile(f) and f.startswith("id_"))]
    agent_list = []
    for i, f in enumerate(file_list):
        # print(i, f) # Commented out for cleaner output during multiple runs
        mod = __import__(f)
        try:
            if is_agent2 is False:
                agent = mod.BiddingAgent1()
            else:
                agent = mod.BiddingAgent2()
            if is_agent_valid(agent):
                agent_list.append(agent)
            else:
                print("file {0} introduced an invalid agent".format(f))
        except Exception as e:
            # print(e) # Commented out for cleaner output during multiple runs
            print("file {0} raised an exception".format(f))
    return agent_list


def is_agent_valid(ba):
    if not hasattr(ba, 'get_bid') or not hasattr(ba, 'get_id') or not hasattr(ba, 'notify_outcome'):
        return False
    return True


class BookKeeping:
    def __init__(self, agent):
        self.id = agent.get_id()
        self.played_rounds = 0
        self.sum_payments = 0.
        self.sum_rewards = 0.
        self.sum_computation_time = 0.
        self.time_out = False

    def add_comp_time(self, t):
        self.sum_computation_time += t

    def set_time_out(self):
        self.time_out = True

    def get_avg_comp_time(self):
        if self.played_rounds == 0:
            return 0
        return self.sum_computation_time / self.played_rounds

    def update(self, reward, payment):
        self.played_rounds += 1
        self.sum_payments += payment
        self.sum_rewards += reward

    def get_id(self):
        return self.id

    def get_all(self):
        # Handle played_rounds = 0 to avoid division by zero
        avg_utility = (self.sum_rewards - self.sum_payments) / self.played_rounds if self.played_rounds > 0 else 0.0
        return {"id": self.id, "played_rounds": self.played_rounds, "sum_payments": self.sum_payments,
                "sum_rewards": self.sum_rewards, "sum_computation_time": self.sum_computation_time,
                "sum_utility": self.sum_rewards - self.sum_payments,
                "avg_utility": avg_utility,
                "was_timeout": self.time_out}


def sample_relevant_agents(all_agents):
    cap = 0.08
    relevant = []
    for agent in all_agents:
        if random.random() < cap:
            relevant.append(agent)
    if len(relevant) < 3:
        relevant = random.sample(all_agents, k=CONSTANTS.MIN_NUM_AGENTS)
    random.shuffle(relevant)
    return relevant


def get_timeout_agents(relevant_agents, book_dict):
    lst = []
    for agent in relevant_agents:
        book = book_dict[agent]
        if book.get_avg_comp_time() > CONSTANTS.TIME_CAP:
            # print("Agent {0} was removed due to slow operation".format(agent.get_id())) # Commented out for cleaner output
            lst.append(agent)
            book.set_time_out()
    return lst


def sample_variables(num_agents):
    v_list = [max(np.random.normal(CONSTANTS.R_MEAN, CONSTANTS.R_STD), 0) for _ in range(num_agents)]
    q_dist = np.random.choice(range(len(CONSTANTS.Q_TYPE)), size=num_agents, p=CONSTANTS.Q_TYPE)
    q_list = [cap_prob(np.random.normal(*CONSTANTS.RELEVANCE_MEAN_STD[z])) for z in q_dist]

    prob_click = []
    prob_first = cap_prob(np.random.normal(*CONSTANTS.P_CLICK))
    decay = cap_prob(np.random.normal(*CONSTANTS.D_DECAY))
    pv = prob_first

    prob_click.append(pv)
    pv = pv * decay

    while pv >= CONSTANTS.MIN_PCLICK:
        prob_click.append(pv)
        pv = pv * decay

    return v_list, q_list, prob_click


def gsp(bids, q_list, n_positions):
    gsp_outcome = {}
    bids_q = [(bids[i][0], bids[i][1] * q_list[i]) for i in
              range(len(q_list))]
    sorted_bids = sorted(bids_q, key=lambda b: b[1], reverse=True)
    sorted_bids.append((len(bids), CONSTANTS.MIN_PAYMENT))
    for pos in range(min(n_positions, len(bids))):
        agent_index = sorted_bids[pos][0]
        gsp_outcome[agent_index] = (pos, sorted_bids[pos + 1][1])
    return gsp_outcome


def sample_rewards(gsp_outcome, q_list, v_list, prob_click):
    rewards = {}
    for k, v in gsp_outcome.items():
        rewards[k] = 0.
        if random.random() < q_list[k] * prob_click[v[0]]:
            rewards[k] = v_list[k]
    return rewards


def sequential_game():
    all_agents = get_agent_list(is_agent2=False)
    book_dict = {a: BookKeeping(a) for a in all_agents}
    for _ in tqdm(range(CONSTANTS.NUM_ROUNDS), leave=False, desc="Simulating Rounds"): # Added leave=False and desc
        relevant_agents = sample_relevant_agents(all_agents)
        num_of_agents = len(relevant_agents)
        v_list, q_list, prob_click = sample_variables(num_of_agents)
        bids = []
        for i, agent in enumerate(relevant_agents):
            comp_t = time.time()
            bids.append((i, agent.get_bid(num_of_agents, prob_click, q_list[i], v_list[i])))
            book_dict[agent].add_comp_time(time.time() - comp_t)

        gsp_outcome = gsp(bids, q_list, len(prob_click))
        rewards = sample_rewards(gsp_outcome, q_list, v_list, prob_click)

        for i, agent in enumerate(relevant_agents):
            comp_t = time.time()
            reward, payment, position = 0., 0., -1
            if i in rewards:
                reward, payment, position = rewards[i], gsp_outcome[i][1], gsp_outcome[i][0]
            agent.notify_outcome(reward, payment, position)
            book_dict[agent].add_comp_time(time.time() - comp_t)
            book_dict[agent].update(reward, payment)

        to_remove = get_timeout_agents(relevant_agents, book_dict)
        for agent in to_remove:
            all_agents.remove(agent)

    return book_dict

# --- End of your provided code ---


def main():
    # Dictionary to accumulate utility for each agent across simulations
    # Keys will be agent IDs, values will be lists of avg_utilities from each simulation
    all_agents_utilities = {}

    print(f"Running {NUM_SIMULATIONS} simulations...")
    for sim_num in tqdm(range(NUM_SIMULATIONS), desc="Overall Simulations"):
        # Reset agents for each simulation if they maintain internal state
        # The get_agent_list function automatically creates new instances, effectively resetting them.
        book_dict = sequential_game()
        
        for bk in book_dict.values():
            agent_data = bk.get_all()
            agent_id = agent_data["id"]
            avg_utility = agent_data["avg_utility"]

            if agent_id not in all_agents_utilities:
                all_agents_utilities[agent_id] = []
            all_agents_utilities[agent_id].append(avg_utility)

    # Calculate average utility across all simulations for each agent
    final_results = []
    for agent_id, utilities in all_agents_utilities.items():
        avg_utility_over_runs = np.mean(utilities)
        final_results.append({"id": agent_id, f"average_utility_over_{NUM_SIMULATIONS}_runs": avg_utility_over_runs})

    df_final = pd.DataFrame(final_results)
    df_final = df_final.sort_values(by=f"average_utility_over_{NUM_SIMULATIONS}_runs", ascending=False)

    print(f"\n--- Final Results (Average over {NUM_SIMULATIONS} Simulations) ---")
    print(df_final)


if __name__ == '__main__':
    main()