with open('simulator/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = '<option value="lightning_bug">💡 Float Bonus: Lightning Bug / Firefly</option>'
replacement = '''<option value="lightning_bug">💡 Float Bonus: Lightning Bug (Restored Version)</option>
                                    <option value="lightningbug_transparent">💡 Float Bonus: Lightning Bug (Transparent Polygon Photo Trace)</option>'''

if target in content:
    content = content.replace(target, replacement, 1)
    with open('simulator/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated simulator/index.html successfully.')
else:
    print('Target not found in index.html')
