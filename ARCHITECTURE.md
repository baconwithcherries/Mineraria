# Mineraria Survival - Technical Architecture

## 1. Overview
This document outlines the technical architecture for "Mineraria Survival", a 2D side-scrolling strategy game. The project will be developed using **Python** and the **Pygame Community Edition (pygame-ce)** library. This stack provides a robust, cross-platform foundation for 2D graphics, input handling, and game loop management without the overhead of a heavy game engine.

## 2. Technology Stack
*   **Language:** Python 3.10+
*   **Core Library:** `pygame-ce` (Graphics, Input, Windowing)
*   **Dependencies:** `numpy` (Optional, for efficient grid management, but Python lists may suffice given the small 150x100 world size). Standard `json` library for serialization.

## 3. High-Level Architecture
The application will follow a modular **Object-Oriented** design, centering on a main `Game` class that orchestrates the **Game Loop** (Input -> Update -> Draw).

### Core Modules
*   **`main.py`**: Entry point. Initializes Pygame and the Game object.
*   **`game_engine.py`**: Contains the `Game` class. Manages the main loop, state transitions (Menu vs Gameplay), and global event handling.
*   **`world_manager.py`**: Manages the Tile Grid (Map), Terrain generation, and Building placement logic.
*   **`entity_manager.py`**: Manages dynamic entities (Villagers, Rocket Ship).
*   **`ui_manager.py`**: Handles all User Interface elements (HUD, Windows, Tooltips).
*   **`resource_manager.py`**: Handles the Economy (Inventory, Production Logic, Upgrades).
*   **`input_handler.py`**: Abstracts raw Pygame events into game actions (e.g., "Place Building", "Open Menu").
*   **`camera.py`**: Manages the viewport, zooming, and panning calculations.
*   **`settings.py`**: Global constants (Screen dimensions, Colors, Tile sizes).

## 4. Detailed Component Design

### 4.1. World System (`world_manager.py`)
*   **Data Structure:** A 2D array (List of Lists) representing the 150 (width) x 100 (height) grid.
*   **Tile Objects:** Each cell contains a `Tile` object or ID (Grass, Stone, Dirt, Air).
*   **Building Layer:** A separate or overlay dictionary mapping `(x, y)` coordinates to `Building` instances.
*   **Coordinate System:** `(0,0)` is Top-Left. `(x, y)` corresponds to Grid Column and Row.

### 4.2. Economy & Resources (`resource_manager.py`)
*   **Inventory:** A dictionary `{ "wood": int, "stone": int, "iron": int, "villagers": int }`.
*   **Production Loop:**
    *   Implements a `tick()` method called once per second.
    *   Iterates through active Buildings.
    *   Applies logic: `If building.has_workers(): inventory[resource] += production_rate`.
*   **Pinning System:** A list of `Recipe` objects targeted by the user.

### 4.3. Entity System (`entity_manager.py`)
*   **Villagers:** Simple state machines.
    *   *States:* `IDLE`, `MOVING_TO_WORK`, `WORKING`, `WANDERING`.
    *   *Pathfinding:* Simple A* or Manhattan distance logic to find valid ground tiles to walk on.
*   **Buildings:**
    *   Attributes: `type`, `level`, `assigned_villagers`, `production_buffer`.
    *   Methods: `upgrade()`, `collect()`.

### 4.4. Rendering & Camera (`camera.py`)
*   **Viewport:** A `Rect` defining the visible world area.
*   **Zoom:** A float scalar `zoom_level`.
*   **World-to-Screen Transform:**
    *   `screen_x = (world_x * TILE_SIZE - camera_x) * zoom_level`
    *   `screen_y = (world_y * TILE_SIZE - camera_y) * zoom_level`
*   **Culling:** Only render tiles/entities within the Viewport + Buffer.

### 4.5. UI System (`ui_manager.py`)
*   **Architecture:** Immediate Mode style drawing for simple HUD, Retained Mode for interactive Windows.
*   **Elements:**
    *   `Button`: Clickable regions.
    *   `Panel`: Background containers.
    *   `Icon`: Sprite wrappers.
    *   `Graph`: Custom component drawing lines based on history data.
*   **Z-Ordering:** UI is always drawn last (on top of the world).

## 5. File Structure
```text
/
├── assets/
│   ├── sprites/       # .png files
│   └── fonts/         # .ttf files
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py      # Settings & Constants
│   ├── game.py        # Main Game Class
│   ├── camera.py
│   ├── world.py
│   ├── entities.py
│   ├── resources.py
│   └── ui/
│       ├── __init__.py
│       ├── manager.py
│       ├── hud.py
│       └── windows.py
├── data/
│   └── savegame.json  # Persistence
└── requirements.txt
```

## 6. Implementation Task List (Phase 1)
1.  **Setup:** Initialize Project Structure, Virtual Env, Pygame.
2.  **Core Loop:** Create Window, Basic Game Loop, Input Processing.
3.  **World Gen:** Implement 150x100 Grid, Terrain Generation, Rendering.
4.  **Camera:** Implement Pan and Zoom.
5.  **Building:** Implement "Place Block/Building" logic (Data only).
6.  **UI:** Implement Main HUD (Icons) and "Building Tab".
7.  **Economy:** Implement Resource counter and Cost deduction.
```
