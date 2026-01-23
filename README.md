# Mineraria Survival

A 2D survival strategy game built with Python and Pygame-CE.

## Installation

1. Install Python 3.10+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Playing the Game

Run the game (using the Python environment where dependencies were installed):
```bash
python -m src.main
```

Or simply double-click `run.bat` on Windows.

## Controls

- **WASD / Arrow Keys**: Pan Camera
- **Mouse Wheel**: Zoom
- **Left Click**: Place Building (in Build Mode)
- **Right Click**: Inspect Building (Collect resources, Upgrade)
- **Top Left Icons**:
    - **B**: Open Building Tab (Select buildings to construct, Pin recipes)
    - **I**: Inventory (Currently displayed in Top Right text)

## Gameplay
1. Build **Houses** to spawn Villagers.
2. Build **Workshops/Mines** to produce resources (Wood, Stone, Iron).
3. Villagers automatically work at workshops (Requires 3 villagers per building).
4. Collect resources by Right-Clicking buildings.
5. Upgrade buildings to increase efficiency.
6. Build the **Rocket Ship** to win!
