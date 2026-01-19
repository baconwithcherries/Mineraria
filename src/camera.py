import pygame
from .config import *

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.world_width = width
        self.world_height = height
        self.zoom_level = 1.0
        
        # Center camera on the surface initially
        # Surface is at Y=50 * 16 = 800.
        # Center of screen is 720/2 = 360.
        # So offset_y should be around 440.
        self.offset_x = 0
        self.offset_y = (50 * TILE_SIZE) - (SCREEN_HEIGHT // 2)

    def apply(self, entity_rect):
        # Apply offset and zoom
        # This is for Rect-based entities or raw coordinates
        return entity_rect.move(-self.offset_x, -self.offset_y)

    def world_to_screen(self, world_x, world_y):
        screen_x = (world_x * TILE_SIZE - self.offset_x) * self.zoom_level
        screen_y = (world_y * TILE_SIZE - self.offset_y) * self.zoom_level
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x, screen_y):
        world_x = (screen_x / self.zoom_level + self.offset_x) / TILE_SIZE
        world_y = (screen_y / self.zoom_level + self.offset_y) / TILE_SIZE
        return world_x, world_y

    def update(self, target_x, target_y):
        # Optional: Follow a target
        pass

    def move(self, dx, dy):
        self.offset_x += dx
        self.offset_y += dy

    def drag(self, dx, dy):
        # Moving the camera in the direction of the drag means subtract the delta
        self.offset_x -= dx / self.zoom_level
        self.offset_y -= dy / self.zoom_level

    def set_zoom(self, change):
        self.zoom_level += change
        self.zoom_level = max(0.5, min(self.zoom_level, 3.0))
