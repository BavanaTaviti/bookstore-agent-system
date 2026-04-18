class BuyerAgent:
    def __init__(self):
        self.max_budget = 1000

    def make_offer(self, current_price):
        return current_price - 50

    def final_decision(self, price, trust):
        return price <= self.max_budget and trust > 0.6