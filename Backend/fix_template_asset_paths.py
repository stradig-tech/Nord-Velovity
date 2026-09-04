import os, re

frontend_dir = os.path.abspath('../Frontend')
updated_files = 0
total_replacements = 0

for root, dirs, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith('.html') and not f.endswith('.bak'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Replace src="images/ with src="/static/images/
            new_content = re.sub(r'src=["\']images/', 'src="/static/images/', content)
            # Replace url('images/ with url('/static/images/
            new_content = re.sub(r'url\([\'"]?images/', 'url(\'/static/images/', new_content)
            # Replace href="style.css" with href="/static/style.css"
            new_content = re.sub(r'href=["\']style\.css["\']', 'href="/static/style.css"', new_content)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                updated_files += 1
                total_replacements += len(content) != len(new_content)

print(f"Updated {updated_files} HTML files with absolute /static/ asset paths.")
