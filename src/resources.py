class ResourceManager:
    def __init__(self):
        self.inventory = {
            "wood": 10,
            "stone": 10,
            "iron": 10,
            "food": 0,
            "steel": 0,
            "copper": 0,
            "gold": 0,
            "emerald": 0,
            "diamond": 0
        }
        self.pinned_costs = [] # List of dicts e.g. [{"wood": 5}, {"stone": 5}]
        self.code_used = False
        self.food_efficiency = 1.0
        self.happiness = 0.0 # 1.0 = 1%
    
    def add_resource(self, resource, amount):
        if resource in self.inventory:
            self.inventory[resource] += amount

    def remove_resource(self, resource, amount):
        if resource in self.inventory and self.inventory[resource] >= amount:
            self.inventory[resource] -= amount
            return True
        return False

    def has_resources(self, cost_dict):
        for res, amount in cost_dict.items():
            if self.inventory.get(res, 0) < amount:
                return False
        return True

    def deduct_resources(self, cost_dict):
        if self.has_resources(cost_dict):
            for res, amount in cost_dict.items():
                self.inventory[res] -= amount
            # Remove from pinned if satisfied? Spec says "Logic: Updates in real-time as player collects resources."
            # Actually, usually pins stay until user unpins or completes.
            # But if I build, I consume resources.
            # "Updates in real-time" likely means the progress bar updates.
            return True
        return False
    
    def pin_cost(self, name, cost_dict):
        self.pinned_costs.append({"name": name, "cost": cost_dict})
    
    def unpin_cost(self, name):
        self.pinned_costs = [p for p in self.pinned_costs if p["name"] != name]