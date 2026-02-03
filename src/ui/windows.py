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
        
        self.upgrade_btn = pygame.Rect(self.rect.x + 350, self.rect.y + 5, 20, 20)
        self.delete_btn = pygame.Rect(self.rect.x + self.rect.width - 40, self.rect.y + self.rect.height - 40, 30, 30)
        self.research_btn = pygame.Rect(self.rect.x + 100, self.rect.y + 360, 200, 30)

    def draw(self, screen):
        super().draw(screen)
        
        # Stats
        rtype = "Resources"
        if self.building.type == "Logging Workshop": rtype = "Wood"
        elif self.building.type == "Stone Refinery": rtype = "Stone"
        elif self.building.type == "Mine": rtype = "Iron"
        elif self.building.type == "Copper Mine": rtype = "Copper"
        elif self.building.type == "Power Plant": rtype = "Batteries"
        elif self.building.type == "Advanced Machine Factory": rtype = "Wiring"
        elif self.building.type == "Oxygenator": rtype = "Oxygen"
        elif self.building.type in ["Farm", "Garden"]: rtype = "Food"
        elif self.building.type == "Laboratory": 
            rtype = "Science"
        elif self.building.type == "Warehouse":
            rtype = "Storage"
        
        assigned = len(self.building.assigned_workers) 
        
        if self.building.type == "House":
            stats = f"Villagers: {self.building.villagers}"
        else:
            if self.building.type == "Laboratory":
                stats = f"Science Gen: {self.building.production_buffer:.2f}"
            elif self.building.type == "Raw Material Factory":
                stats = f"Parts: {int(self.building.production_buffer)}"
            elif self.building.type == "Power Plant":
                stats = f"Batteries: {int(self.building.production_buffer)}"
                i_txt = self.font.render("Consumes Wiring from Inventory", True, (50, 50, 50))
                screen.blit(i_txt, (self.rect.x + 20, self.rect.y + 330))
            elif self.building.type == "Advanced Machine Factory":
                stats = f"Wiring: {int(self.building.production_buffer)}"
                i_txt = self.font.render("Consumes Copper from Inventory", True, (50, 50, 50))
                screen.blit(i_txt, (self.rect.x + 20, self.rect.y + 330))
            elif self.building.type == "Blast Furnace":
                stats = f"Steel: {int(self.building.production_buffer)}"
                
                # Draw Power Status
                has_power = self.rm.inventory.get("batteries", 0) >= (15.0/60.0)
                p_col = (50, 50, 50) if has_power else (200, 50, 50)
                p_status = "POWERED" if has_power else "NO POWER (Needs Batteries)"
                p_txt = self.font.render(p_status, True, p_col)
                screen.blit(p_txt, (self.rect.x + 20, self.rect.y + 310))
            elif self.building.type == "Warehouse":
                assigned = len(self.building.assigned_workers)
                status = "ACTIVE" if assigned >= 3 else "INACTIVE (Needs 3 Workers)"
                stats = f"Effect: +10% Production ({status})"
            else:
                stats = f"{rtype}: {int(self.building.production_buffer)}"
                
                if self.building.type == "Copper Mine":
                    has_power = self.rm.inventory.get("batteries", 0) >= (15.0/60.0)
                    p_col = (50, 50, 50) if has_power else (200, 50, 50)
                    p_status = "POWERED" if has_power else "NO POWER (Needs Batteries)"
                    p_txt = self.font.render(p_status, True, p_col)
                    screen.blit(p_txt, (self.rect.x + 20, self.rect.y + 310))
            
            # Worker count display
            max_workers = 3 * self.building.level
            w_txt = self.font.render(f"Workers: {assigned}/{max_workers}", True, BLACK)
            screen.blit(w_txt, (self.rect.x + 20, self.rect.y + 400))

            if self.building.type == "Raw Material Factory":
                 i_txt = self.font.render("Consumes Stone, Iron + Copper from Inventory", True, (50, 50, 50))
                 screen.blit(i_txt, (self.rect.x + 20, self.rect.y + 330))

            elif self.building.type in ["Blast Furnace", "Power Plant", "Advanced Machine Factory"]:
                 if self.building.type == "Blast Furnace":
                    stats = f"Steel: {int(self.building.production_buffer)}"
                    i_txt = self.font.render("Consumes Wood + Iron from Inventory", True, (50, 50, 50))
                    screen.blit(i_txt, (self.rect.x + 20, self.rect.y + 330))
                 
                 # Toggle Button
                 self.toggle_btn = pygame.Rect(self.rect.x + 20, self.rect.y + 360, 100, 30)
                 btn_col = (100, 200, 100) if self.building.is_on else (200, 100, 100)
                 pygame.draw.rect(screen, btn_col, self.toggle_btn, border_radius=5)
                 pygame.draw.rect(screen, (60, 40, 30), self.toggle_btn, 2, border_radius=5)
                 
                 status_txt = "Status: ON" if self.building.is_on else "Status: OFF"
                 stxt = self.font.render(status_txt, True, WHITE)
                 screen.blit(stxt, (self.toggle_btn.centerx - stxt.get_width()//2, self.toggle_btn.centery - stxt.get_height()//2))
                 
            elif self.building.type == "Laboratory":
                 pygame.draw.rect(screen, (100, 100, 200), self.research_btn, border_radius=5)
                 pygame.draw.rect(screen, (60, 40, 30), self.research_btn, 2, border_radius=5)
                 rtxt = self.font.render("Open Research Tree", True, WHITE)
                 screen.blit(rtxt, (self.research_btn.centerx - rtxt.get_width()//2, self.research_btn.centery - rtxt.get_height()//2))

        text = self.font.render(stats, True, BLACK)
        screen.blit(text, (self.rect.x + 20, self.rect.y + 40))
        
        # Graph area (Hide for Warehouse as it doesn't produce resources)
        if self.building.type != "Warehouse":
            graph_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 70, 360, 150)
            pygame.draw.rect(screen, (235, 225, 205), graph_rect) # Lighter Beige
            pygame.draw.rect(screen, (60, 40, 30), graph_rect, 2) # Dark Brown Border
            
            history = self.building.production_history
            max_val = max(history) if max(history) > 0 else 10
            max_val = math.ceil(max_val / 5) * 5
            max_val = max(max_val, 5)

            # Draw grid lines & Y-axis labels
            steps = 5
            for i in range(steps + 1):
                val = (max_val / steps) * i
                y_pos = graph_rect.bottom - ((val / max_val) * graph_rect.height)
                if i > 0:
                    pygame.draw.line(screen, (200, 190, 170), (graph_rect.x, y_pos), (graph_rect.right, y_pos), 1)
                label = self.font.render(str(int(val)), True, (60, 40, 30))
                screen.blit(label, (graph_rect.x + 5, y_pos - 10))

            # Draw bars
            max_days = 7
            bar_width = graph_rect.width / max_days
            start_slot = max_days - len(history)
            
            for i, val in enumerate(history):
                slot = start_slot + i
                if slot < 0: continue
                h = (val / max_val) * graph_rect.height
                x = graph_rect.x + (slot * bar_width)
                y = graph_rect.y + graph_rect.height - h
                bar_rect = pygame.Rect(x, y, max(1, bar_width - 4), h) 
                pygame.draw.rect(screen, (80, 160, 80), bar_rect) # Greenish bars

                days_ago = len(history) - 1 - i
                lbl_text = "Today" if days_ago == 0 else ("Yesterday" if days_ago == 1 else f"{days_ago} days ago")
                lbl = self.font.render(lbl_text, True, (60, 40, 30))
                rotated_lbl = pygame.transform.rotate(lbl, 90)
                lbl_x = x + (bar_width / 2) - (rotated_lbl.get_width() / 2)
                lbl_y = graph_rect.bottom + 5
                if lbl_y + rotated_lbl.get_height() < self.rect.bottom - 5:
                        screen.blit(rotated_lbl, (lbl_x, lbl_y))
                elif days_ago == 0:
                        screen.blit(rotated_lbl, (lbl_x, lbl_y))
        
        # Upgrade Icon
        assets = Assets.get()
        arrow = assets.get_sprite("icon_arrow_up")
        pygame.draw.rect(screen, (160, 110, 80), self.upgrade_btn, border_radius=5)
        pygame.draw.rect(screen, (60, 40, 30), self.upgrade_btn, 2, border_radius=5)
        if arrow:
            screen.blit(arrow, (self.upgrade_btn.x + 2, self.upgrade_btn.y + 2))
            
        # Delete Button (Trash Can)
        pygame.draw.rect(screen, (200, 60, 60), self.delete_btn, border_radius=5)
        pygame.draw.rect(screen, (60, 40, 30), self.delete_btn, 2, border_radius=5)
        trash_text = self.font.render("DEL", True, WHITE)
        screen.blit(trash_text, (self.delete_btn.x + 2, self.delete_btn.y + 5))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res: return res
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.building.type == "Laboratory" and self.research_btn.collidepoint(event.pos):
                self.game.ui_manager.open_window(ResearchWindow(self.rm, self.world))
                return "HANDLED"

            if self.building.type in ["Blast Furnace", "Power Plant", "Advanced Machine Factory"]:
                if hasattr(self, 'toggle_btn') and self.toggle_btn.collidepoint(event.pos):
                    self.building.is_on = not self.building.is_on
                    return "HANDLED"

            if self.upgrade_btn.collidepoint(event.pos):
                if self.building.level < 100:
                    cost = self.building.get_upgrade_cost()
                    if self.rm.has_resources(cost):
                        self.rm.deduct_resources(cost)
                        self.building.level += 1
                        self.title = f"{self.building.type} (Lvl {self.building.level})"
                return "HANDLED"
                
            if self.delete_btn.collidepoint(event.pos):
                cost = Building.get_cost(self.building.type)
                for res, amount in cost.items():
                    self.rm.add_resource(res, amount)
                self.world.buildings.pop((self.building.x, self.building.y))
                return "CLOSE"
        return None

class ResearchWindow(Window):
    def __init__(self, resource_manager, world):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 500, 400
        super().__init__(cx - w//2, cy - h//2, w, h, "Research Lab")
        self.rm = resource_manager
        self.world = world
        
        self.techs = [
            {"name": "Advanced Architecture", "cost": 100, "desc": "Unlocks Warehouse", "id": "Advanced Architecture"},
            {"name": "Botany", "cost": 75, "desc": "Unlocks Garden", "id": "Botany"},
            {"name": "Life Support", "cost": 150, "desc": "Unlocks Oxygenator", "id": "Life Support"},
            {"name": "Factory Automation", "cost": 100, "desc": "Unlocks Raw Material Factory", "id": "Factory Automation"},
            {"name": "Advanced Metallurgy", "cost": 150, "desc": "Unlocks Blast Furnace", "id": "Advanced Metallurgy"},
            {"name": "Electronics", "cost": 200, "desc": "Unlocks Wiring Recipe", "id": "Electronics"},
            {"name": "Power Generation", "cost": 300, "desc": "Unlocks Power Plant", "id": "Power Generation"},
            {"name": "Advanced Engineering", "cost": 250, "desc": "Unlocks Advanced Machine Factory", "id": "Advanced Engineering"},
            {"name": "Aerospace Engineering", "cost": 500, "desc": "Unlocks Rocket Ship", "id": "Aerospace Engineering"}
        ]
        self.unlock_buttons = []

    def draw(self, screen):
        super().draw(screen)
        
        # Clipping area for content
        content_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 70, self.rect.width - 4, self.rect.height - 72)
        content_surf = pygame.Surface((content_rect.width, content_rect.height), pygame.SRCALPHA)
        
        points = int(self.rm.science_points)
        s_txt = self.font.render(f"Science Points: {points}", True, (50, 50, 150))
        screen.blit(s_txt, (self.rect.x + 20, self.rect.y + 40))
        
        self.unlock_buttons = []
        y_pos = self.scroll_y
        for tech in self.techs:
            box_rect = pygame.Rect(20, y_pos, self.rect.width - 40, 60)
            is_unlocked = tech["id"] in self.rm.unlocked_techs
            color = (200, 255, 200) if is_unlocked else (220, 220, 220)
            pygame.draw.rect(content_surf, color, box_rect)
            pygame.draw.rect(content_surf, BLACK, box_rect, 1)
            content_surf.blit(self.font.render(tech["name"], True, BLACK), (box_rect.x + 10, box_rect.y + 5))
            content_surf.blit(self.font.render(tech["desc"], True, (50, 50, 50)), (box_rect.x + 10, box_rect.y + 25))
            
            if not is_unlocked:
                content_surf.blit(self.font.render(f"Cost: {tech['cost']}", True, (100, 50, 50)), (box_rect.x + 10, box_rect.y + 40))
                btn_rect = pygame.Rect(box_rect.right - 80, box_rect.y + 15, 70, 30)
                btn_color = (100, 160, 100) if self.rm.science_points >= tech["cost"] else (150, 150, 150)
                pygame.draw.rect(content_surf, btn_color, btn_rect, border_radius=5)
                pygame.draw.rect(content_surf, (60, 40, 30), btn_rect, 2, border_radius=5)
                btxt = self.font.render("Unlock", True, WHITE)
                content_surf.blit(btxt, (btn_rect.centerx - btxt.get_width()//2, btn_rect.centery - btxt.get_height()//2))
                
                # Real screen rect for click detection
                screen_btn = btn_rect.copy()
                screen_btn.x += content_rect.x
                screen_btn.y += content_rect.y
                self.unlock_buttons.append((screen_btn, tech))
            else:
                lbl = self.font.render("Unlocked", True, (0, 100, 0))
                content_surf.blit(lbl, (box_rect.right - 80, box_rect.y + 20))
            y_pos += 70
        
        self.content_height = y_pos - self.scroll_y + 20
        screen.blit(content_surf, content_rect.topleft)

    def handle_input(self, event):
        res = super().handle_input(event)
        if res: return res
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn, tech in self.unlock_buttons:
                if btn.collidepoint(event.pos):
                    if self.rm.science_points >= tech["cost"]:
                        self.rm.science_points -= tech["cost"]
                        self.rm.unlocked_techs.append(tech["id"])
                    return "HANDLED"
        return None

class ItemCodexWindow(Window):
    def __init__(self, resource_manager):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 600, 450
        super().__init__(cx - w//2, cy - h//2, w, h, "Item Codex")
        self.rm = resource_manager
        
        self.items = [
            {"name": "Wood", "desc": "Basic building material harvested from Logging Workshops. Essential for early construction.", "tech": None},
            {"name": "Stone", "desc": "Raw stone gathered from Stone Refineries. Used for foundations and heavy structures.", "tech": None},
            {"name": "Iron", "desc": "Raw iron extracted from Mines. Vital for machinery and advanced building components.", "tech": None},
            {"name": "Food", "desc": "Essential sustenance for your villagers. Keeps productivity high; efficiency drops if people are hungry.", "tech": None},
            {"name": "Copper", "desc": "Metallic element mined from Copper Mines. Primarily used in the Advanced Machine Factory to produce wiring.", "tech": None},
            {"name": "Science", "desc": "Abstract knowledge generated by Laboratories. Invested in the Research Tree to unlock new tech.", "tech": None},
            {"name": "Oxygen", "desc": "Breathable air produced by Oxygenators. Required for survival and fueling rocket launches.", "tech": "Life Support"},
            {"name": "Material Parts", "desc": "Precision components manufactured in Raw Material Factories from Iron and Stone.", "tech": "Factory Automation"},
            {"name": "Steel", "desc": "A strong alloy from Blast Furnaces (Wood + Iron). Essential for high-tier technology and the Rocket.", "tech": "Advanced Metallurgy"},
            {"name": "Batteries", "desc": "Energy storage units produced by Power Plants from Wiring. Necessary to power advanced buildings like the Blast Furnace and Copper Mine.", "tech": "Power Generation"},
            {"name": "Wiring", "desc": "Electrical conductors made from Copper in the Advanced Machine Factory. Used in Power Plants to manufacture Batteries.", "tech": "Electronics"}
        ]
        self.selected_item = self.items[0]
        self.list_buttons = []
        self.content_height = len(self.items) * 45

    def draw(self, screen):
        super().draw(screen)
        
        # Split: Left (List), Right (Details)
        list_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 40, 200, self.rect.height - 50)
        detail_rect = pygame.Rect(self.rect.x + 220, self.rect.y + 40, self.rect.width - 230, self.rect.height - 50)
        
        pygame.draw.rect(screen, (200, 170, 130), list_rect, border_radius=5)
        pygame.draw.rect(screen, (60, 40, 30), list_rect, 2, border_radius=5)
        
        # Draw List with Clipping
        list_surf = pygame.Surface((list_rect.width - 4, list_rect.height - 4), pygame.SRCALPHA)
        self.list_buttons = []
        
        y_off = self.scroll_y
        for item in self.items:
            unlocked = item["tech"] is None or item["tech"] in self.rm.unlocked_techs
            if not unlocked:
                y_off += 45
                continue
                
            btn_rect = pygame.Rect(5, y_off, list_rect.width - 15, 40)
            is_selected = self.selected_item == item
            bg_col = (180, 140, 100) if is_selected else (220, 190, 150)
            
            pygame.draw.rect(list_surf, bg_col, btn_rect, border_radius=5)
            pygame.draw.rect(list_surf, (60, 40, 30), btn_rect, 1, border_radius=5)
            
            txt = self.font.render(item["name"], True, (30, 20, 10))
            list_surf.blit(txt, (btn_rect.x + 10, btn_rect.y + 10))
            
            # Real screen rect for click detection
            screen_btn = btn_rect.copy()
            screen_btn.x += list_rect.x + 2
            screen_btn.y += list_rect.y + 2
            self.list_buttons.append((screen_btn, item))
            
            y_off += 45
            
        screen.blit(list_surf, (list_rect.x + 2, list_rect.y + 2))
        
        # Draw Details
        if self.selected_item:
            # Header Picture Area
            pic_rect = pygame.Rect(detail_rect.x + 20, detail_rect.y + 10, detail_rect.width - 40, 150)
            pygame.draw.rect(screen, (235, 225, 205), pic_rect, border_radius=10)
            pygame.draw.rect(screen, (60, 40, 30), pic_rect, 2, border_radius=10)
            
            assets = Assets.get()
            sprite = assets.get_sprite(f"item_{self.selected_item['name']}")
            if sprite:
                # Scaled up for "High Quality" look
                scaled = pygame.transform.scale(sprite, (128, 128))
                screen.blit(scaled, (pic_rect.centerx - 64, pic_rect.centery - 64))
            
            # Name
            name_surf = pygame.font.SysFont("Arial", 24, bold=True).render(self.selected_item["name"], True, (60, 40, 30))
            screen.blit(name_surf, (detail_rect.x + 20, pic_rect.bottom + 15))
            
            # Description (Wrapped)
            desc = self.selected_item["desc"]
            words = desc.split(' ')
            lines = []
            curr_line = ""
            for w in words:
                if self.font.size(curr_line + w)[0] < detail_rect.width - 40:
                    curr_line += w + " "
                else:
                    lines.append(curr_line)
                    curr_line = w + " "
            lines.append(curr_line)
            
            for i, line in enumerate(lines):
                l_surf = self.font.render(line, True, (40, 30, 20))
                screen.blit(l_surf, (detail_rect.x + 20, pic_rect.bottom + 50 + i*22))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res: return res
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn, item in self.list_buttons:
                # Account for scrolling in click detection
                # Wait, screen_btn is calculated with scroll_y inside draw.
                # So we just check collision.
                if btn.collidepoint(event.pos):
                    self.selected_item = item
                    return "HANDLED"
        return None

class WorkerAssignmentWindow(Window):
    def __init__(self, resource_manager, world):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        super().__init__(cx - 300, cy - 225, 600, 450, "Assign Workers")
        self.rm = resource_manager
        self.world = world
        self.jobs = ["House", "Logging Workshop", "Stone Refinery", "Mine", "Copper Mine", "Blast Furnace", "Advanced Machine Factory", "Power Plant", "Farm", "Garden", "Oxygenator", "Laboratory", "Warehouse", "Raw Material Factory"]
        self.controls = [] 
        self.upgrade_buttons = []

    def draw(self, screen):
        super().draw(screen)
        self.controls = []
        self.upgrade_buttons = []
        content_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 70, self.rect.width - 4, self.rect.height - 72)
        content_surf = pygame.Surface((content_rect.width, content_rect.height), pygame.SRCALPHA)
        
        y_pos = self.scroll_y
        row_height = 45
        for job in self.jobs:
            buildings = [b for b in self.world.buildings.values() if b.type == job]
            count = len(buildings)
            if count == 0: continue
            
            if job == "House":
                 total_cap = sum(20 * b.level for b in buildings)
                 assigned = sum(b.villagers for b in buildings)
                 target = -2
            else:
                 total_cap = sum(3 * b.level for b in buildings)
                 assigned = sum(len(b.assigned_workers) for b in buildings)
                 target = self.rm.job_targets.get(job, -1)
            
            assets = Assets.get()
            sprite = assets.get_sprite(job)
            if sprite:
                content_surf.blit(pygame.transform.scale(sprite, (32, 32)), (18, y_pos))
            
            txt = f"x{count}: {assigned}/{total_cap} v"
            content_surf.blit(self.font.render(txt, True, BLACK), (58, y_pos + 8))
            
            upgrade_rect = pygame.Rect(218, y_pos + 5, 30, 25)
            pygame.draw.rect(content_surf, (100, 100, 255), upgrade_rect)
            utxt = self.font.render("U", True, WHITE)
            content_surf.blit(utxt, (upgrade_rect.centerx - utxt.get_width()//2, upgrade_rect.centery - utxt.get_height()//2))
            
            screen_upgrade = upgrade_rect.copy()
            screen_upgrade.x += content_rect.x
            screen_upgrade.y += content_rect.y
            self.upgrade_buttons.append((screen_upgrade, job))

            if job != "House":
                w_minus = pygame.Rect(253, y_pos + 5, 25, 25)
                w_plus = pygame.Rect(333, y_pos + 5, 25, 25)
                pygame.draw.rect(content_surf, (160, 110, 80), w_minus, border_radius=5)
                pygame.draw.rect(content_surf, (160, 110, 80), w_plus, border_radius=5)
                content_surf.blit(self.font.render("-", True, WHITE), (w_minus.centerx - 4, w_minus.centery - 10))
                content_surf.blit(self.font.render("+", True, WHITE), (w_plus.centerx - 6, w_plus.centery - 10))
                vtxt = self.font.render("Max" if target == -1 else str(target), True, BLACK)
                content_surf.blit(vtxt, (288, y_pos + 8))
                
                screen_minus = w_minus.copy()
                screen_minus.x += content_rect.x
                screen_minus.y += content_rect.y
                screen_plus = w_plus.copy()
                screen_plus.x += content_rect.x
                screen_plus.y += content_rect.y
                self.controls.append((screen_minus, screen_plus, job))
            y_pos += row_height
        
        self.content_height = y_pos - self.scroll_y + 20
        screen.blit(content_surf, content_rect.topleft)

    def handle_input(self, event):
        res = super().handle_input(event)
        if res: return res
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn, job in self.upgrade_buttons:
                if btn.collidepoint(event.pos):
                    buildings = sorted([b for b in self.world.buildings.values() if b.type == job], key=lambda b: b.level)
                    for b in buildings:
                        if b.level < 100:
                            cost = b.get_upgrade_cost()
                            if self.rm.has_resources(cost):
                                self.rm.deduct_resources(cost)
                                b.level += 1
                    return "HANDLED"
            for minus, plus, job in self.controls:
                curr = self.rm.job_targets.get(job, -1)
                total_cap = sum(3 * b.level for b in [b for b in self.world.buildings.values() if b.type == job])
                if total_cap == 0: continue
                if minus.collidepoint(event.pos):
                    if curr == -1: self.rm.job_targets[job] = total_cap - 1
                    elif curr > 0: self.rm.job_targets[job] -= 1
                    return "HANDLED"
                if plus.collidepoint(event.pos):
                    if curr != -1:
                        if curr + 1 >= total_cap: self.rm.job_targets[job] = -1
                        else: self.rm.job_targets[job] += 1
                    return "HANDLED"
        return None

class InventoryWindow(Window):
    def __init__(self, resource_manager):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        super().__init__(cx - 150, cy - 100, 300, 200, "Inventory")
        self.rm = resource_manager
        self.content_height = len(self.rm.inventory) * 30 + 50

    def draw(self, screen):
        super().draw(screen)
        content_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 30, self.rect.width - 4, self.rect.height - 32)
        content_surf = pygame.Surface((content_rect.width, content_rect.height), pygame.SRCALPHA)
        y_offset = self.scroll_y + 10
        for res, amount in self.rm.inventory.items():
            txt = f"{res.capitalize()}: {int(amount)}"
            content_surf.blit(self.font.render(txt, True, BLACK), (20, y_offset))
            y_offset += 30
        screen.blit(content_surf, content_rect.topleft)

    def handle_input(self, event):
        res = super().handle_input(event)
        if res: return res
        return None

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
        if res: return res
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.yes_btn.collidepoint(event.pos): return "START_TUTORIAL"
            if self.no_btn.collidepoint(event.pos): return "CLOSE"
        return None

class TutorialWindow(Window):
    def __init__(self, hud):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        super().__init__(cx - 250, cy - 125, 500, 250, "Help Guide")
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
        words = self.pages[self.page].split(' ')
        lines, curr = [], ""
        for word in words:
            if self.font.size(curr + word)[0] < self.rect.width - 40: curr += word + " "
            else:
                lines.append(curr)
                curr = word + " "
        lines.append(curr)
        for i, line in enumerate(lines):
            screen.blit(self.font.render(line, True, BLACK), (self.rect.x + 20, self.rect.y + 40 + i*20))
        pygame.draw.rect(screen, (100, 100, 100), self.next_btn)
        nt = "FINISH" if self.page == len(self.pages) - 1 else "NEXT"
        screen.blit(self.font.render(nt, True, WHITE), (self.next_btn.x + 10, self.next_btn.y + 5))
        assets = Assets.get()
        arrow = assets.get_sprite("icon_arrow_up")
        if arrow:
            if self.page == 1:
                screen.blit(pygame.transform.rotate(arrow, -90), (self.hud.inventory_panel_rect.x - 40, self.hud.inventory_panel_rect.y + 10))
            elif self.page == 2:
                screen.blit(pygame.transform.rotate(arrow, 90), (self.hud.build_icon_rect.x + 40, self.hud.build_icon_rect.y + 8))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res: return res
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.next_btn.collidepoint(event.pos):
                if self.page < len(self.pages) - 1:
                    self.page += 1
                    return "HANDLED"
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
        input_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 50, 260, 30)
        pygame.draw.rect(screen, WHITE, input_rect)
        pygame.draw.rect(screen, BLACK, input_rect, 1)
        screen.blit(self.font.render(self.input_text, True, BLACK), (input_rect.x + 5, input_rect.y + 5))
        if self.message: screen.blit(self.font.render(self.message, True, (200, 50, 50)), (self.rect.x + 20, self.rect.y + 90))
        else: screen.blit(self.font.render("Press Enter to submit", True, (100, 100, 100)), (self.rect.x + 20, self.rect.y + 90))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        if res: return res
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_text in self.rm.used_codes: self.message = "Code already used!"
                elif self.input_text == "baconwithcherries":
                    for res in ["wood", "stone", "iron"]: self.rm.add_resource(res, 1500)
                    self.rm.science_points += 2000
                    self.rm.used_codes.append("baconwithcherries")
                    return "CLOSE"
                elif self.input_text == "banana":
                    self.rm.add_resource("food", 5000)
                    self.rm.used_codes.append("banana")
                    return "CLOSE"
                elif self.input_text == "goldmine":
                    for res in ["wood", "stone", "iron"]: self.rm.add_resource(res, 5000)
                    self.rm.used_codes.append("goldmine")
                    return "CLOSE"
                else: self.message = "Invalid Code!"
            elif event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
            else:
                if len(self.input_text) < 20: self.input_text += event.unicode
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
        res = super().handle_input(event)
        if res: return res
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.exit_btn.collidepoint(event.pos): return "GAME_OVER_EXIT"
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
        pop = self.em.get_count()
        rem = pop - self.building.boarded_population
        screen.blit(self.font.render(f"City Population: {pop}", True, BLACK), (self.rect.x + 20, self.rect.y + 40))
        screen.blit(self.font.render(f"Boarded: {self.building.boarded_population}", True, BLACK), (self.rect.x + 20, self.rect.y + 70))
        if rem > 0:
            pygame.draw.rect(screen, (100, 100, 255), self.board_one_btn)
            b1 = self.font.render("Board 1 (10 all + ox)", True, WHITE)
            screen.blit(b1, (self.board_one_btn.centerx - b1.get_width()//2, self.board_one_btn.centery - b1.get_height()//2))
            pygame.draw.rect(screen, (80, 80, 200), self.board_all_btn)
            ba = self.font.render(f"Board All ({rem * 10} all + ox)", True, WHITE)
            screen.blit(ba, (self.board_all_btn.centerx - ba.get_width()//2, self.board_all_btn.centery - ba.get_height()//2))
        if self.building.boarded_population >= pop and pop > 0:
            pygame.draw.rect(screen, (255, 50, 50), self.launch_btn)
            lt = self.font.render("LAUNCH ROCKET", True, WHITE)
            screen.blit(lt, (self.launch_btn.centerx - lt.get_width()//2, self.launch_btn.centery - lt.get_height()//2))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        if res: return res
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pop = self.em.get_count()
            rem = pop - self.building.boarded_population
            if self.board_one_btn.collidepoint(event.pos) and rem > 0:
                cost = {"wood": 10, "stone": 10, "iron": 10, "oxygen": 10}
                if self.rm.has_resources(cost):
                    self.rm.deduct_resources(cost)
                    self.building.boarded_population += 1
            if self.board_all_btn.collidepoint(event.pos) and rem > 0:
                cost = {"wood": rem * 10, "stone": rem * 10, "iron": rem * 10, "oxygen": rem * 10}
                if self.rm.has_resources(cost):
                    self.rm.deduct_resources(cost)
                    self.building.boarded_population = pop
            if self.launch_btn.collidepoint(event.pos) and self.building.boarded_population >= pop and pop > 0:
                self.building.is_launching = True
                return "CLOSE"
        return None

class TraderWindow(Window):
    def __init__(self, resource_manager):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        super().__init__(cx - 200, cy - 150, 400, 300, "Traveling Merchant")
        self.rm = resource_manager
        self.trades = [{"cost": {"wood": 100}, "reward": {"emerald": 1}}, {"cost": {"stone": 100}, "reward": {"diamond": 1}}, {"cost": {"iron": 50}, "reward": {"gold": 5}}, {"cost": {"food": 50}, "reward": {"copper": 10}}]
        self.trade_buttons = []

    def draw(self, screen):
        super().draw(screen)
        y_pos = self.rect.y + 50
        self.trade_buttons = []
        for trade in self.trades:
            ctx = ", ".join([f"{v} {k.capitalize()}" for k, v in trade["cost"].items()])
            rtx = ", ".join([f"{v} {k.capitalize()}" for k, v in trade["reward"].items()])
            screen.blit(self.font.render(f"{ctx} -> {rtx}", True, (60, 40, 30)), (self.rect.x + 20, y_pos + 5))
            btn_rect = pygame.Rect(self.rect.right - 100, y_pos, 80, 30)
            color = (100, 160, 100) if self.rm.has_resources(trade["cost"]) else (150, 150, 150)
            pygame.draw.rect(screen, color, btn_rect, border_radius=5)
            pygame.draw.rect(screen, (60, 40, 30), btn_rect, 2, border_radius=5)
            bt = self.font.render("Trade", True, WHITE)
            screen.blit(bt, (btn_rect.centerx - bt.get_width()//2, btn_rect.centery - bt.get_height()//2))
            self.trade_buttons.append((btn_rect, trade))
            y_pos += 50

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        if res: return res
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn, trade in self.trade_buttons:
                if btn.collidepoint(event.pos):
                    if self.rm.deduct_resources(trade["cost"]):
                        for res, amount in trade["reward"].items(): self.rm.add_resource(res, amount)
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
        s1, s2 = self.font.render("Save and Exit", True, WHITE), self.font.render("Exit without Saving", True, WHITE)
        screen.blit(s1, (self.save_exit_btn.centerx - s1.get_width()//2, self.save_exit_btn.centery - s1.get_height()//2))
        screen.blit(s2, (self.nosave_exit_btn.centerx - s2.get_width()//2, self.nosave_exit_btn.centery - s2.get_height()//2))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        if res: return res
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.save_exit_btn.collidepoint(event.pos): return "SAVE_EXIT"
            if self.nosave_exit_btn.collidepoint(event.pos): return "NO_SAVE_EXIT"
        return None

class BuildingTab(Window):
    def __init__(self, input_handler, resource_manager, world):
        super().__init__(50, 50, 300, 400, "Construction")
        self.input_handler, self.rm, self.world = input_handler, resource_manager, world
        if not self.world.has_house(): self.options = ["House"]
        elif not self.world.has_all_workshops(): self.options = ["Logging Workshop", "Stone Refinery", "Mine"]
        else: self.options = ["Logging Workshop", "Stone Refinery", "Mine", "Copper Mine", "Blast Furnace", "Advanced Machine Factory", "Power Plant", "House", "Farm", "Garden", "Oxygenator", "Raw Material Factory", "Rocket Ship", "Warehouse", "Laboratory"]
        if any(b.type == "Laboratory" for b in self.world.buildings.values()) and "Laboratory" in self.options: self.options.remove("Laboratory")
        
        self.buttons, self.checkboxes = [], []
        self.content_height = len(self.options) * 50 + 20
        # Start buttons below title area (y + 70)
        start_y = self.rect.y + 75
        for i, opt in enumerate(self.options):
            y = start_y + (i * 50)
            self.buttons.append((pygame.Rect(self.rect.x + 10, y, 240, 40), opt))
            self.checkboxes.append((pygame.Rect(self.rect.x + 260, y + 10, 20, 20), opt))

    def draw(self, screen):
        super().draw(screen)
        # Content area starts at y + 70
        content_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 70, self.rect.width - 4, self.rect.height - 72)
        content_surf = pygame.Surface((content_rect.width, content_rect.height), pygame.SRCALPHA)
        
        lmap = {"Warehouse": "Advanced Architecture", "Garden": "Botany", "Oxygenator": "Life Support", "Raw Material Factory": "Factory Automation", "Blast Furnace": "Advanced Metallurgy", "Power Plant": "Power Generation", "Advanced Machine Factory": "Advanced Engineering", "Rocket Ship": "Aerospace Engineering"}
        
        for btn, opt in self.buttons:
            locked = opt in lmap and lmap[opt] not in self.rm.unlocked_techs
            dbtn = btn.copy()
            # Make relative to content_surf and apply scroll
            dbtn.x -= content_rect.x
            dbtn.y = dbtn.y - content_rect.y + self.scroll_y
            
            pygame.draw.rect(content_surf, (100, 100, 100) if locked else (160, 110, 80), dbtn, border_radius=5)
            pygame.draw.rect(content_surf, (60, 40, 30), dbtn, 2, border_radius=5)
            content_surf.blit(self.font.render(opt, True, (180, 180, 180) if locked else WHITE), (dbtn.x + 10, dbtn.y + 10))
            if locked: content_surf.blit(self.font.render("LOCKED", True, (200, 50, 50)), (dbtn.right - 70, dbtn.y + 10))
            
        for chk, opt in self.checkboxes:
            dchk = chk.copy()
            dchk.x -= content_rect.x
            dchk.y = dchk.y - content_rect.y + self.scroll_y
            
            pygame.draw.rect(content_surf, WHITE, dchk)
            pygame.draw.rect(content_surf, BLACK, dchk, 1)
            if any(p["name"] == opt for p in self.rm.pinned_costs):
                pygame.draw.line(content_surf, BLACK, (dchk.x, dchk.y), (dchk.x + 20, dchk.y + 20), 2)
                pygame.draw.line(content_surf, BLACK, (dchk.x + 20, dchk.y), (dchk.x, dchk.y + 20), 2)
                
        screen.blit(content_surf, content_rect.topleft)

    def handle_input(self, event):
        res = super().handle_input(event)
        if res in ["CLOSE", "HANDLED"]: return res
        
        lmap = {"Warehouse": "Advanced Architecture", "Garden": "Botany", "Oxygenator": "Life Support", "Raw Material Factory": "Factory Automation", "Blast Furnace": "Advanced Metallurgy", "Power Plant": "Power Generation", "Advanced Machine Factory": "Advanced Engineering", "Rocket Ship": "Aerospace Engineering"}
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Click detection must match content_rect
            crect = pygame.Rect(self.rect.x + 2, self.rect.y + 70, self.rect.width - 4, self.rect.height - 72)
            if crect.collidepoint(event.pos):
                for btn, opt in self.buttons:
                    vbtn = btn.copy()
                    vbtn.y += self.scroll_y
                    if vbtn.collidepoint(event.pos):
                        if opt in lmap and lmap[opt] not in self.rm.unlocked_techs: return "HANDLED"
                        self.input_handler.set_build_mode(opt)
                        return "CLOSE"
                for chk, opt in self.checkboxes:
                    vchk = chk.copy()
                    vchk.y += self.scroll_y
                    if vchk.collidepoint(event.pos):
                        if opt in lmap and lmap[opt] not in self.rm.unlocked_techs: return "HANDLED"
                        if any(p["name"] == opt for p in self.rm.pinned_costs): 
                            self.rm.unpin_cost(opt)
                        else:
                            self.rm.pin_cost(opt, Building.get_cost(opt))
                            self.input_handler.set_build_mode(opt)
                        return "HANDLED"
        return None
