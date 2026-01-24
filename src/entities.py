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
        self.assigned_building = None # Building object reference
        
        # Food Timer (Random start to stagger consumption)
        # 60 FPS * 60 Seconds = 3600 frames
        self.food_timer = random.randint(0, 3600)

    def update(self):
        # 0. Food Consumption
        self.food_timer += 1
        if self.food_timer >= 3600:
            self.food_timer = 0
            # Eat 1 food
            self.game.resource_manager.remove_resource("food", 1)
        
        # Check Job Status
        if self.state == "WORKING":
            if not self.assigned_building or self.assigned_building not in self.game.world.buildings.values():
                # Fired or building destroyed
                self.state = "IDLE"
                self.job = "Unemployed"
                self.assigned_building = None
                # Eject slightly to the side
                self.x += random.choice([-1, 1])
            return # Don't move or apply gravity while working inside

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

        # Safety Check: Falling off the world
        if self.y > self.game.world.height + 10:
            if self in self.game.entity_manager.villagers:
                # Remove from manager
                self.game.entity_manager.villagers.remove(self)
                # Remove from building if assigned
                if self.assigned_building:
                    if self in self.assigned_building.assigned_workers:
                        self.assigned_building.assigned_workers.remove(self)
            return

        if not is_grounded:
            return # Falling, don't move X

        # 2. AI Logic
        if self.assigned_building:
            # Move towards building
            target_x = self.assigned_building.x + 0.5 # Center of tile
            dx = target_x - self.x
            
            if abs(dx) < 0.2:
                # Arrived
                self.state = "WORKING"
                self.x = target_x # Snap to center
            else:
                self.state = "WALK"
                direction = 1 if dx > 0 else -1
                self.move_x(direction)
        else:
            # Wander logic
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
                    self.move_x(direction)

    def move_x(self, direction):
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
                if self.state == "WANDER":
                    self.state = "IDLE"
        else:
            self.x = next_x

class Trader:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.x = -10
        self.y = 20 # Sky level
        self.target_x = 100 # Default, will be updated on spawn
        self.speed = 0.05
        self.timer = 0
        
    def spawn(self):
        if self.game.world is None: return
        self.active = True
        self.x = -5
        self.y = 20
        self.target_x = self.game.world.width + 5
        
    def update(self):
        if not self.active or self.game.world is None: return
        
        # Move across screen
        self.x += self.speed
        # Bobbing motion
        self.y = 20 + math.sin(self.x * 0.5) * 2
        
        if self.x > self.target_x:
            self.active = False

class EntityManager:
    def __init__(self, game):
        self.game = game
        self.villagers = []
        self.trader = Trader(game)

    def spawn_villager(self, x, y, job="Unemployed"):
        v = Villager(x, y, self.game, job)
        self.villagers.append(v)
        return v

    def update(self):
        if self.game.world is None:
            return
            
        for v in self.villagers:
            v.update()
        self.trader.update()

    def get_count(self):
        return len(self.villagers)