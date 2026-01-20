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
    def __init__(self, building, resource_manager, world, game):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 400, 350
        super().__init__(cx - w//2, cy - h//2, w, h, f"{building.type} (Lvl {building.level})")
        self.building = building
        self.rm = resource_manager
        self.world = world
        self.game = game
        
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
        
        # Calculate villagers inside (Assumed from tick logic requirements)
        needed = 3 * self.building.level
        # For display, we'll show current assignment vs needed
        # We need to peek into game logic or just show the requirement. 
        # Since villagers run around, let's show how many "slots" are filled.
        # We'll use a simple logic: if enough exist globally, they are "inside".
        
        total_v = self.game.entity_manager.get_count()
        # This is a bit complex without tracking individual building assignment,
        # so let's simplify to "Villagers: X/3" based on global availability.
        assigned = min(needed, total_v) 
        
        if self.building.type == "House":
            stats = f"Villagers: {self.building.villagers}"
        else:
            stats = f"{rtype}: {int(self.building.production_buffer)}"
            v_stats = f"Villagers: {assigned}/{needed}"
            v_surf = self.font.render(v_stats, True, BLACK)
            screen.blit(v_surf, (self.rect.x + 20, self.rect.y + 300))
            
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
        w, h = 300, 200
        super().__init__(cx - w//2, cy - h//2, w, h, "Inventory")
        self.rm = resource_manager

    def draw(self, screen):
        super().draw(screen)
        y_offset = 50
        for res, amount in self.rm.inventory.items():
            txt = f"{res.capitalize()}: {int(amount)}"
            surf = self.font.render(txt, True, BLACK)
            screen.blit(surf, (self.rect.x + 30, self.rect.y + y_offset))
            y_offset += 30

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
        if event.type == pygame.MOUSEBUTTONDOWN:
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
            if self.page == 1: # Point to Inventory
                pos = (self.hud.inventory_icon_rect.x + 40, self.hud.inventory_icon_rect.y + 8)
                # Rotate arrow to point left
                rotated = pygame.transform.rotate(arrow, 90)
                screen.blit(rotated, pos)
            elif self.page == 2: # Point to Building Tab
                pos = (self.hud.build_icon_rect.x + 40, self.hud.build_icon_rect.y + 8)
                rotated = pygame.transform.rotate(arrow, 90)
                screen.blit(rotated, pos)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
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
        if event.type == pygame.MOUSEBUTTONDOWN:
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
            self.options = ["Logging Workshop", "Stone Refinery", "Mine", "House", "Farm", "Garden", "Blast Furnace", "Rocket Ship"]
            
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
                        # Auto-select building for placement
                        self.input_handler.set_build_mode(opt)
                    return "HANDLED"
        return None
