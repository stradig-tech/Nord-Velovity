import os

frontend_dir = os.path.join('d:\\', 'My Works', 'Nord Velocity', 'Frontend')

mapping = [
    ('tour.html', 'Curated Nordic Tours | Nord Velocity'),
    ('view-itinerary.html', 'Tour Itinerary | Nord Velocity'),
    ('tour-booking.html', 'Reserve Tour | Nord Velocity'),
    ('tour-traveler.html', 'Traveler Details | Nord Velocity'),
    ('tour-payment.html', 'Payment | Nord Velocity'),
    ('payment-details.html', 'Payment Details | Nord Velocity')
]

for fname, title in mapping:
    bak_path = os.path.join(frontend_dir, fname + '.bak')
    with open(bak_path, 'r', encoding='utf-8') as f:
        text = f.read()

    s = text.find('<section')
    if s == -1: s = text.find('<main')
    e = text.find('<footer')

    if s != -1 and e != -1:
        content = text[s:e]

        final_template = f"""{{% extends 'base.html' %}}
{{% load static %}}

{{% block title %}}{title}{{% endblock %}}

{{% block content %}}
{content}
{{% endblock %}}
"""
        with open(os.path.join(frontend_dir, fname), 'w', encoding='utf-8') as f:
            f.write(final_template)
        print(f"{fname} converted successfully!")
