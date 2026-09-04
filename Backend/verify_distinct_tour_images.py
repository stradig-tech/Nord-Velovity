import os, django, re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser

admin = CustomUser.objects.filter(is_superuser=True).first()
c = Client()
c.force_login(admin)

res = c.get('/admin/')
html = res.content.decode('utf-8')

matches = re.findall(r'<div class="admin-package-card">\s*<img src="([^"]+)" alt="([^"]+)"', html)

print(f"Total tour cards rendered on /admin/: {len(matches)}")
for img_src, title in matches:
    img_res = c.get(img_src)
    print(f"- Tour: {title:52} | Status: [{img_res.status_code}] | Image: {img_src}")
    assert img_res.status_code == 200, f"Image 404 at {img_src}"

images = [img for img, _ in matches]
unique_images = set(images)
print(f"\nTotal tour cards: {len(images)}, Unique photos: {len(unique_images)}")
assert len(images) == len(unique_images), "Images are still duplicated!"
print("SUCCESS: Every single tour on the admin dashboard now displays its own unique photo!")

# Check Homepage
res_home = c.get('/')
html_home = res_home.content.decode('utf-8')
home_matches = re.findall(r'<div class="tour-card">\s*<div class="tour-img-box">\s*<img src="([^"]+)" alt="([^"]+)"', html_home)

print(f"\nTotal homepage tour cards: {len(home_matches)}")
for img_src, title in home_matches:
    img_res = c.get(img_src)
    print(f"- Tour: {title:52} | Status: [{img_res.status_code}] | Image: {img_src}")
    assert img_res.status_code == 200, f"Image 404 at {img_src}"

home_images = [img for img, _ in home_matches]
assert len(home_images) == len(set(home_images)), "Homepage has duplicate images!"
print("SUCCESS: Homepage also displays unique, distinct photos for every tour!")

