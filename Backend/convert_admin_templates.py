import os

frontend_dir = os.path.join('d:\\', 'My Works', 'Nord Velocity', 'Frontend')

# --- 1. Create admin-base.html ---
admin_base = """{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Executive Portal | Nord Velocity{% endblock %}</title>
    <!-- Google Fonts: Inter -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Phosphor Icons -->
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{% static 'style.css' %}">
</head>
<body class="admin-body">

    <!-- Admin Sidebar -->
    <aside class="admin-sidebar">
        <div class="admin-brand" style="padding: 1.5rem 1rem;">
            <a href="{% url 'home' %}" class="logo" style="display: flex; justify-content: center;">
                <img src="{% static 'images/brand/logo bg-transparent.png' %}" alt="Nord Velocity" style="height: 70px; width: auto; object-fit: contain;">
            </a>
        </div>
        
        <nav class="admin-nav">
            <p class="admin-nav-title">Management</p>
            <ul>
                <li><a href="{% url 'custom_admin:dashboard' %}"><i class="ph-bold ph-squares-four" style="margin-right: 8px;"></i> Dashboard</a></li>
                <li><a href="{% url 'custom_admin:bookings' %}"><i class="ph-bold ph-calendar-check" style="margin-right: 8px;"></i> Bookings</a></li>
                <li><a href="{% url 'custom_admin:guests' %}"><i class="ph-bold ph-users" style="margin-right: 8px;"></i> Guests</a></li>
                <li><a href="{% url 'custom_admin:reviews' %}"><i class="ph-bold ph-star" style="margin-right: 8px;"></i> Reviews</a></li>
                <li><a href="{% url 'custom_admin:earnings' %}"><i class="ph-bold ph-currency-eur" style="margin-right: 8px;"></i> Earnings</a></li>
                <li><a href="{% url 'custom_admin:settings' %}"><i class="ph-bold ph-gear" style="margin-right: 8px;"></i> Admin Settings</a></li>
                <li><a href="/admin/" target="_blank"><i class="ph-bold ph-database" style="margin-right: 8px;"></i> Django DB Admin</a></li>
            </ul>
        </nav>
        
        <div class="admin-sidebar-footer">
            <a href="{% url 'accounts:logout' %}"><i class="ph-bold ph-sign-out"></i> Log out</a>
            <a href="{% url 'home' %}"><i class="ph-bold ph-house"></i></a>
        </div>
    </aside>

    <!-- Admin Main Content -->
    <main class="admin-main">
        <!-- Admin Top Header -->
        <header class="admin-header">
            <div class="admin-search">
                <i class="ph-bold ph-magnifying-glass"></i>
                <input type="text" placeholder="Search bookings, guests...">
            </div>
            
            <div class="admin-user-nav">
                <button class="admin-nav-icon"><i class="ph-bold ph-bell"></i></button>
                <div class="admin-profile">
                    <div style="width: 38px; height: 38px; border-radius: 50%; background: #4F46E5; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                        {{ request.user.first_name|first|default:"A" }}
                    </div>
                    <span>{{ request.user.get_full_name|default:request.user.email }}</span>
                </div>
            </div>
        </header>

        {% if messages %}
        <div style="padding: 1rem 2rem;">
            {% for msg in messages %}
            <div style="padding: 0.75rem 1.25rem; border-radius: 8px; font-weight: 500; background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; margin-bottom: 0.5rem;">
                {{ msg }}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% block admin_content %}
        {% endblock %}
    </main>

    {% block extra_js %}
    {% endblock %}
</body>
</html>
"""

with open(os.path.join(frontend_dir, 'admin-base.html'), 'w', encoding='utf-8') as f:
    f.write(admin_base)
print("admin-base.html created!")

# --- 2. Convert all 8 admin templates to extend admin-base.html ---
admin_templates = [
    ('admin-dashboard.html', 'Dashboard Overview'),
    ('admin-bookings.html', 'Reservations Management'),
    ('admin-booking-detail.html', 'Booking Details'),
    ('admin-earnings.html', 'Financial Reports & Earnings'),
    ('admin-guest-list.html', 'Customer & Guest Directory'),
    ('admin-guest-detail.html', 'Guest Profile & History'),
    ('admin-reviews.html', 'Customer Reviews Moderation'),
    ('admin-settings.html', 'Platform & Portal Settings'),
]

for fname, title in admin_templates:
    bak_path = os.path.join(frontend_dir, fname + '.bak')
    with open(bak_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Find where header ends
    header_end = text.find('</header>')
    if header_end != -1:
        # Content is after </header> up to </main>
        main_end = text.rfind('</main>')
        if main_end != -1:
            body_content = text[header_end + len('</header>'):main_end]
        else:
            body_content = text[header_end + len('</header>'):]
    else:
        body_content = text

    final_admin_page = f"""{{% extends 'admin-base.html' %}}
{{% load static %}}

{{% block title %}}{title} | Nord Velocity Portal{{% endblock %}}

{{% block admin_content %}}
{body_content}
{{% endblock %}}
"""
    with open(os.path.join(frontend_dir, fname), 'w', encoding='utf-8') as f:
        f.write(final_admin_page)
    print(f"{fname} converted successfully!")
