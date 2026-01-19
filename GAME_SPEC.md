# Mineraria Survival - Game Specification

## 1. Game Overview
**Title:** Mineraria Survival  
**Genre:** 2D Survival / Simulation / Builder  
**Visual Style:** Terraria-like (Pixel Art), Side-scrolling.  
**Setting:** A floating island (~150 blocks wide), reminiscent of "Avatar".  
**Core Objective:** Build a colony, manage resources/villagers, and construct a rocket ship to evacuate the population.

## 2. World & Environment
*   **Map Dimensions:** Fixed width (~150 blocks). Max build height: 100 blocks.
*   **Terrain:** Tile-based system. Blocks: Grass, Stone, Dirt.
*   **Visuals:** Blocks appear small initially but the camera must support zooming in to see details.
*   **Day/Night Cycle:** 20-minute total cycle (10m Day, 10m Night).
    *   *Technical Note:* Global timer required to track cycle state.

## 3. Core Gameplay Loop
1.  **Gather:** Passive resource accumulation via buildings.
2.  **Build:** Place workshops/houses.
3.  **Populate:** Houses produce villagers who work at workshops.
4.  **Produce:** Workshops consume villager labor to produce raw materials (Wood, Stone, Iron).
5.  **Upgrade:** Increase efficiency/capacity of buildings.
6.  **Track:** Pin recipes to the HUD to manage resource targets.
7.  **Escape:** Build/Expand Rocket Ship (Endgame).

## 4. Economy & Resources
### Base Resources
*   **Wood** (Logging Workshop)
*   **Stone** (Stone Refinery)
*   **Iron** (Mine)
*   **Villagers** (Houses) - *Acts as a workforce resource.*

### Starting State
*   **Inventory:** 10 Wood, 10 Stone, 10 Iron.

### Building Costs & stats
*Note: All buildings can be stacked vertically.*

| Building | Construction Cost | Production | Requirements |
| :--- | :--- | :--- | :--- |
| **Logging Workshop** | 5 Wood | Generates Wood | Needs 3 Villagers (Lvl 1) |
| **Stone Refinery** | 5 Stone | Generates Stone | Needs 3 Villagers (Lvl 1) |
| **Mine** | 5 Iron | Generates Iron | Needs 3 Villagers (Lvl 1) |
| **House** | 5 Iron, 5 Stone, 5 Wood | Spawns Villagers (10/min) | Max 20 Villagers (Lvl 1) |

## 5. Entities (Villagers)
*   **Spawning:** Automatically produced by Houses until max occupancy is reached.
*   **AI/Behavior:** 
    *   Simple pathfinding: They "run around" the island.
    *   Work assignment: They visually enter/interact with workshops. 
    *   *Technical:* While visually they run around, logically they are "consumed" or "assigned" to workshops to enable production.
*   **Workforce Logic:**
    *   A workshop with < 3 villagers pauses production.
    *   Higher level buildings require more villagers.

## 6. UI / UX Design

### HUD Layout
*   **Top Left (Menu Icons):**
    *   **Building Tab:** Button to open the construction menu.
    *   **Inventory:** Chest icon (Minecraft-style). Opens player inventory.
*   **Top Right (Resource List):**
    *   **Scrollable List:** Shows tracked resources.
    *   **Behavior:** Fixed visual length; becomes scrollable if content overflows.
    *   **Content:** "Pinned" recipes (see 'Pinning System' below).

### Building Tab (Construction Menu)
*   **Content:** Grid of available buildings.
*   **Item View:** Shows building preview and cost.
*   **Pinning:** Contains a "Checklist Box". Clicking it adds this building's cost to the Top Right Resource List.

### Building Interaction (Right-Click)
Opens a modal window in the center of the screen:
1.  **Header:** Building Name & Current Level.
2.  **Visualization:** Line Graph displaying **Materials Produced vs. Villagers Assigned** over time.
3.  **Collection:** "Collect" button below the graph to move produced resources to Inventory.
4.  **Upgrade Section (Top Right of Modal):**
    *   **Icon:** Up Arrow in a Box.
    *   **Action:** Clicking opens the Upgrade View.
        *   Shows: Next level preview image, Resource requirements list.
        *   **Pinning:** "Checklist Box" to add these upgrade requirements to the Top Right Resource List.

### Placement System
*   **Selection:** Clicking a building in the Building Tab.
*   **Visual:** 50% transparent silhouette follows mouse cursor.
*   **Action:** Left-click to place.
*   **Constraint:** Must be on valid ground or on top of another building (Stacking).

### Screen Layout Reference (Visual Description)
*   **Global View:**
    *   **Center:** The game world (Floating Island) takes up the majority of the screen space.
    *   **UI Overlay:**
        *   **Top Left Corner:** A compact vertical column containing the **Building Tab** icon (top) and **Inventory** icon (bottom).
        *   **Top Right Corner:** A semi-transparent list box titled "List". It contains rows of "pinned" recipes (Checkbox + Text/Icons).
*   **World View:**
    *   The island is a floating landmass centered horizontally.
    *   Buildings sit on top of the terrain blocks.
    *   Sky background fills the rest of the view.

## 7. Technical Architecture Requirements
*(To be used for Code Task List)*

### 1. Game Engine & State Management
*   **Grid System:** 2D Array/Grid for the 150x100 world.
*   **Tick System:** 1-second (or less) tick for resource generation calculations.
*   **Persistence:** Save/Load system for building locations and inventory.

### 2. Rendering
*   **Camera:** Implement Zoom and Pan functionality.
*   **Layering:** Background (Sky/Parallax), Midground (Buildings/Terrain), Foreground (UI).

### 3. UI System
*   **Modal Manager:** Handle "Building Window", "Inventory", and "Construction Menu" states.
*   **Overlay:** Top Left Icons and Top Right List must remain static relative to the screen, not the world.

### 4. Input Handling
*   **Mouse:** 
    *   Screen-to-World coordinate conversion (for placing buildings).
    *   UI Hit testing (clicking icons vs clicking world).

## 8. Assets Needed (Placeholder/Final)
*   **Sprites:** Blocks (3 types), Buildings (4 types), Villager (1 type), Icons (Chest, Arrow, Checkbox).
*   **Visual Target:** Simple, readable pixel art.
