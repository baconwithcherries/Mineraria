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
        job_types = ["Logging Workshop", "Stone Refinery", "Mine", "Farm", "Garden", "Oxygenator", "Laboratory", "Warehouse", "Raw Material Factory", "Copper Mine", "Blast Furnace", "Power Plant", "Advanced Machine Factory"]
        
        for job in job_types:
            # Get buildings of this type
            buildings = [b for b in self.game.world.buildings.values() if b.type == job]
            if not buildings: continue
            
            # Calculate total capacity and current workers
            # Total capacity is 3 * level
            total_max_capacity = sum(3 * b.level for b in buildings)
            total_villager_capacity = total_max_capacity
            
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
                    # Space = (3*level) - assigned_workers
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
        # Each staffed warehouse gives 10% happiness
        warehouse_count = sum(1 for b in self.game.world.buildings.values() if b.type == "Warehouse" and len(b.assigned_workers) >= 3)
        self.game.resource_manager.happiness = (garden_count * 1.0) + (warehouse_count * 10.0)

    def run_production(self):
        # Pre-calculate Warehouse bonus map
        warehouses = [b for b in self.game.world.buildings.values() if b.type == "Warehouse"]
        
        for pos, building in self.game.world.buildings.items():
            if building.type == "House":
                building.record_production(building.villagers, self.day_counter, overwrite=True)
                continue 

            # Calculate Warehouse Bonus
            warehouse_bonus = 1.0
            for w in warehouses:
                if len(w.assigned_workers) >= 3:
                    dist = math.sqrt((building.x - w.x)**2 + (building.y - w.y)**2)
                    if dist <= 10:
                        warehouse_bonus += 0.1
            
            # Production scales with workers
            assigned_count = len(building.assigned_workers)
            if assigned_count > 0:
                happiness_bonus = 1.0 + (self.game.resource_manager.happiness * 0.02)
                total_multiplier = happiness_bonus * warehouse_bonus

                produced = 0
                if building.type == "Farm" or building.type == "Garden":
                    base_food = (500.0 / self.total_cycle_time) / 3.0
                    food_rate = base_food * building.level * assigned_count * total_multiplier
                    self.game.resource_manager.inventory["food"] += food_rate
                    produced = food_rate
                elif building.type == "Laboratory":
                    # Produce Science Points - Added directly to global pool
                    science_rate = 0.2 * assigned_count * total_multiplier
                    self.game.resource_manager.science_points += science_rate
                    produced = science_rate
                    if hasattr(self.game, 'particle_manager') and random.random() < 0.05:
                        self.game.particle_manager.spawn_particle(building.x + 0.5, building.y, (100, 100, 255))
                elif building.type == "Oxygenator":
                    base_per_worker = (0.1 * building.level) / 3.0
                    production_rate = base_per_worker * assigned_count * self.game.resource_manager.food_efficiency * total_multiplier
                    self.game.resource_manager.inventory["oxygen"] += production_rate
                    building.production_buffer = 0 
                    produced = production_rate
                elif building.type == "Warehouse":
                    produced = 0
                elif building.type == "Power Plant":
                    # Consumes 15 Wiring -> 1 Battery.
                    if building.is_on:
                        rate_sec = (30 * building.level) / 60.0
                        wiring_req_sec = rate_sec * 15.0
                        wiring_available = self.game.resource_manager.inventory.get("wiring", 0)
                        efficiency = (len(building.assigned_workers) / (3.0 * building.level)) * self.game.resource_manager.food_efficiency * total_multiplier
                        actual_rate = rate_sec * efficiency
                        actual_wiring_req = wiring_req_sec * efficiency
                        
                        if wiring_available >= actual_wiring_req and actual_wiring_req > 0:
                            self.game.resource_manager.remove_resource("wiring", actual_wiring_req)
                            produced_bats = actual_rate
                            self.game.resource_manager.inventory["batteries"] += produced_bats
                            building.production_buffer += produced_bats
                            produced = produced_bats
                        else:
                            produced = 0
                    else:
                        produced = 0
                elif building.type == "Advanced Machine Factory":
                    # Consumes 5 Copper -> 1 Wiring.
                    if building.is_on:
                        rate_sec = (20 * building.level) / 60.0
                        copper_req_sec = rate_sec * 5.0
                        copper_available = self.game.resource_manager.inventory.get("copper", 0)
                        efficiency = (len(building.assigned_workers) / (3.0 * building.level)) * self.game.resource_manager.food_efficiency * total_multiplier
                        actual_rate = rate_sec * efficiency
                        actual_copper_req = copper_req_sec * efficiency
                        
                        if copper_available >= actual_copper_req and actual_copper_req > 0:
                            self.game.resource_manager.remove_resource("copper", actual_copper_req)
                            self.game.resource_manager.inventory["wiring"] += actual_rate
                            building.production_buffer += actual_rate
                            produced = actual_rate
                        else:
                            produced = 0
                    else:
                        produced = 0
                elif building.type == "Blast Furnace":
                    battery_needed = (15.0 / 60.0)
                    has_power = self.game.resource_manager.inventory.get("batteries", 0) >= battery_needed
                    if building.is_on and has_power:
                        self.game.resource_manager.inventory["batteries"] -= battery_needed
                        max_rate_min = 20 * building.level
                        max_rate_sec = max_rate_min / 60.0
                        efficiency = (len(building.assigned_workers) / (3.0 * building.level)) * self.game.resource_manager.food_efficiency * total_multiplier
                        actual_rate = max_rate_sec * efficiency
                        wood = self.game.resource_manager.inventory.get("wood", 0)
                        iron = self.game.resource_manager.inventory.get("iron", 0)
                        consumed = min(wood, iron, actual_rate)
                        if consumed > 0:
                            self.game.resource_manager.remove_resource("wood", consumed)
                            self.game.resource_manager.remove_resource("iron", consumed)
                            self.game.resource_manager.inventory["steel"] += consumed
                            building.production_buffer += consumed
                            produced = consumed
                    else:
                        produced = 0
                elif building.type == "Raw Material Factory":
                    max_rate_min = min(100, 20 * building.level)
                    max_rate_sec = max_rate_min / 60.0
                    efficiency = (len(building.assigned_workers) / (3.0 * building.level)) * self.game.resource_manager.food_efficiency * total_multiplier
                    actual_rate = max_rate_sec * efficiency
                    stone = self.game.resource_manager.inventory.get("stone", 0)
                    iron = self.game.resource_manager.inventory.get("iron", 0)
                    consumed_parts = min(stone, iron, actual_rate)
                    if consumed_parts > 0:
                        self.game.resource_manager.remove_resource("stone", consumed_parts)
                        self.game.resource_manager.remove_resource("iron", consumed_parts)
                        self.game.resource_manager.inventory["material_parts"] += consumed_parts
                        building.production_buffer += consumed_parts
                        produced += consumed_parts
                    if "Electronics" in self.game.resource_manager.unlocked_techs:
                        copper = self.game.resource_manager.inventory.get("copper", 0)
                        iron = self.game.resource_manager.inventory.get("iron", 0)
                        consumed_wiring = min(copper, iron, actual_rate)
                        if consumed_wiring > 0:
                            self.game.resource_manager.remove_resource("copper", consumed_wiring)
                            self.game.resource_manager.remove_resource("iron", consumed_wiring)
                            self.game.resource_manager.inventory["wiring"] += consumed_wiring
                            building.production_buffer += consumed_wiring
                            produced += consumed_wiring
                elif building.type in ["Logging Workshop", "Stone Refinery", "Mine", "Copper Mine"]:
                    base_per_worker = (0.1 * building.level) / 3.0
                    production_rate = base_per_worker * len(building.assigned_workers) * self.game.resource_manager.food_efficiency * total_multiplier
                    res_map = {"Logging Workshop": "wood", "Stone Refinery": "stone", "Mine": "iron", "Copper Mine": "copper"}
                    rtype = res_map.get(building.type)
                    if rtype:
                        self.game.resource_manager.inventory[rtype] += production_rate
                    building.production_buffer = 0
                    produced = production_rate
                    if building.type == "Stone Refinery" and assigned_count > 0 and hasattr(self.game, 'particle_manager'):
                        if random.random() < 0.1:
                            self.game.particle_manager.spawn_particle(building.x + 0.5, building.y, (150, 150, 150))
                else:
                    produced = 0
                building.record_production(produced, self.day_counter)
            else:
                 building.record_production(0, self.day_counter)

    def run_spawning(self):
        for pos, building in self.game.world.buildings.items():
            if building.type == "House":
                if building.villagers < 20 * building.level:
                     if random.random() < (1.0/6.0):
                         building.villagers += 1
                         self.game.entity_manager.spawn_villager(building.x, building.y, "Unemployed")

    def is_day(self):
        return self.current_time < (self.total_cycle_time / 2)