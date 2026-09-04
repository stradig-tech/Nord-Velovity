import os

frontend_dir = os.path.join('d:\\', 'My Works', 'Nord Velocity', 'Frontend')

# --- 1. Refactor tour-packages.html ---
packages_bak = os.path.join(frontend_dir, 'tour-packages.html.bak')
with open(packages_bak, 'r', encoding='utf-8') as f:
    html = f.read()

hero_idx = html.find('<!-- Hero Section -->')
footer_idx = html.find('<!-- Newsletter Banner -->')

if hero_idx != -1 and footer_idx != -1:
    content = html[hero_idx:footer_idx]

    grid_start = content.find('<div class="packages-grid">')
    grid_end = content.find('<div style="text-align: center; margin-top: 3rem;">')

    dynamic_grid = """<div class="packages-grid">
                {% if tours %}
                    {% for tour in tours %}
                    <div class="tour-card package-horizontal-card" style="display: flex; flex-direction: column; background: white; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0;">
                        <div class="tour-img-box" style="position: relative; height: 220px;">
                            {% if tour.banner_image %}
                            <img src="{{ tour.banner_image.url }}" alt="{{ tour.title }}" class="tour-img" style="width: 100%; height: 100%; object-fit: cover;">
                            {% else %}
                            <img src="{% static 'images/packages/31337_54406107252_f4ca19b35f_c_800_600_nofilter.jpg' %}" alt="{{ tour.title }}" class="tour-img" style="width: 100%; height: 100%; object-fit: cover;">
                            {% endif %}
                            <div class="badge-top-left" style="position: absolute; top: 12px; left: 12px; background: white; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;"><i class="ph-fill ph-heart" style="color: #ef4444;"></i></div>
                            <div class="badge-stack-right" style="position: absolute; top: 12px; right: 12px; display: flex; flex-direction: column; gap: 6px;">
                                {% if tour.is_featured %}<span class="tour-badge green-bg" style="background: #10b981; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700;">Featured</span>{% endif %}
                                <span class="tour-badge yellow-bg text-dark" style="background: #fbbf24; color: #1e293b; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700;">{{ tour.travel_style.name|default:'Tour' }}</span>
                            </div>
                        </div>
                        <div class="tour-body" style="padding: 1.5rem; display: flex; flex-direction: column; flex-grow: 1;">
                            <div class="tour-rating" style="color: #f59e0b; margin-bottom: 0.5rem;">
                                <i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i>
                                <span class="rating-val" style="color: #64748b; font-size: 0.85rem;">(4.9)</span>
                            </div>
                            <h4 class="tour-title" style="margin-bottom: 0.5rem; font-size: 1.2rem;"><a href="{% url 'tours:detail' tour.slug %}" style="color: #0f172a; text-decoration: none;">{{ tour.title }}</a></h4>
                            <p style="color: #64748b; font-size: 0.9rem; line-height: 1.5; margin-bottom: 1rem;">{{ tour.short_summary|default:tour.overview|truncatewords:18 }}</p>
                            <div class="tour-meta" style="display: flex; gap: 1rem; color: #64748b; font-size: 0.85rem; margin-bottom: 1.5rem;">
                                <span class="meta-item"><i class="ph-bold ph-map-pin"></i> {{ tour.destination.name|default:'Finland' }}</span>
                                <span class="meta-item"><i class="ph-bold ph-clock"></i> {{ tour.duration_days }} Days</span>
                            </div>
                            <div class="tour-footer" style="margin-top: auto; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 1rem;">
                                <div class="tour-price-box">
                                    <span class="price-label" style="display: block; font-size: 0.75rem; color: #64748b;">Starting From</span>
                                    <div class="price-display">
                                        <span class="price-main" style="font-size: 1.3rem; font-weight: 800; color: #0f172a;">€{{ tour.pricing.first.price|default:'450' }}</span><span class="price-sub" style="font-size: 0.8rem; color: #64748b;">/person</span>
                                    </div>
                                </div>
                                <a href="{% url 'tours:detail' tour.slug %}" class="btn btn-primary rounded-pill" style="padding: 0.5rem 1.25rem; font-size: 0.9rem;">View Tour</a>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 1rem; background: white; border-radius: 16px;">
                        <i class="ph-fill ph-compass" style="font-size: 3rem; color: #4F46E5; margin-bottom: 1rem;"></i>
                        <h3>No tour packages found</h3>
                        <p style="color: #64748B;">Try selecting a different destination or search keyword.</p>
                        <a href="{% url 'tours:list' %}" class="btn btn-primary rounded-pill" style="margin-top: 1rem; display: inline-block;">View All Tours</a>
                    </div>
                {% endif %}
            </div>"""

    if grid_start != -1 and grid_end != -1:
        content = content[:grid_start] + dynamic_grid + content[grid_end:]

    final_packages = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}Tour Packages | Nord Velocity Luxury Nordic Travel{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"

    with open(os.path.join(frontend_dir, 'tour-packages.html'), 'w', encoding='utf-8') as f:
        f.write(final_packages)
    print("tour-packages.html successfully converted!")

# --- 2. Refactor tour-details.html ---
details_bak = os.path.join(frontend_dir, 'tour-details.html.bak')
with open(details_bak, 'r', encoding='utf-8') as f:
    d_html = f.read()

d_main_idx = d_html.find('<!-- Main Layout -->')
d_footer_idx = d_html.find('<!-- Newsletter CTA Section -->')
if d_footer_idx == -1:
    d_footer_idx = d_html.find('<!-- Footer Section -->')

if d_main_idx != -1 and d_footer_idx != -1:
    d_content = d_html[d_main_idx:d_footer_idx]

    old_booking_box_start = d_content.find('<!-- Booking Box -->')
    old_booking_box_end = d_content.find('<!-- Need Help Box -->')

    vue_booking_widget = """<!-- Vue 3 Interactive Booking Widget -->
    <div id="tourBookingWidget" style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span style="font-size: 2.2rem; font-weight: 900; color: #0F172A; line-height: 1;">€{{ pricing.final_total }}</span>
            <span style="font-size: 1.1rem; color: #64748B;">/ total</span>
        </div>
        
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-weight: 800; font-size: 1.1rem; color: #0F172A;">4.9</span>
                <div style="color: #FBBF24; display: flex; gap: 2px;">
                    <i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i>
                </div>
            </div>
            <span style="color: #64748B; font-size: 0.95rem;">({{ reviews.count|default:"120" }} reviews)</span>
        </div>

        <!-- Date Selection -->
        <div style="margin-bottom: 1rem;">
            <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 0.35rem;">Select Departure Date</label>
            <select v-model="selectedDateId" @change="recalculatePrice" style="width: 100%; padding: 0.75rem; border: 1px solid #CBD5E1; border-radius: 8px; font-size: 0.95rem; background: #F8FAFC;">
                {% if available_dates %}
                    {% for d in available_dates %}
                    <option value="{{ d.id }}">{{ d.date|date:"D, d M Y" }} ({{ d.total_capacity|add:"-d.booked_count" }} spots)</option>
                    {% endfor %}
                {% else %}
                    <option value="">Contact us for upcoming departures</option>
                {% endif %}
            </select>
        </div>

        <!-- Guest Counters -->
        <div style="display: flex; gap: 1rem; margin-bottom: 1.25rem;">
            <div style="flex: 1; background: #F8FAFC; padding: 0.75rem; border-radius: 8px; border: 1px solid #E2E8F0;">
                <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.25rem;">Adults (€{{ base_price }})</div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <button type="button" @click="decrementAdults" style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #CBD5E1; background: white; cursor: pointer; font-weight: bold;">-</button>
                    <span style="font-weight: 700; font-size: 1.1rem;">{{ adults }}</span>
                    <button type="button" @click="incrementAdults" style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #CBD5E1; background: white; cursor: pointer; font-weight: bold;">+</button>
                </div>
            </div>

            <div style="flex: 1; background: #F8FAFC; padding: 0.75rem; border-radius: 8px; border: 1px solid #E2E8F0;">
                <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.25rem;">Children (50% off)</div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <button type="button" @click="decrementChildren" style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #CBD5E1; background: white; cursor: pointer; font-weight: bold;">-</button>
                    <span style="font-weight: 700; font-size: 1.1rem;">{{ children }}</span>
                    <button type="button" @click="incrementChildren" style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #CBD5E1; background: white; cursor: pointer; font-weight: bold;">+</button>
                </div>
            </div>
        </div>

        <!-- Group Discount Notice -->
        <div v-if="pricing.discount_amount > 0" style="background: #ECFDF5; border: 1px solid #A7F3D0; color: #065F46; padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.85rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
            <i class="ph-fill ph-tag"></i> Group discount applied: -€{{ pricing.discount_amount }}
        </div>

        <button type="button" @click="bookNow" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 1rem; font-size: 1.1rem; font-weight: 700; border-radius: 8px; margin-bottom: 0.75rem; background-color: #4F46E5; border-color: #4F46E5; text-decoration: none; display: flex; cursor: pointer;">Book Now</button>
        <button type="button" @click="openInquiryModal" class="btn" style="width: 100%; justify-content: center; padding: 0.85rem; font-size: 1rem; font-weight: 600; border-radius: 8px; border: 1px solid #4F46E5; color: #4F46E5; background: transparent; cursor: pointer;"><i class="ph-bold ph-envelope-simple" style="margin-right: 0.5rem;"></i> Send Inquiry</button>
    </div>
    """

    if old_booking_box_start != -1 and old_booking_box_end != -1:
        d_content = d_content[:old_booking_box_start] + vue_booking_widget + d_content[old_booking_box_end:]

    d_content = d_content.replace(
        '<h1 style="font-size: 2.2rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;">Finland Lapland Escape</h1>',
        '<h1 style="font-size: 2.2rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;">{{ tour.title }}</h1>'
    )
    d_content = d_content.replace(
        '<span class="stat-value">6 Days</span>',
        '<span class="stat-value">{{ tour.duration_days }} Days</span>'
    )

    vue_script = """{% block extra_js %}
<script>
const { createApp, ref, reactive, onMounted } = Vue;

createApp({
    setup() {
        const adults = ref(2);
        const children = ref(0);
        const selectedDateId = ref("{% if available_dates %}{{ available_dates.first.id }}{% endif %}");
        const tourId = {{ tour.id }};
        const pricing = reactive({
            final_total: '{{ base_price|default:"280" }}',
            discount_amount: 0,
            currency: 'EUR'
        });

        const recalculatePrice = async () => {
            try {
                const res = await fetch(`/tours/api/${tourId}/calculate-price/?adults=${adults.value}&children=${children.value}&date_id=${selectedDateId.value}`);
                const data = await res.json();
                if (data.success) {
                    pricing.final_total = data.pricing.final_total;
                    pricing.discount_amount = data.pricing.discount_amount;
                }
            } catch (e) {
                console.error("Price calc error:", e);
            }
        };

        const incrementAdults = () => { adults.value++; recalculatePrice(); };
        const decrementAdults = () => { if (adults.value > 1) { adults.value--; recalculatePrice(); } };
        const incrementChildren = () => { children.value++; recalculatePrice(); };
        const decrementChildren = () => { if (children.value > 0) { children.value--; recalculatePrice(); } };

        const bookNow = () => {
            alert(`Proceeding to reserve ${adults.value} adults, ${children.value} children for total €${pricing.final_total}!`);
        };

        const openInquiryModal = () => {
            const name = prompt("Enter your Name:");
            if (!name) return;
            const email = prompt("Enter your Email:");
            if (!email) return;
            const message = prompt("What would you like to ask about {{ tour.title }}?");
            if (!message) return;

            fetch(`/tours/api/${tourId}/enquiry/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': '{{ csrf_token }}' },
                body: JSON.stringify({ name, email, message })
            }).then(r => r.json()).then(d => {
                alert(d.message || d.error);
            });
        };

        onMounted(() => {
            recalculatePrice();
        });

        return {
            adults, children, selectedDateId, pricing,
            incrementAdults, decrementAdults,
            incrementChildren, decrementChildren,
            recalculatePrice, bookNow, openInquiryModal
        };
    }
}).mount('#tourBookingWidget');
</script>
{% endblock %}
"""

    final_details = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}{{ tour.title }} | Nord Velocity Luxury Tours{% endblock %}\n\n{% block seo %}\n<meta name=\"description\" content=\"{{ tour.short_summary|default:tour.overview|truncatewords:25 }}\">\n<meta property=\"og:title\" content=\"{{ tour.title }}\">\n<meta property=\"og:description\" content=\"{{ tour.short_summary|default:tour.overview|truncatewords:25 }}\">\n{% if tour.banner_image %}\n<meta property=\"og:image\" content=\"{{ request.scheme }}://{{ request.get_host }}{{ tour.banner_image.url }}\">\n{% endif %}\n{% endblock %}\n\n{% block content %}\n" + d_content + "\n{% endblock %}\n\n" + vue_script

    with open(os.path.join(frontend_dir, 'tour-details.html'), 'w', encoding='utf-8') as f:
        f.write(final_details)
    print("tour-details.html successfully converted with Vue 3 widget!")
