import os
from PIL import Image, ImageDraw

COLORS = {
    "TRANSPARENT": (0, 0, 0, 0),
    "GRASS_TOP": (50, 205, 50),
    "GRASS_SIDE": (34, 139, 34),
    "DIRT": (139, 69, 19),
    "DIRT_DARK": (101, 67, 33),
    "STONE": (128, 128, 128),
    "STONE_DARK": (105, 105, 105),
    "WOOD": (160, 82, 45),
    "WOOD_DARK": (139, 69, 19),
    "METAL": (192, 192, 192),
    "METAL_DARK": (169, 169, 169),
    "RED": (200, 50, 50),
    "BLUE": (50, 50, 200),
    "SKIN": (255, 224, 189),
    "GOLD": (255, 215, 0),
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "ORANGE": (255, 140, 0)
}

OUTPUT_DIR = os.path.join("assets", "sprites")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_image(name, size, draw_func):
    img = Image.new("RGBA", size, COLORS["TRANSPARENT"])
    draw = ImageDraw.Draw(img)
    draw_func(draw, size[0], size[1])
    img.save(os.path.join(OUTPUT_DIR, name))
    print(f"Generated {name}")

# --- Drawing Functions ---

def draw_grass(d, w, h):
    # Dirt base
    d.rectangle([0, 0, w, h], fill=COLORS["DIRT"])
    # Noise
    for i in range(0, w, 2):
        for j in range(0, h, 2):
            if (i+j)%3 == 0: d.point([i, j], fill=COLORS["DIRT_DARK"])
    # Grass Top
    d.rectangle([0, 0, w, 4], fill=COLORS["GRASS_TOP"])
    # Grass blades
    for i in range(0, w, 2):
        d.line([i, 0, i, 2], fill=COLORS["GRASS_SIDE"])

def draw_dirt(d, w, h):
    d.rectangle([0, 0, w, h], fill=COLORS["DIRT"])
    # Random noise pattern
    import random
    random.seed(42)
    for _ in range(20):
        x, y = random.randint(0, w-1), random.randint(0, h-1)
        d.point([x, y], fill=COLORS["DIRT_DARK"])

def draw_stone(d, w, h):
    d.rectangle([0, 0, w, h], fill=COLORS["STONE"])
    # Crack pattern
    d.line([2, 2, 6, 6], fill=COLORS["STONE_DARK"], width=1)
    d.line([10, 10, 14, 8], fill=COLORS["STONE_DARK"], width=1)
    d.point([5, 12], fill=COLORS["STONE_DARK"])
    d.point([12, 4], fill=COLORS["STONE_DARK"])

def draw_logging(d, w, h):
    d.rectangle([0, 0, w, h], fill=COLORS["WOOD"])
    d.rectangle([2, 2, w-3, h-3], outline=COLORS["WOOD_DARK"])
    # Saw blade
    d.ellipse([4, 4, 12, 12], fill=COLORS["METAL"], outline=COLORS["BLACK"])

def draw_refinery(d, w, h):
    d.rectangle([0, 0, w, h], fill=COLORS["STONE_DARK"])
    # Furnace hole
    d.rectangle([4, 8, 12, 14], fill=COLORS["ORANGE"])
    # Bricks
    d.line([0, 4, w, 4], fill=COLORS["BLACK"])
    d.line([0, 10, w, 10], fill=COLORS["BLACK"])

def draw_mine(d, w, h):
    d.rectangle([0, 0, w, h], fill=COLORS["DIRT_DARK"])
    # Entrance
    d.ellipse([2, 2, 14, 14], fill=COLORS["BLACK"])
    d.rectangle([0, 14, w, h], fill=COLORS["BLACK"])
    # Supports
    d.line([4, 2, 4, 14], fill=COLORS["WOOD"], width=2)
    d.line([12, 2, 12, 14], fill=COLORS["WOOD"], width=2)
    d.line([4, 2, 12, 2], fill=COLORS["WOOD"], width=2)

def draw_house(d, w, h):
    # Walls
    d.rectangle([2, 6, 14, 16], fill=COLORS["WOOD"])
    # Roof
    d.polygon([(1, 6), (8, 0), (15, 6)], fill=COLORS["RED"])
    # Door
    d.rectangle([6, 10, 10, 16], fill=COLORS["WOOD_DARK"])
    # Window
    d.rectangle([3, 8, 5, 10], fill=COLORS["BLUE"])
    d.rectangle([11, 8, 13, 10], fill=COLORS["BLUE"])

def draw_rocket(d, w, h):
    # Fins
    d.polygon([(2, 14), (0, 16), (4, 12)], fill=COLORS["RED"])
    d.polygon([(14, 14), (16, 16), (12, 12)], fill=COLORS["RED"])
    # Body
    d.ellipse([4, 2, 12, 14], fill=COLORS["METAL"])
    # Window
    d.ellipse([6, 6, 10, 10], fill=COLORS["BLUE"], outline=COLORS["METAL_DARK"])

def draw_villager(d, w, h):
    # Head
    d.rectangle([6, 2, 10, 6], fill=COLORS["SKIN"])
    # Body
    d.rectangle([5, 6, 11, 12], fill=COLORS["BLUE"])
    # Legs
    d.rectangle([6, 12, 7, 16], fill=COLORS["BLACK"])
    d.rectangle([9, 12, 10, 16], fill=COLORS["BLACK"])

def draw_icon_build(d, w, h):
    # Hammer
    d.line([6, 26, 16, 16], fill=COLORS["WOOD"], width=4) # Handle
    d.rectangle([14, 8, 24, 18], fill=COLORS["GOLD"]) # Head

def draw_icon_inv(d, w, h):
    d.rectangle([4, 8, 28, 24], fill=COLORS["WOOD"])
    d.rectangle([4, 8, 28, 24], outline=COLORS["BLACK"], width=2)
    d.rectangle([12, 14, 20, 18], fill=COLORS["GOLD"]) # Lock
    d.arc([4, 4, 28, 12], 180, 360, fill=COLORS["WOOD"]) # Lid curve attempt

def draw_icon_arrow(d, w, h):
    d.polygon([(8, 0), (16, 8), (12, 8), (12, 16), (4, 16), (4, 8), (0, 8)], fill=COLORS["GRASS_TOP"], outline=COLORS["BLACK"])

def draw_cloud(d, w, h):
    # Fluffy white clouds
    d.ellipse([2, 8, 10, 14], fill=COLORS["WHITE"])
    d.ellipse([6, 4, 18, 14], fill=COLORS["WHITE"])
    d.ellipse([14, 8, 26, 14], fill=COLORS["WHITE"])
    d.ellipse([10, 10, 22, 18], fill=COLORS["WHITE"])

def draw_title_bg(d, w, h):
    # Sky
    d.rectangle([0, 0, w, h], fill=(135, 206, 235))
    # Ground
    d.rectangle([0, h-40, w, h], fill=COLORS["GRASS_TOP"])
    # Some buildings and villagers to look "cool"
    # House
    d.rectangle([40, h-80, 80, h-40], fill=COLORS["WOOD"])
    d.polygon([(40, h-80), (60, h-110), (80, h-80)], fill=COLORS["RED"])
    # Mine
    d.ellipse([150, h-70, 200, h-40], fill=COLORS["BLACK"])
    # Villagers
    for i in range(5):
        vx = 100 + i*40
        d.rectangle([vx, h-60, vx+10, h-40], fill=COLORS["BLUE"])
        d.rectangle([vx+2, h-70, vx+8, h-60], fill=COLORS["SKIN"])

def generate_all():
    create_image("grass.png", (16, 16), draw_grass)
    create_image("title_bg.png", (640, 360), draw_title_bg)
    create_image("cloud.png", (32, 20), draw_cloud)
    # ...
    create_image("dirt.png", (16, 16), draw_dirt)
    create_image("stone.png", (16, 16), draw_stone)
    
    create_image("logging_workshop.png", (16, 16), draw_logging)
    create_image("stone_refinery.png", (16, 16), draw_refinery)
    create_image("mine.png", (16, 16), draw_mine)
    create_image("house.png", (16, 16), draw_house)
    create_image("rocket_ship.png", (16, 16), draw_rocket)
    
    create_image("villager.png", (16, 16), draw_villager)
    
    create_image("icon_build.png", (32, 32), draw_icon_build)
    create_image("icon_inventory.png", (32, 32), draw_icon_inv)
    create_image("icon_arrow_up.png", (16, 16), draw_icon_arrow)

if __name__ == "__main__":
    generate_all()
