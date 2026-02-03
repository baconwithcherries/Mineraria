import pygame
import os
import sys

# Mock pygame to avoid video driver init issues if running headless
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1,1))

from src.assets import Assets

print("Initializing Assets...")
try:
    assets = Assets.get()
    
    print("Checking 'Power Plant' sprite...")
    pp_sprite = assets.get_sprite("Power Plant")
    
    if pp_sprite:
        print(f"Power Plant sprite found. Size: {pp_sprite.get_size()}")
        # Check if it matches fallback (32x32)
        if pp_sprite.get_size() == (32, 32):
             print("Size matches fallback/standard.")
        else:
             print("Size DOES NOT match standard 32x32.")
             
        # Check pixel color at (10, 14) which is Blue in fallback
        # Fallback: pygame.draw.rect(surf, (0, 100, 255), (10, 14, 12, 10))
        # (10, 14) should be (0, 100, 255)
        try:
            col = pp_sprite.get_at((10, 14))
            print(f"Pixel at (10, 14): {col}")
            
            # House check? House usually has different colors.
            # Let's check 'House' sprite too.
            h_sprite = assets.get_sprite("House")
            if h_sprite:
                h_col = h_sprite.get_at((10, 14))
                print(f"House Pixel at (10, 14): {h_col}")
                
                if col == h_col:
                    print("WARNING: Power Plant pixel matches House pixel!")
                else:
                    print("Power Plant pixel differs from House pixel.")
            else:
                print("House sprite not found.")
                
        except Exception as e:
            print(f"Error checking pixels: {e}")

    else:
        print("Power Plant sprite is None!")

    # Check file existence explicitly
    path = os.path.join("assets", "sprites", "power_plant.png")
    if os.path.exists(path):
        print(f"File {path} EXISTS.")
    else:
        print(f"File {path} DOES NOT EXIST.")

except Exception as e:
    print(f"Error: {e}")
