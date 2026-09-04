import os, re

frontend_dir = os.path.abspath('../Frontend')
html_links = []
forms_missing_csrf = []

for root, dirs, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith('.html') and not f.endswith('.bak'):
            filepath = os.path.join(root, f)
            rel_file = os.path.relpath(filepath, frontend_dir)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Check for hardcoded .html links in href
            matches = re.findall(r'href=["\']([^"\']+\.html(?:#[^"\']*)?)["\']', content)
            for m in set(matches):
                if not m.startswith(('http://', 'https://')):
                    html_links.append((rel_file, m))
            
            # Check for <form method="post"> missing csrf_token
            form_matches = re.finditer(r'<form\b[^>]*method=["\']post["\'][^>]*>(.*?)</form>', content, re.I | re.S)
            for form in form_matches:
                form_body = form.group(1)
                if 'csrf_token' not in form_body:
                    forms_missing_csrf.append(rel_file)

print(f"Total hardcoded .html links found: {len(html_links)}")
for f, link in html_links[:30]:
    print(f"[{f}] -> href='{link}'")

print(f"\nForms missing CSRF token: {len(forms_missing_csrf)}")
for f in set(forms_missing_csrf):
    print(f"[{f}] has a POST form missing {{% csrf_token %}}")
