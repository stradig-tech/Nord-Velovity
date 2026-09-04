import os, re

frontend = os.path.abspath('../Frontend')
count = 0

for root, dirs, files in os.walk(frontend):
    for f in files:
        if f.endswith('.html') and not f.endswith('.bak'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            orig = content
            # Fix onclick="window.location.href="{% url '...' %}""
            # Match onclick="window.location.href="..."" or similar
            pattern = re.compile(r'onclick="window\.location\.href="({% url [^%]+ %})""')
            content = pattern.sub(r"onclick=\"window.location.href='\1'\"", content)
            
            if content != orig:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)
                count += 1
                print(f"Fixed broken onclick quotes in {f}")

print(f"Total files updated: {count}")
