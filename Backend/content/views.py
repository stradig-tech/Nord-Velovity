from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost, BlogCategory, BlogTag

def blog_list_view(request):
    """
    Renders the blog catalog (blog.html) with category, tag, and keyword filtering.
    """
    posts = BlogPost.objects.filter(status='PUBLISHED').select_related('author').prefetch_related('categories', 'tags')

    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(categories__slug=category_slug)

    tag_slug = request.GET.get('tag')
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)

    search_query = request.GET.get('q')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(body__icontains=search_query)
        )

    posts = posts.order_by('-publish_date', '-created_at')

    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = BlogCategory.objects.all().order_by('sort_order')
    recent_posts = BlogPost.objects.filter(status='PUBLISHED').order_by('-created_at')[:4]
    tags = BlogTag.objects.all()[:12]

    context = {
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'categories': categories,
        'recent_posts': recent_posts,
        'tags': tags,
        'selected_category': category_slug,
        'selected_tag': tag_slug,
        'search_query': search_query,
    }
    return render(request, 'content/blog.html', context)


def blog_detail_view(request, slug):
    """
    Renders the full article view (blog-details.html) with rich typography and related posts.
    """
    post = get_object_or_404(
        BlogPost.objects.select_related('author').prefetch_related('categories', 'tags', 'related_tours'),
        slug=slug,
        status='PUBLISHED'
    )

    # Fetch 3 related posts from same categories
    related_posts = BlogPost.objects.filter(
        status='PUBLISHED',
        categories__in=post.categories.all()
    ).exclude(id=post.id).distinct()[:3]

    categories = BlogCategory.objects.all().order_by('sort_order')
    recent_posts = BlogPost.objects.filter(status='PUBLISHED').order_by('-created_at')[:4]

    context = {
        'post': post,
        'related_posts': related_posts,
        'categories': categories,
        'recent_posts': recent_posts,
    }
    return render(request, 'content/blog-details.html', context)
