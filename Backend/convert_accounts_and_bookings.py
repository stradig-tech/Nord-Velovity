import os

frontend_dir = os.path.join('d:\\', 'My Works', 'Nord Velocity', 'Frontend')

# --- 1. Refactor login.html ---
with open(os.path.join(frontend_dir, 'login.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()
s = text.find('<main')
e = text.find('<footer')
if s != -1 and e != -1:
    content = text[s:e]
    # Replace static form with Django POST form
    content = content.replace(
        '<form class="auth-form" action="index.html">',
        '<form class="auth-form" method="POST">\n                {% csrf_token %}\n                {% if messages %}\n                <div style="margin-bottom: 1rem;">\n                    {% for msg in messages %}\n                    <div style="padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.9rem; background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; margin-bottom: 0.5rem;">{{ msg }}</div>\n                    {% endfor %}\n                </div>\n                {% endif %}'
    )
    content = content.replace('id="email"', 'id="email" name="email"')
    content = content.replace('id="password"', 'id="password" name="password"')
    content = content.replace('href="signup.html"', 'href="{% url \'accounts:signup\' %}"')

    final_login = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}Sign In | Nord Velocity{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"
    with open(os.path.join(frontend_dir, 'login.html'), 'w', encoding='utf-8') as f:
        f.write(final_login)
    print("login.html converted!")

# --- 2. Refactor signup.html ---
with open(os.path.join(frontend_dir, 'signup.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()
s = text.find('<main')
if s == -1: s = text.find('<section')
e = text.find('<footer')
if s != -1 and e != -1:
    content = text[s:e]
    content = content.replace(
        '<form class="auth-form"',
        '<form class="auth-form" method="POST">\n                {% csrf_token %}\n                {% if messages %}\n                <div style="margin-bottom: 1rem;">\n                    {% for msg in messages %}\n                    <div style="padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.9rem; background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; margin-bottom: 0.5rem;">{{ msg }}</div>\n                    {% endfor %}\n                </div>\n                {% endif %}'
    )
    content = content.replace('id="firstName"', 'id="firstName" name="first_name"')
    content = content.replace('id="lastName"', 'id="lastName" name="last_name"')
    content = content.replace('id="email"', 'id="email" name="email"')
    content = content.replace('id="phone"', 'id="phone" name="phone"')
    content = content.replace('id="password"', 'id="password" name="password"')
    content = content.replace('id="confirmPassword"', 'id="confirmPassword" name="confirm_password"')
    content = content.replace('href="login.html"', 'href="{% url \'accounts:login\' %}"')

    final_signup = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}Create Account | Nord Velocity{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"
    with open(os.path.join(frontend_dir, 'signup.html'), 'w', encoding='utf-8') as f:
        f.write(final_signup)
    print("signup.html converted!")

# --- 3. Refactor user-dashboard.html ---
with open(os.path.join(frontend_dir, 'user-dashboard.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()
s = text.find('<section')
e = text.find('<footer')
if s != -1 and e != -1:
    content = text[s:e]
    content = content.replace('href="login.html"', 'href="{% url \'accounts:logout\' %}"')
    final_dash = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}Dashboard | Nord Velocity Customer Portal{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"
    with open(os.path.join(frontend_dir, 'user-dashboard.html'), 'w', encoding='utf-8') as f:
        f.write(final_dash)
    print("user-dashboard.html converted!")

# --- 4. Refactor my-bookings.html ---
with open(os.path.join(frontend_dir, 'my-bookings.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()
s = text.find('<section')
e = text.find('<footer')
if s != -1 and e != -1:
    content = text[s:e]
    final_bookings = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}My Bookings | Nord Velocity{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"
    with open(os.path.join(frontend_dir, 'my-bookings.html'), 'w', encoding='utf-8') as f:
        f.write(final_bookings)
    print("my-bookings.html converted!")

# --- 5. Refactor my-wishlist.html ---
with open(os.path.join(frontend_dir, 'my-wishlist.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()
s = text.find('<section')
e = text.find('<footer')
if s != -1 and e != -1:
    content = text[s:e]
    final_wish = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}My Saved Tours | Nord Velocity{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"
    with open(os.path.join(frontend_dir, 'my-wishlist.html'), 'w', encoding='utf-8') as f:
        f.write(final_wish)
    print("my-wishlist.html converted!")

# --- 6. Refactor settings.html ---
with open(os.path.join(frontend_dir, 'settings.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()
s = text.find('<section')
e = text.find('<footer')
if s != -1 and e != -1:
    content = text[s:e]
    final_settings = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}Account Settings | Nord Velocity{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"
    with open(os.path.join(frontend_dir, 'settings.html'), 'w', encoding='utf-8') as f:
        f.write(final_settings)
    print("settings.html converted!")

# --- 7. Refactor booking-summary.html with Stripe button ---
with open(os.path.join(frontend_dir, 'booking-summary.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()
s = text.find('<section')
e = text.find('<footer')
if s != -1 and e != -1:
    content = text[s:e]
    
    # Inject dynamic Stripe payment button
    content = content.replace(
        '<a href="booking-success.html" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 1rem; font-size: 1.1rem; font-weight: 700; border-radius: 8px; margin-bottom: 1rem; text-decoration: none; display: flex;">Proceed to Payment</a>',
        '<button type="button" id="stripePayBtn" onclick="initiateStripeCheckout()" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 1rem; font-size: 1.1rem; font-weight: 700; border-radius: 8px; margin-bottom: 1rem; text-decoration: none; display: flex; cursor: pointer;">Pay with Stripe (Secure Checkout)</button>'
    )
    
    stripe_js = """{% block extra_js %}
<script>
async function initiateStripeCheckout() {
    const btn = document.getElementById('stripePayBtn');
    btn.innerText = 'Redirecting to Stripe...';
    btn.disabled = true;
    try {
        const res = await fetch('/payments/checkout/{{ booking.id }}/');
        const data = await res.json();
        if (data.checkout_url) {
            window.location.href = data.checkout_url;
        } else {
            alert(data.error || 'Failed to initiate payment.');
            btn.innerText = 'Pay with Stripe (Secure Checkout)';
            btn.disabled = false;
        }
    } catch (err) {
        alert('Network error connecting to Stripe gateway.');
        btn.innerText = 'Pay with Stripe (Secure Checkout)';
        btn.disabled = false;
    }
}
</script>
{% endblock %}"""

    final_summary = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}Booking Review & Payment | Nord Velocity{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n\n" + stripe_js
    with open(os.path.join(frontend_dir, 'booking-summary.html'), 'w', encoding='utf-8') as f:
        f.write(final_summary)
    print("booking-summary.html converted with Stripe Checkout button!")

# --- 8. Refactor booking-success.html ---
with open(os.path.join(frontend_dir, 'booking-success.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()
s = text.find('<section')
e = text.find('<footer')
if s != -1 and e != -1:
    content = text[s:e]
    content = content.replace('href="user-dashboard.html"', 'href="{% url \'accounts:dashboard\' %}"')
    content = content.replace('href="my-bookings.html"', 'href="{% url \'accounts:my_bookings\' %}"')
    final_success = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}Booking Confirmed! | Nord Velocity{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"
    with open(os.path.join(frontend_dir, 'booking-success.html'), 'w', encoding='utf-8') as f:
        f.write(final_success)
    print("booking-success.html converted!")
