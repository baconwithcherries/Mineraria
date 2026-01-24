class ResourceManager:
    def __init__(self):
        self.inventory = {
            "wood": 10,
            "stone": 10,
            "iron": 10,
            "food": 0,
            "oxygen": 0,
            "robots": 0,
            "steel": 0,
            "copper": 0,
            "gold": 0,
            "emerald": 0,
            "diamond": 0
        }
        
        # Job Targets (-1 means Max)
        self.job_targets = {
            "Logging Workshop": -1,
            "Stone Refinery": -1,
            "Mine": -1,
            "Farm": -1,
            "Garden": -1,
            "Oxygenator": -1,
            "Laboratory": -1
        }
        
        self.pinned_costs = [] # List of dicts e.g. [{"wood": 5}, {"stone": 5}]
        self.used_codes = []
        self.food_efficiency = 1.0
        self.happiness = 0.0 # 1.0 = 1%
        self.happiness_from_upgrades = 0.0
        
        # Tech
        self.unlocked_techs = ["Woodworking"] # Starting tech
        self.science_points = 0
    
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