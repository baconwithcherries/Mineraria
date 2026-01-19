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

    def handle_input(self, event):
        if self.active_window:
            return self.active_window.handle_input(event)
        return False # Not handled

    def draw(self, screen):
        for window in self.windows:
            window.draw(screen)
