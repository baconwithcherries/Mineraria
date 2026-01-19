import pygame
from .config import *
from .world import Building
from .assets import Assets

class InputHandler:
    def __init__(self, game):
        self.game = game
        self.build_mode_active = False
        self.selected_building_type = None
        self.preview_x = 0
        self.preview_y = 0

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        
        # --- Toggle Build Mode (Debug/Temp) ---
        # 1: Logging, 2: Stone, 3: Mine, 4: House
        if keys[pygame.K_1]:
            self.set_build_mode("Logging Workshop")
        elif keys[pygame.K_2]:
            self.set_build_mode("Stone Refinery")
        elif keys[pygame.K_3]:
            self.set_build_mode("Mine")
        elif keys[pygame.K_4]:
            self.set_build_mode("House")
        elif keys[pygame.K_ESCAPE]:
            self.build_mode_active = False

        # --- Mouse Interaction ---
        if self.build_mode_active:
            # Convert screen to world
            world_x_float, world_y_float = self.game.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
            self.preview_x = int(world_x_float)
            self.preview_y = int(world_y_float)

            # Click to Place
            if pygame.mouse.get_pressed()[0]: # Left Click
                self.try_place_building()

    def set_build_mode(self, b_type):
        self.build_mode_active = True
        self.selected_building_type = b_type
        # Debounce or wait for release could be good, but simple for now.

    def is_placement_valid(self, tx, ty):
        target_tile = self.game.world.get_tile(tx, ty)
        below_tile = self.game.world.get_tile(tx, ty + 1)
        
        if not target_tile or not below_tile:
            return False

        # Must be AIR at target
        if target_tile.tile_type != "air":
            return False
            
        # Space cannot be occupied by another building
        if self.game.world.get_building_at(tx, ty):
            return False

        # Surface check: SURFACE_LEVEL is 50. Placement at < 50 is above ground.
        # ty=49 is directly on top of y=50 (surface).
        if ty >= 50:
            return False # Cannot place "under" the surface level

        # Support check: Must be on solid ground (grass/dirt/stone) or a building
        has_support = False
        if below_tile.tile_type != "air":
            has_support = True
        if self.game.world.get_building_at(tx, ty + 1):
            has_support = True
            
        return has_support

    def try_place_building(self):
        tx, ty = self.preview_x, self.preview_y
        
        if not self.is_placement_valid(tx, ty):
            return

        # 2. Check Resources
        cost = Building.get_cost(self.selected_building_type)
        if self.game.resource_manager.has_resources(cost):
            # 3. Deduct & Place
            self.game.resource_manager.deduct_resources(cost)
            self.game.world.place_building(tx, ty, self.selected_building_type)
            # Stop silhouette immediately after successful placement
            self.build_mode_active = False
            pygame.time.wait(200) 

    def draw_preview(self, screen):
        if self.build_mode_active:
            screen_x, screen_y = self.game.camera.world_to_screen(self.preview_x, self.preview_y)
            size = TILE_SIZE * self.game.camera.zoom_level
            
            rect = pygame.Rect(int(screen_x), int(screen_y), int(size), int(size))
            
            # Check validity for color
            is_valid = self.is_placement_valid(self.preview_x, self.preview_y)
            
            # Get Sprite from Assets
            assets = Assets.get()
            sprite = assets.get_sprite(self.selected_building_type)
            
            if sprite:
                scaled = pygame.transform.scale(sprite, (int(size), int(size)))
                ghost = scaled.copy()
                
                # If invalid, tint red. Otherwise use white multiplier for transparency.
                tint_color = (255, 100, 100, 128) if not is_valid else (255, 255, 255, 128)
                ghost.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(ghost, (rect.x, rect.y))
            else:
                s = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
                color = (255, 0, 0, 128) if not is_valid else (128, 128, 128, 128)
                s.fill(color) 
                screen.blit(s, (rect.x, rect.y))
