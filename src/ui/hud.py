import pygame
from ..config import *
from ..assets import Assets

class HUD:
    def __init__(self, game):
        self.game = game
        self.rm = game.resource_manager
        self.font = pygame.font.SysFont("Arial", 16)
        
        # Icons (Top Left)
        self.build_icon_rect = pygame.Rect(10, 10, 32, 32)
        self.jobs_icon_rect = pygame.Rect(10, 50, 32, 32)
        self.speed_btn_rect = pygame.Rect(10, 90, 32, 32)
        
        # New Inventory List Position (Bottom Right)
        self.inventory_panel_rect = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 220, 190, 210)
        self.code_btn_rect = pygame.Rect(10, SCREEN_HEIGHT - 40, 60, 30)

    def draw(self, screen):
        assets = Assets.get()
        
        # Update button position for resizing
        self.code_btn_rect.y = screen.get_height() - 40
        self.inventory_panel_rect.x = screen.get_width() - 200
        self.inventory_panel_rect.y = screen.get_height() - 220
        
        # Helper for icon background
        def draw_icon_bg(rect):
            pygame.draw.rect(screen, (210, 180, 140), rect, border_radius=5)
            pygame.draw.rect(screen, (60, 40, 30), rect, 2, border_radius=5)

        # Draw Icons (Top Left)
        # Build
        draw_icon_bg(self.build_icon_rect)
        b_sprite = assets.get_sprite("icon_build")
        if b_sprite:
            screen.blit(b_sprite, self.build_icon_rect)
        else:
            b_text = self.font.render("B", True, (60, 40, 30))
            screen.blit(b_text, (18, 18))

        # Jobs
        draw_icon_bg(self.jobs_icon_rect)
        v_sprite = assets.get_sprite("villager")
        if v_sprite:
            scaled = pygame.transform.scale(v_sprite, (32, 32))
            screen.blit(scaled, self.jobs_icon_rect)
        else:
            j_text = self.font.render("J", True, (60, 40, 30))
            screen.blit(j_text, (self.jobs_icon_rect.centerx - j_text.get_width()//2, self.jobs_icon_rect.centery - j_text.get_height()//2))

        # Speed Toggle
        draw_icon_bg(self.speed_btn_rect)
        speed_val = self.game.tick_manager.time_scale
        s_text = self.font.render(f"{speed_val}x", True, (60, 40, 30))
        screen.blit(s_text, (self.speed_btn_rect.centerx - s_text.get_width()//2, self.speed_btn_rect.centery - s_text.get_height()//2))

        # Persistent Inventory (Bottom Right)
        pygame.draw.rect(screen, (100, 110, 130), self.inventory_panel_rect, border_radius=10)
        pygame.draw.rect(screen, (60, 40, 30), self.inventory_panel_rect, 2, border_radius=10)
        
        inv_title = self.font.render("Inventory", True, WHITE)
        screen.blit(inv_title, (self.inventory_panel_rect.x + 10, self.inventory_panel_rect.y + 10))
        
        y_off = 35
        for res, amount in self.rm.inventory.items():
            if amount > 0 or res in ["wood", "stone", "iron", "food"]: # Show core items or items player has
                txt = f"{res.capitalize()}: {int(amount)}"
                surf = self.font.render(txt, True, WHITE)
                screen.blit(surf, (self.inventory_panel_rect.x + 15, self.inventory_panel_rect.y + y_off))
                y_off += 18
                if y_off > self.inventory_panel_rect.height - 20: break

        # Draw Code Button (Bottom Left)
        pygame.draw.rect(screen, (160, 110, 80), self.code_btn_rect, border_radius=5)
        pygame.draw.rect(screen, (60, 40, 30), self.code_btn_rect, 2, border_radius=5)
        code_text = self.font.render("CODE", True, WHITE)
        screen.blit(code_text, (self.code_btn_rect.centerx - code_text.get_width()//2, self.code_btn_rect.centery - code_text.get_height()//2))

        # Day Counter (Top Middle)
        day_text = f"Day {self.game.tick_manager.day_counter}"
        d_surf = self.font.render(day_text, True, WHITE)
        screen.blit(d_surf, (screen.get_width()//2 - d_surf.get_width()//2, 10))

        # Villager Counter
        v_count = self.game.entity_manager.get_count()
        
        # We don't really have a single "needed" number anymore since priorities are global and can be "Max".
        # Just show count.
        v_text = f"Villagers: {v_count}"
        v_surf = self.font.render(v_text, True, WHITE)
        screen.blit(v_surf, (screen.get_width()//2 - v_surf.get_width()//2, 30))

        # --- Resource List Hidden from Main HUD as per request ---

        # Top Right List Container (Pinned items ONLY)
        if self.rm.pinned_costs:
            list_rect = pygame.Rect(screen.get_width() - 200, 40, 190, 300)
            
            # Draw Panel Background (Slate Grey/Blue)
            pygame.draw.rect(screen, (100, 110, 130), list_rect, border_radius=10)
            pygame.draw.rect(screen, (60, 40, 30), list_rect, 2, border_radius=10)
            
            title = self.font.render("Tasks", True, WHITE)
            screen.blit(title, (list_rect.x + 10, list_rect.y + 10))
            
            y_offset = 35
            for item in self.rm.pinned_costs:
                name = item["name"]
                cost = item["cost"]
                
                # Draw Name
                name_surf = self.font.render(name, True, WHITE)
                screen.blit(name_surf, (list_rect.x + 10, list_rect.y + y_offset))
                y_offset += 20
                
                # Draw Costs
                for res, amount in cost.items():
                    current = self.rm.inventory.get(res, 0)
                    color = (150, 255, 150) if current >= amount else (255, 150, 150)
                    txt = f" {res}: {current}/{amount}"
                    c_surf = self.font.render(txt, True, color)
                    screen.blit(c_surf, (list_rect.x + 15, list_rect.y + y_offset))
                    y_offset += 15
                
                y_offset += 5 # Spacer
                if y_offset > list_rect.height - 20:
                    break

            # Draw Food Status under the list
            # Background for stats
            stat_bg = pygame.Rect(list_rect.x, list_rect.bottom + 5, list_rect.width, 60)
            pygame.draw.rect(screen, (100, 110, 130), stat_bg, border_radius=10)
            pygame.draw.rect(screen, (60, 40, 30), stat_bg, 2, border_radius=10)

            food_val = int(self.rm.inventory.get("food", 0))
            eff_val = int(self.rm.food_efficiency * 100)
            
            # Food Icon (Small red circle placeholder)
            pygame.draw.circle(screen, (255, 80, 80), (stat_bg.x + 15, stat_bg.y + 20), 6)
            
            food_txt = f" {food_val}"
            if eff_val < 100:
                food_txt += f" (Eff: {eff_val}%)"
            
            f_surf = self.font.render(food_txt, True, WHITE)
            screen.blit(f_surf, (stat_bg.x + 25, stat_bg.y + 10))
            
            h_txt = f"Happiness: {int(self.rm.happiness)}%"
            h_surf = self.font.render(h_txt, True, WHITE)
            screen.blit(h_surf, (stat_bg.x + 10, stat_bg.y + 35))