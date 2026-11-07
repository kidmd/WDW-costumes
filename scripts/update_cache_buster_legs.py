with open('simulator/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "lightningBugImg.src = 'assets/lightning_bug.png?v=20261104_5color_facets';",
    "lightningBugImg.src = 'assets/lightning_bug.png?v=20261104_between_legs_green';"
)

content = content.replace(
    "lightningBugTransparentImg.src = 'assets/lightningbug_transparent.png?v=20261104_5color_facets';",
    "lightningBugTransparentImg.src = 'assets/lightningbug_transparent.png?v=20261104_between_legs_green';"
)

with open('simulator/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated simulator/app.js cache-buster.')
