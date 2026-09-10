from django.apps import AppConfig


class ContentConfig(AppConfig):
    name = 'content'

    def ready(self):
        try:
            from .models import BlogPost
            for post in BlogPost.objects.all():
                if not post.featured_image or post.featured_image == '':
                    slug_str = f"{post.slug} {post.title}".lower()
                    if 'sauna' in slug_str:
                        post.featured_image = 'blog/sauna_loyly.jpg'
                        post.save(update_fields=['featured_image'])
                    elif 'northern' in slug_str or 'light' in slug_str or 'lapland' in slug_str or 'aurora' in slug_str:
                        post.featured_image = 'blog/northern_lights_lapland.jpg'
                        post.save(update_fields=['featured_image'])
        except Exception:
            pass
