import os

index_path = os.path.abspath('../Frontend/index.html')
with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('onclick=\\"', 'onclick="')
content = content.replace('\\">', '">')
content = content.replace('\\" style=', '" style=')

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed escaped quotes in Frontend/index.html!")
