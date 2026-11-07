import shutil
import os
from PIL import Image

src = 'scripts/Turtle_clean_perfect3.png'

# Also let's copy to artifact directory for the user
import glob
artifact_dir = 'C:/Users/Kiddi/.gemini/antigravity/brain/ba8699af-4574-4f1e-9678-f6f40a0f19fe'
artifact_dest = os.path.join(artifact_dir, 'turtle_5color_final.png')
shutil.copy2(src, artifact_dest)
print(f"Copied to artifact: {artifact_dest}")

# Target destinations in codebase
destinations = [
    'assets/Turtle_clean.png',
    'assets/spinning_turtle.png',
    'assets/Turtle.png',
    'simulator/assets/Turtle_clean.png',
    'simulator/assets/spinning_turtle.png',
    'simulator/assets/Turtle.png',
]

for dst in destinations:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f"Updated: {dst}")

print("All turtle assets successfully deployed!")
