with open('backend/main.py', encoding='utf-8') as f:
    lines = f.read()

lines = lines.replace('\\"\\"\\"', '"""')
lines = lines.replace('\\"', '"')

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(lines)

print("Done fixing syntax")
