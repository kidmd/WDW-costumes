with open('simulator/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "lightningBugImg.src = 'assets/lightning_bug.png?v=20261104_transparent';",
    "lightningBugImg.src = 'assets/lightning_bug.png?v=20261104_dots_removed';"
)

content = content.replace(
    "lightningBugTransparentImg.src = 'assets/lightningbug_transparent.png?v=20261104_transparent';",
    "lightningBugTransparentImg.src = 'assets/lightningbug_transparent.png?v=20261104_dots_removed';"
)

with open('simulator/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated simulator/app.js with new cache-busters.')
