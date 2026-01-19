import pygame
import os

class Assets:
    _instance = None
    
    def __init__(self):
        self.sprites = {}
        self.load_all()

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = Assets()
        return cls._instance

    def load_all(self):
        base_path = os.path.join("assets", "sprites")
        
        # Helper to load and convert
        def load(name):
            path = os.path.join(base_path, name)
            try:
                img = pygame.image.load(path).convert_alpha()
                return img
            except Exception as e:
                print(f"Failed to load {name}: {e}")
                return None

        # Tiles
        self.sprites["grass"] = load("grass.png")
        self.sprites["dirt"] = load("dirt.png")
        self.sprites["stone"] = load("stone.png")
        
        # Buildings
        self.sprites["Logging Workshop"] = load("logging_workshop.png")
        self.sprites["Stone Refinery"] = load("stone_refinery.png")
        self.sprites["Mine"] = load("mine.png")
        self.sprites["House"] = load("house.png")
        self.sprites["Rocket Ship"] = load("rocket_ship.png")
        
        # Entities
        self.sprites["villager"] = load("villager.png")
        
        # UI
        self.sprites["icon_build"] = load("icon_build.png")
        self.sprites["icon_inventory"] = load("icon_inventory.png")
        self.sprites["icon_arrow_up"] = load("icon_arrow_up.png")
        self.sprites["cloud"] = load("cloud.png")
        self.sprites["title_bg"] = load("title_bg.png")

    def get_sprite(self, name):
        return self.sprites.get(name)
