import os

frontend_dir = os.path.join('d:\\', 'My Works', 'Nord Velocity', 'Frontend')

# --- 1. Refactor destination.html ---
with open(os.path.join(frontend_dir, 'destination.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('<section')
e = text.find('<footer')

if s != -1 and e != -1:
    content = text[s:e]

    final_dest = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}Top Nordic Destinations | Nord Velocity{% endblock %}\n\n{% block seo %}\n<meta name=\"description\" content=\"Explore Finland, Lapland, Helsinki, Rovaniemi, and iconic Nordic destinations.\">\n{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"

    with open(os.path.join(frontend_dir, 'destination.html'), 'w', encoding='utf-8') as f:
        f.write(final_dest)
    print("destination.html converted!")

# --- 2. Refactor destination-details.html ---
with open(os.path.join(frontend_dir, 'destination-details.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('<section')
e = text.find('<footer')

if s != -1 and e != -1:
    content = text[s:e]

    final_dest_details = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}{{ destination.name|default:'Destination Guide' }} | Nord Velocity Travel{% endblock %}\n\n{% block seo %}\n<meta name=\"description\" content=\"{{ destination.description|default:destination.name }}\">\n<meta property=\"og:title\" content=\"{{ destination.name }}\">\n{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"

    with open(os.path.join(frontend_dir, 'destination-details.html'), 'w', encoding='utf-8') as f:
        f.write(final_dest_details)
    print("destination-details.html converted!")
