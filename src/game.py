import pygame
import sys
from .config import *
from .world import World, Building
from .camera import Camera
from .resources import ResourceManager
from .ui.hud import HUD
from .ui.manager import UIManager
from .ui.windows import BuildingInspector, BuildingTab, InventoryWindow, RocketWindow, EndGameWindow, CodeWindow, TutorialPrompt, TutorialWindow, ExitConfirmationWindow, BlastFurnaceInspector, WorkerAssignmentWindow, ResearchWindow
from .ui.title_screen import TitleScreen
from .input_handler import InputHandler
from .entities import EntityManager
from .tick_manager import TickManager
from .save_manager import SaveManager
from .assets import Assets
from .particles import ParticleManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # State
        self.state = STATE_TITLE
        self.world_name = None
        self.is_completed = False
        self.game_time = 0 # In seconds
        self.last_minute_tick = 0
        
        # Managers
        self.assets = Assets.get()
        self.save_manager = SaveManager(self)
        self.title_screen = TitleScreen(self)
        self.particle_manager = ParticleManager()
        
        # World/Gameplay objects
        self.world = None
        self.camera = None
        self.resource_manager = None
        self.hud = None
        self.ui_manager = None
        self.input_handler = None
        self.entity_manager = None
        self.tick_manager = None
        
        # Interaction state
        self.is_dragging = False
        self.last_mouse_pos = (0, 0)
        
        # Initial Music
        self.assets.play_music("ambiente-mineraria.mp3")

    def init_managers(self):
        if self.resource_manager is None:
            self.resource_manager = ResourceManager()
        if self.hud is None:
            self.hud = HUD(self)
        if self.ui_manager is None:
            self.ui_manager = UIManager(self)
        if self.input_handler is None:
            self.input_handler = InputHandler(self)
        if self.entity_manager is None:
            self.entity_manager = EntityManager(self)
        if self.tick_manager is None:
            self.tick_manager = TickManager(self)

    def start_new_game(self, name, width):
        self.world_name = name
        self.is_completed = False
        self.world = World(width)
        self.camera = Camera(width * TILE_SIZE, WORLD_HEIGHT * TILE_SIZE)
        
        # Camera Center and Zoom
        self.camera.zoom_level = 2.0
        self.camera.offset_x = (width * TILE_SIZE) // 2 - (SCREEN_WIDTH // 4)
        
        # Fresh managers for new game
        self.resource_manager = ResourceManager()
        self.hud = HUD(self)
        self.ui_manager = UIManager(self)
        self.input_handler = InputHandler(self)
        self.entity_manager = EntityManager(self)
        self.tick_manager = TickManager(self)
        
        self.state = STATE_GAME
        
        # Music Transition
        self.assets.play_music("ambiente-mineraria.mp3")
        
        self.ui_manager.open_window(TutorialPrompt())

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.state == STATE_GAME:
                    self.save_manager.save_game()
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                global SCREEN_WIDTH, SCREEN_HEIGHT
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()

            if self.state == STATE_TITLE:
                self.title_screen.handle_input(event)
            else:
                self.handle_game_events(event)

    def handle_game_events(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.camera.set_zoom(event.y * 0.1)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Priority 1: HUD buttons
            if self.hud.build_icon_rect.collidepoint(event.pos):
                self.input_handler.build_mode_active = False
                self.ui_manager.windows = []
                self.ui_manager.open_window(BuildingTab(self.input_handler, self.resource_manager, self.world))
                return
            elif self.hud.inventory_icon_rect.collidepoint(event.pos):
                self.ui_manager.windows = []
                self.ui_manager.open_window(InventoryWindow(self.resource_manager))
                return
            elif self.hud.jobs_icon_rect.collidepoint(event.pos):
                self.ui_manager.windows = []
                self.ui_manager.open_window(WorkerAssignmentWindow(self.resource_manager, self.world))
                return
            elif self.hud.speed_btn_rect.collidepoint(event.pos):
                if self.tick_manager.time_scale == 1:
                    self.tick_manager.time_scale = 10
                else:
                    self.tick_manager.time_scale = 1
                return
            elif self.hud.code_btn_rect.collidepoint(event.pos):
                self.ui_manager.windows = []
                self.ui_manager.open_window(CodeWindow(self.resource_manager))
                return
            elif self.hud.exit_btn_rect.collidepoint(event.pos):
                self.ui_manager.windows = []
                self.ui_manager.active_window = None
                self.ui_manager.open_window(ExitConfirmationWindow())
                return
            
            # Priority 2: Right-click building switching
            if event.button == 3:
                wx, wy = self.camera.screen_to_world(event.pos[0], event.pos[1])
                ix, iy = int(wx), int(wy)
                building = self.world.get_building_at(ix, iy)
                if building:
                    self.input_handler.build_mode_active = False
                    self.ui_manager.windows = [] # Clear existing windows
                    if building.type == "Rocket Ship":
                        self.ui_manager.open_window(RocketWindow(building, self.resource_manager, self.entity_manager, self))
                    elif building.type == "Blast Furnace":
                        self.ui_manager.open_window(BlastFurnaceInspector(building, self.resource_manager, self.world, self))
                    elif building.type == "Laboratory":
                        self.ui_manager.open_window(ResearchWindow(self.resource_manager))
                    else:
                        self.ui_manager.open_window(BuildingInspector(building, self.resource_manager, self.world, self))
                    return

            if event.button == 1:
                if not self.ui_manager.active_window and not self.hud.build_icon_rect.collidepoint(event.pos) and not self.input_handler.build_mode_active and not self.hud.inventory_icon_rect.collidepoint(event.pos):
                    self.is_dragging = True
                    self.last_mouse_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                self.camera.drag(dx, dy)
                self.last_mouse_pos = event.pos

        if self.ui_manager.active_window:
            res = self.ui_manager.handle_input(event)
            if res == "CLOSE":
                self.ui_manager.close_window(self.ui_manager.active_window)
            elif res == "SAVE_EXIT":
                self.save_manager.save_game()
                self.state = STATE_TITLE
                self.title_screen.state = "MAIN"
                self.title_screen.world_name_input = ""
                self.assets.play_music("ambiente-mineraria.mp3")
                self.ui_manager.windows = []
                self.ui_manager.active_window = None
            elif res == "NO_SAVE_EXIT":
                self.state = STATE_TITLE
                self.title_screen.state = "MAIN"
                self.title_screen.world_name_input = ""
                self.assets.play_music("ambiente-mineraria.mp3")
                self.ui_manager.windows = []
                self.ui_manager.active_window = None
            elif res == "GAME_OVER_EXIT":
                self.is_completed = True
                self.save_manager.save_game()
                self.state = STATE_TITLE
                self.title_screen.state = "MAIN"
                self.title_screen.world_name_input = ""
                self.assets.play_music("ambiente-mineraria.mp3")
                self.ui_manager.windows = []
                self.ui_manager.active_window = None
            elif res == "START_TUTORIAL":
                self.ui_manager.close_window(self.ui_manager.active_window)
                self.ui_manager.open_window(TutorialWindow(self.hud))
            return

        if not self.ui_manager.active_window and not self.is_completed:
            self.input_handler.handle_input()

    def update(self):
        if self.state == STATE_GAME:
            self.tick_manager.update()
            self.entity_manager.update()
            self.particle_manager.update()
            
            # Time tracking for food mechanics
            self.game_time += self.clock.get_time() / 1000.0
            current_minute = int(self.game_time / 60)
            if current_minute > self.last_minute_tick:
                # Every new minute
                self.last_minute_tick = current_minute
                if current_minute > 3:
                    # Only drop production efficiency if OUT of food
                    if self.resource_manager.inventory.get("food", 0) <= 0:
                        self.resource_manager.food_efficiency = max(0.0, self.resource_manager.food_efficiency - 0.05)
                    else:
                        # Optional: recover efficiency if fed? 
                        # Let's keep it at current level or slowly recover to 1.0
                        self.resource_manager.food_efficiency = min(1.0, self.resource_manager.food_efficiency + 0.05)
            
            # Launch Logic
            for b in self.world.buildings.values():
                if b.type == "Rocket Ship" and b.is_launching:
                    b.launch_y_offset += 2
                    if b.launch_y_offset > 300 and not b.game_over_triggered:
                        b.game_over_triggered = True
                        self.ui_manager.open_window(EndGameWindow())

    def draw(self):
        if self.state == STATE_TITLE:
            self.title_screen.draw(self.screen)
        else:
            self.draw_game()
        pygame.display.flip()

    def draw_game(self):
        sky_color = SKY_BLUE if self.tick_manager.is_day() else (10, 10, 50)
        self.screen.fill(sky_color)
        
        cloud_sprite = self.assets.get_sprite("cloud")
        if cloud_sprite:
            for i in range(5):
                cx = (i * 400 - self.camera.offset_x * 0.3) % (SCREEN_WIDTH + 100) - 50
                cy = 100 + (i * 50) % 200
                self.screen.blit(cloud_sprite, (cx, cy))
        
        start_col = int(self.camera.offset_x / TILE_SIZE)
        end_col = int((self.camera.offset_x + SCREEN_WIDTH / self.camera.zoom_level) / TILE_SIZE) + 1
        start_row = int(self.camera.offset_y / TILE_SIZE)
        end_row = int((self.camera.offset_y + SCREEN_HEIGHT / self.camera.zoom_level) / TILE_SIZE) + 1

        start_col, end_col = max(0, start_col), min(self.world.width, end_col)
        start_row, end_row = max(0, start_row), min(self.world.height, end_row)

        for x in range(start_col, end_col):
            for y in range(start_row, end_row):
                tile = self.world.get_tile(x, y)
                screen_x, screen_y = self.camera.world_to_screen(x, y)
                size = TILE_SIZE * self.camera.zoom_level
                rect = pygame.Rect(int(screen_x), int(screen_y), int(size) + 1, int(size) + 1)
                
                if tile and tile.tile_type != "air":
                    sprite = self.assets.get_sprite(tile.tile_type)
                    if sprite:
                        scaled = pygame.transform.scale(sprite, (int(size) + 1, int(size) + 1))
                        self.screen.blit(scaled, rect)
                
                building = self.world.get_building_at(x, y)
                if building:
                    sprite = self.assets.get_sprite(building.type)
                    draw_y = rect.y
                    if building.type == "Rocket Ship" and building.is_launching:
                        draw_y -= building.launch_y_offset
                        # Draw Flames
                        flame_rect = pygame.Rect(rect.x + rect.width//4, draw_y + rect.height, rect.width//2, rect.height//2)
                        import random
                        f_color = random.choice([(255, 100, 0), (255, 200, 0), (255, 50, 0)])
                        pygame.draw.ellipse(self.screen, f_color, flame_rect)

                    if sprite:
                         scaled = pygame.transform.scale(sprite, (int(size) + 1, int(size) + 1))
                         self.screen.blit(scaled, (rect.x, draw_y))
                    else:
                        # Fallback for buildings without sprites
                        pygame.draw.rect(self.screen, Building.get_color(building.type), (rect.x, draw_y, rect.width, rect.height))

        for villager in self.entity_manager.villagers:
            if villager.state == "WORKING":
                continue

            screen_x, screen_y = self.camera.world_to_screen(villager.x, villager.y)
            size = TILE_SIZE * self.camera.zoom_level
            v_size = size * 0.8
            sprite = self.assets.get_sprite("villager")
            if sprite:
                scaled = pygame.transform.scale(sprite, (int(v_size), int(v_size)))
                
                # Shirt color based on job
                job_colors = {
                    "Logging Workshop": (139, 69, 19), # Brown
                    "Stone Refinery": (50, 50, 255),   # Blue
                    "Blast Furnace": (128, 0, 128),    # Purple
                    "Mine": (20, 20, 20),              # Black
                    "Farm": (34, 139, 34)              # Green
                }
                color = job_colors.get(villager.job, (255, 255, 255)) # Default white
                
                # Create a colored version of the sprite (tinting the shirt area)
                # Since the whole sprite is small, we tint the whole thing or just a part.
                # For simplicity, we'll tint the whole sprite using BLEND_RGB_MULT
                tinted = scaled.copy()
                tinted.fill(color, special_flags=pygame.BLEND_RGB_MULT);
                
                dest = (int(screen_x + (size-v_size)/2), int(screen_y + (size-v_size)))
                self.screen.blit(tinted, dest)
                
                # Draw Hats
                hat_color = None
                if villager.job == "Farm": hat_color = (200, 200, 100) # Straw Hat
                elif villager.job == "Mine": hat_color = (255, 255, 0) # Hard Hat
                elif villager.job == "Logging Workshop": hat_color = (139, 69, 19) # Beanie
                elif villager.job == "Blast Furnace": hat_color = (50, 50, 50) # Dark Helmet
                
                if hat_color:
                    hat_rect = pygame.Rect(dest[0], dest[1], v_size, v_size // 4)
                    pygame.draw.rect(self.screen, hat_color, hat_rect)

        self.particle_manager.draw(self.screen, self.camera)

        # --- Dynamic Lighting ---
        # Calculate darkness: 0 (Day) -> 150 (Night)
        # Cycle: 0-600 Day, 600-1200 Night
        time = self.tick_manager.current_time
        max_alpha = 180
        if time < 500: # Day
            alpha = 0
        elif time < 600: # Sunset
            alpha = int(((time - 500) / 100) * max_alpha)
        elif time < 1100: # Night
            alpha = max_alpha
        else: # Sunrise
            alpha = int(((1200 - time) / 100) * max_alpha)
            
        if alpha > 0:
            lighting = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            lighting.fill((0, 0, 20, alpha)) # Dark Blue tint
            
            # Draw Lights (Glows)
            # Iterate visible buildings to add lights
            for x in range(start_col, end_col):
                for y in range(start_row, end_row):
                    building = self.world.get_building_at(x, y)
                    if building and building.type in ["House", "Blast Furnace", "Stone Refinery"]:
                        screen_x, screen_y = self.camera.world_to_screen(x, y)
                        size = TILE_SIZE * self.camera.zoom_level
                        
                        # Create a glow circle
                        radius = int(size * 1.5)
                        glow = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                        
                        # Warm yellow/orange light
                        glow_color = (255, 200, 100, 100) # Semi-transparent
                        pygame.draw.circle(glow, glow_color, (radius, radius), radius)
                        
                        # "Cut out" the darkness using ADD blend mode which brightens the underlying layers
                        # Actually, better approach for 2D lighting overlay:
                        # Draw transparency on the darkness layer using BLEND_RGBA_SUB (subtract alpha)
                        # Or simple approach: draw glow ON TOP of darkness with ADD.
                        
                        # Let's draw glow on lighting surf using BLEND_RGBA_SUB to make it transparent
                        # pygame.draw.circle(lighting, (0, 0, 0, 0), ...) doesn't work easily with fill.
                        
                        # Alternative: Blit special light sprites with BLEND_RGBA_MIN or similar? 
                        # Easiest readable way: Draw the lighting surface, then draw additive lights on top.
                        pass # Done in next loop for batching or just here
            
            self.screen.blit(lighting, (0, 0))
            
            # Additive Lights Pass
            for x in range(start_col, end_col):
                for y in range(start_row, end_row):
                    building = self.world.get_building_at(x, y)
                    if building and building.type in ["House", "Blast Furnace"]:
                        screen_x, screen_y = self.camera.world_to_screen(x, y)
                        size = TILE_SIZE * self.camera.zoom_level
                        
                        # Draw a warm glow
                        center = (int(screen_x + size/2), int(screen_y + size/2))
                        radius = int(size * 2)
                        
                        # We simulate glow by drawing a circle with special flags
                        # Since pygame drawing doesn't support gradients easily, we use a pre-made surface or simple concentric circles
                        
                        # Simple: concentric circles
                        for r in range(radius, 0, -5):
                            alpha_step = 5
                            # Yellowish
                            pygame.draw.circle(self.screen, (20, 15, 5), center, r, 0) 
                            # This just paints on top. 
                            # To "light up" the dark overlay, we should have cut holes in it.
                            
            # Correction: The best way without complex shaders in Pygame is:
            # 1. Create darkness surface (filled with dark color)
            # 2. Draw "light" shapes (white/transparent) onto the darkness surface with BLEND_RGBA_SUB to reduce alpha.
            # 3. Blit darkness surface.
            
            lighting = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            lighting.fill((0, 0, 20, alpha))
            
            # Cut holes
            for x in range(start_col, end_col):
                for y in range(start_row, end_row):
                    building = self.world.get_building_at(x, y)
                    if building and building.type in ["House", "Blast Furnace", "Stone Refinery"]:
                        screen_x, screen_y = self.camera.world_to_screen(x, y)
                        size = TILE_SIZE * self.camera.zoom_level
                        center = (int(screen_x + size/2), int(screen_y + size/2))
                        radius = int(size * 2.5)
                        
                        # Draw circle with 0 alpha (transparent) onto the lighting surface?
                        # No, we need to Subtract Alpha. 
                        # Pygame method: blit a surface with BLEND_RGBA_SUB
                        
                        light_mask = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                        # Gradient hack: multiple circles
                        for r in range(radius, 0, -2):
                            # Subtract a small amount of alpha each step
                            pygame.draw.circle(light_mask, (0, 0, 0, 3), (radius, radius), r)
                        
                        lighting.blit(light_mask, (center[0]-radius, center[1]-radius), special_flags=pygame.BLEND_RGBA_SUB)

            self.screen.blit(lighting, (0, 0))

        if not self.ui_manager.active_window:
            self.input_handler.draw_preview(self.screen)

        self.hud.draw(self.screen)
        self.ui_manager.draw(self.screen)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()
