import os

frontend_dir = os.path.join('d:\\', 'My Works', 'Nord Velocity', 'Frontend')

# --- 1. Refactor blog.html ---
with open(os.path.join(frontend_dir, 'blog.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('<section')
e = text.find('<footer')

if s != -1 and e != -1:
    content = text[s:e]

    final_blog = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}Travel Stories & Nordic Inspirations | Nord Velocity{% endblock %}\n\n{% block seo %}\n<meta name=\"description\" content=\"Discover insider tips, Arctic travel guides, and curated stories across Finland, Lapland, and the Nordics.\">\n{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"

    with open(os.path.join(frontend_dir, 'blog.html'), 'w', encoding='utf-8') as f:
        f.write(final_blog)
    print("blog.html converted!")

# --- 2. Refactor blog-details.html ---
with open(os.path.join(frontend_dir, 'blog-details.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('<section')
e = text.find('<footer')

if s != -1 and e != -1:
    content = text[s:e]

    final_blog_details = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}{{ post.title|default:'Nordic Travel Article' }} | Nord Velocity Blog{% endblock %}\n\n{% block seo %}\n<meta name=\"description\" content=\"{{ post.excerpt|default:post.title }}\">\n<meta property=\"og:title\" content=\"{{ post.title }}\">\n{% if post.featured_image %}\n<meta property=\"og:image\" content=\"{{ request.scheme }}://{{ request.get_host }}{{ post.featured_image.url }}\">\n{% endif %}\n{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"

    with open(os.path.join(frontend_dir, 'blog-details.html'), 'w', encoding='utf-8') as f:
        f.write(final_blog_details)
    print("blog-details.html converted!")
