import os

base_path = os.path.join('d:\\', 'My Works', 'Nord Velocity', 'Frontend', 'base.html')

with open(base_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace static links with dynamic Django urls
text = text.replace('href="index.html"', 'href="{% url \'home\' %}"')
text = text.replace('href="destination.html"', 'href="{% url \'tours:destination_list\' %}"')
text = text.replace('href="tour-packages.html"', 'href="{% url \'tours:list\' %}"')
text = text.replace('href="tour.html"', 'href="{% url \'tours:list\' %}"')
text = text.replace('href="transport.html"', 'href="{% url \'chauffeur:hub\' %}"')
text = text.replace('href="about.html"', 'href="{% url \'about\' %}"')
text = text.replace('href="faq.html"', 'href="{% url \'faq\' %}"')
text = text.replace('href="contact.html"', 'href="{% url \'contact\' %}"')
text = text.replace('href="blog.html"', 'href="{% url \'content:blog_list\' %}"')
text = text.replace('href="login.html"', 'href="{% url \'accounts:login\' %}"')
text = text.replace('href="signup.html"', 'href="{% url \'accounts:signup\' %}"')

# Dynamic Auth button in navbar
old_auth = '<div class="nav-actions"><a href="{% url \'accounts:login\' %}" class="btn btn-primary">Log In / Sign Up</a></div>'
new_auth = '''<div class="nav-actions">
    {% if request.user.is_authenticated %}
        <a href="{% url 'accounts:dashboard' %}" class="btn btn-primary" style="display: inline-flex; align-items: center; gap: 0.5rem;">
            <i class="ph-bold ph-user-circle"></i> {{ request.user.first_name|default:request.user.email|truncatechars:15 }}
        </a>
    {% else %}
        <a href="{% url 'accounts:login' %}" class="btn btn-primary">Log In / Sign Up</a>
    {% endif %}
</div>'''
text = text.replace(old_auth, new_auth)

# Dynamic top bar currency & user icon
text = text.replace(
    '<div class="currency-selector">                     <i class="ph ph-globe"></i> EUR &euro;                 </div>',
    '<div class="currency-selector"><i class="ph ph-globe"></i> {{ site_settings.default_currency }} {{ site_settings.currency_symbol }}</div>'
)

# Dynamic Footer info
old_footer_info = '''<h5 class="footer-agency-name">Nord Velocity Travel Agency</h5>                     <p class="footer-address">                         Mannerheimintie 12, 5th Floor<br>                         00100 Helsinki, Finland                     </p>                     <div class="footer-socials">                         <a href="#"><i class="ph-fill ph-facebook-logo"></i></a>                         <a href="#"><i class="ph-fill ph-linkedin-logo"></i></a>                         <a href="#"><i class="ph-fill ph-youtube-logo"></i></a>                         <a href="#"><i class="ph-fill ph-instagram-logo"></i></a>                     </div>'''

new_footer_info = '''<h5 class="footer-agency-name">{{ site_settings.site_name }}</h5>
                    <p class="footer-address">
                        {{ site_settings.office_address }}<br>
                        Tel: <a href="tel:{{ site_settings.contact_phone }}" style="color: inherit; text-decoration: none;">{{ site_settings.contact_phone }}</a><br>
                        Email: <a href="mailto:{{ site_settings.contact_email }}" style="color: inherit; text-decoration: none;">{{ site_settings.contact_email }}</a>
                    </p>
                    <div class="footer-socials">
                        {% if site_settings.facebook_url %}<a href="{{ site_settings.facebook_url }}" target="_blank"><i class="ph-fill ph-facebook-logo"></i></a>{% endif %}
                        {% if site_settings.linkedin_url %}<a href="{{ site_settings.linkedin_url }}" target="_blank"><i class="ph-fill ph-linkedin-logo"></i></a>{% endif %}
                        {% if site_settings.instagram_url %}<a href="{{ site_settings.instagram_url }}" target="_blank"><i class="ph-fill ph-instagram-logo"></i></a>{% endif %}
                    </div>'''

text = text.replace(old_footer_info, new_footer_info)

# Dynamic Copyright
text = text.replace(
    '&copy; 2026 Nord Velocity. All Rights Reserved.',
    '{{ site_settings.copyright_text }}'
)

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Frontend/base.html updated with dynamic site_settings and URLs!")
