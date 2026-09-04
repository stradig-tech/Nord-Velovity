import os

frontend_dir = os.path.join('d:\\', 'My Works', 'Nord Velocity', 'Frontend')

# --- 1. Refactor transport.html ---
with open(os.path.join(frontend_dir, 'transport.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('<section')
e = text.find('<footer')

if s != -1 and e != -1:
    content = text[s:e]

    # Replace static booking card with our Vue 3 Interactive Fare Estimator
    booking_card_start = content.find('<div class="cab-booking-card">')
    booking_card_end = content.find('<!-- Right Visual: Car -->')

    vue_fare_estimator = """<!-- Vue 3 Interactive Fare Estimator -->
        <div class="cab-booking-card" id="chauffeurFareWidget" style="background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;">
            <h2 class="cab-booking-title" style="font-size: 1.6rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem;">Book Executive Chauffeur</h2>
            <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1.5rem;">Instant quotation & transparent fixed pricing across Finland & Nordics.</p>

            <!-- Service Type Selector -->
            <div style="display: flex; gap: 0.5rem; margin-bottom: 1.25rem; background: #F1F5F9; padding: 4px; border-radius: 12px;">
                <button type="button" @click="serviceType = 'distance'; recalculateFare()" :style="serviceType === 'distance' ? 'background: #007bff; color: white; border-radius: 8px; font-weight: 600;' : 'background: transparent; color: #64748b;'" style="flex: 1; border: none; padding: 0.6rem; cursor: pointer; transition: all 0.2s;">Distance Transfer</button>
                <button type="button" @click="serviceType = 'hourly'; recalculateFare()" :style="serviceType === 'hourly' ? 'background: #007bff; color: white; border-radius: 8px; font-weight: 600;' : 'background: transparent; color: #64748b;'" style="flex: 1; border: none; padding: 0.6rem; cursor: pointer; transition: all 0.2s;">Hourly Charter</button>
            </div>

            <!-- Vehicle Class Selector -->
            <div style="margin-bottom: 1rem;">
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 0.35rem;">Vehicle Class</label>
                <select v-model="selectedClassId" @change="recalculateFare" style="width: 100%; padding: 0.75rem; border: 1px solid #CBD5E1; border-radius: 10px; font-size: 0.95rem; background: #F8FAFC;">
                    {% if vehicle_classes %}
                        {% for vc in vehicle_classes %}
                        <option value="{{ vc.id }}">{{ vc.name }} (Up to {{ vc.vehicles.first.passenger_capacity|default:4 }} passengers)</option>
                        {% endfor %}
                    {% else %}
                        <option value="1">Business Class (Mercedes E-Class / EQE)</option>
                        <option value="2">First Class VIP (Mercedes S-Class)</option>
                        <option value="3">Executive Van (Mercedes V-Class)</option>
                    {% endif %}
                </select>
            </div>

            <!-- Distance Options -->
            <div v-if="serviceType === 'distance'" style="margin-bottom: 1rem;">
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 0.35rem;">Estimated Distance (KM)</label>
                <div style="display: flex; gap: 0.5rem;">
                    <input type="number" v-model="distanceKm" @input="recalculateFare" min="5" max="500" style="flex: 1; padding: 0.75rem; border: 1px solid #CBD5E1; border-radius: 10px; font-size: 1rem; background: #F8FAFC;">
                    <span style="display: flex; align-items: center; padding: 0 1rem; background: #F1F5F9; border-radius: 10px; font-weight: 600; color: #475569;">km</span>
                </div>
            </div>

            <!-- Hourly Options -->
            <div v-if="serviceType === 'hourly'" style="margin-bottom: 1rem;">
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 0.35rem;">Charter Duration (Hours)</label>
                <div style="display: flex; gap: 0.5rem;">
                    <button type="button" v-for="h in [2, 4, 6, 8]" :key="h" @click="hours = h; recalculateFare()" :style="hours === h ? 'background: #007bff; color: white;' : 'background: #F1F5F9; color: #475569;'" style="flex: 1; border: none; padding: 0.6rem; border-radius: 8px; font-weight: 600; cursor: pointer;">{{ h }} hrs</button>
                </div>
            </div>

            <!-- Price Output Box -->
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.25rem;">
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
                    <span style="color: #64748B; font-size: 0.9rem;">Estimated Total</span>
                    <span style="font-size: 2rem; font-weight: 900; color: #0F172A;">€{{ fare.final_fare }}</span>
                </div>
                <div style="font-size: 0.8rem; color: #94A3B8; display: flex; justify-content: space-between;">
                    <span>Includes: Meet & Greet, Tolls & Flight Tracking</span>
                    <span v-if="fare.surcharge_amount > 0" style="color: #F59E0B;">Surcharges incl.</span>
                </div>
            </div>

            <button type="button" @click="bookChauffeur" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 1rem; font-size: 1.1rem; font-weight: 700; border-radius: 10px; cursor: pointer;">Reserve Chauffeur</button>
        </div>"""

    if booking_card_start != -1 and booking_card_end != -1:
        content = content[:booking_card_start] + vue_fare_estimator + content[booking_card_end:]

    vue_chauffeur_script = """{% block extra_js %}
<script>
const { createApp, ref, reactive, onMounted } = Vue;

createApp({
    setup() {
        const serviceType = ref('distance');
        const selectedClassId = ref("{% if vehicle_classes %}{{ vehicle_classes.first.id }}{% else %}1{% endif %}");
        const distanceKm = ref(20);
        const hours = ref(3);
        const fare = reactive({
            final_fare: '75.00',
            surcharge_amount: 0,
            currency: 'EUR'
        });

        const recalculateFare = async () => {
            try {
                let url = `/transport/api/calculate-fare/?type=${serviceType.value}&class_id=${selectedClassId.value}`;
                if (serviceType.value === 'hourly') {
                    url += `&hours=${hours.value}`;
                } else {
                    url += `&distance_km=${distanceKm.value}`;
                }
                const res = await fetch(url);
                const data = await res.json();
                if (data.success) {
                    fare.final_fare = data.fare.final_fare;
                    fare.surcharge_amount = data.fare.surcharge_amount;
                }
            } catch (e) {
                console.error("Fare quote error:", e);
            }
        };

        const bookChauffeur = () => {
            alert(`Chauffeur reservation requested! Service: ${serviceType.value.toUpperCase()}, Total: €${fare.final_fare}. Our chauffeur desk will contact you to confirm pickup details.`);
        };

        onMounted(() => {
            recalculateFare();
        });

        return {
            serviceType, selectedClassId, distanceKm, hours, fare,
            recalculateFare, bookChauffeur
        };
    }
}).mount('#chauffeurFareWidget');
</script>
{% endblock %}"""

    final_transport = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}VIP Chauffeur & Executive Transfers | Nord Velocity{% endblock %}\n\n{% block seo %}\n<meta name=\"description\" content=\"Executive chauffeur service and luxury airport transfers in Helsinki, Rovaniemi, and across the Nordics.\">\n{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n\n" + vue_chauffeur_script

    with open(os.path.join(frontend_dir, 'transport.html'), 'w', encoding='utf-8') as f:
        f.write(final_transport)
    print("transport.html successfully converted with Vue 3 fare estimator!")

# --- 2. Refactor cab-list.html ---
with open(os.path.join(frontend_dir, 'cab-list.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('<section')
e = text.find('<footer')

if s != -1 and e != -1:
    content = text[s:e]
    final_cab_list = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}Executive Fleet | Nord Velocity Luxury Chauffeur{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"
    with open(os.path.join(frontend_dir, 'cab-list.html'), 'w', encoding='utf-8') as f:
        f.write(final_cab_list)
    print("cab-list.html successfully converted!")

# --- 3. Refactor cab-details.html ---
with open(os.path.join(frontend_dir, 'cab-details.html.bak'), 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('<section')
e = text.find('<footer')

if s != -1 and e != -1:
    content = text[s:e]
    final_cab_details = "{% extends 'base.html' %}\n{% load static %}\n\n{% block title %}{{ vehicle_class.name|default:'Vehicle Details' }} | Nord Velocity Fleet{% endblock %}\n\n{% block content %}\n" + content + "\n{% endblock %}\n"
    with open(os.path.join(frontend_dir, 'cab-details.html'), 'w', encoding='utf-8') as f:
        f.write(final_cab_details)
    print("cab-details.html successfully converted!")
