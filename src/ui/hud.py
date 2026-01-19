import pygame
from ..config import *
from ..assets import Assets

class HUD:
    def __init__(self, resource_manager):
        self.rm = resource_manager
        self.font = pygame.font.SysFont("Arial", 16)
        
        # Placeholder Icons (Rects)
        self.build_icon_rect = pygame.Rect(10, 10, 32, 32)
        self.inventory_icon_rect = pygame.Rect(10, 50, 32, 32)
        self.code_btn_rect = pygame.Rect(10, SCREEN_HEIGHT - 40, 60, 30)

    def draw(self, screen):
        assets = Assets.get()
        
        # Update button position for resizing
        self.code_btn_rect.y = screen.get_height() - 40
        
        # Draw Icons (Top Left)
        # Build
        b_sprite = assets.get_sprite("icon_build")
        if b_sprite:
            screen.blit(b_sprite, self.build_icon_rect)
        else:
            pygame.draw.rect(screen, (200, 200, 200), self.build_icon_rect)
            b_text = self.font.render("B", True, BLACK)
            screen.blit(b_text, (18, 18))

        # Inventory
        i_sprite = assets.get_sprite("icon_inventory")
        if i_sprite:
            screen.blit(i_sprite, self.inventory_icon_rect)
        else:
            pygame.draw.rect(screen, (150, 100, 50), self.inventory_icon_rect)
            i_text = self.font.render("I", True, BLACK)
            screen.blit(i_text, (18, 58))

        # Draw Code Button (Bottom Left)
        pygame.draw.rect(screen, (100, 100, 100), self.code_btn_rect)
        pygame.draw.rect(screen, WHITE, self.code_btn_rect, 2)
        code_text = self.font.render("CODE", True, WHITE)
        screen.blit(code_text, (self.code_btn_rect.centerx - code_text.get_width()//2, self.code_btn_rect.centery - code_text.get_height()//2))

        # --- Resource List Hidden from Main HUD as per request ---

        # Top Right List Container (Pinned items ONLY)
        if self.rm.pinned_costs:
            list_rect = pygame.Rect(SCREEN_WIDTH - 200, 40, 190, 300)
            s = pygame.Surface((list_rect.width, list_rect.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 50)) 
            screen.blit(s, (list_rect.x, list_rect.y))
            
            title = self.font.render("Tasks", True, WHITE)
            screen.blit(title, (list_rect.x + 5, list_rect.y + 5))
            
            y_offset = 30
            for item in self.rm.pinned_costs:
                name = item["name"]
                cost = item["cost"]
                
                # Draw Name
                name_surf = self.font.render(name, True, WHITE)
                screen.blit(name_surf, (list_rect.x + 5, list_rect.y + y_offset))
                y_offset += 20
                
                # Draw Costs
                for res, amount in cost.items():
                    current = self.rm.inventory.get(res, 0)
                    color = (100, 255, 100) if current >= amount else (255, 100, 100)
                    txt = f" {res}: {current}/{amount}"
                    c_surf = self.font.render(txt, True, color)
                    screen.blit(c_surf, (list_rect.x + 10, list_rect.y + y_offset))
                    y_offset += 15
                
                y_offset += 5 # Spacer
                if y_offset > list_rect.height - 20:
                    break