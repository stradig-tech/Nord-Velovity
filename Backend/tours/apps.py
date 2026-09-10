from django.apps import AppConfig


class ToursConfig(AppConfig):
    name = 'tours'

    def ready(self):
        try:
            from .models import Country, Destination
            flag_map = {
                'finland': 'countries/flags/flag_finland.svg',
                'sweden': 'countries/flags/flag_sweden.svg',
                'norway': 'countries/flags/flag_norway.svg',
                'denmark': 'countries/flags/flag_denmark.svg',
                'iceland': 'countries/flags/flag_iceland.svg',
            }
            for c in Country.objects.all():
                slug_lower = c.slug.lower()
                for key, flag_path in flag_map.items():
                    if key in slug_lower and (not c.flag_icon or c.flag_icon == ''):
                        c.flag_icon = flag_path
                        c.save(update_fields=['flag_icon'])
                        break

            country_slug_map = {c.slug.lower(): c for c in Country.objects.all()}
            country_name_map = {c.name.lower(): c for c in Country.objects.all()}

            dest_country_assign = {
                'copenhagen': 'denmark',
                'helsinki': 'finland',
                'stockholm': 'sweden',
                'tromso': 'norway',
                'tromsø': 'norway',
                'kiruna': 'sweden',
                'abisko': 'sweden',
                'oslo': 'norway',
                'rovaniemi': 'finland',
                'turku': 'finland',
                'finnish': 'finland',
                'lakeland': 'finland',
                'tampere': 'finland',
                'levi': 'finland',
            }
            for d in Destination.objects.all():
                d_slug = d.slug.lower()
                d_name = d.name.lower()
                if not d.country:
                    for keyword, c_key in dest_country_assign.items():
                        if keyword in d_slug or keyword in d_name:
                            matched_c = country_slug_map.get(c_key) or country_name_map.get(c_key)
                            if matched_c:
                                d.country = matched_c
                                d.save(update_fields=['country'])
                                break
        except Exception:
            pass
