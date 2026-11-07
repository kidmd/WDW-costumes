with open('simulator/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Update cache-buster and add lightningBugTransparentImg
old_block = """// Lightning Bug Artwork (5-color transparent PNG)
const lightningBugImg = new Image();
let lightningBugLoaded = false;
lightningBugImg.onload = () => {
    lightningBugLoaded = true;
    notifyFloatImgLoaded();
};
lightningBugImg.src = 'assets/lightning_bug.png?v=20261103_5color_clean';"""

new_block = """// Lightning Bug Artwork
const lightningBugImg = new Image();
let lightningBugLoaded = false;
lightningBugImg.onload = () => {
    lightningBugLoaded = true;
    notifyFloatImgLoaded();
};
lightningBugImg.src = 'assets/lightning_bug.png?v=20261103_restored_v1';

const lightningBugTransparentImg = new Image();
let lightningBugTransparentLoaded = false;
lightningBugTransparentImg.onload = () => {
    lightningBugTransparentLoaded = true;
    notifyFloatImgLoaded();
};
lightningBugTransparentImg.src = 'assets/lightningbug_transparent.png?v=20261103_trans_v1';"""

assert old_block in content, 'old_block not found'
content = content.replace(old_block, new_block, 1)

# Add to floatArtworkImgs
old_dict = """'lightning_bug': lightningBugImg,
    'lightningbug': lightningBugImg"""

new_dict = """'lightning_bug': lightningBugImg,
    'lightningbug': lightningBugImg,
    'lightning_bug_transparent': lightningBugTransparentImg,
    'lightningbug_transparent': lightningBugTransparentImg"""

assert old_dict in content, 'old_dict not found'
content = content.replace(old_dict, new_dict, 1)

# Add to getGraphicImgForType
old_getter = """if (gType === 'lightning_bug' || gType === 'lightningbug') {
        if (lightningBugImg && lightningBugImg.naturalWidth > 0) return lightningBugImg;
        return floatArtworkImgs['lightning_bug'];
    }"""

new_getter = """if (gType === 'lightning_bug' || gType === 'lightningbug') {
        if (lightningBugImg && lightningBugImg.naturalWidth > 0) return lightningBugImg;
        return floatArtworkImgs['lightning_bug'];
    }
    if (gType === 'lightning_bug_transparent' || gType === 'lightningbug_transparent') {
        if (lightningBugTransparentImg && lightningBugTransparentImg.naturalWidth > 0) return lightningBugTransparentImg;
        return floatArtworkImgs['lightning_bug_transparent'];
    }"""

assert old_getter in content, 'old_getter not found'
content = content.replace(old_getter, new_getter, 1)

with open('simulator/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated simulator/app.js successfully.')
