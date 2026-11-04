with open("PROJECT_PROGRESS.md", "rb") as f:
    data = f.read()

target = b"## Progress Log\r\n\r\n### 2026-11-04: Recolor of Yellow Spur Above Eye to Green on Lightning Bug Graphic"
if target not in data:
    target = b"## Progress Log\n\n### 2026-11-04: Recolor of Yellow Spur Above Eye to Green on Lightning Bug Graphic"

new_entry = """## Progress Log

### 2026-11-04: Clean-Up of Wing, Tail Triangle & Antennae Gap on Lightning Bug Graphic
- **3 Targeted Image Corrections from User Annotations:**
  1. **Wing Interior Recolor to Blue:**
     - Removed the erroneous yellow facet split inside the blue wing (Facet 10); full facet 10 is now unified with the surrounding wing as pure Blue (`#2563eb` / `[37, 99, 235]`).
  2. **Tail Triangle Recolor to Yellow:**
     - Recolored the tail facet triangle (`x: 61..96, y: 161..184`) adjacent to the yellow lantern dome and blue wing to solid Yellow (`#facc15` / `[250, 204, 21]`).
     - Sealed the previous transparent artifact/hole (the "white splotch") cleanly into the yellow facet.
  3. **Antennae Gap Transparency:**
     - Converted the wedge area between the two antennae before they merge together (Facet 41, 393 px) to transparent (`alpha = 0`), cleanly separating the two physical antenna shafts emerging from the head before merging at the tip.
     - Preserved crisp black wireframe boundary lines enclosing both antenna shafts.
- **Palette & Silhouette Integrity:**
  - 100.00% 5-color palette compliance maintained across all foreground pixels (`#141414`, `#22c55e`, `#e61919`, `#facc15`, `#2563eb`).
  - Bit-exact preservation of character geometry, facet boundaries, and wireframe lines.
- **Asset Deployment & Simulator Synchronization:**
  - Updated `assets/lightningbug_transparent.png`, `assets/lightning_bug.png`, `simulator/assets/lightningbug_transparent.png`, and `simulator/assets/lightning_bug.png`.
  - Bumped cache-buster in `simulator/app.js` to `?v=20261104_wing_tail_ant_clean`.

### 2026-11-04: Recolor of Yellow Spur Above Eye to Green on Lightning Bug Graphic"""

replacement = new_entry.encode("utf-8")
if b"\r\n" in target:
    replacement = replacement.replace(b"\n", b"\r\n")

data = data.replace(target, replacement, 1)
with open("PROJECT_PROGRESS.md", "wb") as f:
    f.write(data)
print("Updated PROJECT_PROGRESS.md successfully")
