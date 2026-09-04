import os

frontend_dir = os.path.join('d:\\', 'My Works', 'Nord Velocity', 'Frontend')
index_path = os.path.join(frontend_dir, 'index.html.bak')

with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Split points
hero_idx = html.find('<!-- Hero Section -->')
footer_idx = html.find('<!-- Newsletter CTA Section -->')

if hero_idx == -1 or footer_idx == -1:
    print("Could not find split points")
    exit(1)

head_and_header = html[:hero_idx]
body_content = html[hero_idx:footer_idx]
footer_and_scripts = html[footer_idx:]

# Process head_and_header for base.html
head_and_header = head_and_header.replace('href="style.css"', 'href="{% static \'style.css\' %}"')
head_and_header = head_and_header.replace('src="images/brand/logo%20bg-transparent.png"', 'src="{% static \'images/brand/logo bg-transparent.png\' %}"')
head_and_header = head_and_header.replace(
    '<title>Nord Velocity | Home</title>',
    '<title>{% block title %}Nord Velocity | Luxury Travel & Chauffeur{% endblock %}</title>\n    {% block seo %}\n    <meta name="description" content="Nord Velocity - Curated luxury travel experiences and executive chauffeur services across Finland and the Nordics.">\n    {% endblock %}\n    <!-- Vue 3 for reactive booking widgets -->\n    <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>'
)

# Process footer_and_scripts for base.html
footer_and_scripts = footer_and_scripts.replace('src="images/brand/logo%20foote.jpeg"', 'src="{% static \'images/brand/logo foote.jpeg\' %}"')
footer_and_scripts = footer_and_scripts.replace('src="js/main.js"', 'src="{% static \'js/main.js\' %}"')

# Add extra_js block before </body>
footer_and_scripts = footer_and_scripts.replace(
    '</body>',
    '    {% block extra_js %}{% endblock %}\n</body>'
)

base_html = f"{{% load static %}}\n{head_and_header}\n    {{% block content %}}\n    {{% endblock %}}\n\n{footer_and_scripts}"

with open(os.path.join(frontend_dir, 'base.html'), 'w', encoding='utf-8') as f:
    f.write(base_html)

# Process index.html
index_html = f"""{{% extends 'base.html' %}}
{{% load static %}}

{{% block title %}}Nord Velocity | Discover the Extraordinary{{% endblock %}}

{{% block content %}}
{body_content}
{{% endblock %}}
"""

with open(os.path.join(frontend_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)

print("Template split successful! base.html and index.html created.")
