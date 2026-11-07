with open('SIMULATOR_USER_GUIDE.md', 'r', encoding='utf-8') as f:
    text = f.read()

target = """  - **The Spinning Turtle Palette:**
    1. **Slot 1 (Chassis Black `#11161d`):** Chassis tray, 7.0mm perimeter rim (9.0mm total thickness), 16 mounting tabs, LED collars, and all black linework/outlines.
    2. **Slot 2 (Shell Plates & Glasses `#00cc66`):** Turtle hexagonal shell plates and glasses frame.
    3. **Slot 3 (Shell & Eyes `#2563eb`):** Rest of the outer shell and iris accents.
    4. **Slot 4 (Body & Head `#facc15`):** Turtle skin, head, neck, and limbs.
    5. **Slot 5 (Tie & Lips `#ef4444`):** Red bow tie and cheerful lips."""

replacement = """  - **The Spinning Turtle Palette (Production 5-Color Multi-Material Edition):**
    1. **Slot 1 (Chassis Black `#11161d`):** Chassis tray, 7.0mm perimeter rim (9.0mm total thickness), 16 mounting tabs, LED collars, and all crisp cartoon linework/outlines (including 3px glasses perimeter outline).
    2. **Slot 2 (Shell Plates & Feet `#21652e`):** Turtle hexagonal shell plates and walking feet/pads.
    3. **Slot 3 (Shell Grid, Glasses & Pupil `#294062`):** Structural shell grid/ribs, circular eyeglass frames, nasal bridge, temple arm, and eye pupil.
    4. **Slot 4 (Body, Head & Shirt `#eccb2e`):** Turtle head, neck, and unified full front dress shirt (clean, fully tucked front torso).
    5. **Slot 5 (Tie & Lips `#d81d17`):** Classic Disney red necktie and cheerful lips."""

if target in text:
    text = text.replace(target, replacement, 1)
    with open('SIMULATOR_USER_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated SIMULATOR_USER_GUIDE.md successfully (LF)!")
else:
    target_crlf = target.replace('\r\n', '\n').replace('\n', '\r\n')
    replacement_crlf = replacement.replace('\r\n', '\n').replace('\n', '\r\n')
    if target_crlf in text:
        text = text.replace(target_crlf, replacement_crlf, 1)
        with open('SIMULATOR_USER_GUIDE.md', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Updated SIMULATOR_USER_GUIDE.md successfully (CRLF)!")
    else:
        print("Target not found in SIMULATOR_USER_GUIDE.md.")
