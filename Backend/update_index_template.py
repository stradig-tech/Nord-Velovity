import os

index_path = os.path.join('d:\\', 'My Works', 'Nord Velocity', 'Frontend', 'index.html')

with open(index_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Dynamic Hero Titles
text = text.replace(
    '<h1 class="hero-title">Discover the Extraordinary</h1>                 <p class="hero-subtitle">We curate exceptional travel experiences & 10,000+ our trusted travelers world-wide.</p>',
    '<h1 class="hero-title">{{ site_settings.hero_title }}</h1>                 <p class="hero-subtitle">{{ site_settings.hero_subtitle }}</p>'
)

# 2. Dynamic Best Selling Tours
old_tours_section_start = '<div class="tours-grid">'
tours_grid_idx = text.find(old_tours_section_start)
tours_grid_end = text.find('</div>                          <div class="view-all-container">', tours_grid_idx)

if tours_grid_idx != -1 and tours_grid_end != -1:
    dynamic_tours_html = '''<div class="tours-grid">
                {% if featured_tours %}
                    {% for tour in featured_tours %}
                    <div class="tour-card">
                        <div class="tour-img-box">
                            {% if tour.media.first %}
                                <img src="{{ tour.media.first.file.url }}" alt="{{ tour.title }}" class="tour-img" style="object-fit: cover;">
                            {% else %}
                                <img src="{% static 'images/packages/31337_54406107252_f4ca19b35f_c_800_600_nofilter.jpg' %}" alt="{{ tour.title }}" class="tour-img" style="object-fit: cover;">
                            {% endif %}
                            <div class="badge-top-left"><i class="ph ph-heart"></i></div>
                            <div class="badge-stack-right">
                                {% if tour.is_featured %}<span class="tour-badge green-bg">Featured</span>{% endif %}
                                <span class="tour-badge yellow-bg text-dark">{{ tour.travel_style.name|default:"Luxury Tour" }}</span>
                            </div>
                        </div>
                        <div class="tour-body">
                            <div class="tour-rating">
                                <i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i>
                                <span class="rating-val">(5.0)</span>
                            </div>
                            <h4 class="tour-title">{{ tour.title }}</h4>
                            <div class="tour-meta">
                                <span class="meta-item"><i class="ph ph-map-pin"></i> {{ tour.destination.name }}, Finland</span>
                                <span class="meta-item"><i class="ph ph-clock"></i> {{ tour.duration_text }}</span>
                            </div>
                            <div class="tour-footer">
                                <div class="tour-price-box">
                                    <span class="price-label">Starting From</span>
                                    <div class="price-display">
                                        <span class="price-main">{{ site_settings.currency_symbol }}{{ tour.pricing.first.price|default:"750"|floatformat:0 }}</span><span class="price-sub">/per person</span>
                                    </div>
                                </div>
                                <a href="{% url 'tours:detail' tour.slug %}" class="btn btn-primary rounded-pill" style="text-decoration: none; display: inline-block;">View Tour</a>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="grid-column: 1/-1; text-align: center; color: #64748B;">No tours currently published.</p>
                {% endif %}
            '''
    text = text[:tours_grid_idx] + dynamic_tours_html + text[tours_grid_end:]

# 3. Dynamic Testimonials
old_testi_start = '<div class="testimonials-track">'
testi_start_idx = text.find(old_testi_start)
testi_end_idx = text.find('</div>             </div>              <!-- Footer -->', testi_start_idx)

if testi_start_idx != -1 and testi_end_idx != -1:
    dynamic_testi_html = '''<div class="testimonials-track" style="display: flex; gap: 1.5rem; overflow-x: auto; padding-bottom: 1rem;">
                    {% if testimonials %}
                        {% for t in testimonials %}
                        <div class="testi-card" style="flex: 0 0 340px; background: white; border-radius: 16px; padding: 1.75rem; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                            <div class="testi-card-header" style="margin-bottom: 1rem;">
                                <div class="testi-rating-dots" style="color: #F59E0B; font-size: 1.1rem;">
                                    {% for i in "12345" %}<i class="ph-fill ph-star"></i>{% endfor %}
                                </div>
                            </div>
                            <h4 class="testi-title" style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;">{{ t.tour_name|default:"Extraordinary Journey" }}</h4>
                            <p class="testi-desc" style="color: #475569; font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.5rem;">"{{ t.quote }}"</p>
                            <div class="testi-user" style="display: flex; align-items: center; gap: 0.75rem;">
                                <div style="width: 44px; height: 44px; border-radius: 50%; background: #EEF2FF; color: #4F46E5; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.1rem;">
                                    {{ t.author_name|first }}
                                </div>
                                <div class="testi-user-info">
                                    <h6 class="testi-name" style="font-size: 0.95rem; font-weight: 700; color: #0F172A; margin: 0;">{{ t.author_name }}</h6>
                                    <span class="testi-role" style="font-size: 0.8rem; color: #64748B;">{{ t.author_location }}</span>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    {% endif %}
                '''
    text = text[:testi_start_idx] + dynamic_testi_html + text[testi_end_idx:]

# 4. Dynamic Travel Inspirations / Blog Stories
old_tips_start = '<div class="tips-grid">'
tips_start_idx = text.find(old_tips_start)
tips_end_idx = text.find('</div></div>         </div>     </section>', tips_start_idx)

if tips_start_idx != -1 and tips_end_idx != -1:
    dynamic_tips_html = '''<div class="tips-grid">
                {% if recent_posts %}
                    {% for post in recent_posts %}
                    <div class="tip-card">
                        <div class="tip-img-box">
                            {% if post.featured_image %}
                                <img src="{{ post.featured_image.url }}" alt="{{ post.title }}" class="tip-img" style="object-fit: cover;">
                            {% else %}
                                <img src="{% static 'images/citys/Pyha_Sunrise-550x358.jpg' %}" alt="{{ post.title }}" class="tip-img" style="object-fit: cover;">
                            {% endif %}
                            <div class="tip-badge"><i class="ph-bold ph-calendar"></i> {{ post.publish_date|default:post.created_at|date:"d M Y" }}</div>
                        </div>
                        <div class="tip-body">
                            <h4 class="tip-title">{{ post.title }}</h4>
                            <p class="tip-desc">{{ post.excerpt|truncatewords:16 }}</p>
                            <a href="{% url 'content:blog_detail' post.slug %}" class="tip-link">Read Story <i class="ph-bold ph-caret-right"></i></a>
                        </div>
                    </div>
                    {% endfor %}
                {% endif %}
            '''
    text = text[:tips_start_idx] + dynamic_tips_html + text[tips_end_idx:]

# Dynamic Links
text = text.replace('href="transport.html"', 'href="{% url \'chauffeur:hub\' %}"')
text = text.replace('href="tour-packages.html"', 'href="{% url \'tours:list\' %}"')
text = text.replace('href="destination.html"', 'href="{% url \'tours:destination_list\' %}"')
text = text.replace('href="destination-details.html"', 'href="{% url \'tours:destination_list\' %}"')

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Frontend/index.html updated with dynamic tours, testimonials, blog stories, and site settings!")
