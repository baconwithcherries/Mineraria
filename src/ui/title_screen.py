import pygame
import sys
from ..config import *
from ..assets import Assets

class TitleScreen:
    def __init__(self, game):
        self.game = game
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 24)
        self.font_small = pygame.font.SysFont("Arial", 18)
        
        self.state = "MAIN" # MAIN, NEW_NAME, NEW_SIZE, LOAD
        
        # Buttons
        self.buttons = {
            "new": pygame.Rect(SCREEN_WIDTH//2 - 100, 180, 200, 50),
            "exit": pygame.Rect(SCREEN_WIDTH//2 - 100, 260, 200, 50)
        }
        
        # New Game Input
        self.world_name_input = ""
        self.size_buttons = {
            "Small": pygame.Rect(SCREEN_WIDTH//2 - 150, 200, 90, 40),
            "Medium": pygame.Rect(SCREEN_WIDTH//2 - 45, 200, 90, 40),
            "Large": pygame.Rect(SCREEN_WIDTH//2 + 60, 200, 90, 40)
        }

    def handle_input(self, event):
        if self.state == "MAIN":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.buttons["new"].collidepoint(event.pos):
                    self.state = "NEW_NAME"
                elif self.buttons["exit"].collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        elif self.state == "NEW_NAME":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.world_name_input:
                    self.state = "NEW_SIZE"
                elif event.key == pygame.K_BACKSPACE:
                    self.world_name_input = self.world_name_input[:-1]
                else:
                    if len(self.world_name_input) < 15 and event.unicode.isalnum():
                        self.world_name_input += event.unicode

        elif self.state == "NEW_SIZE":
            if event.type == pygame.MOUSEBUTTONDOWN:
                for size, rect in self.size_buttons.items():
                    if rect.collidepoint(event.pos):
                        self.game.start_new_game(self.world_name_input, WORLD_SIZES[size])

        elif self.state == "LOAD":
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check list of saves
                for i, name in enumerate(self.saves):
                    rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 100 + i*40, 200, 30)
                    if rect.collidepoint(event.pos):
                        if self.game.save_manager.load_game(name):
                            self.game.state = STATE_GAME
                
                # Back button
                back_rect = pygame.Rect(10, 10, 60, 30)
                if back_rect.collidepoint(event.pos):
                    self.state = "MAIN"

    def draw(self, screen):
        # Draw Background
        bg = Assets.get().get_sprite("title_bg")
        if bg:
            # Scale to screen
            screen.blit(pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        else:
            screen.fill((50, 50, 100))

        # Title Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        if self.state == "MAIN":
            title = self.font_large.render("MINERARIA SURVIVAL", True, WHITE)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
            
            for key, rect in self.buttons.items():
                pygame.draw.rect(screen, (100, 100, 100), rect)
                pygame.draw.rect(screen, WHITE, rect, 2)
                txt = self.font_med.render(key.replace("_", " ").upper(), True, WHITE)
                screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

        elif self.state == "NEW_NAME":
            txt = self.font_med.render("Enter World Name:", True, WHITE)
            screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 150))
            
            input_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 200, 300, 40)
            pygame.draw.rect(screen, WHITE, input_rect, 2)
            name_surf = self.font_med.render(self.world_name_input, True, WHITE)
            screen.blit(name_surf, (input_rect.x + 5, input_rect.y + 5))
            
            hint = self.font_small.render("Press Enter to continue", True, (200, 200, 200))
            screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 260))

        elif self.state == "NEW_SIZE":
            txt = self.font_med.render(f"Select Size for '{self.world_name_input}':", True, WHITE)
            screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 150))
            
            for size, rect in self.size_buttons.items():
                pygame.draw.rect(screen, (100, 100, 100), rect)
                pygame.draw.rect(screen, WHITE, rect, 2)
                stxt = self.font_small.render(size, True, WHITE)
                screen.blit(stxt, (rect.centerx - stxt.get_width()//2, rect.centery - stxt.get_height()//2))

        elif self.state == "LOAD":
            txt = self.font_med.render("Select Save to Load:", True, WHITE)
            screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 50))
            
            for i, name in enumerate(self.saves):
                rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 100 + i*40, 200, 30)
                pygame.draw.rect(screen, (80, 80, 80), rect)
                stxt = self.font_small.render(name, True, WHITE)
                screen.blit(stxt, (rect.centerx - stxt.get_width()//2, rect.centery - stxt.get_height()//2))
            
            back_rect = pygame.Rect(10, 10, 60, 30)
            pygame.draw.rect(screen, (150, 50, 50), back_rect)
            btxt = self.font_small.render("BACK", True, WHITE)
            screen.blit(btxt, (back_rect.centerx - btxt.get_width()//2, back_rect.centery - btxt.get_height()//2))
