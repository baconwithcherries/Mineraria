import random
import math

class Villager:
    def __init__(self, x, y, game, job="Unemployed"):
        self.x = x
        self.y = y
        self.game = game
        self.state = "IDLE"
        self.target_x = x
        self.speed = 0.05
        self.vy = 0 # Vertical velocity
        self.job = job

    def update(self):
        # 1. Gravity
        # Check block below
        ix = int(self.x)
        iy = int(self.y + 1) # tile below feet
        
        below_tile = self.game.world.get_tile(ix, iy)
        building_below = self.game.world.get_building_at(ix, iy)
        
        is_grounded = False
        if (below_tile and below_tile.tile_type != "air") or building_below:
            is_grounded = True
            self.vy = 0
            self.y = math.floor(self.y) # Snap to grid
        else:
            self.vy += 0.01 # Gravity
            self.y += self.vy

        if not is_grounded:
            return # Falling, don't move X

        # 2. AI Logic
        if self.state == "IDLE":
            if random.random() < 0.01:
                self.state = "WANDER"
                self.target_x = self.x + random.randint(-5, 5)
                # Clamp to island
                self.target_x = max(0, min(self.game.world.width - 1, self.target_x))

        if self.state == "WANDER":
            dx = self.target_x - self.x
            if abs(dx) < 0.1:
                self.state = "IDLE"
            else:
                direction = 1 if dx > 0 else -1
                next_x = self.x + direction * self.speed
                
                # Check wall ahead
                next_ix = int(next_x + (0.5 * direction))
                iy_head = int(self.y)
                wall_tile = self.game.world.get_tile(next_ix, iy_head)
                wall_building = self.game.world.get_building_at(next_ix, iy_head)
                
                if (wall_tile and wall_tile.tile_type != "air") or wall_building:
                    # Jump?
                    # Check if space above wall is empty
                    above_wall = self.game.world.get_tile(next_ix, iy_head - 1)
                    if above_wall and above_wall.tile_type == "air":
                        self.y -= 1.1 # Jump up
                        self.x += direction * self.speed
                    else:
                        # Blocked, stop
                        self.state = "IDLE"
                else:
                    self.x = next_x

class EntityManager:
    def __init__(self, game):
        self.game = game
        self.villagers = []

    def spawn_villager(self, x, y, job="Unemployed"):
        v = Villager(x, y, self.game, job)
        self.villagers.append(v)

    def update(self):
        for v in self.villagers:
            v.update()

    def get_count(self):
        return len(self.villagers)