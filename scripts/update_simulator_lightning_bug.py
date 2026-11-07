with open('simulator/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add lightningBugImg
old1 = "titleDrumImg.src = 'assets/title_drum.png';"
new1 = """titleDrumImg.src = 'assets/title_drum.png';

// Lightning Bug Artwork (5-color transparent PNG)
const lightningBugImg = new Image();
let lightningBugLoaded = false;
lightningBugImg.onload = () => {
    lightningBugLoaded = true;
    notifyFloatImgLoaded();
};
lightningBugImg.src = 'assets/lightning_bug.png?v=20261103_5color_clean';"""

# 2. Add to floatArtworkImgs
old2 = "'honor_america_eagle': new Image()"
new2 = """'honor_america_eagle': new Image(),
    'lightning_bug': lightningBugImg,
    'lightningbug': lightningBugImg"""

# 3. Add to getGraphicImgForType
old3 = "if (gType === 'carriage_nohorses') {"
new3 = """if (gType === 'lightning_bug' || gType === 'lightningbug') {
        if (lightningBugImg && lightningBugImg.naturalWidth > 0) return lightningBugImg;
        return floatArtworkImgs['lightning_bug'];
    }
    if (gType === 'carriage_nohorses') {"""

assert old1 in content, 'old1 not found'
assert old2 in content, 'old2 not found'
assert old3 in content, 'old3 not found'

content = content.replace(old1, new1, 1)
content = content.replace(old2, new2, 1)
content = content.replace(old3, new3, 1)

with open('simulator/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated simulator/app.js successfully.')
