with open('PROJECT_PROGRESS.md', 'r', encoding='utf-8') as f:
    content = f.read()

target = "## Progress Log\n\n"
new_entry = """## Progress Log

### 2026-11-03: Rollback of Lightning Bug Vectorization to Previous Version
- **Reversion of Experimental Vectorization:**
  - Reverted `assets/lightning_bug.png` and `simulator/assets/lightning_bug.png` to the previous version (`commit 285c1c8`), removing the aggressive levelset organic curve smoothing and cartoon facial feature alterations.
  - Preserved the user's authentic polygonal trace asset (`assets/lightningbug_transparent.png` and `simulator/assets/lightningbug_transparent.png`, 436×460 RGBA) containing the added yellow tail lantern dome, foreground-layered blue wing, and removed chassis/wheels.
- **Simulator Registration Updates:**
  - Updated `simulator/app.js` and `simulator/index.html` to register both options with updated cache-busters:
    - **`lightning_bug`:** Restored graphic asset (`assets/lightning_bug.png`).
    - **`lightningbug_transparent`:** Authentic transparent polygon float trace (`assets/lightningbug_transparent.png`).

"""

assert target in content, 'target not found'
content = content.replace(target, new_entry, 1)

with open('PROJECT_PROGRESS.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated PROJECT_PROGRESS.md successfully.')
