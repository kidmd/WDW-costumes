with open('PROJECT_PROGRESS.md', 'r', encoding='utf-8') as f:
    content = f.read()

target = "## Progress Log\n\n"
new_entry = """## Progress Log

### 2026-11-04: Removal of Incandescent Light Bulb Dots from Transparent Lightning Bug Graphic
- **Shape & Color Integrity Preservation:**
  - Preserved 100% of character silhouette, polygon facet geometry, and black outline boundaries with zero shape warping or curve distortion.
  - 100% bit-exact preservation of the eye (`x: 295..360, y: 95..160`) and added yellow tail lantern dome (`x: 30..85, y: 140..190`).
  - Created safety backup files (`assets/lightningbug_transparent_backup.png` and `simulator/assets/lightningbug_transparent_backup.png`, 436×460 RGBA) preserving the raw version with dots.
- **Computer Vision Dot Removal Pipeline:**
  - Local luminance peak detection relative to 13px median filter isolating bright specular incandescent light bulb centers (`peak > 20`).
  - Component area filtering targeting individual bulbs (`3 <= area <= 120` px) while protecting all structural features and lines.
  - Wire mesh pit detection targeting dark shadow cavities (`peak < -25`).
  - Fast-marching inpainting (`cv2.INPAINT_TELEA`) with 4px radius replacing dots with surrounding facet tones.
  - Subtle bilateral smoothing (`d=7, sigmaColor=35, sigmaSpace=7`) flattening internal grain while locking sharp structural lines.
- **Asset Deployment:**
  - Deployed to `assets/lightningbug_transparent.png`, `simulator/assets/lightningbug_transparent.png`, `assets/lightning_bug.png`, and `simulator/assets/lightning_bug.png` with cache-buster `?v=20261104_dots_removed`.

"""

assert target in content, 'target not found'
content = content.replace(target, new_entry, 1)

with open('PROJECT_PROGRESS.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated PROJECT_PROGRESS.md.')
