from .config import *
import random

class Building:
    def __init__(self, x, y, b_type):
        self.x = x
        self.y = y
        self.type = b_type
        self.width = 1
        self.height = 1
        self.level = 1
        self.villagers = 0
        
        # Production buffer
        self.production_buffer = 0
        self.production_history = [0] * 30 # Store last 30 ticks of production
        
        # Rocket specific
        self.is_launching = False
        self.launch_y_offset = 0
        self.boarded_population = 0
        self.game_over_triggered = False

    def record_production(self, amount):
        self.production_history.pop(0)
        self.production_history.append(amount)

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
        
        for x in range(self.width):
            # Triangle logic: width decreases as depth increases
            # Surface (y=50) is 150 wide. At some depth, it becomes 0.
            # Let's say depth is 40 blocks.
            dist_from_center = abs(x - CENTER_X)
            
            for y in range(self.height):
                tile_type = "air"
                
                if y >= SURFACE_LEVEL:
                    depth = y - SURFACE_LEVEL
                    # Max allowed distance at this depth
                    # At depth 0, max_dist is 75. At depth 40, max_dist is 0.
                    max_dist = 75 - (depth * 1.8) 
                    
                    if dist_from_center <= max_dist:
                        if y == SURFACE_LEVEL:
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

    