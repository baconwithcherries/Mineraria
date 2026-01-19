# Development Task List - Mineraria Survival

This task list is derived from `GAME_SPEC.md` and `ARCHITECTURE.md`. It outlines the step-by-step development process to build the game using Python and `pygame-ce`.

## Phase 1: Project Setup & Core Engine
- [ ] **1.1. Environment Setup**
    - [ ] Create project directory structure (`assets/`, `src/`, `src/ui`, `data/`).
    - [ ] Create virtual environment.
    - [ ] Create `requirements.txt` containing `pygame-ce`.
    - [ ] Install dependencies.
- [ ] **1.2. Configuration**
    - [ ] Create `src/config.py` with constants:
        - [ ] Screen Width/Height (e.g., 1280x720).
        - [ ] Tile Size (e.g., 16px).
        - [ ] Colors (WHITE, BLACK, SKY_BLUE).
        - [ ] FPS (60).
- [ ] **1.3. Main Loop Skeleton**
    - [ ] Create `src/game.py`: `Game` class with `__init__`, `run`, `handle_events`, `update`, `draw`.
    - [ ] Create `src/main.py`: Entry point to instantiate and run `Game`.
    - [ ] **Test 1.1:** Run `main.py`. Verify a window opens with a solid background color and closes when the X is clicked.

## Phase 2: World Generation & Rendering
- [ ] **2.1. Tile & Grid System**
    - [ ] Create `src/world.py`.
    - [ ] Implement `Tile` class (type, x, y).
    - [ ] Implement `World` class with a 150x100 2D list/array.
    - [ ] Implement `World.generate()`: Fill bottom layers with Stone/Dirt, top layer with Grass. Empty air above.
- [ ] **2.2. Camera System**
    - [ ] Create `src/camera.py`.
    - [ ] Implement `Camera` class with `offset_x`, `offset_y`, `zoom_level`.
    - [ ] Implement `world_to_screen` and `screen_to_world` conversion methods.
    - [ ] Implement Input handling in `Game` to modify Camera offset (Arrow Keys) and Zoom (Mouse Wheel).
- [ ] **2.3. World Rendering**
    - [ ] Update `Game.draw` to iterate visible tiles in `World`.
    - [ ] Draw colored rectangles for tiles using `Camera` transforms.
    - [ ] **Test 2.1:** Run game. Verify 150x100 grid renders. Verify Pan/Zoom works correctly. Verify culling (performance check).

## Phase 3: Economy Backend & Basic UI
- [ ] **3.1. Resource Manager**
    - [ ] Create `src/resources.py`.
    - [ ] Implement `ResourceManager` class.
    - [ ] Initialize Inventory: 10 Wood, 10 Stone, 10 Iron.
    - [ ] Add methods: `add_resource`, `remove_resource`, `has_resources`.
- [ ] **3.2. UI Overlay (Static)**
    - [ ] Create `src/ui/manager.py` and `src/ui/hud.py`.
    - [ ] Implement `draw_hud(surface, inventory)` function.
    - [ ] Draw Top Left: Placeholder icons for "Build" and "Inventory".
    - [ ] Draw Top Right: Empty "List" container.
    - [ ] **Test 3.1:** Run game. Verify UI elements hover *stationary* over the moving world map.

## Phase 4: Building System (Construction)
- [ ] **4.1. Building Data Structures**
    - [ ] Update `src/world.py` to include a `Building` class.
    - [ ] Define types: `LoggingWorkshop`, `StoneRefinery`, `Mine`, `House`.
    - [ ] Define costs and dimensions (1x1 or larger).
- [ ] **4.2. Placement Interaction**
    - [ ] Create `src/input_handler.py` (or expand `Game.handle_events`).
    - [ ] Implement "Build Mode": Select a building type (simulated via number keys temporarily).
    - [ ] Implement "Ghost" rendering: Show semi-transparent building under cursor (snapped to grid).
    - [ ] Implement "Placement":
        - [ ] Left Click -> Check collision (must be on ground or building).
        - [ ] Check resources (call `ResourceManager`).
        - [ ] Deduct resources and add `Building` object to `World`.
    - [ ] **Test 4.1:** Select building. Check ghost follows mouse. Click to place. Verify inventory decreases. Verify cannot place in air or without resources.

## Phase 5: Game Loop & Production
- [ ] **5.1. Time System**
    - [ ] Implement `TickManager` in `Game`. Fire a "Tick" event every 1 second.
    - [ ] Implement Day/Night cycle timer (1200 seconds total).
- [ ] **5.2. Villager & Workforce Logic**
    - [ ] Create `src/entities.py`.
    - [ ] Implement `Villager` class (spawned by Houses).
    - [ ] Implement `ResourceManager.calculate_workforce()`: Count villagers vs required slots.
- [ ] **5.3. Production Logic**
    - [ ] Update `Building` class with `produce()` method.
    - [ ] In `Tick` event: Iterate buildings.
    - [ ] If `building.has_workers`: generate resource -> Add to internal buffer.
    - [ ] **Test 5.1:** Place House (spawns villager logic). Place Mine. Wait. Verify Mine generates Iron (via console log).

## Phase 6: Interactive UI (Windows & Menus)
- [ ] **6.1. Building Selection Window**
    - [ ] Implement `BuildingTab` UI (Grid of buttons).
    - [ ] Toggle visibility when clicking Top Left "Build" icon.
    - [ ] Clicking grid item enters "Placement Mode".
- [ ] **6.2. Building Inspector**
    - [ ] Implement Right-Click detection on placed buildings.
    - [ ] Create `BuildingWindow` class (Modal).
    - [ ] Display Name, Level.
    - [ ] Implement "Collect" button: Transfers buffer to `ResourceManager` inventory.
- [ ] **6.3. Charts & Graphs**
    - [ ] Implement basic Line Graph renderer in `BuildingWindow`.
    - [ ] Feed mock production data to graph.
    - [ ] **Test 6.1:** Build Mode -> Place -> Right Click -> Collect Resources.

## Phase 7: Entities & Simulation
- [ ] **7.1. Villager Visuals**
    - [ ] Implement `Villager` sprite rendering.
    - [ ] Implement simple AI: Move randomly on X-axis, jump up 1 block if stuck, fall if air.
    - [ ] Constrain to island bounds.
- [ ] **7.2. Upgrade System**
    - [ ] Add `level` attribute to Buildings.
    - [ ] Add `upgrade_cost` property.
    - [ ] Add "Upgrade" button (Arrow icon) to `BuildingWindow`.
    - [ ] Implement upgrade logic: Cost deduction, Stats increase (Production/Capacity).

## Phase 8: Pinning System (Quest Tracking)
- [ ] **8.1. Data Structure**
    - [ ] Create `Recipe` class (Target Item, Required Resources).
    - [ ] Add `pinned_recipes` list to `ResourceManager`.
- [ ] **8.2. UI Integration**
    - [ ] Add "Checkbox" to Building Tab items and Upgrade Window.
    - [ ] Implement Toggle logic: Add/Remove from `pinned_recipes`.
    - [ ] Implement Top Right "List" rendering: Iterate `pinned_recipes` and draw icon + current/required count.
    - [ ] **Test 8.1:** Pin a building. Gather resources. Verify numbers update in the list.

## Phase 9: Assets & Audio
- [ ] **9.1. Sprite Integration**
    - [ ] Create/Import assets for: Grass, Dirt, Stone, Wood, Iron, Villager, Background.
    - [ ] Load images in `src/assets_loader.py`.
    - [ ] Replace rect drawing with `surface.blit`.
- [ ] **9.2. Day/Night Visuals**
    - [ ] Draw sky background based on timer (Blue -> Orange -> Black).

## Phase 10: Save System & Polish
- [ ] **10.1. Persistence**
    - [ ] Implement `World.to_dict()` and `World.from_dict()`.
    - [ ] Implement `ResourceManager.to_dict()` (Inventory).
    - [ ] Create `src/save_manager.py`: Write/Read JSON to `data/savegame.json`.
    - [ ] Auto-save on exit or timer.
- [ ] **10.2. Rocket Ending**
    - [ ] Implement "Rocket Ship" building type (Multi-stage).
    - [ ] Win condition check.

## Final Verification
- [ ] **Test Full Loop:** Start -> Build House -> Build Mine -> Collect Iron -> Build Refinery -> Upgrade -> Build Rocket.
