from .config import *
import random
import math

class Building:
    def __init__(self, x, y, b_type):
        self.x = x
        self.y = y
        self.type = b_type
        self.width = 1
        self.height = 1
        self.level = 1
        self.villagers = 0
        
        # Worker Management
        self.target_workers = 0 if b_type == "House" else 3 * self.level
        
        self.production_buffer = 0
        self.production_history = [0] # Store daily production
        self.last_day = 1
        
        # Specific worker assignments
        self.assigned_workers = [] # List of Villager objects
        
        # Multi-resource support (for Blast Furnace)
        self.buffers = {"steel": 0, "copper": 0, "gold": 0, "emerald": 0, "diamond": 0}
        self.histories = {res: [0] for res in self.buffers}
        
        # Rocket specific
        self.is_launching = False
        self.launch_y_offset = 0
        self.boarded_population = 0
        self.game_over_triggered = False

    def record_production(self, amount, current_day, res_type=None):
        # Check for new day
        if current_day > self.last_day:
            self.production_history.append(0)
            if len(self.production_history) > 7:
                self.production_history.pop(0)
            
            for h in self.histories.values():
                h.append(0)
                if len(h) > 7:
                    h.pop(0)
            
            self.last_day = current_day
            
        if res_type and res_type in self.histories:
            self.histories[res_type][-1] += amount
        else:
            self.production_history[-1] += amount

    @staticmethod
    def get_cost(b_type):
        if b_type == "Logging Workshop": return {"wood": 5}
        if b_type == "Stone Refinery": return {"stone": 5}
        if b_type == "Mine": return {"iron": 5}
        if b_type == "House": return {"wood": 5, "stone": 5, "iron": 5}
        if b_type == "Farm": return {"iron": 5, "stone": 5, "wood": 5}
        if b_type == "Garden": return {"iron": 15, "stone": 15, "wood": 15, "food": 15}
        if b_type == "Blast Furnace": return {"iron": 20, "stone": 20, "wood": 10}
        if b_type == "Rocket Ship": return {"wood": 1000, "stone": 1000, "iron": 1000}
        if b_type == "Warehouse": return {"wood": 50, "stone": 50}
        if b_type == "Laboratory": return {"wood": 100, "stone": 100, "iron": 20}
        return {}

    def get_upgrade_cost(self):
        # Spec says "Higher level buildings require more villagers"
        # and "requirements for what you will need to level the building up"
        # Let's say cost scales with level.
        factor = self.level
        if self.type == "Logging Workshop": return {"wood": 10 * factor}
        if self.type == "Stone Refinery": return {"stone": 10 * factor}
        if self.type == "Mine": return {"iron": 10 * factor}
        if self.type == "House": return {"wood": 10 * factor, "stone": 10 * factor}
        if self.type == "Farm": return {"wood": 10 * factor, "stone": 10 * factor, "iron": 10 * factor}
        if self.type == "Rocket Ship": return {"wood": 200 * factor, "stone": 200 * factor, "iron": 200 * factor}
        if self.type == "Warehouse": return {"wood": 50 * factor, "stone": 50 * factor}
        if self.type == "Laboratory": return {"wood": 100 * factor, "iron": 20 * factor}
        return {}

    @staticmethod
    def get_color(b_type):
        if b_type == "Logging Workshop": return (139, 69, 19) # SaddleBrown
        if b_type == "Stone Refinery": return (169, 169, 169) # DarkGray
        if b_type == "Mine": return (47, 79, 79) # DarkSlateGray
        if b_type == "House": return (255, 215, 0) # Gold
        if b_type == "Farm": return (50, 205, 50) # LimeGreen
        if b_type == "Garden": return (255, 105, 180) # HotPink
        if b_type == "Blast Furnace": return (70, 70, 70) # DarkGray
        if b_type == "Rocket Ship": return (200, 0, 0) # Red
        if b_type == "Warehouse": return (100, 100, 200) # Slate Blue
        if b_type == "Laboratory": return (200, 200, 255) # Light Blue
        return (255, 0, 255)

class Tile:
    def __init__(self, x, y, tile_type):
        self.x = x
        self.y = y
        self.tile_type = tile_type  # "grass", "dirt", "stone", "air"

class World:
    def __init__(self, width=150):
        self.width = width
        self.height = WORLD_HEIGHT
        self.grid = [[None for _ in range(self.height)] for _ in range(self.width)]
        self.buildings = {} # Key: (x,y) tuple, Value: Building object
        self.generate()

    def generate(self):
        SURFACE_LEVEL = 50
        CENTER_X = self.width // 2
        
        # Pre-calculate surface heights for a smoother rolling feel
        surface_offsets = []
        for x in range(self.width):
            # Lower frequency waves for smoother hills
            s1 = math.sin(x * 0.05) * 2.5
            s2 = math.sin(x * 0.02) * 1.5
            surface_offsets.append(int(s1 + s2))

        # Smooth bottom variations using a long sine wave instead of random noise
        bottom_variations = [1.0 + math.sin(x * 0.03) * 0.15 for x in range(self.width)]

        for x in range(self.width):
            dist_from_center = abs(x - CENTER_X)
            local_surface = SURFACE_LEVEL + surface_offsets[x]
            
            for y in range(self.height):
                tile_type = "air"
                
                # Base shape logic
                base_max_dist = (self.width // 2) * 0.85
                
                if y >= local_surface:
                    depth = y - local_surface
                    
                    # Smoothly narrow the width as we go deeper
                    width_variance = math.sin(y * 0.1) * 1.5
                    max_dist = (base_max_dist - (depth * 2.0)) * bottom_variations[x] + width_variance
                    
                    if dist_from_center <= max_dist:
                        if y == local_surface:
                            tile_type = "grass"
                        elif depth < 5:
                            tile_type = "dirt"
                        else:
                            tile_type = "stone"
                
                self.grid[x][y] = Tile(x, y, tile_type)

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return None

    def place_building(self, x, y, b_type):
        # Check bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
            
        # Check collision with existing buildings
        if (x, y) in self.buildings:
            # Stacking logic? Spec says "Buildings can be built on top of each other"
            # So if there is a building, we place ON TOP of it (y-1).
            # But the 'place_building' is called with specific coords. 
            # The input handler should determine the correct Y.
            # If the user clicks (x,y), and (x,y) is occupied, we fail?
            # Or does stacking mean we can build at (x, y-1)?
            # "Buildings can be built on top of each other until a max height of 100"
            # This implies if I click a building, I might place one above it.
            return False 

        self.buildings[(x, y)] = Building(x, y, b_type)
        return True

    def get_building_at(self, x, y):
        return self.buildings.get((x, y))

    def has_house(self):
        for b in self.buildings.values():
            if b.type == "House":
                return True
        return False

    def has_all_workshops(self):
        types = [b.type for b in self.buildings.values()]
        return "Logging Workshop" in types and "Stone Refinery" in types and "Mine" in types

    