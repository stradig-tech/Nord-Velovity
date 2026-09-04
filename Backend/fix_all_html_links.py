import os, re

frontend_dir = os.path.abspath('../Frontend')

url_mapping = {
    'index.html': "{% url 'home' %}",
    'tour-packages.html': "{% url 'tours:list' %}",
    'tour.html': "{% url 'tours:list' %}",
    'tour-details.html': "{% url 'tours:list' %}",
    'destination.html': "{% url 'tours:destination_list' %}",
    'destination-details.html': "{% url 'tours:destination_list' %}",
    'transport.html': "{% url 'chauffeur:hub' %}",
    'cab-list.html': "{% url 'chauffeur:list' %}",
    'cab-details.html': "{% url 'chauffeur:list' %}",
    'login.html': "{% url 'accounts:login' %}",
    'signup.html': "{% url 'accounts:signup' %}",
    'user-dashboard.html': "{% url 'accounts:dashboard' %}",
    'my-bookings.html': "{% url 'accounts:my_bookings' %}",
    'my-wishlist.html': "{% url 'accounts:my_wishlist' %}",
    'settings.html': "{% url 'accounts:settings' %}",
    'payment-details.html': "{% url 'accounts:my_bookings' %}",
    'view-itinerary.html': "{% url 'accounts:my_bookings' %}",
    'contact.html': "{% url 'contact' %}",
    'about.html': "{% url 'about' %}",
    'faq.html': "{% url 'faq' %}",
    'blog.html': "{% url 'content:blog_list' %}",
    'blog-details.html': "{% url 'content:blog_list' %}",
}

total_files_updated = 0
total_replacements = 0

for root, dirs, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith('.html') and not f.endswith('.bak'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            orig_content = content
            for old_html, new_url in url_mapping.items():
                # Replace href="xyz.html" or href='xyz.html'
                pattern1 = rf'href=["\']{re.escape(old_html)}["\']'
                content = re.sub(pattern1, f'href="{new_url}"', content)
                # Replace onclick="window.location.href='xyz.html'"
                pattern2 = rf'window\.location\.href=["\']{re.escape(old_html)}["\']'
                content = re.sub(pattern2, f"window.location.href='{new_url}'", content)

            if content != orig_content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(content)
                total_files_updated += 1

print(f"Replaced all static .html links across {total_files_updated} templates with Django dynamic URL tags!")
