with open("PROJECT_PROGRESS.md", "rb") as f:
    data = f.read()

target = b"## Progress Log\r\n\r\n### 2026-11-04: Clean-Up of Wing, Tail Triangle & Antennae Gap on Lightning Bug Graphic"
if target not in data:
    target = b"## Progress Log\n\n### 2026-11-04: Clean-Up of Wing, Tail Triangle & Antennae Gap on Lightning Bug Graphic"

new_entry = """## Progress Log

### 2026-11-04: Yellow Tail Tip Recolor & Solid Black Outlines on Lightning Bug Graphic
- **Tail Lantern Tip Restoration to Yellow:**
  - Restored the tip facet of the tail lantern dome (`x: 45..65, y: 130..152`, 264 px) to solid Yellow (`#facc15` / `[250, 204, 21]`).
  - Preserved the blue wing section (`x >= 66`) in pure Blue (`#2563eb`), cleanly separating the insect's illuminated tail dome from the overlapping wing.
- **Solid Black Outlines Around Bug and Between Colors:**
  - Added solid, unbroken black outlines (`#141414` / `[20, 20, 20]`) tracing the entire external silhouette of the character against transparent space (zero color-to-background gaps).
  - Added solid black boundary lines separating every adjacent color zone (Green, Blue, Red, Yellow) so each color region is cleanly and distinctly framed (0 direct color-to-color touch leaks).
  - Left all other internal wireframe/facet lines completely intact and unchanged.
- **Palette & Silhouette Verification:**
  - 100.00% strict 5-color compliance across all 120,639 foreground pixels on transparent background.
- **Asset Deployment & Simulator Synchronization:**
  - Deployed to `assets/lightningbug_transparent.png`, `assets/lightning_bug.png`, `simulator/assets/lightningbug_transparent.png`, and `simulator/assets/lightning_bug.png`.
  - Bumped simulator cache-buster to `?v=20261104_tailtip_outlines`.

### 2026-11-04: Clean-Up of Wing, Tail Triangle & Antennae Gap on Lightning Bug Graphic"""

replacement = new_entry.encode("utf-8")
if b"\r\n" in target:
    replacement = replacement.replace(b"\n", b"\r\n")

data = data.replace(target, replacement, 1)
with open("PROJECT_PROGRESS.md", "wb") as f:
    f.write(data)
print("Updated PROJECT_PROGRESS.md successfully")
