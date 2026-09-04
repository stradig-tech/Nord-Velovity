import os, django, re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser

admin = CustomUser.objects.filter(is_superuser=True).first()
c = Client()
c.force_login(admin)

pages_to_check = [
    '/',
    '/tours/',
    '/tours/lapland-northern-lights-glass-igloo-escape/',
    '/transport/',
    '/admin/',
    '/custom-admin/',
    '/about/',
    '/faq/',
    '/contact/',
    '/blog/',
    '/accounts/dashboard/',
    '/accounts/my-bookings/',
    '/accounts/login/'
]

broken_assets = []

for page in pages_to_check:
    res = c.get(page)
    html = res.content.decode('utf-8')
    
    # Find all src and href for images, css, js
    matches = re.findall(r'(?:src|href)=["\']([^"\']+\.(?:png|jpg|jpeg|svg|css|js|webp))["\']', html, re.I)
    for asset in set(matches):
        if asset.startswith(('http://', 'https://')):
            continue
        
        # In browser, if asset doesn't start with '/', it resolves relative to current page directory!
        if asset.startswith('/'):
            target = asset
        else:
            if page.endswith('/'):
                target = page + asset
            else:
                target = page.rsplit('/', 1)[0] + '/' + asset
        
        asset_res = c.get(target)
        if asset_res.status_code == 404:
            broken_assets.append((page, asset, target))

print(f"Total broken (404) static assets found: {len(broken_assets)}")
for page, asset, target in broken_assets[:30]:
    print(f"[{page}] -> raw: '{asset}' -> requested: '{target}' (404 Not Found)")
