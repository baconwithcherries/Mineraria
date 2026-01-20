import pygame
import math
import random

class TickManager:
    def __init__(self, game):
        self.game = game
        self.last_tick = pygame.time.get_ticks()
        self.tick_interval = 1000 # 1 second
        
        # Day/Night Cycle
        self.total_cycle_time = 1200 # 20 minutes = 1200 seconds
        self.current_time = 0 # 0-600 Day, 600-1200 Night
        self.day_counter = 1

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_tick >= self.tick_interval:
            self.last_tick = now
            self.on_tick()

    def on_tick(self):
        # 1. Update Time
        self.current_time += 1
        if self.current_time >= self.total_cycle_time:
            self.current_time = 0
            self.day_counter += 1
        
        # 2. Happiness Calculation
        self.update_happiness()
        
        # 3. Food Logic (Consumption)
        self.run_food_logic()

        # 4. Production Logic
        self.run_production()
        
        # 5. Villager Spawning
        self.run_spawning()

    def update_happiness(self):
        # Each garden gives 1% happiness
        garden_count = sum(1 for b in self.game.world.buildings.values() if b.type == "Garden")
        self.game.resource_manager.happiness = garden_count * 1.0 # 1.0 = 1%

    def run_food_logic(self):
        # Villagers consume food at 1 per minute -> 1/60 per second
        total_villagers = self.game.entity_manager.get_count()
        consumption = (total_villagers / 60.0)
        self.game.resource_manager.inventory["food"] = max(0.0, self.game.resource_manager.inventory["food"] - consumption)

    def run_production(self):
        # Count available villagers per job
        available_jobs = {
            "Logging Workshop": 0,
            "Stone Refinery": 0,
            "Blast Furnace": 0,
            "Mine": 0,
            "Farm": 0,
            "Garden": 0 # Garden can use Farm workers or we treat it as Farm
        }
        for v in self.game.entity_manager.villagers:
            if v.job in available_jobs:
                available_jobs[v.job] += 1
            elif v.job == "Farm": # Garden uses Farm workers
                available_jobs["Garden"] += 1
        
        # Garden and Farm share the "Farm" job pool for simplicity or specific Garden job
        # User didn't specify Garden job color, so assuming it uses Farm pool.
        
        # Sort buildings to prioritize older ones or specific types if needed, 
        # but here we just need to ensure ALL are processed.
        for pos, building in self.game.world.buildings.items():
            if building.type == "House":
                building.record_production(building.villagers)
                continue 

            required = 3 * building.level 
            produced = 0
            
            # Use specific job pool
            job_type = building.type
            if building.type == "Garden": job_type = "Farm" # Gardens use farm workers
            
            if available_jobs.get(job_type, 0) >= required:
                available_jobs[job_type] -= required
                
                # --- Production Balancing ---
                # Original was 1 unit per tick (1 second).
                # New: 10x slower at Level 1 (0.1 units per tick).
                # At Level 10, should be 1 unit per tick.
                # Scaling formula: 0.1 * level
                # At Level 25: 2.5 units per tick.
                
                # Happiness bonus: 1% happiness = 2% production speedup
                happiness_bonus = 1.0 + (self.game.resource_manager.happiness * 0.02)
                production_rate = 0.1 * building.level * self.game.resource_manager.food_efficiency * happiness_bonus
                
                if building.type == "Farm" or building.type == "Garden":
                    # Garden acts like a Farm (produces food)
                    food_rate = (100.0 / 60.0) * building.level * self.game.resource_manager.food_efficiency * happiness_bonus
                    self.game.resource_manager.inventory["food"] += food_rate
                    produced = food_rate
                elif building.type == "Blast Furnace":
                    # Blast Furnace production (chance based)
                    # Needs to be within 10 blocks of a stone refinery (Check in building tab placement, but here too for logic)
                    can_produce = False
                    for b in self.game.world.buildings.values():
                        if b.type == "Stone Refinery":
                            dist = math.sqrt((building.x - b.x)**2 + (building.y - b.y)**2)
                            if dist <= 10:
                                can_produce = True
                                break
                    
                    if can_produce:
                        # Percentage checks (per tick)
                        # 75% steel, 50% copper, 25% gold, 10% emerald, 0.1% diamond
                        # Since this runs every second, these chances are VERY high. 
                        # I'll scale them down to per-tick equivalent or keep as requested if that's the literal intent.
                        # The request says "percentage here is the percentage 75% steel 50% copper..."
                        
                        if random.random() < 0.75: self.game.resource_manager.inventory["steel"] += 1
                        if random.random() < 0.50: self.game.resource_manager.inventory["copper"] += 1
                        if random.random() < 0.25: self.game.resource_manager.inventory["gold"] += 1
                        if random.random() < 0.10: self.game.resource_manager.inventory["emerald"] += 1
                        if random.random() < 0.001: self.game.resource_manager.inventory["diamond"] += 1
                        produced = 1 # Indicator for record_production
                else:
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
                     if random.random() < (1.0/6.0):
                         building.villagers += 1
                         # Assign random job on spawn
                         jobs = ["Logging Workshop", "Stone Refinery", "Blast Furnace", "Mine", "Farm"]
                         job = random.choice(jobs)
                         self.game.entity_manager.spawn_villager(building.x, building.y, job)

    def is_day(self):
        return self.current_time < (self.total_cycle_time / 2)
