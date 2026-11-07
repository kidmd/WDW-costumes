import shutil
import os

artifact_dir = r'C:\Users\Kiddi\.gemini\antigravity\brain\ba8699af-4574-4f1e-9678-f6f40a0f19fe'

# Copy comparison images
shutil.copy2('scripts/turtle_overview_grid.png', os.path.join(artifact_dir, 'turtle_orig_overview.png'))
shutil.copy2('scripts/perfect2_overview.png', os.path.join(artifact_dir, 'turtle_5color_overview.png'))
shutil.copy2('scripts/perfect3_head.png', os.path.join(artifact_dir, 'turtle_glasses_detail.png'))
shutil.copy2('scripts/perfect3_chest.png', os.path.join(artifact_dir, 'turtle_shirt_detail.png'))

print("Artifact images copied.")
