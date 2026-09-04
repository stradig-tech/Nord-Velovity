import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser
from core.models import SiteSetting, FAQItem, Testimonial

admin = CustomUser.objects.filter(is_superuser=True).first()
c = Client()
c.force_login(admin)

pages = [
    ('/', 'Home'),
    ('/about/', 'About Us'),
    ('/faq/', 'FAQ Center'),
    ('/contact/', 'Contact Concierge'),
    ('/tours/', 'Tours Catalog'),
    ('/transport/', 'VIP Chauffeur Hub'),
    ('/blog/', 'Blog & Stories'),
    ('/admin/core/sitesetting/', 'Admin Site Settings'),
    ('/admin/core/faqitem/', 'Admin FAQs'),
    ('/admin/core/testimonial/', 'Admin Testimonials'),
]

print("--- TESTING DYNAMIC PAGES & ADMIN PANEL ---")
for url, label in pages:
    res = c.get(url, follow=True)
    print(f"[{res.status_code}] {label:28} -> {url}")
    assert res.status_code == 200, f"Failed at {url}"

# Verify dynamic content appears in HTML
home_html = c.get('/').content.decode('utf-8')
setting = SiteSetting.objects.first()
assert setting.site_name in home_html, "site_name not in home HTML"
assert setting.contact_phone in home_html, "contact_phone not in home HTML"
print("\n[VERIFIED] Database site_name and contact_phone dynamically rendered on homepage!")

faq_html = c.get('/faq/').content.decode('utf-8')
faq1 = FAQItem.objects.first()
assert faq1.question in faq_html, "FAQ question not in faq HTML"
print("[VERIFIED] Database FAQ items dynamically rendered on /faq/ page!")

print("\nALL DYNAMIC DATA VERIFICATION PASSED SUCCESSFULLY!")
