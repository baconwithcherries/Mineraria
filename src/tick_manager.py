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
        if self.game.world is None:
            return
            
        now = pygame.time.get_ticks()
        current_interval = self.tick_interval / self.time_scale
        
        if now - self.last_tick >= current_interval:
            self.last_tick = now
            self.on_tick()

    def on_tick(self):
        # 1. Update Time
        self.current_time += 1
        if self.current_time >= self.total_cycle_time:
            self.current_time = 0
            self.day_counter += 1
            
            # Trader Spawn Chance (20% each morning)
            if random.random() < 0.2:
                if not self.game.entity_manager.trader.active:
                    self.game.entity_manager.trader.spawn()
        
        # 2. Happiness Calculation
        self.update_happiness()
        
        # 2.5 Job Balancing
        self.balance_jobs()
        
        # 4. Production Logic
        self.run_production()
        
        # 5. Villager Spawning
        self.run_spawning()

    def balance_jobs(self):
        job_types = ["Logging Workshop", "Stone Refinery", "Mine", "Farm", "Garden", "Oxygenator", "Laboratory", "Warehouse"]
        
        for job in job_types:
            # Get buildings of this type
            buildings = [b for b in self.game.world.buildings.values() if b.type == job]
            if not buildings: continue
            
            # Calculate total capacity and current workers
            # Total capacity is 3 * level, but robots take up slots first
            total_max_capacity = sum(3 * b.level for b in buildings)
            total_robots = sum(b.robots_assigned for b in buildings)
            total_villager_capacity = max(0, total_max_capacity - total_robots)
            
            all_workers = []
            for b in buildings:
                all_workers.extend(b.assigned_workers)
            
            # Determine target
            target_setting = self.game.resource_manager.job_targets.get(job, -1)
            if target_setting == -1:
                desired_total = total_villager_capacity
            else:
                desired_total = min(target_setting, total_villager_capacity)
            
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
                    # Space = (3*level) - assigned_workers - robots_assigned
                    assigned = False
                    for b in buildings:
                        cap = 3 * b.level
                        if (len(b.assigned_workers) + b.robots_assigned) < cap:
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
        
        # Pre-calculate Warehouse bonus map
        # Warehouse gives 10% bonus to buildings within 10 blocks
        warehouses = [b for b in self.game.world.buildings.values() if b.type == "Warehouse"]
        
        for pos, building in self.game.world.buildings.items():
            if building.type == "House":
                # Houses record occupancy, not cumulative production
                building.record_production(building.villagers, self.day_counter, overwrite=True)
                continue 

            # Calculate Warehouse Bonus
            warehouse_bonus = 1.0
            for w in warehouses:
                dist = math.sqrt((building.x - w.x)**2 + (building.y - w.y)**2)
                if dist <= 10:
                    warehouse_bonus += 0.1 # 10% per warehouse? or just flat 10%? 
                    # Spec says "nearby buildings produce 10% more"
                    # Let's say it stacks but cap it or just allow it. 
                    # Usually multiple warehouses should help.
            
            # Production scales with workers
            assigned_count = len(building.assigned_workers) + building.robots_assigned
            if assigned_count > 0:
                # Happiness bonus: 1% happiness = 2% production speedup
                happiness_bonus = 1.0 + (self.game.resource_manager.happiness * 0.02)
                
                total_multiplier = happiness_bonus * warehouse_bonus

                produced = 0
                if building.type == "Farm" or building.type == "Garden":
                    # Calibrate for 500 food per day at Lvl 1 with 3 workers
                    # Day = 1200 seconds. 500 / 1200 = 0.416 per second total.
                    # base_food = (500 / 1200) / 3 per worker
                    base_food = (500.0 / self.total_cycle_time) / 3.0
                    food_rate = base_food * building.level * assigned_count * total_multiplier
                    self.game.resource_manager.inventory["food"] += food_rate
                    produced = food_rate
                elif building.type == "Laboratory":
                    # Produce Science Points
                    science_rate = 0.05 * assigned_count * total_multiplier
                    self.game.resource_manager.science_points += science_rate
                    produced = science_rate
                    if hasattr(self.game, 'particle_manager') and random.random() < 0.05:
                        self.game.particle_manager.spawn_particle(building.x + 0.5, building.y, (100, 100, 255))
                elif building.type == "Oxygenator":
                    # Produce Oxygen Bottles
                    base_per_worker = (0.1 * building.level) / 3.0
                    production_rate = base_per_worker * assigned_count * self.game.resource_manager.food_efficiency * total_multiplier
                    building.production_buffer += production_rate
                    produced = production_rate
                elif building.type == "Warehouse":
                    produced = 0 # Doesn't produce itself
                else:
                    # Generic production (Wood, Stone, Iron)
                    base_per_worker = (0.1 * building.level) / 3.0
                    production_rate = base_per_worker * assigned_count * self.game.resource_manager.food_efficiency * total_multiplier
                    building.production_buffer += production_rate
                    produced = production_rate
                    
                    # Smoke for Stone Refinery if working
                    if building.type == "Stone Refinery" and assigned_count > 0 and hasattr(self.game, 'particle_manager'):
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
