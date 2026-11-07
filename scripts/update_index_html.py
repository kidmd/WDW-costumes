with open('simulator/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = '<option value="honor_america_eagle">🦅 Float 07: To Honor America (Eagle)</option>'
replacement = '''<option value="honor_america_eagle">🦅 Float 07: To Honor America (Eagle)</option>
                                    <option value="lightning_bug">💡 Float Bonus: Lightning Bug / Firefly</option>'''

assert target in content, 'target not found in index.html'
content = content.replace(target, replacement, 1)

with open('simulator/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated simulator/index.html successfully.')
