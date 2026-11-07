with open('simulator/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "lightningBugImg.src = 'assets/lightning_bug.png?v=20261104_dots_removed';",
    "lightningBugImg.src = 'assets/lightning_bug.png?v=20261104_5color_facets';"
)

content = content.replace(
    "lightningBugTransparentImg.src = 'assets/lightningbug_transparent.png?v=20261104_dots_removed';",
    "lightningBugTransparentImg.src = 'assets/lightningbug_transparent.png?v=20261104_5color_facets';"
)

with open('simulator/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated simulator/app.js cache-buster.')
