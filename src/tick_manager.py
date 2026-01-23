import pygame
import math
import random

class TickManager:
    def __init__(self, game):
        self.game = game
        self.last_tick = pygame.time.get_ticks()
        self.tick_interval = 1000 # 1 second
        self.time_scale = 1 # 1x speed
        
        # Day/Night Cycle
        self.total_cycle_time = 1200 # 20 minutes = 1200 seconds
        self.current_time = 0 # 0-600 Day, 600-1200 Night
        self.day_counter = 1

    def update(self):
        now = pygame.time.get_ticks()
        current_interval = self.tick_interval / self.time_scale
        
        # Calculate Storage Cap
        warehouse_count = sum(1 for b in self.game.world.buildings.values() if b.type == "Warehouse")
        self.game.resource_manager.max_storage = 100 + (warehouse_count * 200)
        
        if now - self.last_tick >= current_interval:
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
        
        # 2.5 Job Balancing
        self.balance_jobs()
        
        # 4. Production Logic
        self.run_production()
        
        # 5. Villager Spawning
        self.run_spawning()

    def balance_jobs(self):
        job_types = ["Logging Workshop", "Stone Refinery", "Mine", "Farm", "Garden", "Blast Furnace", "Laboratory"]
        
        for job in job_types:
            # Get buildings of this type
            buildings = [b for b in self.game.world.buildings.values() if b.type == job]
            if not buildings: continue
            
            # Calculate total capacity and current workers
            total_capacity = sum(3 * b.level for b in buildings)
            
            all_workers = []
            for b in buildings:
                all_workers.extend(b.assigned_workers)
            
            # Determine target
            target_setting = self.game.resource_manager.job_targets.get(job, -1)
            if target_setting == -1:
                desired_total = total_capacity
            else:
                desired_total = min(target_setting, total_capacity)
            
            current_count = len(all_workers)
            
            # Fire if too many
            if current_count > desired_total:
                to_fire = current_count - desired_total
                # Fire from last added (simple logic)
                for _ in range(to_fire):
                    if not all_workers: break
                    worker = all_workers.pop()
                    # Remove from building
                    if worker.assigned_building:
                        worker.assigned_building.assigned_workers.remove(worker)
                        worker.assigned_building = None
                    worker.job = "Unemployed"
            
            # Hire if too few
            elif current_count < desired_total:
                to_hire = desired_total - current_count
                unemployed = [v for v in self.game.entity_manager.villagers if v.job == "Unemployed"]
                
                count = 0
                for worker in unemployed:
                    if count >= to_hire: break
                    
                    # Find a building with space
                    # We should probably fill them evenly or just first available
                    # Let's fill first available for simplicity
                    assigned = False
                    for b in buildings:
                        cap = 3 * b.level
                        if len(b.assigned_workers) < cap:
                            b.assigned_workers.append(worker)
                            worker.assigned_building = b
                            worker.job = job
                            assigned = True
                            count += 1
                            break
                    
                    if not assigned:
                        break # No space left (shouldn't happen given logic above)

    def update_happiness(self):
        # Each garden gives 1% happiness
        garden_count = sum(1 for b in self.game.world.buildings.values() if b.type == "Garden")
        self.game.resource_manager.happiness = garden_count * 1.0 # 1.0 = 1%

    def run_production(self):
        # Sort buildings to prioritize older ones or specific types if needed, 
        # but here we just need to ensure ALL are processed.
        for pos, building in self.game.world.buildings.items():
            if building.type == "House":
                building.record_production(building.villagers, self.day_counter)
                continue 

            # Production scales with workers
            assigned_count = len(building.assigned_workers)
            if assigned_count > 0:
                # Base efficiency: 1 worker = 33% of original speed (since orig required 3)
                # But let's make it simpler.
                # Old logic: 3 workers = 0.1 * level
                # New logic: 1 worker = (0.1 * level) / 3
                
                base_per_worker = (0.1 * building.level) / 3.0
                
                # Happiness bonus: 1% happiness = 2% production speedup
                happiness_bonus = 1.0 + (self.game.resource_manager.happiness * 0.02)
                production_rate = base_per_worker * assigned_count * self.game.resource_manager.food_efficiency * happiness_bonus
                
                produced = 0
                if building.type == "Farm" or building.type == "Garden":
                    # Garden acts like a Farm (produces food)
                    # Food production is NOT affected by the starvation efficiency penalty (to allow recovery)
                    # Old: (100.0 / 60.0) * level
                    # New: (100.0 / 60.0) * level / 3 * assigned
                    base_food = (100.0 / 60.0) * building.level / 3.0
                    food_rate = base_food * assigned_count * happiness_bonus
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
                        # Chance scales with workers too? Yes.
                        # Old: 1 check per tick if 3 workers.
                        # New: assigned_count checks per tick? Or chance * (assigned/3)?
                        # Let's do chance * (assigned/3)
                        scale = assigned_count / 3.0
                        
                        resources = ["steel", "copper", "gold", "emerald", "diamond"]
                        chances = [0.75, 0.50, 0.25, 0.10, 0.001]
                        
                        did_produce = False
                        for res, chance in zip(resources, chances):
                            if random.random() < (chance * scale):
                                building.buffers[res] += 1
                                building.record_production(1, self.day_counter, res)
                                did_produce = True
                            else:
                                building.record_production(0, self.day_counter, res)
                        
                        if did_produce and hasattr(self.game, 'particle_manager'):
                            self.game.particle_manager.spawn_particle(building.x + 0.5, building.y, (100, 100, 100))
                            
                        produced = 1 # Indicator for record_production (global history)
                elif building.type == "Laboratory":
                    # Produce Science Points
                    # Base: 0.1 per tick? 
                    # Let's say 1 point per day per worker approx?
                    # 1200 ticks = 1 day.
                    # 1/1200 rate = very slow.
                    # Let's do 0.05 per worker per tick.
                    science_rate = 0.05 * assigned_count * happiness_bonus
                    self.game.resource_manager.science_points += science_rate
                    produced = science_rate
                    
                    if assigned_count > 0 and hasattr(self.game, 'particle_manager'):
                         if random.random() < 0.05:
                              # Blue/Purple bubbles
                             self.game.particle_manager.spawn_particle(building.x + 0.5, building.y, (100, 100, 255))
                else:
                    building.production_buffer += production_rate
                    produced = production_rate
                    
                    # Smoke for Stone Refinery if working
                    if building.type == "Stone Refinery" and assigned_count > 0 and hasattr(self.game, 'particle_manager'):
                        # Spawn less frequently for refinery (e.g., 10% chance per tick)
                        if random.random() < 0.1:
                            self.game.particle_manager.spawn_particle(building.x + 0.5, building.y, (150, 150, 150))
            
                building.record_production(produced, self.day_counter)
            else:
                 building.record_production(0, self.day_counter)

    def run_spawning(self):
        # Houses produce villagers 10/min -> 1 every 6 seconds.
        # Max 20 per house (Lvl 1).
        
        for pos, building in self.game.world.buildings.items():
            if building.type == "House":
                if building.villagers < 20 * building.level:
                     # 10 per minute = 1 per 6 seconds.
                     if random.random() < (1.0/6.0):
                         building.villagers += 1
                         # Spawn Unemployed
                         self.game.entity_manager.spawn_villager(building.x, building.y, "Unemployed")
                         # Logic will be handled by balance_jobs next tick

    def is_day(self):
        return self.current_time < (self.total_cycle_time / 2)
