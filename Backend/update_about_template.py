import os

about_path = os.path.join('d:\\', 'My Works', 'Nord Velocity', 'Frontend', 'about.html')

with open(about_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('href="index.html"', 'href="{% url \'home\' %}"')
text = text.replace('href="contact.html"', 'href="{% url \'contact\' %}"')
text = text.replace('href="tour-packages.html"', 'href="{% url \'tours:list\' %}"')
text = text.replace('href="tour.html"', 'href="{% url \'tours:list\' %}"')
text = text.replace('href="destination.html"', 'href="{% url \'tours:destination_list\' %}"')
text = text.replace('href="transport.html"', 'href="{% url \'chauffeur:hub\' %}"')

text = text.replace(
    '<span class="text-dark">Nord Velocity,</span> Trusted Travel Partner!',
    '<span class="text-dark">{{ site_settings.site_name }},</span> Trusted Travel Partner!'
)
text = text.replace(
    'We are an independent travel agency dedicated to arranging tailored travel experiences across Finland and the Nordics.',
    '{{ site_settings.tagline }}'
)

with open(about_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('about.html updated with dynamic site_settings!')
