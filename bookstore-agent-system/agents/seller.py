import random

class SellerAgent:
    def __init__(self, name, reputation, base_price):
        self.name = name
        self.reputation = reputation
        self.current_price = base_price + random.randint(50, 150)

    def negotiate(self, buyer_offer):
        if buyer_offer < self.current_price:
            self.current_price -= random.randint(10, 40)
        return self.current_price