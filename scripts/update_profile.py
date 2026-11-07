with open('simulator/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    'spinning_turtle': {
        'black': { name: "Chassis Black", hex: "#11161d", targetRgb: [34, 43, 51], role: "chassis" },
        'green': { name: "Shell Plates & Glasses", hex: "#00cc66", targetRgb: [43, 109, 49], role: "inlay", filename: "color_green.stl" },
        'blue': { name: "Shell & Eyes", hex: "#2563eb", targetRgb: [41, 63, 96], role: "inlay", filename: "color_blue.stl" },
        'yellow': { name: "Body & Head", hex: "#facc15", targetRgb: [231, 199, 49], role: "inlay", filename: "color_yellow.stl" },
        'red': { name: "Tie & Lips", hex: "#ef4444", targetRgb: [217, 29, 22], role: "inlay", filename: "color_red.stl" }
    },"""

replacement = """    'spinning_turtle': {
        'black': { name: "Chassis & Outlines", hex: "#11161d", targetRgb: [17, 22, 29], role: "chassis" },
        'green': { name: "Shell Plates & Feet", hex: "#21652e", targetRgb: [33, 101, 46], role: "inlay", filename: "color_green.stl" },
        'blue': { name: "Shell Grid, Glasses & Pupil", hex: "#294062", targetRgb: [41, 64, 98], role: "inlay", filename: "color_blue.stl" },
        'yellow': { name: "Body, Head & Shirt", hex: "#eccb2e", targetRgb: [236, 203, 46], role: "inlay", filename: "color_yellow.stl" },
        'red': { name: "Tie & Lips", hex: "#d81d17", targetRgb: [216, 29, 23], role: "inlay", filename: "color_red.stl" }
    },"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open('simulator/app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated MULTI_COLOR_STL_PROFILES['spinning_turtle'] in simulator/app.js!")
else:
    print("Target not found directly, checking normalized line endings...")
    # Normalize CRLF
    target_crlf = target.replace('\r\n', '\n').replace('\n', '\r\n')
    replacement_crlf = replacement.replace('\r\n', '\n').replace('\n', '\r\n')
    if target_crlf in content:
        content = content.replace(target_crlf, replacement_crlf, 1)
        with open('simulator/app.js', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully updated with CRLF line endings!")
    else:
        print("Target still not found. Please inspect.")
