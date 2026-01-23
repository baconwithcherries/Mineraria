import os
import pygame
import random

# Initialize pygame for image handling
pygame.init()

# Enhanced Color Palette (Earthy, Pixel Art style)
COLORS = {
    "TRANSPARENT": (0, 0, 0, 0),
    # Grass / Nature
    "GRASS_LIGHT": (124, 189, 70),
    "GRASS_MID": (86, 161, 56),
    "GRASS_DARK": (45, 105, 45),
    # Dirt
    "DIRT_LIGHT": (160, 110, 80),
    "DIRT_MID": (120, 80, 55),
    "DIRT_DARK": (80, 50, 35),
    # Stone
    "STONE_LIGHT": (160, 160, 170),
    "STONE_MID": (120, 125, 135),
    "STONE_DARK": (80, 85, 95),
    "STONE_BLACK": (40, 40, 50),
    # Wood
    "WOOD_LIGHT": (210, 160, 110),
    "WOOD_MID": (160, 110, 60),
    "WOOD_DARK": (100, 70, 40),
    # Metal / Industrial
    "METAL_LIGHT": (200, 200, 210),
    "METAL_MID": (140, 145, 155),
    "METAL_DARK": (80, 85, 90),
    "RUST": (180, 90, 60),
    # Special
    "SKY": (135, 206, 235),
    "LAVA_LIGHT": (255, 200, 50),
    "LAVA_MID": (255, 100, 0),
    "LAVA_DARK": (180, 20, 0),
    "WATER": (60, 100, 200),
    "GLASS": (200, 240, 255, 150),
    "SKIN": (255, 200, 160),
    "SHIRT": (60, 100, 180),
    "PANTS": (40, 40, 60),
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GOLD": (255, 215, 0),
    "RED": (200, 50, 50),
    "BLUE": (50, 50, 200),
    "RED_DARK": (150, 20, 20),
    "PINK": (255, 182, 193)
}

OUTPUT_DIR = os.path.join("assets", "sprites")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_image(name, size, draw_func):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    draw_func(surf, size[0], size[1])
    pygame.image.save(surf, os.path.join(OUTPUT_DIR, name))
    print(f"Generated {name}")

# --- Helper: Draw Pixel Noise ---
def draw_noise(surf, x, y, w, h, c_base, c_noise, density=0.3):
    pygame.draw.rect(surf, c_base, (x, y, w, h))
    for _ in range(int(w * h * density)):
        px, py = random.randint(x, x+w-1), random.randint(y, y+h-1)
        surf.set_at((px, py), c_noise)

# --- Helper: Draw Bricks ---
def draw_bricks(surf, x, y, w, h, c_mortar, c_brick):
    pygame.draw.rect(surf, c_mortar, (x, y, w, h))
    brick_h = 4
    brick_w = 8
    for by in range(0, h, brick_h):
        offset = (by // brick_h) % 2 * (brick_w // 2)
        for bx in range(-brick_w, w, brick_w):
            rect = pygame.Rect(x + bx + offset + 1, y + by + 1, brick_w - 2, brick_h - 2)
            # Clip to bounds
            clipped = rect.clip(pygame.Rect(x, y, w, h))
            if clipped.width > 0 and clipped.height > 0:
                pygame.draw.rect(surf, c_brick, clipped)

# --- Drawing Functions ---

def draw_grass(surf, w, h):
    # Top grass layer
    draw_noise(surf, 0, 0, w, 8, COLORS["GRASS_MID"], COLORS["GRASS_LIGHT"], 0.2)
    # Highlight top edge
    pygame.draw.line(surf, COLORS["GRASS_LIGHT"], (0, 0), (w, 0))
    # Dirt below
    draw_noise(surf, 0, 8, w, h-8, COLORS["DIRT_MID"], COLORS["DIRT_DARK"], 0.2)
    # Grass hanging down
    for i in range(0, w, 4):
        pygame.draw.line(surf, COLORS["GRASS_MID"], (i, 8), (i, 10 + random.randint(0, 2)), 2)

def draw_dirt(surf, w, h):
    draw_noise(surf, 0, 0, w, h, COLORS["DIRT_MID"], COLORS["DIRT_DARK"], 0.3)
    # Random stones
    for _ in range(3):
        sx, sy = random.randint(2, w-6), random.randint(2, h-6)
        pygame.draw.rect(surf, COLORS["DIRT_LIGHT"], (sx, sy, 3, 3))

def draw_stone(surf, w, h):
    draw_noise(surf, 0, 0, w, h, COLORS["STONE_MID"], COLORS["STONE_DARK"], 0.4)
    # Cracks
    pygame.draw.line(surf, COLORS["STONE_BLACK"], (5, 5), (10, 10))
    pygame.draw.line(surf, COLORS["STONE_BLACK"], (20, 25), (25, 20))

def draw_house(surf, w, h):
    # Wooden Walls (Planks)
    pygame.draw.rect(surf, COLORS["WOOD_MID"], (4, 12, 24, 20))
    for y in range(12, 32, 4):
        pygame.draw.line(surf, COLORS["WOOD_DARK"], (4, y), (28, y))
    
    # Roof (A-Frame)
    # Triangle shape
    pygame.draw.polygon(surf, COLORS["WOOD_DARK"], [(2, 12), (16, 2), (30, 12)])
    pygame.draw.polygon(surf, COLORS["WOOD_LIGHT"], [(4, 12), (16, 4), (28, 12)])
    
    # Door
    pygame.draw.rect(surf, COLORS["WOOD_DARK"], (12, 20, 8, 12))
    surf.set_at((18, 26), COLORS["GOLD"]) # Knob
    
    # Window
    pygame.draw.rect(surf, COLORS["SKY"], (22, 16, 4, 4))
    pygame.draw.rect(surf, COLORS["WOOD_DARK"], (22, 16, 4, 4), 1)

def draw_logging(surf, w, h):
    # Open Shed Structure
    # Pillars
    pygame.draw.rect(surf, COLORS["WOOD_DARK"], (4, 10, 4, 22))
    pygame.draw.rect(surf, COLORS["WOOD_DARK"], (24, 10, 4, 22))
    # Roof (Slanted)
    pygame.draw.polygon(surf, COLORS["WOOD_LIGHT"], [(2, 10), (30, 6), (30, 14), (2, 18)])
    pygame.draw.polygon(surf, COLORS["WOOD_DARK"], [(2, 10), (30, 6), (30, 14), (2, 18)], 1)
    
    # Saw Icon Sign
    pygame.draw.rect(surf, COLORS["WOOD_MID"], (10, 2, 12, 12))
    pygame.draw.rect(surf, COLORS["WOOD_DARK"], (10, 2, 12, 12), 1)
    pygame.draw.line(surf, COLORS["METAL_LIGHT"], (12, 4), (20, 12), 2) # Saw blade approximation
    
    # Log Pile
    for i in range(3):
        y = 28 - (i*3)
        pygame.draw.ellipse(surf, COLORS["WOOD_LIGHT"], (10, y, 12, 4))
        pygame.draw.ellipse(surf, COLORS["WOOD_DARK"], (10, y, 12, 4), 1)

def draw_refinery(surf, w, h):
    # Stone Furnace / Chimney
    draw_bricks(surf, 4, 10, 24, 22, COLORS["STONE_DARK"], COLORS["STONE_MID"])
    
    # Chimney Stack
    pygame.draw.rect(surf, COLORS["STONE_MID"], (20, 0, 6, 10))
    pygame.draw.rect(surf, COLORS["STONE_DARK"], (20, 0, 6, 10), 1)
    pygame.draw.rect(surf, COLORS["STONE_DARK"], (18, 0, 10, 2)) # Top rim
    
    # Fire Pit
    pygame.draw.rect(surf, COLORS["LAVA_MID"], (10, 22, 8, 6))
    pygame.draw.rect(surf, COLORS["STONE_BLACK"], (10, 22, 8, 6), 1)

def draw_mine(surf, w, h):
    # Stone/Dirt mound shape
    # Using arc to simulate mound? Pygame arc is thin line. 
    # Use polygon or ellipse
    pygame.draw.ellipse(surf, COLORS["DIRT_MID"], (2, 10, 28, 30))
    pygame.draw.ellipse(surf, COLORS["DIRT_DARK"], (2, 10, 28, 30), 1)
    
    # Cave Entrance (Dark Arch)
    pygame.draw.rect(surf, COLORS["BLACK"], (10, 18, 12, 14))
    pygame.draw.ellipse(surf, COLORS["BLACK"], (10, 12, 12, 12)) # Top arch part
    
    # Wood Beams
    pygame.draw.rect(surf, COLORS["WOOD_DARK"], (8, 18, 2, 14))
    pygame.draw.rect(surf, COLORS["WOOD_DARK"], (22, 18, 2, 14))
    pygame.draw.rect(surf, COLORS["WOOD_DARK"], (8, 16, 16, 2))

def draw_farm(surf, w, h):
    # Fenced area
    pygame.draw.rect(surf, COLORS["DIRT_MID"], (2, 20, 28, 12))
    pygame.draw.rect(surf, COLORS["WOOD_LIGHT"], (2, 20, 28, 12), 1)
    
    # Crops
    for i in range(3):
        x = 6 + (i * 8)
        # Stalk
        pygame.draw.line(surf, COLORS["GRASS_MID"], (x+2, 28), (x+2, 18), 2)
        # Fruit/Wheat
        pygame.draw.ellipse(surf, COLORS["GOLD"], (x, 14, 4, 4))

def draw_garden(surf, w, h):
    # Planter box
    pygame.draw.rect(surf, COLORS["WOOD_MID"], (2, 22, 28, 10))
    pygame.draw.rect(surf, COLORS["WOOD_DARK"], (2, 22, 28, 10), 1)
    
    # Flowers
    colors = [COLORS["RED"], COLORS["BLUE"], COLORS["WHITE"]]
    for i, c in enumerate(colors):
        x = 6 + (i*8)
        pygame.draw.line(surf, COLORS["GRASS_MID"], (x+2, 24), (x+2, 14))
        pygame.draw.ellipse(surf, c, (x, 10, 5, 5))

def draw_blast_furnace(surf, w, h):
    # Big Industrial Furnace
    pygame.draw.rect(surf, COLORS["METAL_DARK"], (2, 4, 28, 28))
    pygame.draw.rect(surf, COLORS["BLACK"], (2, 4, 28, 28), 1)
    
    # Rivets
    for x in [4, 28]:
        for y in range(4, 32, 6):
            surf.set_at((x, y), COLORS["METAL_LIGHT"])
            
    # Molten Core Window
    pygame.draw.rect(surf, COLORS["LAVA_LIGHT"], (8, 12, 16, 10))
    pygame.draw.rect(surf, COLORS["BLACK"], (8, 12, 16, 10), 1)
    
    # Pipes
    pygame.draw.rect(surf, COLORS["METAL_MID"], (0, 8, 4, 4))
    pygame.draw.rect(surf, COLORS["METAL_MID"], (28, 20, 4, 4))

def draw_rocket(surf, w, h):
    # Retro Rocket
    # Body
    pygame.draw.ellipse(surf, COLORS["METAL_LIGHT"], (8, 2, 16, 26))
    pygame.draw.ellipse(surf, COLORS["METAL_MID"], (8, 2, 16, 26), 1)
    # Fins
    pygame.draw.polygon(surf, COLORS["RED"], [(8, 20), (2, 30), (8, 26)])
    pygame.draw.polygon(surf, COLORS["RED"], [(24, 20), (30, 30), (24, 26)])
    # Window
    pygame.draw.ellipse(surf, COLORS["GLASS"], (12, 10, 8, 8))
    pygame.draw.ellipse(surf, COLORS["METAL_DARK"], (12, 10, 8, 8), 1)

def draw_villager(surf, w, h):
    # Head
    pygame.draw.rect(surf, COLORS["SKIN"], (10, 4, 12, 8))
    # Eyes
    surf.set_at((12, 8), COLORS["BLACK"])
    surf.set_at((18, 8), COLORS["BLACK"])
    # Shirt
    pygame.draw.rect(surf, COLORS["SHIRT"], (8, 12, 16, 12))
    # Pants
    pygame.draw.rect(surf, COLORS["PANTS"], (10, 24, 4, 8))
    pygame.draw.rect(surf, COLORS["PANTS"], (18, 24, 4, 8))

def draw_warehouse(surf, w, h):
    # Large Storage Barn
    # Main building
    pygame.draw.rect(surf, COLORS["WOOD_MID"], (2, 10, 28, 22))
    pygame.draw.rect(surf, COLORS["WOOD_DARK"], (2, 10, 28, 22), 1)
    # Big Double Doors
    pygame.draw.rect(surf, COLORS["WOOD_DARK"], (10, 18, 12, 14))
    pygame.draw.line(surf, COLORS["WOOD_MID"], (16, 18), (16, 32)) # Split
    # Roof
    pygame.draw.polygon(surf, COLORS["RED_DARK"], [(0, 10), (16, 0), (32, 10)])
    pygame.draw.polygon(surf, COLORS["BLACK"], [(0, 10), (16, 0), (32, 10)], 1)

def draw_lab(surf, w, h):
    # Modern-ish Lab
    pygame.draw.rect(surf, COLORS["WHITE"], (4, 10, 24, 22))
    pygame.draw.rect(surf, COLORS["METAL_MID"], (4, 10, 24, 22), 1)
    # Glass Windows
    pygame.draw.rect(surf, COLORS["GLASS"], (6, 14, 6, 6))
    pygame.draw.rect(surf, COLORS["GLASS"], (20, 14, 6, 6))
    # Antenna on roof
    pygame.draw.line(surf, COLORS["METAL_DARK"], (16, 10), (16, 2))
    pygame.draw.ellipse(surf, COLORS["RED"], (14, 0, 4, 4))

# --- UI Icons ---
def draw_icon_build(surf, w, h):
    # Hammer
    pygame.draw.rect(surf, COLORS["WOOD_LIGHT"], (0, 0, w, h))
    pygame.draw.line(surf, COLORS["WOOD_DARK"], (8, 24), (24, 8), 3)
    pygame.draw.rect(surf, COLORS["METAL_MID"], (20, 4, 8, 8))
    pygame.draw.rect(surf, COLORS["BLACK"], (20, 4, 8, 8), 1)

def draw_icon_inv(surf, w, h):
    # Chest
    pygame.draw.rect(surf, COLORS["WOOD_MID"], (4, 8, 24, 16))
    pygame.draw.rect(surf, COLORS["BLACK"], (4, 8, 24, 16), 1)
    pygame.draw.rect(surf, COLORS["WOOD_LIGHT"], (4, 8, 24, 6)) # Lid
    pygame.draw.rect(surf, COLORS["BLACK"], (4, 8, 24, 6), 1)
    pygame.draw.rect(surf, COLORS["GOLD"], (14, 14, 4, 4)) # Lock

def draw_icon_arrow(surf, w, h):
    pygame.draw.polygon(surf, COLORS["GRASS_MID"], [(16, 4), (28, 20), (20, 20), (20, 28), (12, 28), (12, 20), (4, 20)])
    pygame.draw.polygon(surf, COLORS["BLACK"], [(16, 4), (28, 20), (20, 20), (20, 28), (12, 28), (12, 20), (4, 20)], 1)

def draw_cloud(surf, w, h):
    pygame.draw.ellipse(surf, COLORS["WHITE"], (4, 10, 12, 12))
    pygame.draw.ellipse(surf, COLORS["WHITE"], (12, 4, 20, 16))
    pygame.draw.ellipse(surf, COLORS["WHITE"], (20, 8, 10, 12))

def draw_title_bg(surf, w, h):
    # Gradient Sky
    for y in range(h):
        r = max(0, min(255, int(135 - (y/h)*50)))
        g = max(0, min(255, int(206 - (y/h)*50)))
        b = max(0, min(255, int(235 - (y/h)*20)))
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
    
    # Hills
    # Pieslice logic in pygame is draw.arc or complex polygon. 
    # Use ellipse for hills
    pygame.draw.ellipse(surf, COLORS["GRASS_MID"], (-50, h-100, 250, 150))
    pygame.draw.ellipse(surf, COLORS["GRASS_LIGHT"], (150, h-80, 300, 160))
    pygame.draw.ellipse(surf, COLORS["GRASS_MID"], (400, h-120, 300, 170))

def generate_all():
    random.seed(42) # Consistent noise
    
    # Blocks and Tiles
    create_image("grass.png", (32, 32), draw_grass)
    create_image("dirt.png", (32, 32), draw_dirt)
    create_image("stone.png", (32, 32), draw_stone)
    
    # Buildings
    create_image("logging_workshop.png", (32, 32), draw_logging)
    create_image("stone_refinery.png", (32, 32), draw_refinery)
    create_image("mine.png", (32, 32), draw_mine)
    create_image("house.png", (32, 32), draw_house)
    create_image("rocket_ship.png", (32, 32), draw_rocket)
    create_image("farm.png", (32, 32), draw_farm)
    create_image("garden.png", (32, 32), draw_garden)
    create_image("blast_furnace.png", (32, 32), draw_blast_furnace)
    create_image("warehouse.png", (32, 32), draw_warehouse)
    create_image("laboratory.png", (32, 32), draw_lab)
    
    # Entities
    create_image("villager.png", (32, 32), draw_villager)
    
    # UI
    create_image("cloud.png", (64, 32), draw_cloud)
    create_image("icon_build.png", (32, 32), draw_icon_build)
    create_image("icon_inventory.png", (32, 32), draw_icon_inv)
    create_image("icon_arrow_up.png", (32, 32), draw_icon_arrow)
    create_image("title_bg.png", (640, 360), draw_title_bg)

if __name__ == "__main__":
    generate_all()