# Inspect all cases in evalGlobalPattern
with open('simulator/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('function evalGlobalPattern(')
end = text.find('function computeLedColor(', start)
eval_func = text[start:end]

lines = eval_func.splitlines()
curr_case = None
case_lines = {}

for line in lines:
    stripped = line.strip()
    if stripped.startswith('case '):
        parts = stripped[5:].split(':')
        curr_case = parts[0].strip().strip("'\"")
        case_lines[curr_case] = []
    elif curr_case and stripped == 'break;':
        curr_case = None
    elif curr_case:
        case_lines[curr_case].append(line)

print("Cases in evalGlobalPattern:")
for c, clines in case_lines.items():
    code = "\n".join(clines)
    uses_effC = 'effC' in code or 'effHasColor' in code or 'hasColor' in code
    has_hsl = 'hslToRgb' in code
    print(f"  case '{c}': uses_effC={uses_effC}, has_hsl={has_hsl}")
