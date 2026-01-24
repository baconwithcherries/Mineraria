import pygame
import math
from ..config import *
from ..world import Building
from ..assets import Assets

class Window:
    def __init__(self, x, y, width, height, title):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.font = pygame.font.SysFont("Arial", 16)
        self.close_btn_rect = pygame.Rect(x + width - 20, y, 20, 20)
        self.scroll_y = 0
        self.content_height = height # To be set by subclasses

    def draw(self, screen):
        # Background
        pygame.draw.rect(screen, (210, 180, 140), self.rect, border_radius=10) # Beige
        pygame.draw.rect(screen, (60, 40, 30), self.rect, 3, border_radius=10) # Dark Brown Border
        
        # Title
        title_surf = self.font.render(self.title, True, (60, 40, 30))
        screen.blit(title_surf, (self.rect.x + 15, self.rect.y + 10))
        
        # Close Button
        pygame.draw.rect(screen, (160, 60, 60), self.close_btn_rect, border_radius=5)
        x_surf = self.font.render("X", True, WHITE)
        screen.blit(x_surf, (self.close_btn_rect.x + 5, self.close_btn_rect.y))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (4, 5): # Scroll wheel
                return "HANDLED"
            if self.close_btn_rect.collidepoint(event.pos) and event.button == 1:
                return "CLOSE"
        
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_y += event.y * 20
                # Clamp scroll
                max_scroll = 0
                min_scroll = -(max(0, self.content_height - (self.rect.height - 40)))
                self.scroll_y = max(min_scroll, min(max_scroll, self.scroll_y))
                return "HANDLED"
        return None

class BuildingInspector(Window):
    def __init__(self, building, resource_manager, world, game):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 400, 450
        super().__init__(cx - w//2, cy - h//2, w, h, f"{building.type} (Lvl {building.level})")
        self.building = building
        self.rm = resource_manager
        self.world = world
        self.game = game
        
        self.collect_btn = pygame.Rect(self.rect.x + 100, self.rect.y + 360, 200, 30)
        self.upgrade_btn = pygame.Rect(self.rect.x + 350, self.rect.y + 5, 20, 20)
        self.delete_btn = pygame.Rect(self.rect.x + self.rect.width - 40, self.rect.y + self.rect.height - 40, 30, 30)

    def draw(self, screen):
        super().draw(screen)
        
        # Stats
        rtype = "Resources"
        show_collect = True
        if self.building.type == "Logging Workshop": rtype = "Wood"
        elif self.building.type == "Stone Refinery": rtype = "Stone"
        elif self.building.type == "Mine": rtype = "Iron"
        elif self.building.type == "Oxygenator": rtype = "Oxygen"
        elif self.building.type in ["Farm", "Garden"]: rtype = "Food"
        elif self.building.type == "Laboratory": 
            rtype = "Science"
            show_collect = False
        elif self.building.type == "Warehouse":
            rtype = "Storage"
            show_collect = False
        
        assigned = len(self.building.assigned_workers) 
        
        if self.building.type == "House":
            stats = f"Villagers: {self.building.villagers}"
        else:
            if self.building.type == "Laboratory":
                stats = f"Science Gen: {self.building.production_buffer:.2f}"
            else:
                stats = f"{rtype}: {int(self.building.production_buffer)}"
            # Worker count display
            max_workers = 3 * self.building.level
            w_txt = self.font.render(f"Workers: {assigned}/{max_workers}", True, BLACK)
            screen.blit(w_txt, (self.rect.x + 20, self.rect.y + 400))
            
            # Robot controls
            r_txt = self.font.render(f"Robots: {self.building.robots_assigned}", True, (0, 50, 150))
            screen.blit(r_txt, (self.rect.x + 200, self.rect.y + 400))
            
            self.robot_minus_btn = pygame.Rect(self.rect.x + 280, self.rect.y + 400, 25, 25)
            self.robot_plus_btn = pygame.Rect(self.rect.x + 315, self.rect.y + 400, 25, 25)
            
            pygame.draw.rect(screen, (100, 100, 100), self.robot_minus_btn, border_radius=5)
            pygame.draw.rect(screen, (100, 100, 100), self.robot_plus_btn, border_radius=5)
            screen.blit(self.font.render("-", True, WHITE), (self.robot_minus_btn.centerx - 4, self.robot_minus_btn.centery - 10))
            screen.blit(self.font.render("+", True, WHITE), (self.robot_plus_btn.centerx - 6, self.robot_plus_btn.centery - 10))
            
        text = self.font.render(stats, True, BLACK)
        screen.blit(text, (self.rect.x + 20, self.rect.y + 40))
        
        # Graph area
        graph_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 70, 360, 150)
        # Light background similar to reference
        pygame.draw.rect(screen, (235, 225, 205), graph_rect) # Lighter Beige
        pygame.draw.rect(screen, (60, 40, 30), graph_rect, 2) # Dark Brown Border
        
        history = self.building.production_history
        max_val = max(history) if max(history) > 0 else 10
        # Round up to next multiple of 5
        max_val = math.ceil(max_val / 5) * 5
        max_val = max(max_val, 5)

        # Draw grid lines & Y-axis labels
        steps = 5
        for i in range(steps + 1):
            val = (max_val / steps) * i
            y_pos = graph_rect.bottom - ((val / max_val) * graph_rect.height)
            
            # Grid line
            if i > 0:
                pygame.draw.line(screen, (200, 190, 170), (graph_rect.x, y_pos), (graph_rect.right, y_pos), 1)
            
            # Label
            label = self.font.render(str(int(val)), True, (60, 40, 30))
            screen.blit(label, (graph_rect.x + 5, y_pos - 10))

        # Draw bars
        # Fixed 7-day layout
        max_days = 7
        bar_width = graph_rect.width / max_days
        
        # Calculate where to start drawing (right-aligned)
        # history[-1] is Today -> Slot 6 (index max_days-1)
        # start_slot ensures the last item lands in the last slot
        start_slot = max_days - len(history)
        
        for i, val in enumerate(history):
            slot = start_slot + i
            if slot < 0: continue # Should not happen with len <= 7 logic
            
            h = (val / max_val) * graph_rect.height
            x = graph_rect.x + (slot * bar_width)
            y = graph_rect.y + graph_rect.height - h
            
            # Blue bars (Reference uses Green/Blue line, let's stick to Blue or change to Green)
            # Reference image graph has Green line. Let's use Green bars to match "Materials Produced".
            bar_rect = pygame.Rect(x, y, max(1, bar_width - 4), h) 
            pygame.draw.rect(screen, (80, 160, 80), bar_rect) # Greenish bars

            # Date Labels
            days_ago = len(history) - 1 - i
            if days_ago == 0:
                lbl_text = "Today"
            elif days_ago == 1:
                lbl_text = "Yesterday"
            else:
                lbl_text = f"{days_ago} days ago"
            
            lbl = self.font.render(lbl_text, True, (60, 40, 30))
            rotated_lbl = pygame.transform.rotate(lbl, 90)
            
            # Position centered under bar
            lbl_x = x + (bar_width / 2) - (rotated_lbl.get_width() / 2)
            lbl_y = graph_rect.bottom + 5
            
            # Only draw if it fits within the window bounds roughly
            if lbl_y + rotated_lbl.get_height() < self.rect.bottom - 5:
                    screen.blit(rotated_lbl, (lbl_x, lbl_y))
            elif days_ago == 0: # Always try to show Today
                    screen.blit(rotated_lbl, (lbl_x, lbl_y))
        
        # Collect Button
        if show_collect and self.building.type != "House":
            pygame.draw.rect(screen, (160, 110, 80), self.collect_btn, border_radius=5)
            pygame.draw.rect(screen, (60, 40, 30), self.collect_btn, 2, border_radius=5)
            c_text = self.font.render("Collect", True, WHITE)
            screen.blit(c_text, (self.collect_btn.centerx - c_text.get_width()//2, self.collect_btn.centery - c_text.get_height()//2))

        # Upgrade Icon
        assets = Assets.get()
        arrow = assets.get_sprite("icon_arrow_up")
        
        pygame.draw.rect(screen, (160, 110, 80), self.upgrade_btn, border_radius=5)
        pygame.draw.rect(screen, (60, 40, 30), self.upgrade_btn, 2, border_radius=5)
        if arrow:
            dest = (self.upgrade_btn.x + 2, self.upgrade_btn.y + 2)
            screen.blit(arrow, dest)
            
        # Delete Button (Trash Can)
        pygame.draw.rect(screen, (200, 60, 60), self.delete_btn, border_radius=5)
        pygame.draw.rect(screen, (60, 40, 30), self.delete_btn, 2, border_radius=5)
        trash_text = self.font.render("DEL", True, WHITE) # Placeholder for trash icon
        screen.blit(trash_text, (self.delete_btn.x + 2, self.delete_btn.y + 5))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.collect_btn.collidepoint(event.pos):
                if self.building.production_buffer >= 1:
                    rtype = ""
                    if self.building.type == "Logging Workshop": rtype = "wood"
                    elif self.building.type == "Stone Refinery": rtype = "stone"
                    elif self.building.type == "Mine": rtype = "iron"
                    elif self.building.type == "Oxygenator": rtype = "oxygen"
                    elif self.building.type in ["Farm", "Garden"]: rtype = "food"
                    
                    if rtype:
                        amount = int(self.building.production_buffer)
                        self.rm.add_resource(rtype, amount)
                        self.building.production_buffer -= amount
                return "HANDLED"
            
            if self.upgrade_btn.collidepoint(event.pos):
                if self.building.level < 100:
                    cost = self.building.get_upgrade_cost()
                    if self.rm.has_resources(cost):
                        self.rm.deduct_resources(cost)
                        self.building.level += 1
                        self.title = f"{self.building.type} (Lvl {self.building.level})"
                        # Update worker target if it was set to old max (3 * old_level)
                        # Actually, target_workers is manually set now or defaults on init.
                        # If we upgrade, capacity increases (3 * new_level).
                        # We should probably increase target_workers automatically if it was maxed?
                        # Or just leave it to the user. The user can adjust max in the assignment window.
                        pass
                return "HANDLED"
                
            if self.delete_btn.collidepoint(event.pos):
                # Delete Building and Refund
                cost = Building.get_cost(self.building.type)
                for res, amount in cost.items():
                    self.rm.add_resource(res, amount)
                self.world.buildings.pop((self.building.x, self.building.y))
                return "CLOSE"
            
            if hasattr(self, 'robot_minus_btn') and self.robot_minus_btn.collidepoint(event.pos):
                if self.building.robots_assigned > 0:
                    self.building.robots_assigned -= 1
                    self.rm.inventory["robots"] = self.rm.inventory.get("robots", 0) + 1
                return "HANDLED"
            
            if hasattr(self, 'robot_plus_btn') and self.robot_plus_btn.collidepoint(event.pos):
                if self.rm.inventory.get("robots", 0) > 0:
                    current_total = len(self.building.assigned_workers) + self.building.robots_assigned
                    if current_total < 3 * self.building.level:
                        self.building.robots_assigned += 1
                        self.rm.inventory["robots"] -= 1
                return "HANDLED"
            
            if hasattr(self, 'minus_btn') and self.minus_btn.collidepoint(event.pos):
                pass # Removed
                return "HANDLED"
            
            if hasattr(self, 'plus_btn') and self.plus_btn.collidepoint(event.pos):
                pass # Removed
                return "HANDLED"
        return None

class ResearchWindow(Window):
    def __init__(self, resource_manager):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 500, 400
        super().__init__(cx - w//2, cy - h//2, w, h, "Research Lab")
        self.rm = resource_manager
        
        # Tech Tree: Name, Cost, Description, ID
        self.techs = [
            {"name": "Advanced Architecture", "cost": 100, "desc": "Unlocks Warehouse", "id": "Advanced Architecture"},
            {"name": "Botany", "cost": 75, "desc": "Unlocks Garden", "id": "Botany"},
            {"name": "Life Support", "cost": 150, "desc": "Unlocks Oxygenator", "id": "Life Support"},
            {"name": "Aerospace Engineering", "cost": 500, "desc": "Unlocks Rocket Ship", "id": "Aerospace Engineering"}
        ]
        
        self.unlock_buttons = []

    def draw(self, screen):
        super().draw(screen)
        
        # Header: Science Points
        points = int(self.rm.science_points)
        s_txt = self.font.render(f"Science Points: {points}", True, (50, 50, 150))
        screen.blit(s_txt, (self.rect.x + 20, self.rect.y + 40))
        
        self.unlock_buttons = []
        y_pos = self.rect.y + 70
        
        for tech in self.techs:
            # Box
            box_rect = pygame.Rect(self.rect.x + 20, y_pos, self.rect.width - 40, 60)
            is_unlocked = tech["id"] in self.rm.unlocked_techs
            
            color = (200, 255, 200) if is_unlocked else (220, 220, 220)
            pygame.draw.rect(screen, color, box_rect)
            pygame.draw.rect(screen, BLACK, box_rect, 1)
            
            # Text
            name_surf = self.font.render(tech["name"], True, BLACK)
            desc_surf = self.font.render(tech["desc"], True, (50, 50, 50))
            cost_surf = self.font.render(f"Cost: {tech['cost']}", True, (100, 50, 50))
            
            screen.blit(name_surf, (box_rect.x + 10, box_rect.y + 5))
            screen.blit(desc_surf, (box_rect.x + 10, box_rect.y + 25))
            
            if not is_unlocked:
                screen.blit(cost_surf, (box_rect.x + 10, box_rect.y + 40))
                
                # Unlock Button
                btn_rect = pygame.Rect(box_rect.right - 80, box_rect.y + 15, 70, 30)
                can_afford = self.rm.science_points >= tech["cost"]
                
                if can_afford:
                    btn_color = (100, 160, 100) # Greenish
                else:
                    btn_color = (150, 150, 150) # Grey
                
                pygame.draw.rect(screen, btn_color, btn_rect, border_radius=5)
                pygame.draw.rect(screen, (60, 40, 30), btn_rect, 2, border_radius=5)
                
                btn_txt = self.font.render("Unlock", True, WHITE)
                screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - btn_txt.get_height()//2))
                
                self.unlock_buttons.append((btn_rect, tech))
            else:
                lbl = self.font.render("Unlocked", True, (0, 100, 0))
                screen.blit(lbl, (box_rect.right - 80, box_rect.y + 20))
                
            y_pos += 70

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn, tech in self.unlock_buttons:
                if btn.collidepoint(event.pos):
                    if self.rm.science_points >= tech["cost"]:
                        self.rm.science_points -= tech["cost"]
                        self.rm.unlocked_techs.append(tech["id"])
                    return "HANDLED"
        return None

class WorkerAssignmentWindow(Window):
    def __init__(self, resource_manager, world):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 600, 450
        super().__init__(cx - w//2, cy - h//2, w, h, "Assign Workers & Robots")
        self.rm = resource_manager
        self.world = world
        
        # Define jobs order
        self.jobs = ["House", "Logging Workshop", "Stone Refinery", "Mine", "Farm", "Garden", "Oxygenator", "Laboratory", "Warehouse"]
        self.controls = [] # List of tuples (minus_rect, plus_rect, job_name)
        self.robot_controls = [] # List of tuples (minus_rect, plus_rect, job_name)
        self.collect_buttons = [] # List of tuples (rect, job_name)
        self.upgrade_buttons = [] # List of tuples (rect, job_name)

    def draw(self, screen):
        super().draw(screen)
        
        # Reset lists for hit detection
        self.controls = []
        self.robot_controls = []
        self.collect_buttons = []
        self.upgrade_buttons = []
        
        # Create a surface for scrollable content
        content_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 70, self.rect.width - 4, self.rect.height - 72)
        content_surf = pygame.Surface((content_rect.width, content_rect.height), pygame.SRCALPHA)
        
        # Available Robots
        avail_robots = self.rm.inventory.get("robots", 0)
        r_txt = self.font.render(f"Available Robots: {avail_robots}", True, (0, 100, 200))
        screen.blit(r_txt, (self.rect.x + 20, self.rect.y + 40))

        y_pos = self.scroll_y
        row_height = 45
        
        for job in self.jobs:
            # Gather stats
            buildings = [b for b in self.world.buildings.values() if b.type == job]
            count = len(buildings)
            if count == 0: continue
            
            # Special case for House display
            if job == "House":
                 total_capacity = sum(20 * b.level for b in buildings)
                 assigned_count = sum(b.villagers for b in buildings)
                 robots_count = 0
                 target = -2 # Special flag to hide controls
            else:
                 total_capacity = sum(3 * b.level for b in buildings)
                 assigned_count = sum(len(b.assigned_workers) for b in buildings)
                 robots_count = sum(b.robots_assigned for b in buildings)
                 target = self.rm.job_targets.get(job, -1)
            
            # Draw Icon
            assets = Assets.get()
            sprite = assets.get_sprite(job)
            if sprite:
                scaled = pygame.transform.scale(sprite, (32, 32))
                content_surf.blit(scaled, (18, y_pos))
            
            # Text
            if job == "House":
                 txt = f"x{count}: {assigned_count}/{total_capacity} v"
            else:
                 txt = f"x{count}: {assigned_count}/{total_capacity} v, {robots_count} r"
            
            t_surf = self.font.render(txt, True, BLACK)
            content_surf.blit(t_surf, (58, y_pos + 8))
            
            # Controls Layout
            # [U] [C] | Workers [-] [Val] [+] | Robots [-] [+]
            
            # Upgrade Button
            upgrade_rect = pygame.Rect(218, y_pos + 5, 30, 25)
            pygame.draw.rect(content_surf, (100, 100, 255), upgrade_rect)
            u_txt = self.font.render("U", True, WHITE)
            content_surf.blit(u_txt, (upgrade_rect.centerx - u_txt.get_width()//2, upgrade_rect.centery - u_txt.get_height()//2))
            
            # Real screen rect for collision
            screen_upgrade = upgrade_rect.copy()
            screen_upgrade.x += content_rect.x
            screen_upgrade.y += content_rect.y
            self.upgrade_buttons.append((screen_upgrade, job))

            if job != "House":
                # Collect Button
                collect_rect = pygame.Rect(253, y_pos + 5, 30, 25)
                pygame.draw.rect(content_surf, (100, 160, 100), collect_rect, border_radius=5)
                c_txt = self.font.render("C", True, WHITE)
                content_surf.blit(c_txt, (collect_rect.centerx - c_txt.get_width()//2, collect_rect.centery - c_txt.get_height()//2))
                
                screen_collect = collect_rect.copy()
                screen_collect.x += content_rect.x
                screen_collect.y += content_rect.y
                self.collect_buttons.append((screen_collect, job))
                
                # Worker Target Controls
                w_minus = pygame.Rect(298, y_pos + 5, 25, 25)
                w_plus = pygame.Rect(378, y_pos + 5, 25, 25)
                
                pygame.draw.rect(content_surf, (160, 110, 80), w_minus, border_radius=5)
                pygame.draw.rect(content_surf, (160, 110, 80), w_plus, border_radius=5)
                content_surf.blit(self.font.render("-", True, WHITE), (w_minus.centerx - 4, w_minus.centery - 10))
                content_surf.blit(self.font.render("+", True, WHITE), (w_plus.centerx - 6, w_plus.centery - 10))
                
                val_str = "Max" if target == -1 else str(target)
                v_surf = self.font.render(val_str, True, BLACK)
                content_surf.blit(v_surf, (333, y_pos + 8))
                
                screen_w_minus = w_minus.copy()
                screen_w_minus.x += content_rect.x
                screen_w_minus.y += content_rect.y
                screen_w_plus = w_plus.copy()
                screen_w_plus.x += content_rect.x
                screen_w_plus.y += content_rect.y
                self.controls.append((screen_w_minus, screen_w_plus, job))

                # Robot Controls
                r_minus = pygame.Rect(428, y_pos + 5, 25, 25)
                r_plus = pygame.Rect(508, y_pos + 5, 25, 25)
                
                pygame.draw.rect(content_surf, (100, 100, 100), r_minus, border_radius=5)
                pygame.draw.rect(content_surf, (100, 100, 100), r_plus, border_radius=5)
                content_surf.blit(self.font.render("-", True, WHITE), (r_minus.centerx - 4, r_minus.centery - 10))
                content_surf.blit(self.font.render("+", True, WHITE), (r_plus.centerx - 6, r_plus.centery - 10))
                
                r_val_surf = self.font.render(f"R:{robots_count}", True, (0, 50, 150))
                content_surf.blit(r_val_surf, (458, y_pos + 8))
                
                screen_r_minus = r_minus.copy()
                screen_r_minus.x += content_rect.x
                screen_r_minus.y += content_rect.y
                screen_r_plus = r_plus.copy()
                screen_r_plus.x += content_rect.x
                screen_r_plus.y += content_rect.y
                self.robot_controls.append((screen_r_minus, screen_r_plus, job))

            y_pos += row_height
        
        self.content_height = y_pos - self.scroll_y + 20
        screen.blit(content_surf, content_rect.topleft)
    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn, job in self.upgrade_buttons:
                if btn.collidepoint(event.pos):
                    # Upgrade all buildings of this type
                    buildings = [b for b in self.world.buildings.values() if b.type == job]
                    # Sort by level (cheapest first? or random?)
                    # Let's do lowest level first to maximize upgrades
                    buildings.sort(key=lambda b: b.level)
                    
                    for b in buildings:
                        if b.level < 100:
                            cost = b.get_upgrade_cost()
                            if self.rm.has_resources(cost):
                                self.rm.deduct_resources(cost)
                                b.level += 1
                    return "HANDLED"

            for btn, job in self.collect_buttons:
                if btn.collidepoint(event.pos):
                    # Collect from all buildings of this type
                    buildings = [b for b in self.world.buildings.values() if b.type == job]
                    for b in buildings:
                        if b.production_buffer >= 1:
                            rtype = ""
                            if b.type == "Logging Workshop": rtype = "wood"
                            elif b.type == "Stone Refinery": rtype = "stone"
                            elif b.type == "Mine": rtype = "iron"
                            elif b.type == "Oxygenator": rtype = "oxygen"
                            elif b.type in ["Farm", "Garden"]: rtype = "food"
                            
                            if rtype:
                                amount = int(b.production_buffer)
                                self.rm.add_resource(rtype, amount)
                                b.production_buffer -= amount
                    return "HANDLED"

            for minus, plus, job in self.controls:
                current_target = self.rm.job_targets.get(job, -1)
                
                # Calculate max capacity for clamping logic
                buildings = [b for b in self.world.buildings.values() if b.type == job]
                total_capacity = sum(3 * b.level for b in buildings)
                if total_capacity == 0: continue

                if minus.collidepoint(event.pos):
                    if current_target == -1:
                        # Max -> Max - 1 (or total capacity - 1)
                        self.rm.job_targets[job] = total_capacity - 1
                    elif current_target > 0:
                        self.rm.job_targets[job] -= 1
                    return "HANDLED"
                
                if plus.collidepoint(event.pos):
                    if current_target != -1:
                        if current_target + 1 >= total_capacity:
                            self.rm.job_targets[job] = -1 # Set to Max
                        else:
                            self.rm.job_targets[job] += 1
                    return "HANDLED"
            
            for minus, plus, job in self.robot_controls:
                buildings = [b for b in self.world.buildings.values() if b.type == job]
                total_capacity = sum(3 * b.level for b in buildings)
                robots_count = sum(b.robots_assigned for b in buildings)
                
                if minus.collidepoint(event.pos):
                    if robots_count > 0:
                        # Remove robot from first available building
                        for b in buildings:
                            if b.robots_assigned > 0:
                                b.robots_assigned -= 1
                                self.rm.inventory["robots"] = self.rm.inventory.get("robots", 0) + 1
                                break
                    return "HANDLED"
                
                if plus.collidepoint(event.pos):
                    avail_robots = self.rm.inventory.get("robots", 0)
                    if avail_robots > 0:
                        # Add robot to first building with space
                        for b in buildings:
                            current_workers = len(b.assigned_workers) + b.robots_assigned
                            if current_workers < (3 * b.level):
                                b.robots_assigned += 1
                                self.rm.inventory["robots"] -= 1
                                break
                    return "HANDLED"
        return None

class InventoryWindow(Window):
    def __init__(self, resource_manager):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 300, 200
        super().__init__(cx - w//2, cy - h//2, w, h, "Inventory")
        self.rm = resource_manager
        self.content_height = len(self.rm.inventory) * 30 + 50

    def draw(self, screen):
        super().draw(screen)
        
        # Create a surface for scrollable content
        content_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 30, self.rect.width - 4, self.rect.height - 32)
        content_surf = pygame.Surface((content_rect.width, content_rect.height), pygame.SRCALPHA)
        
        y_offset = self.scroll_y + 10
        for res, amount in self.rm.inventory.items():
            txt = f"{res.capitalize()}: {int(amount)}"
            surf = self.font.render(txt, True, BLACK)
            content_surf.blit(surf, (20, y_offset))
            y_offset += 30
            
        screen.blit(content_surf, content_rect.topleft)

    def handle_input(self, event):
        return super().handle_input(event)

class TutorialPrompt(Window):
    def __init__(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        super().__init__(cx - 150, cy - 75, 300, 150, "Tutorial")
        self.yes_btn = pygame.Rect(self.rect.x + 20, self.rect.y + 70, 120, 40)
        self.no_btn = pygame.Rect(self.rect.x + 160, self.rect.y + 70, 120, 40)

    def draw(self, screen):
        super().draw(screen)
        t = self.font.render("Would you like a tutorial?", True, BLACK)
        screen.blit(t, (self.rect.centerx - t.get_width()//2, self.rect.y + 40))
        
        pygame.draw.rect(screen, (50, 150, 50), self.yes_btn)
        pygame.draw.rect(screen, (150, 50, 50), self.no_btn)
        screen.blit(self.font.render("YES", True, WHITE), (self.yes_btn.centerx - 15, self.yes_btn.centery - 10))
        screen.blit(self.font.render("NO", True, WHITE), (self.no_btn.centerx - 10, self.no_btn.centery - 10))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.yes_btn.collidepoint(event.pos): return "START_TUTORIAL"
            if self.no_btn.collidepoint(event.pos): return "CLOSE"
        return None

class TutorialWindow(Window):
    def __init__(self, hud):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 500, 250
        super().__init__(cx - w//2, cy - h//2, w, h, "Help Guide")
        self.hud = hud
        self.page = 0
        self.next_btn = pygame.Rect(self.rect.x + self.rect.width - 100, self.rect.y + self.rect.height - 40, 80, 30)
        
        self.pages = [
            "Hello this is your floating island that you are stuck on your main goal is to build a rocket ship to escape your floating island to do this you must build buildings to collect these resources iron, stone.",
            "How do you make buildings you might ask, well I will show you. First in the inventory (there will be a little arrow pointing to the inventory icon) by left clicking on it and you will see: 10 wood, 10 stone, and 10 iron.",
            "These are the building blocks for everything in the game you can use these resources in the Buildings Tab. In the buildings tab (there would be an arrow point to the building tab) you can click on it and build your first building a house.",
            "Click on the box just beside it and you will be able to place it down anywhere on the surface with left click once you have done that then you can build more buildings like a Logging workshop, Stone Refinery, and a Mine.",
            "(Note: Once you build a house, you cannot build another until you have built a Logging workshop, Stone Refinery, and Mine.) Once those are built, your villagers will start moving in and working in the buildings.",
            "You will need 3 people to work inside of your building for it to start producing. You will also need to build a farm to keep your villagers fed. You need to do it quickly because for every minute that they aren’t fed their production speed will slow down.",
            "You can see your production and how many people are inside your building. This is the place where you can collect your resources from your buildings and keep building and collecting until you have enough to build a rocket ship.",
            "Note: For every villager that you have you will have to collect 10 of each resource to send them on the rocket ship. Have fun and Blast Off."
        ]

    def draw(self, screen):
        super().draw(screen)
        # Wrap and draw text
        words = self.pages[self.page].split(' ')
        lines = []
        curr_line = ""
        for word in words:
            if self.font.size(curr_line + word)[0] < self.rect.width - 40:
                curr_line += word + " "
            else:
                lines.append(curr_line)
                curr_line = word + " "
        lines.append(curr_line)
        
        for i, line in enumerate(lines):
            ls = self.font.render(line, True, BLACK)
            screen.blit(ls, (self.rect.x + 20, self.rect.y + 40 + i*20))

        pygame.draw.rect(screen, (100, 100, 100), self.next_btn)
        nt = "FINISH" if self.page == len(self.pages) - 1 else "NEXT"
        screen.blit(self.font.render(nt, True, WHITE), (self.next_btn.x + 10, self.next_btn.y + 5))

        # Draw Arrows
        assets = Assets.get()
        arrow = assets.get_sprite("icon_arrow_up")
        if arrow:
            if self.page == 1: # Point to Inventory Panel
                pos = (self.hud.inventory_panel_rect.x - 40, self.hud.inventory_panel_rect.y + 10)
                # Rotate arrow to point right
                rotated = pygame.transform.rotate(arrow, -90)
                screen.blit(rotated, pos)
            elif self.page == 2: # Point to Building Tab
                pos = (self.hud.build_icon_rect.x + 40, self.hud.build_icon_rect.y + 8)
                rotated = pygame.transform.rotate(arrow, 90)
                screen.blit(rotated, pos)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.next_btn.collidepoint(event.pos):
                if self.page < len(self.pages) - 1:
                    self.page += 1
                    return "HANDLED"
                else:
                    return "CLOSE"
        return None

class CodeWindow(Window):
    def __init__(self, resource_manager):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        super().__init__(cx - 150, cy - 75, 300, 150, "Enter Code")
        self.rm = resource_manager
        self.input_text = ""
        self.message = ""

    def draw(self, screen):
        super().draw(screen)
        # Input Box
        input_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 50, 260, 30)
        pygame.draw.rect(screen, WHITE, input_rect)
        pygame.draw.rect(screen, BLACK, input_rect, 1)
        
        txt_surf = self.font.render(self.input_text, True, BLACK)
        screen.blit(txt_surf, (input_rect.x + 5, input_rect.y + 5))
        
        if self.message:
            m_surf = self.font.render(self.message, True, (200, 50, 50))
            screen.blit(m_surf, (self.rect.x + 20, self.rect.y + 90))
        else:
            hint = self.font.render("Press Enter to submit", True, (100, 100, 100))
            screen.blit(hint, (self.rect.x + 20, self.rect.y + 90))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_text in self.rm.used_codes:
                    self.message = "Code already used!"
                elif self.input_text == "baconwithcherries":
                    for res in ["wood", "stone", "iron"]:
                        self.rm.add_resource(res, 1500)
                    self.rm.science_points += 2000
                    self.rm.used_codes.append("baconwithcherries")
                    return "CLOSE"
                elif self.input_text == "banana":
                    self.rm.add_resource("food", 5000)
                    self.rm.inventory["robots"] += 10
                    self.rm.used_codes.append("banana")
                    return "CLOSE"
                elif self.input_text == "goldmine":
                    for res in ["wood", "stone", "iron"]:
                        self.rm.add_resource(res, 5000)
                    self.rm.used_codes.append("goldmine")
                    return "CLOSE"
                else:
                    self.message = "Invalid Code!"
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                if len(self.input_text) < 20:
                    self.input_text += event.unicode
        return None

class EndGameWindow(Window):
    def __init__(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        super().__init__(cx - 150, cy - 75, 300, 150, "Victory!")
        self.exit_btn = pygame.Rect(self.rect.x + 50, self.rect.y + 80, 200, 40)

    def draw(self, screen):
        super().draw(screen)
        t = self.font.render("Congrats Game Over", True, BLACK)
        screen.blit(t, (self.rect.centerx - t.get_width()//2, self.rect.y + 40))
        
        pygame.draw.rect(screen, (50, 150, 50), self.exit_btn)
        et = self.font.render("Exit to Title Screen", True, WHITE)
        screen.blit(et, (self.exit_btn.centerx - et.get_width()//2, self.exit_btn.centery - et.get_height()//2))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.exit_btn.collidepoint(event.pos):
                return "GAME_OVER_EXIT"
        return None

class RocketWindow(Window):
    def __init__(self, building, resource_manager, entity_manager, game):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        super().__init__(cx - 150, cy - 125, 300, 300, "Rocket Controls")
        self.building = building
        self.rm = resource_manager
        self.em = entity_manager
        self.game = game
        
        self.board_one_btn = pygame.Rect(self.rect.x + 50, self.rect.y + 110, 200, 35)
        self.board_all_btn = pygame.Rect(self.rect.x + 50, self.rect.y + 155, 200, 35)
        self.launch_btn = pygame.Rect(self.rect.x + 50, self.rect.y + 220, 200, 45)

    def draw(self, screen):
        super().draw(screen)
        total_pop = self.em.get_count()
        remaining = total_pop - self.building.boarded_population
        
        t1 = self.font.render(f"City Population: {total_pop}", True, BLACK)
        t2 = self.font.render(f"Boarded: {self.building.boarded_population}", True, BLACK)
        screen.blit(t1, (self.rect.x + 20, self.rect.y + 40))
        screen.blit(t2, (self.rect.x + 20, self.rect.y + 70))
        
        if remaining > 0:
            # Board One
            pygame.draw.rect(screen, (100, 100, 255), self.board_one_btn)
            bt1 = self.font.render(f"Board 1 (10 all + ox)", True, WHITE)
            screen.blit(bt1, (self.board_one_btn.centerx - bt1.get_width()//2, self.board_one_btn.centery - bt1.get_height()//2))
            
            # Board All
            pygame.draw.rect(screen, (80, 80, 200), self.board_all_btn)
            bt2 = self.font.render(f"Board All ({remaining * 10} all + ox)", True, WHITE)
            screen.blit(bt2, (self.board_all_btn.centerx - bt2.get_width()//2, self.board_all_btn.centery - bt2.get_height()//2))
        
        if self.building.boarded_population >= total_pop and total_pop > 0:
            pygame.draw.rect(screen, (255, 50, 50), self.launch_btn)
            lt = self.font.render("LAUNCH ROCKET", True, WHITE)
            screen.blit(lt, (self.launch_btn.centerx - lt.get_width()//2, self.launch_btn.centery - lt.get_height()//2))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            total_pop = self.em.get_count()
            remaining = total_pop - self.building.boarded_population
            
            # Board One
            if self.board_one_btn.collidepoint(event.pos) and remaining > 0:
                cost = {"wood": 10, "stone": 10, "iron": 10, "oxygen": 10}
                if self.rm.has_resources(cost):
                    self.rm.deduct_resources(cost)
                    self.building.boarded_population += 1
            
            # Board All
            if self.board_all_btn.collidepoint(event.pos) and remaining > 0:
                cost = {"wood": remaining * 10, "stone": remaining * 10, "iron": remaining * 10, "oxygen": remaining * 10}
                if self.rm.has_resources(cost):
                    self.rm.deduct_resources(cost)
                    self.building.boarded_population = total_pop
            
            # Launch
            if self.launch_btn.collidepoint(event.pos):
                if self.building.boarded_population >= total_pop and total_pop > 0:
                    self.building.is_launching = True
                    return "CLOSE"
        return None

class TraderWindow(Window):
    def __init__(self, resource_manager):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 400, 300
        super().__init__(cx - w//2, cy - h//2, w, h, "Traveling Merchant")
        self.rm = resource_manager
        
        # Trades: Cost -> Reward
        self.trades = [
            {"cost": {"wood": 100}, "reward": {"emerald": 1}},
            {"cost": {"stone": 100}, "reward": {"diamond": 1}},
            {"cost": {"iron": 50}, "reward": {"gold": 5}},
            {"cost": {"food": 50}, "reward": {"copper": 10}}
        ]
        
        self.trade_buttons = []

    def draw(self, screen):
        super().draw(screen)
        
        y_pos = self.rect.y + 50
        for trade in self.trades:
            # Format text
            cost_txt = ", ".join([f"{v} {k.capitalize()}" for k, v in trade["cost"].items()])
            reward_txt = ", ".join([f"{v} {k.capitalize()}" for k, v in trade["reward"].items()])
            
            label = self.font.render(f"{cost_txt}  ->  {reward_txt}", True, (60, 40, 30))
            screen.blit(label, (self.rect.x + 20, y_pos + 5))
            
            # Button
            btn_rect = pygame.Rect(self.rect.right - 100, y_pos, 80, 30)
            
            can_afford = self.rm.has_resources(trade["cost"])
            color = (100, 160, 100) if can_afford else (150, 150, 150)
            
            pygame.draw.rect(screen, color, btn_rect, border_radius=5)
            pygame.draw.rect(screen, (60, 40, 30), btn_rect, 2, border_radius=5)
            
            bt = self.font.render("Trade", True, WHITE)
            screen.blit(bt, (btn_rect.centerx - bt.get_width()//2, btn_rect.centery - bt.get_height()//2))
            
            self.trade_buttons.append((btn_rect, trade))
            y_pos += 50

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn, trade in self.trade_buttons:
                if btn.collidepoint(event.pos):
                    if self.rm.deduct_resources(trade["cost"]):
                        for res, amount in trade["reward"].items():
                            self.rm.add_resource(res, amount)
                    return "HANDLED"
        return None

class LaboratoryInspector(Window):
    def __init__(self, building, resource_manager, world, game):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 400, 300
        super().__init__(cx - w//2, cy - h//2, w, h, "Laboratory")
        self.building = building
        self.rm = resource_manager
        self.world = world
        self.game = game
        self.research_btn = pygame.Rect(self.rect.x + 100, self.rect.y + 200, 200, 40)

    def draw(self, screen):
        super().draw(screen)
        
        # Stats
        science_gen = self.building.production_buffer
        txt = self.font.render(f"Science Generated: {science_gen:.2f}", True, BLACK)
        screen.blit(txt, (self.rect.x + 20, self.rect.y + 50))
        
        # Open Research Button
        pygame.draw.rect(screen, (100, 100, 200), self.research_btn, border_radius=5)
        pygame.draw.rect(screen, (60, 40, 30), self.research_btn, 2, border_radius=5)
        bt = self.font.render("Open Research Tree", True, WHITE)
        screen.blit(bt, (self.research_btn.centerx - bt.get_width()//2, self.research_btn.centery - bt.get_height()//2))

        # Assignment Controls
        assigned = len(self.building.assigned_workers)
        max_workers = 3 * self.building.level
        w_txt = self.font.render(f"Workers: {assigned}/{max_workers}", True, BLACK)
        screen.blit(w_txt, (self.rect.x + 20, self.rect.y + 100))
        
        r_txt = self.font.render(f"Robots Assigned: {self.building.robots_assigned}", True, (0, 50, 150))
        screen.blit(r_txt, (self.rect.x + 20, self.rect.y + 130))
        
        self.robot_minus_btn = pygame.Rect(self.rect.x + 220, self.rect.y + 130, 25, 25)
        self.robot_plus_btn = pygame.Rect(self.rect.x + 255, self.rect.y + 130, 25, 25)
        
        pygame.draw.rect(screen, (100, 100, 100), self.robot_minus_btn, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), self.robot_plus_btn, border_radius=5)
        screen.blit(self.font.render("-", True, WHITE), (self.robot_minus_btn.centerx - 4, self.robot_minus_btn.centery - 10))
        screen.blit(self.font.render("+", True, WHITE), (self.robot_plus_btn.centerx - 6, self.robot_plus_btn.centery - 10))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.research_btn.collidepoint(event.pos):
                self.game.ui_manager.open_window(ResearchWindow(self.rm))
                return "HANDLED"
            
            if hasattr(self, 'robot_minus_btn') and self.robot_minus_btn.collidepoint(event.pos):
                if self.building.robots_assigned > 0:
                    self.building.robots_assigned -= 1
                    self.rm.inventory["robots"] = self.rm.inventory.get("robots", 0) + 1
                return "HANDLED"
            
            if hasattr(self, 'robot_plus_btn') and self.robot_plus_btn.collidepoint(event.pos):
                if self.rm.inventory.get("robots", 0) > 0:
                    current_total = len(self.building.assigned_workers) + self.building.robots_assigned
                    if current_total < 3 * self.building.level:
                        self.building.robots_assigned += 1
                        self.rm.inventory["robots"] -= 1
                return "HANDLED"
        return None

class ExitConfirmationWindow(Window):
    def __init__(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        super().__init__(cx - 150, cy - 75, 300, 150, "Exit to Title?")
        self.save_exit_btn = pygame.Rect(self.rect.x + 20, self.rect.y + 50, 260, 30)
        self.nosave_exit_btn = pygame.Rect(self.rect.x + 20, self.rect.y + 100, 260, 30)

    def draw(self, screen):
        super().draw(screen)
        pygame.draw.rect(screen, (50, 150, 50), self.save_exit_btn)
        pygame.draw.rect(screen, (150, 50, 50), self.nosave_exit_btn)
        s1 = self.font.render("Save and Exit", True, WHITE)
        s2 = self.font.render("Exit without Saving", True, WHITE)
        screen.blit(s1, (self.save_exit_btn.centerx - s1.get_width()//2, self.save_exit_btn.centery - s1.get_height()//2))
        screen.blit(s2, (self.nosave_exit_btn.centerx - s2.get_width()//2, self.nosave_exit_btn.centery - s2.get_height()//2))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.save_exit_btn.collidepoint(event.pos): return "SAVE_EXIT"
            if self.nosave_exit_btn.collidepoint(event.pos): return "NO_SAVE_EXIT"
        return None

class BuildingTab(Window):
    def __init__(self, input_handler, resource_manager, world):
        super().__init__(50, 50, 300, 400, "Construction")
        self.input_handler = input_handler
        self.rm = resource_manager
        self.world = world
        
        # Progression logic
        if not self.world.has_house():
            self.options = ["House"]
        elif not self.world.has_all_workshops():
            self.options = ["Logging Workshop", "Stone Refinery", "Mine"]
        else:
            self.options = ["Logging Workshop", "Stone Refinery", "Mine", "House", "Farm", "Garden", "Oxygenator", "Rocket Ship", "Warehouse", "Laboratory"]
            
        self.buttons = []
        self.checkboxes = []
        self.content_height = len(self.options) * 50 + 50
        
        for i, opt in enumerate(self.options):
            y_pos = self.rect.y + 40 + (i * 50)
            btn = pygame.Rect(self.rect.x + 10, y_pos, 240, 40)
            chk = pygame.Rect(self.rect.x + 260, y_pos + 10, 20, 20)
            self.buttons.append((btn, opt))
            self.checkboxes.append((chk, opt))

    def draw(self, screen):
        super().draw(screen)
        
        content_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 30, self.rect.width - 4, self.rect.height - 32)
        content_surf = pygame.Surface((content_rect.width, content_rect.height), pygame.SRCALPHA)
        
        locked_map = {
            "Warehouse": "Advanced Architecture",
            "Garden": "Botany",
            "Oxygenator": "Life Support",
            "Rocket Ship": "Aerospace Engineering"
        }
        
        for btn, opt in self.buttons:
            # Check if locked
            is_locked = False
            if opt in locked_map:
                tech_id = locked_map[opt]
                if tech_id not in self.rm.unlocked_techs:
                    is_locked = True

            # Adjust btn position for drawing on local surface
            draw_btn = btn.copy()
            draw_btn.x -= self.rect.x + 2
            draw_btn.y -= self.rect.y + 30
            draw_btn.y += self.scroll_y
            
            # Button Style
            btn_color = (100, 100, 100) if is_locked else (160, 110, 80)
            pygame.draw.rect(content_surf, btn_color, draw_btn, border_radius=5)
            pygame.draw.rect(content_surf, (60, 40, 30), draw_btn, 2, border_radius=5)
            
            text_color = (180, 180, 180) if is_locked else WHITE
            text = self.font.render(opt, True, text_color)
            content_surf.blit(text, (draw_btn.x + 10, draw_btn.y + 10))
            
            if is_locked:
                lock_txt = self.font.render("LOCKED", True, (200, 50, 50))
                content_surf.blit(lock_txt, (draw_btn.right - 70, draw_btn.y + 10))
            
        for chk, opt in self.checkboxes:
            draw_chk = chk.copy()
            draw_chk.x -= self.rect.x + 2
            draw_chk.y -= self.rect.y + 30
            draw_chk.y += self.scroll_y
            
            pygame.draw.rect(content_surf, WHITE, draw_chk)
            pygame.draw.rect(content_surf, BLACK, draw_chk, 1)
            is_pinned = any(p["name"] == opt for p in self.rm.pinned_costs)
            if is_pinned:
                pygame.draw.line(content_surf, BLACK, (draw_chk.x, draw_chk.y), (draw_chk.x + 20, draw_chk.y + 20), 2)
                pygame.draw.line(content_surf, BLACK, (draw_chk.x + 20, draw_chk.y), (draw_chk.x, draw_chk.y + 20), 2)
                
        screen.blit(content_surf, content_rect.topleft)

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        if res == "HANDLED": return "HANDLED"
        
        locked_map = {
            "Warehouse": "Advanced Architecture",
            "Garden": "Botany",
            "Oxygenator": "Life Support",
            "Rocket Ship": "Aerospace Engineering"
        }

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Adjust mouse pos for scrolling content space
            mx, my = event.pos
            # The buttons are stored with screen-relative Y in __init__, 
            # but we draw them with scroll_y.
            # Let's check collision against the VISUAL position or adjust mouse.
            
            for btn, opt in self.buttons:
                # Visual rect:
                visual_btn = btn.copy()
                visual_btn.y += self.scroll_y
                # Also need to check if mouse is within the content clip area
                content_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 30, self.rect.width - 4, self.rect.height - 32)
                
                if content_rect.collidepoint(event.pos) and visual_btn.collidepoint(event.pos):
                    if opt in locked_map and locked_map[opt] not in self.rm.unlocked_techs:
                        return "HANDLED" # Locked
                    self.input_handler.set_build_mode(opt)
                    return "CLOSE"
            
            for chk, opt in self.checkboxes:
                visual_chk = chk.copy()
                visual_chk.y += self.scroll_y
                content_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 30, self.rect.width - 4, self.rect.height - 32)

                if content_rect.collidepoint(event.pos) and visual_chk.collidepoint(event.pos):
                    if opt in locked_map and locked_map[opt] not in self.rm.unlocked_techs:
                        return "HANDLED" # Locked
                    is_pinned = any(p["name"] == opt for p in self.rm.pinned_costs)
                    if is_pinned:
                        self.rm.unpin_cost(opt)
                    else:
                        cost = Building.get_cost(opt)
                        self.rm.pin_cost(opt, cost)
                        self.input_handler.set_build_mode(opt)
                    return "HANDLED"
        return None
