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
        self.last_place_time = 0
        self.place_cooldown = 250 # ms

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # ESC or Right Click to cancel build mode
        if self.build_mode_active:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE] or pygame.mouse.get_pressed()[2]:
                self.build_mode_active = False
                return

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
        self.last_place_time = pygame.time.get_ticks() # Prevent instant placement

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

        # Support check: Must be on solid ground (grass/dirt/stone) or a building
        has_support = False
        if below_tile.tile_type != "air":
            has_support = True
        if self.game.world.get_building_at(tx, ty + 1):
            has_support = True
            
        if not has_support:
            return False

        # Blast Furnace proximity check: within 10 blocks of a stone refinery
        if self.selected_building_type == "Blast Furnace":
            import math
            near_refinery = False
            for b in self.game.world.buildings.values():
                if b.type == "Stone Refinery":
                    dist = math.sqrt((tx - b.x)**2 + (ty - b.y)**2)
                    if dist <= 10:
                        near_refinery = True
                        break
            if not near_refinery:
                return False

        return True

    def try_place_building(self):
        now = pygame.time.get_ticks()
        if now - self.last_place_time < self.place_cooldown:
            return

        tx, ty = self.preview_x, self.preview_y
        
        if not self.is_placement_valid(tx, ty):
            return

        # 2. Check Resources
        cost = Building.get_cost(self.selected_building_type)
        if self.game.resource_manager.has_resources(cost):
            # 3. Deduct & Place
            if self.game.world.place_building(tx, ty, self.selected_building_type):
                self.game.resource_manager.deduct_resources(cost)
                self.last_place_time = now
                
                # Spawn Dust
                if hasattr(self.game, 'particle_manager'):
                    # Burst of particles
                    for _ in range(5):
                        self.game.particle_manager.spawn_particle(tx + 0.5, ty + 0.5, (101, 67, 33)) # Dirt Brown
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
