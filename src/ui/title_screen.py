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
        
        # New Game Input
        self.world_name_input = ""

    def get_buttons(self):
        sw, sh = self.game.screen.get_size()
        return {
            "new": pygame.Rect(sw//2 - 100, sh//2 - 100, 200, 50),
            "load": pygame.Rect(sw//2 - 100, sh//2 - 30, 200, 50),
            "exit": pygame.Rect(sw//2 - 100, sh//2 + 40, 200, 50)
        }

    def get_size_buttons(self):
        sw, sh = self.game.screen.get_size()
        return {
            "Small": pygame.Rect(sw//2 - 150, sh//2 + 20, 90, 40),
            "Medium": pygame.Rect(sw//2 - 45, sh//2 + 20, 90, 40),
            "Large": pygame.Rect(sw//2 + 60, sh//2 + 20, 90, 40)
        }

    def handle_input(self, event):
        sw, sh = self.game.screen.get_size()
        if self.state == "MAIN":
            buttons = self.get_buttons()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons["new"].collidepoint(event.pos):
                    self.state = "NEW_NAME"
                elif buttons["load"].collidepoint(event.pos):
                    self.saves = self.game.save_manager.list_saves()
                    self.state = "LOAD"
                elif buttons["exit"].collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        elif self.state == "NEW_NAME":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "MAIN"
                elif event.key == pygame.K_RETURN and self.world_name_input:
                    self.state = "NEW_SIZE"
                elif event.key == pygame.K_BACKSPACE:
                    self.world_name_input = self.world_name_input[:-1]
                else:
                    if len(self.world_name_input) < 15 and event.unicode.isalnum():
                        self.world_name_input += event.unicode

        elif self.state == "NEW_SIZE":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "NEW_NAME"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for size, rect in self.get_size_buttons().items():
                    if rect.collidepoint(event.pos):
                        self.game.start_new_game(self.world_name_input, WORLD_SIZES[size])
        
        elif self.state == "LOAD":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "MAIN"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sw, sh = self.game.screen.get_size()
                for i, save in enumerate(self.saves):
                    rect = pygame.Rect(sw//2 - 150, sh//2 - 100 + i*45, 300, 40)
                    if rect.collidepoint(event.pos):
                        if self.game.save_manager.load_game(save):
                            self.game.state = STATE_GAME
                            self.game.assets.play_music("ambiente-mineraria.mp3")

    def draw(self, screen):
        sw, sh = screen.get_size()
        # Draw Background
        bg = Assets.get().get_sprite("title_bg")
        if bg:
            screen.blit(pygame.transform.scale(bg, (sw, sh)), (0, 0))
        else:
            screen.fill((50, 50, 100))

        # Title Overlay
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        if self.state == "MAIN":
            title = self.font_large.render("MINERARIA SURVIVAL", True, WHITE)
            screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 150))
            
            buttons = self.get_buttons()
            for key, rect in buttons.items():
                pygame.draw.rect(screen, (100, 100, 100), rect)
                pygame.draw.rect(screen, WHITE, rect, 2)
                txt = self.font_med.render(key.replace("_", " ").upper(), True, WHITE)
                screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

        elif self.state == "NEW_NAME":
            txt = self.font_med.render("Enter World Name:", True, WHITE)
            screen.blit(txt, (sw//2 - txt.get_width()//2, sh//2 - 50))
            
            input_rect = pygame.Rect(sw//2 - 150, sh//2, 300, 40)
            pygame.draw.rect(screen, WHITE, input_rect, 2)
            name_surf = self.font_med.render(self.world_name_input, True, WHITE)
            screen.blit(name_surf, (input_rect.x + 5, input_rect.y + 5))
            
            hint = self.font_small.render("Press Enter to continue", True, (200, 200, 200))
            screen.blit(hint, (sw//2 - hint.get_width()//2, sh//2 + 60))

        elif self.state == "NEW_SIZE":
            txt = self.font_med.render(f"Select Size for '{self.world_name_input}':", True, WHITE)
            screen.blit(txt, (sw//2 - txt.get_width()//2, sh//2 - 50))
            
            for size, rect in self.get_size_buttons().items():
                pygame.draw.rect(screen, (100, 100, 100), rect)
                pygame.draw.rect(screen, WHITE, rect, 2)
                stxt = self.font_small.render(size, True, WHITE)
                screen.blit(stxt, (rect.centerx - stxt.get_width()//2, rect.centery - stxt.get_height()//2))

        elif self.state == "LOAD":
            txt = self.font_med.render("Select a World to Load:", True, WHITE)
            screen.blit(txt, (sw//2 - txt.get_width()//2, sh//2 - 150))
            
            if not self.saves:
                err = self.font_small.render("No saves found", True, (200, 100, 100))
                screen.blit(err, (sw//2 - err.get_width()//2, sh//2))
            
            for i, save in enumerate(self.saves):
                rect = pygame.Rect(sw//2 - 150, sh//2 - 100 + i*45, 300, 40)
                pygame.draw.rect(screen, (80, 80, 80), rect)
                pygame.draw.rect(screen, WHITE, rect, 1)
                stxt = self.font_med.render(save, True, WHITE)
                screen.blit(stxt, (rect.centerx - stxt.get_width()//2, rect.centery - stxt.get_height()//2))
            
            hint = self.font_small.render("Press ESC to go back", True, (200, 200, 200))
            screen.blit(hint, (sw//2 - hint.get_width()//2, sh//2 + 200))
