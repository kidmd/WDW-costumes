with open('PROJECT_PROGRESS.md', 'r', encoding='utf-8') as f:
    content = f.read()

target = "## Progress Log\n\n"
new_entry = """## Progress Log

### 2026-11-04: Deployment of Transparent Lightning Bug Float Graphic (`assets/lightningbug_transparent.png`)
- **Master Asset Synchronization:**
  - Deployed `assets/lightningbug_transparent.png` (436×460 RGBA freestanding polygon trace bug with added yellow tail lantern dome, wing layered in front of red tail, and removed cart/wheels) directly to `assets/lightning_bug.png` and `simulator/assets/lightning_bug.png`.
  - Updated simulator loaders with cache-buster `?v=20261104_transparent` across `simulator/app.js` and `simulator/index.html` to guarantee immediate rendering.

"""

assert target in content, 'target not found'
content = content.replace(target, new_entry, 1)

with open('PROJECT_PROGRESS.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated PROJECT_PROGRESS.md.')
