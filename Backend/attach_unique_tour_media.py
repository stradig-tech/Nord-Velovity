import os, shutil, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.conf import settings
from django.core.files import File
from tours.models import Tour, TourMedia

media_dir = os.path.join(settings.MEDIA_ROOT, 'tours', 'media')
os.makedirs(media_dir, exist_ok=True)

frontend_images = os.path.abspath('../Frontend/images')

tour_image_map = {
    'helsinki-city-suomenlinna-tour': os.path.join(frontend_images, 'packages', '65535_54274700516_8d0245d0c1_b_800_600_nofilter.jpg'),
    'lapland-northern-lights-glass-igloo-escape': os.path.join(frontend_images, 'packages', '31337_54406107252_f4ca19b35f_c_800_600_nofilter.jpg'),
    'levi-arctic-adventure-snowmobiling-husky-safari': os.path.join(frontend_images, 'citys', '15-Kilometers-Self-Driving-Husky-Tour-in-Levi1-2-550x358.jpg'),
    'finnish-lakeland-luxury-sauna-villa-retreat': os.path.join(frontend_images, 'packages', '7111_13901216855_cca37b8607_b_800_600_nofilter.jpg'),
    'helsinki-archipelago-modern-nordic-design-journey': os.path.join(frontend_images, 'packages', '65535_54407223633_9fc6ebf472_c_800_600_nofilter.jpg'),
}

for slug, src_path in tour_image_map.items():
    tour = Tour.objects.filter(slug=slug).first()
    if not tour:
        # Try matching by title keywords
        if 'helsinki-city' in slug:
            tour = Tour.objects.filter(title__icontains='Helsinki City').first()
        elif 'lapland' in slug:
            tour = Tour.objects.filter(title__icontains='Lapland Northern Lights').first()
        elif 'levi' in slug:
            tour = Tour.objects.filter(title__icontains='Levi Arctic').first()
        elif 'lakeland' in slug:
            tour = Tour.objects.filter(title__icontains='Lakeland').first()
        elif 'archipelago' in slug:
            tour = Tour.objects.filter(title__icontains='Archipelago').first()

    if tour and os.path.exists(src_path):
        filename = os.path.basename(src_path)
        dest_path = os.path.join(media_dir, filename)
        shutil.copy2(src_path, dest_path)
        
        # Clear existing media and add new distinct cover image
        tour.media.all().delete()
        rel_path = os.path.join('tours', 'media', filename).replace('\\', '/')
        
        TourMedia.objects.create(
            tour=tour,
            file=rel_path,
            alt_text=f"{tour.title} Cover Photo",
            media_type='IMAGE',
            is_hero=True,
            sort_order=1
        )
        print(f"[OK] Attached unique image to tour: {tour.title} -> {rel_path}")
    else:
        print(f"[WARN] Could not find tour or file for {slug}: tour={tour}, exists={os.path.exists(src_path)}")

print("\nVerifying TourMedia records in DB:")
for t in Tour.objects.all():
    m = t.media.first()
    print(f"- {t.title}: media file={m.file if m else 'None'}")
