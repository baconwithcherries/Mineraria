import pygame
from ..config import *
from ..world import Building
from ..assets import Assets

class Window:
    def __init__(self, x, y, width, height, title):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.font = pygame.font.SysFont("Arial", 16)
        self.close_btn_rect = pygame.Rect(x + width - 20, y, 20, 20)

    def draw(self, screen):
        # Background
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Title
        title_surf = self.font.render(self.title, True, BLACK)
        screen.blit(title_surf, (self.rect.x + 5, self.rect.y + 5))
        
        # Close Button
        pygame.draw.rect(screen, (200, 50, 50), self.close_btn_rect)
        x_surf = self.font.render("X", True, WHITE)
        screen.blit(x_surf, (self.close_btn_rect.x + 5, self.close_btn_rect.y))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_btn_rect.collidepoint(event.pos):
                return "CLOSE"
        return None

class BuildingInspector(Window):
    def __init__(self, building, resource_manager, world):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 400, 350
        super().__init__(cx - w//2, cy - h//2, w, h, f"{building.type} (Lvl {building.level})")
        self.building = building
        self.rm = resource_manager
        self.world = world
        
        self.collect_btn = pygame.Rect(self.rect.x + 100, self.rect.y + 250, 200, 30)
        self.upgrade_btn = pygame.Rect(self.rect.x + 350, self.rect.y + 5, 20, 20)
        self.delete_btn = pygame.Rect(self.rect.x + self.rect.width - 40, self.rect.y + self.rect.height - 40, 30, 30)

    def draw(self, screen):
        super().draw(screen)
        
        # Stats
        rtype = "Resources"
        if self.building.type == "Logging Workshop": rtype = "Wood"
        elif self.building.type == "Stone Refinery": rtype = "Stone"
        elif self.building.type == "Mine": rtype = "Iron"
        
        stats = f"{rtype}: {int(self.building.production_buffer)}"
        if self.building.type == "House":
            stats = f"Villagers: {self.building.villagers}"
            
        text = self.font.render(stats, True, BLACK)
        screen.blit(text, (self.rect.x + 20, self.rect.y + 40))
        
        # Graph area
        graph_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 70, 360, 150)
        pygame.draw.rect(screen, (30, 30, 30), graph_rect)
        pygame.draw.rect(screen, BLACK, graph_rect, 1)
        
        # Draw dynamic graph
        history = self.building.production_history
        max_val = max(history) if max(history) > 0 else 1
        
        points = []
        for i, val in enumerate(history):
            x = graph_rect.x + (i * (graph_rect.width / (len(history) - 1)))
            y = graph_rect.y + graph_rect.height - (val / max_val * graph_rect.height)
            points.append((x, y))
            
        if len(points) > 1:
            pygame.draw.lines(screen, (0, 255, 0), False, points, 2)
        
        max_surf = self.font.render(str(round(max_val, 1)), True, (100, 100, 100))
        screen.blit(max_surf, (graph_rect.x + 5, graph_rect.y + 5))
        
        # Collect Button
        pygame.draw.rect(screen, (50, 200, 50), self.collect_btn)
        c_text = self.font.render("Collect", True, BLACK)
        screen.blit(c_text, (self.collect_btn.x + 75, self.collect_btn.y + 5))

        # Upgrade Icon
        assets = Assets.get()
        arrow = assets.get_sprite("icon_arrow_up")
        
        pygame.draw.rect(screen, (100, 100, 255), self.upgrade_btn)
        if arrow:
            dest = (self.upgrade_btn.x + 2, self.upgrade_btn.y + 2)
            screen.blit(arrow, dest)
            
        # Delete Button (Trash Can)
        pygame.draw.rect(screen, (200, 50, 50), self.delete_btn)
        trash_text = self.font.render("DEL", True, WHITE) # Placeholder for trash icon
        screen.blit(trash_text, (self.delete_btn.x + 2, self.delete_btn.y + 5))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.collect_btn.collidepoint(event.pos):
                if self.building.production_buffer >= 1:
                    rtype = ""
                    if self.building.type == "Logging Workshop": rtype = "wood"
                    elif self.building.type == "Stone Refinery": rtype = "stone"
                    elif self.building.type == "Mine": rtype = "iron"
                    
                    if rtype:
                        amount = int(self.building.production_buffer)
                        self.rm.add_resource(rtype, amount)
                        self.building.production_buffer -= amount
                return "HANDLED"
            
            if self.upgrade_btn.collidepoint(event.pos):
                if self.building.level < 25:
                    cost = self.building.get_upgrade_cost()
                    if self.rm.has_resources(cost):
                        self.rm.deduct_resources(cost)
                        self.building.level += 1
                        self.title = f"{self.building.type} (Lvl {self.building.level})"
                return "HANDLED"
                
            if self.delete_btn.collidepoint(event.pos):
                # Delete Building and Refund
                cost = Building.get_cost(self.building.type)
                for res, amount in cost.items():
                    self.rm.add_resource(res, amount)
                self.world.buildings.pop((self.building.x, self.building.y))
                return "CLOSE"
        return None

class InventoryWindow(Window):
    def __init__(self, resource_manager):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        super().__init__(cx - 150, cy - 100, 300, 200, "Inventory")
        self.rm = resource_manager

    def draw(self, screen):
        super().draw(screen)
        y = self.rect.y + 40
        for res, amount in self.rm.inventory.items():
            txt = f"{res.capitalize()}: {int(amount)}"
            surf = self.font.render(txt, True, BLACK)
            screen.blit(surf, (self.rect.x + 20, y))
            y += 30

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
                if self.rm.code_used:
                    self.message = "Code already used!"
                elif self.input_text == "baconwithcherries":
                    for res in ["wood", "stone", "iron"]:
                        self.rm.add_resource(res, 1500)
                    self.rm.code_used = True
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
        if event.type == pygame.MOUSEBUTTONDOWN:
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
            bt1 = self.font.render(f"Board 1 (10 all)", True, WHITE)
            screen.blit(bt1, (self.board_one_btn.centerx - bt1.get_width()//2, self.board_one_btn.centery - bt1.get_height()//2))
            
            # Board All
            pygame.draw.rect(screen, (80, 80, 200), self.board_all_btn)
            bt2 = self.font.render(f"Board All ({remaining * 10} all)", True, WHITE)
            screen.blit(bt2, (self.board_all_btn.centerx - bt2.get_width()//2, self.board_all_btn.centery - bt2.get_height()//2))
        
        if self.building.boarded_population >= total_pop and total_pop > 0:
            pygame.draw.rect(screen, (255, 50, 50), self.launch_btn)
            lt = self.font.render("LAUNCH ROCKET", True, WHITE)
            screen.blit(lt, (self.launch_btn.centerx - lt.get_width()//2, self.launch_btn.centery - lt.get_height()//2))

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            total_pop = self.em.get_count()
            remaining = total_pop - self.building.boarded_population
            
            # Board One
            if self.board_one_btn.collidepoint(event.pos) and remaining > 0:
                cost = {"wood": 10, "stone": 10, "iron": 10}
                if self.rm.has_resources(cost):
                    self.rm.deduct_resources(cost)
                    self.building.boarded_population += 1
            
            # Board All
            if self.board_all_btn.collidepoint(event.pos) and remaining > 0:
                cost = {"wood": remaining * 10, "stone": remaining * 10, "iron": remaining * 10}
                if self.rm.has_resources(cost):
                    self.rm.deduct_resources(cost)
                    self.building.boarded_population = total_pop
            
            # Launch
            if self.launch_btn.collidepoint(event.pos):
                if self.building.boarded_population >= total_pop and total_pop > 0:
                    self.building.is_launching = True
                    return "CLOSE"
        return None

class BuildingTab(Window):
    def __init__(self, input_handler, resource_manager, world):
        super().__init__(50, 50, 300, 400, "Construction")
        self.input_handler = input_handler
        self.rm = resource_manager
        self.world = world
        
        # Progression logic: Only show House first.
        if self.world.has_house():
            self.options = ["Logging Workshop", "Stone Refinery", "Mine", "House", "Rocket Ship"]
        else:
            self.options = ["House"]
            
        self.buttons = []
        self.checkboxes = []
        
        for i, opt in enumerate(self.options):
            y_pos = self.rect.y + 40 + (i * 50)
            btn = pygame.Rect(self.rect.x + 10, y_pos, 240, 40)
            chk = pygame.Rect(self.rect.x + 260, y_pos + 10, 20, 20)
            self.buttons.append((btn, opt))
            self.checkboxes.append((chk, opt))

    def draw(self, screen):
        super().draw(screen)
        for btn, opt in self.buttons:
            pygame.draw.rect(screen, (220, 220, 220), btn)
            text = self.font.render(opt, True, BLACK)
            screen.blit(text, (btn.x + 10, btn.y + 10))
            
        for chk, opt in self.checkboxes:
            pygame.draw.rect(screen, WHITE, chk)
            pygame.draw.rect(screen, BLACK, chk, 1)
            # Check if pinned (naive check by name)
            is_pinned = any(p["name"] == opt for p in self.rm.pinned_costs)
            if is_pinned:
                pygame.draw.line(screen, BLACK, (chk.x, chk.y), (chk.x + 20, chk.y + 20), 2)
                pygame.draw.line(screen, BLACK, (chk.x + 20, chk.y), (chk.x, chk.y + 20), 2)

    def handle_input(self, event):
        res = super().handle_input(event)
        if res == "CLOSE": return "CLOSE"
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn, opt in self.buttons:
                if btn.collidepoint(event.pos):
                    self.input_handler.set_build_mode(opt)
                    return "CLOSE"
            
            for chk, opt in self.checkboxes:
                if chk.collidepoint(event.pos):
                    is_pinned = any(p["name"] == opt for p in self.rm.pinned_costs)
                    if is_pinned:
                        self.rm.unpin_cost(opt)
                    else:
                        cost = Building.get_cost(opt)
                        self.rm.pin_cost(opt, cost)
                    return "HANDLED"
        return None
