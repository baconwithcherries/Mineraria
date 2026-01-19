import pygame

class TickManager:
    def __init__(self, game):
        self.game = game
        self.last_tick = pygame.time.get_ticks()
        self.tick_interval = 1000 # 1 second
        
        # Day/Night Cycle
        self.total_cycle_time = 1200 # 20 minutes = 1200 seconds
        self.current_time = 0 # 0-600 Day, 600-1200 Night

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_tick >= self.tick_interval:
            self.last_tick = now
            self.on_tick()

    def on_tick(self):
        # 1. Update Time
        self.current_time = (self.current_time + 1) % self.total_cycle_time
        
        # 2. Production Logic
        self.run_production()
        
        # 3. Villager Spawning
        self.run_spawning()

    def run_production(self):
        total_villagers = self.game.entity_manager.get_count()
        used_villagers = 0
        
        # Sort buildings to prioritize older ones or specific types if needed, 
        # but here we just need to ensure ALL are processed.
        for pos, building in self.game.world.buildings.items():
            if building.type == "House":
                building.record_production(building.villagers)
                continue 

            required = 3 * building.level 
            produced = 0
            
            if total_villagers - used_villagers >= required:
                used_villagers += required
                
                # --- Production Balancing ---
                # Original was 1 unit per tick (1 second).
                # New: 10x slower at Level 1 (0.1 units per tick).
                # At Level 10, should be 1 unit per tick.
                # Scaling formula: 0.1 * level
                # At Level 25: 2.5 units per tick.
                
                production_rate = 0.1 * building.level
                building.production_buffer += production_rate
                produced = production_rate
            
            building.record_production(produced)

    def run_spawning(self):
        # Houses produce villagers 10/min -> 1 every 6 seconds.
        # Max 20 per house (Lvl 1).
        
        for pos, building in self.game.world.buildings.items():
            if building.type == "House":
                # Check current occupancy linked to this house?
                # For now, let's just use global cap or simple local counter if we link villagers to houses.
                # Spec: "max out at each house for level 1 at a max of 20 occupancy"
                
                # We need to track how many villagers belong to this house.
                # For MVP, let's just add a counter to the building.
                if building.villagers < 20 * building.level:
                     # 10 per minute = 1 per 6 seconds.
                     # We can use a timer or random chance. 1/6 chance per second.
                     import random
                     if random.random() < (1.0/6.0):
                         building.villagers += 1
                         self.game.entity_manager.spawn_villager(building.x, building.y)

    def is_day(self):
        return self.current_time < (self.total_cycle_time / 2)
