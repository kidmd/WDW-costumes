with open('simulator/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "lightningBugImg.src = 'assets/lightning_bug.png?v=20261103_restored_v1';",
    "lightningBugImg.src = 'assets/lightning_bug.png?v=20261104_transparent';"
)

content = content.replace(
    "lightningBugTransparentImg.src = 'assets/lightningbug_transparent.png?v=20261103_trans_v1';",
    "lightningBugTransparentImg.src = 'assets/lightningbug_transparent.png?v=20261104_transparent';"
)

with open('simulator/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

with open('simulator/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace(
    '<option value="lightning_bug">💡 Float Bonus: Lightning Bug (Restored Version)</option>',
    '<option value="lightning_bug">💡 Float Bonus: Lightning Bug (Transparent)</option>'
)

with open('simulator/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated app.js and index.html.')
