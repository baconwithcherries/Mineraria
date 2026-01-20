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
    "RED_DARK": (150, 20, 20),
    "BLUE": (50, 50, 200),
    "SKIN": (255, 224, 189),
    "GOLD": (255, 215, 0),
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "ORANGE": (255, 140, 0),
    "GLASS": (200, 255, 255, 120),
    "LEAF": (34, 139, 34),
    "PINK": (255, 182, 193),
    "EMERALD": (80, 200, 120),
    "DIAMOND": (185, 242, 255)
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
    d.rectangle([0, 0, w, h], fill=COLORS["DIRT"])
    d.rectangle([0, 0, w, h//4], fill=COLORS["GRASS_TOP"])
    for i in range(0, w, 4):
        d.rectangle([i, h//4, i+2, h//2], fill=COLORS["GRASS_SIDE"])

def draw_dirt(d, w, h):
    d.rectangle([0, 0, w, h], fill=COLORS["DIRT"])
    import random
    random.seed(42)
    for _ in range(30):
        x, y = random.randint(0, w-1), random.randint(0, h-1)
        d.point([x, y], fill=COLORS["DIRT_DARK"])

def draw_stone(d, w, h):
    d.rectangle([0, 0, w, h], fill=COLORS["STONE"])
    d.line([4, 4, 12, 12], fill=COLORS["STONE_DARK"], width=2)
    d.line([20, 5, 28, 15], fill=COLORS["STONE_DARK"], width=2)
    d.line([5, 25, 15, 20], fill=COLORS["STONE_DARK"], width=2)

def draw_logging(d, w, h):
    # Log cabin style
    d.rectangle([4, 10, 28, 30], fill=COLORS["WOOD"], outline=COLORS["BLACK"])
    for i in range(12, 30, 6):
        d.line([4, i, 28, i], fill=COLORS["WOOD_DARK"])
    # Saw blade decoration
    d.ellipse([10, 14, 22, 26], fill=COLORS["METAL"], outline=COLORS["BLACK"])
    d.point([16, 20], fill=COLORS["BLACK"])

def draw_refinery(d, w, h):
    # Brick factory
    d.rectangle([4, 6, 28, 30], fill=COLORS["STONE_DARK"], outline=COLORS["BLACK"])
    for i in range(8, 30, 4):
        d.line([4, i, 28, i], fill=COLORS["BLACK"])
    # Chimney
    d.rectangle([20, 0, 26, 6], fill=COLORS["STONE_DARK"], outline=COLORS["BLACK"])
    # Furnace
    d.rectangle([10, 20, 22, 30], fill=COLORS["BLACK"])
    d.rectangle([12, 22, 20, 28], fill=COLORS["ORANGE"])

def draw_mine(d, w, h):
    d.rectangle([0, 0, w, h], fill=COLORS["DIRT_DARK"])
    # Mine shaft
    d.rectangle([6, 10, 26, 30], fill=COLORS["BLACK"])
    # Wood supports
    d.rectangle([4, 8, 8, 30], fill=COLORS["WOOD"])
    d.rectangle([24, 8, 28, 30], fill=COLORS["WOOD"])
    d.rectangle([4, 8, 28, 12], fill=COLORS["WOOD"])
    # Lantern
    d.rectangle([14, 12, 18, 18], fill=COLORS["GOLD"])

def draw_house(d, w, h):
    # Better house
    d.rectangle([4, 12, 28, 30], fill=COLORS["WHITE"], outline=COLORS["BLACK"])
    d.polygon([(2, 12), (16, 2), (30, 12)], fill=COLORS["RED_DARK"], outline=COLORS["BLACK"])
    d.rectangle([12, 20, 20, 30], fill=COLORS["WOOD_DARK"]) # Door
    d.rectangle([6, 16, 10, 20], fill=COLORS["BLUE"]) # Window
    d.rectangle([22, 16, 26, 20], fill=COLORS["BLUE"])

def draw_farm(d, w, h):
    # Glass box
    d.rectangle([2, 2, 29, 29], fill=COLORS["GLASS"], outline=COLORS["WHITE"])
    # Vines
    d.line([8, 28, 16, 10], fill=COLORS["LEAF"], width=2)
    d.line([24, 28, 16, 15], fill=COLORS["LEAF"], width=2)
    # Fruit
    d.ellipse([14, 8, 18, 12], fill=COLORS["RED"])
    d.ellipse([10, 18, 14, 22], fill=COLORS["RED"])
    d.ellipse([20, 16, 24, 20], fill=COLORS["RED"])

def draw_garden(d, w, h):
    # More detailed version of Farm
    d.rectangle([2, 2, 29, 29], fill=COLORS["GLASS"], outline=COLORS["WHITE"])
    # Flowers
    d.line([16, 28, 16, 10], fill=COLORS["LEAF"], width=2)
    d.ellipse([12, 6, 20, 10], fill=COLORS["PINK"]) # Center flower
    d.ellipse([6, 14, 10, 18], fill=COLORS["GOLD"]) # Left flower
    d.ellipse([22, 14, 26, 18], fill=(255, 255, 255)) # Right flower
    # Grass patches
    d.rectangle([4, 26, 28, 29], fill=COLORS["GRASS_TOP"])

def draw_blast_furnace(d, w, h):
    # Heavy industrial furnace
    d.rectangle([2, 4, 30, 30], fill=(50, 50, 50), outline=COLORS["BLACK"])
    d.rectangle([6, 0, 12, 4], fill=(50, 50, 50)) # Pipe 1
    d.rectangle([20, 0, 26, 4], fill=(50, 50, 50)) # Pipe 2
    # Lava/Molten metal glow
    d.rectangle([8, 15, 24, 25], fill=COLORS["ORANGE"])
    d.line([8, 15, 24, 15], fill=COLORS["BLACK"])
    d.line([8, 25, 24, 25], fill=COLORS["BLACK"])
    # Rivets
    for i in range(6, 30, 8):
        d.point([4, i], fill=COLORS["METAL"])
        d.point([28, i], fill=COLORS["METAL"])

def draw_rocket(d, w, h):
    # Detailed Rocket
    d.polygon([(16, 0), (8, 10), (24, 10)], fill=COLORS["RED"]) # Nose
    d.rectangle([8, 10, 24, 26], fill=COLORS["METAL"], outline=COLORS["BLACK"]) # Body
    d.ellipse([12, 14, 20, 22], fill=COLORS["BLUE"], outline=COLORS["BLACK"]) # Window
    d.polygon([(8, 20), (2, 30), (8, 30)], fill=COLORS["RED"]) # Left fin
    d.polygon([(24, 20), (30, 30), (24, 30)], fill=COLORS["RED"]) # Right fin

def draw_villager(d, w, h):
    d.rectangle([12, 4, 20, 12], fill=COLORS["SKIN"]) # Head
    d.rectangle([10, 12, 22, 24], fill=COLORS["BLUE"]) # Body
    d.rectangle([12, 24, 14, 30], fill=COLORS["BLACK"]) # Leg L
    d.rectangle([18, 24, 20, 30], fill=COLORS["BLACK"]) # Leg R

def draw_icon_build(d, w, h):
    d.line([6, 26, 16, 16], fill=COLORS["WOOD"], width=4)
    d.rectangle([14, 8, 24, 18], fill=COLORS["GOLD"], outline=COLORS["BLACK"])

def draw_icon_inv(d, w, h):
    d.rectangle([4, 10, 28, 26], fill=COLORS["WOOD"], outline=COLORS["BLACK"])
    d.rectangle([14, 16, 18, 20], fill=COLORS["GOLD"])

def draw_icon_arrow(d, w, h):
    d.polygon([(16, 2), (28, 14), (20, 14), (20, 28), (12, 28), (12, 14), (4, 14)], fill=COLORS["GRASS_TOP"], outline=COLORS["BLACK"])

def draw_cloud(d, w, h):
    d.ellipse([2, 10, 14, 22], fill=COLORS["WHITE"])
    d.ellipse([10, 4, 22, 22], fill=COLORS["WHITE"])
    d.ellipse([18, 10, 30, 22], fill=COLORS["WHITE"])

def draw_title_bg(d, w, h):
    d.rectangle([0, 0, w, h], fill=(135, 206, 235))
    d.rectangle([0, h-40, w, h], fill=COLORS["GRASS_TOP"])

def generate_all():
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
    
    # Entities
    create_image("villager.png", (32, 32), draw_villager)
    
    # UI
    create_image("cloud.png", (32, 32), draw_cloud)
    create_image("icon_build.png", (32, 32), draw_icon_build)
    create_image("icon_inventory.png", (32, 32), draw_icon_inv)
    create_image("icon_arrow_up.png", (32, 32), draw_icon_arrow)
    create_image("title_bg.png", (640, 360), draw_title_bg)

if __name__ == "__main__":
    generate_all()