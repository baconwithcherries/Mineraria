import pygame
import os
import math
import random

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
        
        # --- Procedural Fallbacks for Copper Mine & Blast Furnace ---
        self.sprites["Copper Mine"] = load("copper_mine.png")
        if self.sprites["Copper Mine"] is None:
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Jagged stone mound base
            pygame.draw.polygon(surf, (100, 105, 115), [(2, 30), (8, 12), (24, 12), (30, 30)])
            # Noise/Texture for rock feel
            import random
            random.seed(42)
            for _ in range(50):
                rx, ry = random.randint(4, 28), random.randint(14, 28)
                if rx < 32 and ry < 32 and surf.get_at((rx, ry)).a > 0:
                    surf.set_at((rx, ry), (80, 85, 95))
            # Copper Veins (multi-colored metallic orange)
            for _ in range(8):
                vx, vy = random.randint(6, 24), random.randint(14, 26)
                if vx < 30 and vy < 30 and surf.get_at((vx, vy)).a > 0:
                    pygame.draw.rect(surf, (184, 115, 51), (vx, vy, 3, 3))
                    surf.set_at((vx, vy), (210, 140, 80)) # highlight
            # Wooden Frame Entrance (matches Mine style)
            pygame.draw.rect(surf, (20, 20, 20), (11, 20, 10, 12)) # Tunnel
            pygame.draw.rect(surf, (100, 70, 40), (10, 18, 12, 3)) # Top beam
            pygame.draw.rect(surf, (100, 70, 40), (10, 18, 2, 14)) # Left beam
            pygame.draw.rect(surf, (20, 20, 20), (20, 18, 2, 14)) # Shadow beam
            self.sprites["Copper Mine"] = surf

        self.sprites["Blast Furnace"] = load("blast_furnace.png")
        if self.sprites["Blast Furnace"] is None:
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Main metal tower body
            pygame.draw.rect(surf, (50, 50, 60), (6, 6, 20, 26))
            # Panel lines and texture
            pygame.draw.line(surf, (30, 30, 40), (6, 15), (26, 15))
            pygame.draw.line(surf, (30, 30, 40), (6, 24), (26, 24))
            # Chimney with decorative Rim
            pygame.draw.rect(surf, (60, 65, 75), (10, 0, 12, 6))
            pygame.draw.rect(surf, (40, 40, 50), (8, 0, 16, 3)) # Top Rim
            # Molten Metal Glow (layered for intensity)
            pygame.draw.rect(surf, (180, 20, 0), (10, 22, 12, 8)) # Deep red
            pygame.draw.rect(surf, (255, 100, 0), (11, 24, 10, 5)) # Bright orange
            pygame.draw.rect(surf, (255, 200, 50), (13, 26, 6, 2)) # Yellow core
            # Industrial piping
            pygame.draw.rect(surf, (100, 100, 110), (2, 12, 4, 4))
            pygame.draw.rect(surf, (100, 100, 110), (26, 18, 4, 4))
            # Surface noise for weathered metal look
            for _ in range(40):
                rx, ry = random.randint(7, 25), random.randint(7, 31)
                surf.set_at((rx, ry), (40, 40, 50))
            self.sprites["Blast Furnace"] = surf

        self.sprites["Power Plant"] = load("power_plant.png")
        if self.sprites["Power Plant"] is None:
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Main Building (Concrete Grey)
            pygame.draw.rect(surf, (140, 140, 150), (4, 14, 24, 18))
            pygame.draw.rect(surf, (80, 80, 90), (4, 14, 24, 18), 1)
            
            # Cooling Tower (Tapered shape)
            pygame.draw.polygon(surf, (160, 160, 170), [(8, 14), (24, 14), (22, 2), (10, 2)])
            pygame.draw.polygon(surf, (100, 100, 110), [(8, 14), (24, 14), (22, 2), (10, 2)], 1)
            # Top of tower (dark opening)
            pygame.draw.ellipse(surf, (40, 40, 50), (10, 0, 12, 4))
            
            # Energy Core / Windows (Bright Blue)
            pygame.draw.rect(surf, (0, 180, 255), (10, 18, 12, 8))
            pygame.draw.rect(surf, (200, 240, 255), (12, 20, 8, 4)) # Glow
            
            # Hazard stripes
            for i in range(4, 28, 8):
                pygame.draw.line(surf, (255, 200, 0), (i, 30), (i+4, 32), 2)
            
            # Steam particles (simple circles)
            pygame.draw.circle(surf, (255, 255, 255, 150), (16, -2), 3)
            
            self.sprites["Power Plant"] = surf

        self.sprites["Advanced Machine Factory"] = load("advanced_machine_factory.png")
        if self.sprites["Advanced Machine Factory"] is None:
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Metallic industrial body
            pygame.draw.rect(surf, (100, 110, 120), (2, 10, 28, 22))
            pygame.draw.rect(surf, (60, 70, 80), (2, 10, 28, 22), 1)
            # Tech details / Wiring patterns
            pygame.draw.rect(surf, (200, 120, 40), (6, 14, 20, 4)) # Copper output port
            pygame.draw.line(surf, (0, 255, 0), (8, 22), (24, 22), 2) # Green circuit line
            # Smokestack (smaller)
            pygame.draw.rect(surf, (80, 85, 90), (20, 2, 6, 8))
            # Glass observation panel
            pygame.draw.rect(surf, (200, 240, 255, 180), (8, 24, 8, 6))
            self.sprites["Advanced Machine Factory"] = surf

        self.sprites["House"] = load("house.png")
        self.sprites["Rocket Ship"] = load("rocket_ship.png")
        self.sprites["Farm"] = load("farm.png")
        self.sprites["Garden"] = load("garden.png")
        self.sprites["Oxygenator"] = load("oxygenator.png")
        self.sprites["Warehouse"] = load("warehouse.png")
        self.sprites["Laboratory"] = load("laboratory.png")
        
        # --- Procedural Fallback for Raw Material Factory ---
        self.sprites["Raw Material Factory"] = load("raw_material_factory.png")
        if self.sprites["Raw Material Factory"] is None:
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Blue-grey metal building body
            pygame.draw.rect(surf, (70, 80, 100), (2, 8, 28, 24))
            # Darker roof with ridges
            pygame.draw.rect(surf, (40, 50, 60), (0, 6, 32, 4))
            for i in range(0, 32, 4):
                pygame.draw.line(surf, (30, 40, 50), (i, 6), (i, 10))
            # Large industrial windows
            pygame.draw.rect(surf, (150, 200, 255), (6, 12, 8, 8)) # Window 1
            pygame.draw.rect(surf, (150, 200, 255), (18, 12, 8, 8)) # Window 2
            # Smokestacks
            pygame.draw.rect(surf, (100, 100, 110), (6, 0, 4, 6))
            pygame.draw.rect(surf, (100, 100, 110), (22, 0, 4, 6))
            # Detail texture
            import random
            random.seed(123)
            for _ in range(30):
                rx, ry = random.randint(2, 29), random.randint(8, 31)
                surf.set_at((rx, ry), (50, 60, 80))
            self.sprites["Raw Material Factory"] = surf
        
        # Entities
        self.sprites["villager"] = load("villager.png")
        self.sprites["trader"] = load("trader.png")
        
        # UI
        self.sprites["icon_build"] = load("icon_build.png")
        self.sprites["icon_inventory"] = load("icon_inventory.png")
        self.sprites["icon_arrow_up"] = load("icon_arrow_up.png")
        self.sprites["cloud"] = load("cloud.png")
        self.sprites["title_bg"] = load("title_bg.png")
        
        # --- Procedural Item Sprites for Codex ---
        self.load_item_sprites()
        
        # Music
        self.music_path = os.path.join("assets", "audio")

    def load_item_sprites(self):
        def create_item(name, draw_func):
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            draw_func(surf)
            self.sprites[f"item_{name}"] = surf

        def draw_wood(surf):
            # Log shape
            pygame.draw.ellipse(surf, (100, 70, 40), (10, 20, 44, 24))
            pygame.draw.ellipse(surf, (139, 90, 60), (44, 20, 10, 24)) # End grain
            pygame.draw.ellipse(surf, (160, 120, 90), (46, 24, 6, 16)) # Inner ring
            # Bark lines
            pygame.draw.line(surf, (80, 50, 30), (12, 28), (44, 28), 2)
            pygame.draw.line(surf, (80, 50, 30), (15, 36), (44, 36), 2)

        def draw_stone(surf):
            # Jagged rock
            pts = [(10, 40), (20, 15), (45, 10), (55, 30), (50, 50), (25, 55)]
            pygame.draw.polygon(surf, (120, 125, 135), pts)
            pygame.draw.polygon(surf, (80, 85, 95), pts, 3)
            # Highlights
            pygame.draw.line(surf, (160, 160, 170), (22, 20), (40, 15), 3)
            pygame.draw.line(surf, (160, 160, 170), (20, 25), (25, 45), 2)

        def draw_iron(surf):
            # Ingot
            pts = [(10, 45), (15, 25), (45, 25), (50, 45)]
            pygame.draw.polygon(surf, (160, 165, 175), pts)
            pygame.draw.polygon(surf, (100, 105, 115), pts, 2)
            # Top face
            t_pts = [(15, 25), (20, 15), (50, 15), (45, 25)]
            pygame.draw.polygon(surf, (200, 205, 215), t_pts)
            pygame.draw.polygon(surf, (100, 105, 115), t_pts, 2)

        def draw_copper(surf):
            # Ingot (Orange/Brown)
            pts = [(10, 45), (15, 25), (45, 25), (50, 45)]
            pygame.draw.polygon(surf, (184, 115, 51), pts)
            # Top face
            t_pts = [(15, 25), (20, 15), (50, 15), (45, 25)]
            pygame.draw.polygon(surf, (210, 140, 80), t_pts)
            pygame.draw.polygon(surf, (100, 60, 20), t_pts, 2)

        def draw_steel(surf):
            # Shiny Ingot
            pts = [(10, 45), (15, 25), (45, 25), (50, 45)]
            pygame.draw.polygon(surf, (70, 80, 90), pts)
            # Top face
            t_pts = [(15, 25), (20, 15), (50, 15), (45, 25)]
            pygame.draw.polygon(surf, (120, 130, 140), t_pts)
            pygame.draw.line(surf, (255, 255, 255), (25, 18), (45, 18), 2) # Reflection

        def draw_batteries(surf):
            # Cylinder
            pygame.draw.rect(surf, (50, 50, 50), (20, 15, 24, 34))
            pygame.draw.rect(surf, (255, 200, 0), (20, 25, 24, 15)) # Label
            # Bolt icon
            pygame.draw.polygon(surf, (255, 255, 255), [(32, 27), (28, 33), (31, 33), (29, 39), (36, 31), (32, 31)])
            # Terminals
            pygame.draw.rect(surf, (200, 200, 200), (28, 10, 8, 5)) # Top
            pygame.draw.rect(surf, (150, 50, 50), (20, 15, 24, 4), border_radius=2) # Red rim

        def draw_food(surf):
            # Red Apple
            pygame.draw.circle(surf, (200, 50, 50), (32, 35), 18)
            pygame.draw.circle(surf, (230, 80, 80), (25, 28), 6) # Highlight
            # Stem and Leaf
            pygame.draw.line(surf, (100, 70, 40), (32, 17), (32, 10), 3)
            pygame.draw.ellipse(surf, (50, 150, 50), (32, 8, 15, 8))

        def draw_oxygen(surf):
            # Blue Gas Tank
            pygame.draw.rect(surf, (60, 100, 200), (20, 15, 24, 40), border_radius=8)
            pygame.draw.rect(surf, (255, 255, 255), (20, 25, 24, 10)) # White band
            # Valve
            pygame.draw.rect(surf, (150, 150, 150), (28, 8, 8, 7))
            pygame.draw.rect(surf, (100, 100, 100), (24, 5, 16, 4))

        def draw_science(surf):
            # Flask
            pts = [(20, 55), (44, 55), (36, 30), (36, 15), (28, 15), (28, 30)]
            pygame.draw.polygon(surf, (200, 200, 255, 180), pts)
            # Liquid
            l_pts = [(22, 53), (42, 53), (38, 38), (26, 38)]
            pygame.draw.polygon(surf, (150, 50, 250), l_pts)
            # Bubbles
            pygame.draw.circle(surf, (255, 255, 255, 100), (30, 45), 3)
            pygame.draw.circle(surf, (255, 255, 255, 100), (36, 48), 2)
            pygame.draw.rect(surf, (150, 150, 200), (26, 12, 12, 4), border_radius=2)

        def draw_parts(surf):
            # Gear
            center = (32, 32)
            pygame.draw.circle(surf, (140, 145, 155), center, 15)
            pygame.draw.circle(surf, (0, 0, 0, 0), center, 5) # Hole
            for i in range(8):
                angle = (i / 8) * math.pi * 2
                px = center[0] + math.cos(angle) * 18
                py = center[1] + math.sin(angle) * 18
                pygame.draw.circle(surf, (140, 145, 155), (int(px), int(py)), 5)
            pygame.draw.circle(surf, (100, 105, 115), center, 15, 2)

        def draw_wiring(surf):
            # Coil of orange wire
            for i in range(5):
                rect = (12 + i*2, 15 + i*2, 40 - i*4, 34 - i*4)
                pygame.draw.ellipse(surf, (200, 120, 40), rect, 3)
            pygame.draw.line(surf, (180, 100, 30), (10, 40), (20, 50), 4)

        create_item("Wood", draw_wood)
        create_item("Stone", draw_stone)
        create_item("Iron", draw_iron)
        create_item("Copper", draw_copper)
        create_item("Steel", draw_steel)
        create_item("Batteries", draw_batteries)
        create_item("Food", draw_food)
        create_item("Oxygen", draw_oxygen)
        create_item("Science", draw_science)
        create_item("Material Parts", draw_parts)
        create_item("Wiring", draw_wiring)

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
