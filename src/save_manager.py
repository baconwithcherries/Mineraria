import json
import os
from .world import Building, Tile
from .config import *

class SaveManager:
    def __init__(self, game):
        self.game = game
        self.save_dir = "data"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def get_save_path(self, world_name):
        return os.path.join(self.save_dir, f"{world_name}.json")

    def save_game(self):
        if not self.game.world_name:
            return
            
        data = {
            "world_name": self.game.world_name,
            "world_width": self.game.world.width,
            "completed": self.game.is_completed,
            "game_time": self.game.game_time,
            "day_counter": self.game.tick_manager.day_counter,
            "food_efficiency": self.game.resource_manager.food_efficiency,
            "happiness": self.game.resource_manager.happiness,
            "inventory": self.game.resource_manager.inventory,
            "pinned": self.game.resource_manager.pinned_costs,
            "code_used": self.game.resource_manager.code_used,
            "camera": {
                "x": self.game.camera.offset_x,
                "y": self.game.camera.offset_y,
                "zoom": self.game.camera.zoom_level
            },
            "buildings": []
        }
        
        for (x, y), b in self.game.world.buildings.items():
            b_data = {
                "x": x, "y": y, "type": b.type,
                "level": b.level,
                "villagers": b.villagers,
                "buffer": b.production_buffer
            }
            data["buildings"].append(b_data)
            
        villagers = []
        for v in self.game.entity_manager.villagers:
            villagers.append({"x": v.x, "y": v.y, "job": v.job})
        data["villagers"] = villagers

        path = self.get_save_path(self.game.world_name)
        try:
            with open(path, "w") as f:
                json.dump(data, f)
            print(f"Game Saved: {self.game.world_name}")
        except Exception as e:
            print(f"Save Failed: {e}")

    def load_game(self, world_name):
        path = self.get_save_path(world_name)
        if not os.path.exists(path):
            return False
            
        try:
            with open(path, "r") as f:
                data = json.load(f)
            
            self.game.init_managers()
            self.game.world_name = data["world_name"]
            self.game.is_completed = data.get("completed", False)
            self.game.game_time = data.get("game_time", 0)
            self.game.tick_manager.day_counter = data.get("day_counter", 1)
            self.game.resource_manager.food_efficiency = data.get("food_efficiency", 1.0)
            self.game.resource_manager.happiness = data.get("happiness", 0.0)
            # Re-init world with saved width
            from .world import World
            self.game.world = World(data.get("world_width", 150))
            
            # Re-init camera
            from .camera import Camera
            self.game.camera = Camera(self.game.world.width * TILE_SIZE, WORLD_HEIGHT * TILE_SIZE)
            
            self.game.resource_manager.inventory = data["inventory"]
            self.game.resource_manager.pinned_costs = data.get("pinned", [])
            self.game.resource_manager.code_used = data.get("code_used", False)
            
            cam = data["camera"]
            self.game.camera.offset_x = cam["x"]
            self.game.camera.offset_y = cam["y"]
            self.game.camera.zoom_level = cam["zoom"]
            
            self.game.world.buildings = {}
            for b_data in data["buildings"]:
                b = Building(b_data["x"], b_data["y"], b_data["type"])
                b.level = b_data["level"]
                b.villagers = b_data.get("villagers", 0)
                b.production_buffer = b_data.get("buffer", 0)
                self.game.world.buildings[(b_data["x"], b_data["y"])] = b
                
            self.game.entity_manager.villagers = []
            for v_data in data.get("villagers", []):
                v = self.game.entity_manager.spawn_villager(v_data["x"], v_data["y"], v_data.get("job", "Unemployed"))
                
                # Re-link assignment based on job
                if v.job != "Unemployed" and v.job != "House":
                    target_type = v.job
                    possible_buildings = [b for b in self.game.world.buildings.values() 
                                         if (b.type == target_type or (target_type == "Farm" and b.type == "Garden"))
                                         and len(b.assigned_workers) < 3 * b.level]
                    if possible_buildings:
                        workplace = possible_buildings[0]
                        v.assigned_building = workplace
                        workplace.assigned_workers.append(v)
                
            print(f"Game Loaded: {world_name}")
            return True
        except Exception as e:
            print(f"Load Failed: {e}")
            return False

    def list_saves(self):
        saves = []
        for file in os.listdir(self.save_dir):
            if file.endswith(".json"):
                saves.append(file.replace(".json", ""))
        return saves