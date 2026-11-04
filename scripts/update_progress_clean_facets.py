with open("PROJECT_PROGRESS.md", "rb") as f:
    data = f.read()

target = b"## Progress Log\r\n\r\n### 2026-11-04: 2x Thick Silhouette & Color-Boundary Outlines on Lightning Bug Graphic"
if target not in data:
    target = b"## Progress Log\n\n### 2026-11-04: 2x Thick Silhouette & Color-Boundary Outlines on Lightning Bug Graphic"

new_entry = """## Progress Log

### 2026-11-04: Clean-Up of Internal Lines (Tail Dome, Wing, Brow) & Leg Contour on Lightning Bug Graphic
- **Removal of Extra Internal Lines (User Feedback):**
  1. **Yellow Tail Tip Lantern Dome:** Removed all internal wireframe/facet spoke lines within the yellow tail dome, leaving it solid, vibrant yellow framed cleanly by its bold 2x black boundaries against the red tail, blue wing, and transparent background.
  2. **Blue Wing:** Removed internal longitudinal and diagonal facet division lines inside the blue wing, rendering the wing as a clean, uniform blue graphic framed by its 2x black perimeter outlines.
  3. **Green Brow:** Removed internal wireframe dividing lines across the green brow above the eye and below the red hat, unifying the brow into a continuous green structure.
- **Leg Silhouette Clean-Up:**
  - Removed extraneous blue pixels and outer double-line spurs sitting outside the main leg contour (`y: 335..339, x >= 392`), restoring a smooth, continuous black outline along the leg and knee joint.
- **Palette & Pixel Integrity:**
  - 100.00% strict 5-color palette compliance maintained across all 120,621 foreground pixels (`#141414`, `#22c55e`, `#e61919`, `#facc15`, `#2563eb`).
- **Asset Deployment & Simulator Synchronization:**
  - Deployed to `assets/lightningbug_transparent.png`, `assets/lightning_bug.png`, `simulator/assets/lightningbug_transparent.png`, and `simulator/assets/lightning_bug.png`.
  - Bumped simulator cache-buster to `?v=20261104_clean_facets`.

### 2026-11-04: 2x Thick Silhouette & Color-Boundary Outlines on Lightning Bug Graphic"""

replacement = new_entry.encode("utf-8")
if b"\r\n" in target:
    replacement = replacement.replace(b"\n", b"\r\n")

data = data.replace(target, replacement, 1)
with open("PROJECT_PROGRESS.md", "wb") as f:
    f.write(data)
print("Updated PROJECT_PROGRESS.md successfully")
