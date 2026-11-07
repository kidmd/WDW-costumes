with open('simulator/app.js', 'r', encoding='utf-8') as f:
    txt = f.read()

old_profile = '''    'honor_america_eagle': {
        floatId: 7,
        name: "To Honor America",
        role: "FOLLOWER",
        tag: "FINALE",
        svgFile: "honor_america_eagle.svg",
        layers: [
            { id: "Layer_1_Blue_Vinyl", name: "Navy Starfield & Wings", hex: "#1d3557", r: 29, g: 53, b: 87 },
            { id: "Layer_2_Red_Vinyl", name: "Crimson Flag Stripes", hex: "#e63946", r: 230, g: 57, b: 70 },
            { id: "Layer_3_Gold_Vinyl", name: "Gold Eagle Beak & Trim", hex: "#ffb703", r: 255, g: 183, b: 3 },
            { id: "Layer_4_White_Vinyl", name: "Crisp White Stars & Head", hex: "#ffffff", r: 255, g: 255, b: 255 }
        ]
    }'''

new_profile = '''    'honor_america_eagle': {
        floatId: 7,
        name: "To Honor America",
        role: "FOLLOWER",
        tag: "FINALE",
        svgFile: "honor_america_eagle.png",
        layers: [
            { id: "Layer_1_Black_Chassis", name: "Chassis, Outlines & Firework Struts", hex: "#11161d", r: 17, g: 22, b: 29 },
            { id: "Layer_2_Blue_Vinyl", name: "Starfield Canton, Eagle Wings & Trim", hex: "#1f4a7d", r: 31, g: 74, b: 125 },
            { id: "Layer_3_Red_Vinyl", name: "Flag Stripes, Fireworks & Eagle Beak", hex: "#d81d17", r: 216, g: 29, b: 23 },
            { id: "Layer_4_White_Vinyl", name: "Marquee Banner, Stars, Stripes & Eagle Head", hex: "#ffffff", r: 255, g: 255, b: 255 }
        ]
    }'''

assert old_profile in txt, 'old_profile not found'
txt = txt.replace(old_profile, new_profile, 1)

old_stl_end = '''    'drumcleanedup': {
        'black': { name: "Chassis, Drum Face & Wheels", hex: "#11161d", targetRgb: [17, 22, 29], role: "chassis" },
        'gold': { name: "Drum Ring, Text & Flag", hex: "#facc15", targetRgb: [250, 204, 21], role: "inlay", filename: "color_gold.stl" },
        'red': { name: "Cab Body Panels, Arches & Streamer", hex: "#ef4444", targetRgb: [239, 68, 68], role: "inlay", filename: "color_red.stl" },
        'blue': { name: "Streamer Pennant Tip", hex: "#2563eb", targetRgb: [37, 99, 235], role: "inlay", filename: "color_blue.stl" },
        'green': { name: "Lead Flag", hex: "#10b981", targetRgb: [16, 185, 129], role: "inlay", filename: "color_green.stl" }
    }
};'''

new_stl_end = '''    'drumcleanedup': {
        'black': { name: "Chassis, Drum Face & Wheels", hex: "#11161d", targetRgb: [17, 22, 29], role: "chassis" },
        'gold': { name: "Drum Ring, Text & Flag", hex: "#facc15", targetRgb: [250, 204, 21], role: "inlay", filename: "color_gold.stl" },
        'red': { name: "Cab Body Panels, Arches & Streamer", hex: "#ef4444", targetRgb: [239, 68, 68], role: "inlay", filename: "color_red.stl" },
        'blue': { name: "Streamer Pennant Tip", hex: "#2563eb", targetRgb: [37, 99, 235], role: "inlay", filename: "color_blue.stl" },
        'green': { name: "Lead Flag", hex: "#10b981", targetRgb: [16, 185, 129], role: "inlay", filename: "color_green.stl" }
    },
    'honor_america_eagle': {
        'black': { name: "Chassis, Outlines & Firework Struts", hex: "#11161d", targetRgb: [17, 22, 29], role: "chassis" },
        'blue': { name: "Starfield Canton, Eagle Wings & Trim", hex: "#1f4a7d", targetRgb: [31, 74, 125], role: "inlay", filename: "color_blue.stl" },
        'red': { name: "Flag Stripes, Fireworks & Eagle Beak", hex: "#d81d17", targetRgb: [216, 29, 23], role: "inlay", filename: "color_red.stl" },
        'white': { name: "Marquee Banner, Stars, Stripes & Eagle Head", hex: "#ffffff", targetRgb: [255, 255, 255], role: "inlay", filename: "color_white.stl" }
    }
};'''

assert old_stl_end in txt, 'old_stl_end not found'
txt = txt.replace(old_stl_end, new_stl_end, 1)

with open('simulator/app.js', 'w', encoding='utf-8') as f:
    f.write(txt)
print('Updated simulator/app.js successfully!')
