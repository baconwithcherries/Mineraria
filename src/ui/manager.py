import pygame

class UIManager:
    def __init__(self, game):
        self.game = game
        self.windows = [] # Stack of active windows
        self.active_window = None

    def open_window(self, window):
        self.windows.append(window)
        self.active_window = window

    def close_window(self, window):
        if window in self.windows:
            self.windows.remove(window)
            if self.windows:
                self.active_window = self.windows[-1]
            else:
                self.active_window = None

    def draw_tooltip(self, screen, text, pos):
        font = pygame.font.SysFont("Arial", 14)
        surf = font.render(text, True, (255, 255, 255))
        padding = 4
        rect = pygame.Rect(pos[0], pos[1] - 25, surf.get_width() + padding*2, surf.get_height() + padding*2)
        
        # Clamp to screen
        if rect.right > screen.get_width(): rect.right = screen.get_width()
        if rect.top < 0: rect.top = 0
        
        pygame.draw.rect(screen, (50, 50, 50), rect, border_radius=4)
        pygame.draw.rect(screen, (200, 200, 200), rect, 1, border_radius=4)
        screen.blit(surf, (rect.x + padding, rect.y + padding))

    def handle_input(self, event):
        if self.active_window:
            return self.active_window.handle_input(event)
        return False # Not handled

    def draw(self, screen):
        for window in self.windows:
            window.draw(screen)
