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
        self.sprites["Farm"] = load("farm.png")
        self.sprites["Garden"] = load("garden.png")
        self.sprites["Blast Furnace"] = load("blast_furnace.png")
        self.sprites["Warehouse"] = load("warehouse.png")
        self.sprites["Laboratory"] = load("laboratory.png")
        
        # Entities
        self.sprites["villager"] = load("villager.png")
        
        # UI
        self.sprites["icon_build"] = load("icon_build.png")
        self.sprites["icon_inventory"] = load("icon_inventory.png")
        self.sprites["icon_arrow_up"] = load("icon_arrow_up.png")
        self.sprites["cloud"] = load("cloud.png")
        self.sprites["title_bg"] = load("title_bg.png")
        
        # Music
        self.music_path = os.path.join("assets", "audio")

    def play_music(self, name):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            
            path = os.path.join(self.music_path, name)
            print(f"Attempting to play music: {path}")
            if os.path.exists(path):
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                print("Music started successfully.")
            else:
                print(f"Music file not found: {path}")
        except Exception as e:
            print(f"Music error playing {name}: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()

    def get_sprite(self, name):
        return self.sprites.get(name)
