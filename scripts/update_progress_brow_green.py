with open('PROJECT_PROGRESS.md', 'r', encoding='utf-8') as f:
    content = f.read()

target = "## Progress Log\n\n"
new_entry = """## Progress Log

### 2026-11-04: Recolor Brow Area Above Eye to Green on Lightning Bug Graphic
- **User Annotation Correction:**
  - Recolor facet 12 (brow facet between the red hat and eye socket) from Yellow (`#facc15`) to Green (`#22c55e` / `[34, 197, 94]`).
  - Forehead, brow, and temples now form a unified, continuous green head above the eye, leaving the eye sclera (yellow) and iris (blue) with its black eyelid arch distinctly framed.
  - 100.00% strict 5-color palette compliance across all 120,904 foreground pixels on a 100% transparent background.
- **Deployment:**
  - Deployed to `assets/lightning_bug.png`, `simulator/assets/lightning_bug.png`, `assets/lightningbug_transparent.png`, and `simulator/assets/lightningbug_transparent.png`.
  - Updated simulator cache-buster to `?v=20261104_brow_green`.

"""

assert target in content, 'target not found'
content = content.replace(target, new_entry, 1)

with open('PROJECT_PROGRESS.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated PROJECT_PROGRESS.md successfully.')
