import os

frontend_dir = os.path.join('d:\\', 'My Works', 'Nord Velocity', 'Frontend')

for fname in ['about.html', 'faq.html', 'contact.html']:
    bak_path = os.path.join(frontend_dir, fname + '.bak')
    with open(bak_path, 'r', encoding='utf-8') as f:
        text = f.read()

    s = text.find('<section')
    e = text.find('<footer')

    if s != -1 and e != -1:
        content = text[s:e]

        # Specific enhancement for contact.html: CSRF token, POST method, and message display
        if fname == 'contact.html':
            # Ensure form has method="POST" and {% csrf_token %}
            form_tag = '<form class="contact-form"'
            if form_tag in content:
                content = content.replace(form_tag, '<form class="contact-form" method="POST">\n                    {% csrf_token %}')
            elif '<form' in content:
                content = content.replace('<form', '<form method="POST">\n                    {% csrf_token %}', 1)

            # Insert message alerts right above the form
            alerts = """{% if messages %}
            <div style="margin-bottom: 1.5rem;">
                {% for msg in messages %}
                <div style="padding: 1rem; border-radius: 8px; font-weight: 500; background: {% if msg.tags == 'success' %}#ECFDF5; color: #065F46; border: 1px solid #A7F3D0;{% else %}#FEF2F2; color: #991B1B; border: 1px solid #FECACA;{% endif %};">
                    {{ msg }}
                </div>
                {% endfor %}
            </div>
            {% endif %}"""

            content = content.replace('<!-- Contact Form -->', '<!-- Contact Form -->\n' + alerts)

        page_title = fname.replace('.html', '').capitalize()
        if page_title == 'Faq':
            page_title = 'FAQ'

        final_template = f"""{{% extends 'base.html' %}}
{{% load static %}}

{{% block title %}}{page_title} | Nord Velocity Luxury Nordic Travel{{% endblock %}}

{{% block content %}}
{content}
{{% endblock %}}
"""
        with open(os.path.join(frontend_dir, fname), 'w', encoding='utf-8') as f:
            f.write(final_template)
        print(f"{fname} converted successfully!")
