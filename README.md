# 🌌 Nord Velocity

> **Next-Generation Luxury Arctic & Nordic Travel, Curated Tour Experiences & VIP Chauffeur Platform**  
> *Engineered with Django 6, PostgreSQL 17, Vue 3 Micro-Widgets & Vanilla Luxury Design System.*  
> **Developed by [StradigTech](https://www.stradigtech.com)** (`www.stradigtech.com`)

[![Developed by StradigTech](https://img.shields.io/badge/Developed%20by-StradigTech-0A66C2?style=for-the-badge&logo=rocket&logoColor=white)](https://www.stradigtech.com)
[![Website](https://img.shields.io/badge/Website-stradigtech.com-2563EB?style=for-the-badge&logo=googlechrome&logoColor=white)](https://www.stradigtech.com)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.0_Micro--Widgets-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![Stripe](https://img.shields.io/badge/Stripe-Payments-008CDD?style=for-the-badge&logo=stripe&logoColor=white)](https://stripe.com/)
[![PayPal](https://img.shields.io/badge/PayPal-Orders_v2-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://developer.paypal.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](Instruction.txt)

---

## 🧭 1. Executive Overview & Brand Vision

**Nord Velocity** is a high-performance digital travel platform designed for the ultra-luxury Nordic and Arctic travel market (Finland, Lapland, Sweden, Norway, and Iceland). The platform unites two distinct customer journeys into a single cohesive ecosystem:

1. **Curated Arctic Tours & Expeditions**: Aurora Borealis hunting, snowmobile safaris, husky sledding expeditions, icebreaker cruises, and glass igloo experiences with dynamic capacity management, group volume discounts, and guaranteed aurora re-attempt tracking.
2. **VIP Chauffeur & Executive Fleet**: First Class, Business Class, and Luxury Electric airport transfers, long-distance charters, and private chauffeur bookings powered by live Haversine geo-distance math and hourly rate models.

### 🎨 Design Language: Nordic Minimalist Luxury
Moving away from generic black/gold cliches, Nord Velocity's visual language is inspired by leading benchmarks in global hospitality and travel:
- **Aman (30%)**: Generous whitespace, restrained typography, and architectural breathing room.
- **Explora Journeys (25%)**: Cinematic Nordic imagery, subtle motion, and modern journey storytelling.
- **Black Tomato (20%)**: Emotional narrative layers for bespoke adventures and expeditions.
- **Wheely (15%)**: Ultra-restrained, discrete luxury chauffeur presentation.
- **Blacklane (10%)**: Frictionless, conversion-optimized booking flows.

---

## 📸 2. Visual Showcase & Project Screenshots

High-resolution screenshots and architectural previews of the platform are organized inside the [`Project Screenshots/`](Project%20Screenshots/) directory.

| Showcase Module | Preview | Key Features Displayed |
|---|---|---|
| **Public Homepage & Hero** | ![Homepage](Project%20Screenshots/01_homepage_showcase.png) | Nordic minimalist hero, live destination search, bento grid showcases, luxury typography |
| **Curated Tour Catalog & Filters** | ![Tour Catalog](Project%20Screenshots/02_tour_catalog_filters.png) | Dynamic category filtering, starting-from price display, interactive wishlist toggle |
| **Tour Details & Booking Engine** | ![Tour Details](Project%20Screenshots/03_tour_details_pricing.png) | Interactive day-by-day itineraries, real-time pricing calculator, atomic capacity locks |
| **VIP Chauffeur & Fleet Dispatch** | ![VIP Chauffeur](Project%20Screenshots/04_vip_chauffeur_booking.png) | Haversine distance matrix, vehicle tier selection (First Class, Business Class, Van) |
| **Central Operations Calendar** | ![Operations Calendar](Project%20Screenshots/05_operations_calendar.png) | FullCalendar 6 interactive console, zero-reload capacity overrides, status blocking |
| **Customer Portal & Order Details** | ![Customer Portal](Project%20Screenshots/06_customer_order_details.png) | Customer booking timeline, meeting logistics, live receipts, wishlist management |
| **Executive Admin Console** | ![Admin Console](Project%20Screenshots/07_admin_console_dark.png) | Slate & Indigo dark dashboard, real-time revenue analytics, mobile drawer menu |
| **Mobile Responsive Experience** | ![Mobile UI](Project%20Screenshots/08_mobile_responsive_ui.png) | Fluid mobile view, touch-optimized booking flows, and responsive off-canvas drawer |

> [!TIP]
> **Adding or Updating Screenshots:**  
> Drop your screenshot files into the [`Project Screenshots/`](Project%20Screenshots/) folder using the filenames listed above. The relative Markdown image tags automatically render inline across GitHub, GitLab, and local viewers. See [`Project Screenshots/README.md`](Project%20Screenshots/README.md) for naming guidelines.

---

## ⚡ 3. Core Platform Capabilities

### 🏔️ A. Curated Tour & Experience Engine
- **Dynamic Pricing Calculator**: Live calculations factoring in adults, children, seasonal multipliers, early-bird deadlines, and automatic volume discounts (e.g., 5% off for 4+ travelers).
- **Atomic Date Capacity Locking**: Guarantees zero overbooking with real-time seat decrementing and atomic database transactions.
- **Guaranteed Aurora Re-Attempt Tracking**: Dedicated operations module enabling guests whose northern lights tours were cancelled due to weather to re-attempt on subsequent evenings without administrative friction.
- **Interactive Itineraries & Inclusions**: Day-by-day expandable itinerary accordions with visual icons, meeting points, and clear inclusion/exclusion checklists.

### 🚘 B. VIP Chauffeur & Fleet Management
- **Fleet Hierarchy**: Tiered vehicle classification (Business Class, First Class, Luxury Van/Electric) with bespoke luggage, seat capacity, and amenity specifications.
- **Dynamic Route & Charter Engine**: Live Haversine route pricing for ad-hoc journeys, fixed airport-hotel transfer routes, and hourly charter bookings with automated night/weekend surcharges.

### 📅 C. Central Operations Calendar (`/admin/operations/calendar/`)
- **FullCalendar 6 Interactive Operations Hub**: Full monthly, weekly, and daily operational schedules of all tour departures.
- **Zero-Reload Status & Capacity Toggling**: Instant API-backed status updates (`ACTIVE`, `BLOCKED`, `COMPLETED`, `CANCELLED`) and instant capacity adjustments directly from modal popups.
- **Drag-and-Drop Rebooking API**: Allows operations managers to reassign bookings from one departure date to another with automated seat count recalculation.

### 🌐 D. OTA Channel Manager Distribution Hub (`/admin/channels/`)
- **Multi-Channel Distribution**: Architectural framework for two-way synchronization with major OTAs (GetYourGuide, Viator, Bokun, and Direct APIs).
- **Audit & Health Trail (`ChannelSyncLog`)**: Complete record of availability pushes, booking imports, webhook receipts, and retry counts.

### 💳 E. Multi-Gateway Payment Infrastructure
- **Stripe Hosted Checkout**: Secure checkout sessions with automated webhook handling (`/payments/webhook/`) and cryptographic signature verification.
- **PayPal Orders API v2**: Client-side PayPal Smart Buttons integration with server-side order capture.
- **Offline & On-Arrival Options**: Instant seat reservations for **Pay on Arrival / Cash to Chauffeur** and **Bank Wire Transfer (SEPA / IBAN)** with 1-click admin reconciliation.
- **Promotions & Coupons**: Flexible discount codes with percentage/fixed-amount reductions, expiry dates, minimum spend rules, and per-user usage limits.

### 👑 F. Executive Admin Console (`luxury_admin.css`)
- **Luxury Dark-Mode Interface**: Polished Slate & Indigo dashboard with fluid typography, responsive stat cards, and real-time revenue counters.
- **Mobile Off-Canvas Navigation Drawer**: Responsive drawer navigation with hamburger toggle `[☰]` and close button `[✕]` supporting seamless mobile administration on phones and tablets.
- **Horizontal Scrolling Changelists**: Wide data tables (Bookings, Departures, Vehicles) feature custom styled scrollbars to guarantee zero layout clipping on any display.

---

## 🏗️ 4. System Architecture & Tech Stack

```
Nord Velocity Ecosystem
│
├── Public Web Portal (Django Templates + Vue 3 Micro-Widgets + Vanilla CSS)
│   ├── Tour Catalog, Details & Live Booking Engine
│   ├── VIP Chauffeur Quote & Charter Checkout
│   ├── Customer Dashboard, Bookings & Wishlists
│   └── Editorial Blog, Destinations & Dynamic Mega Menus
│
├── Backend Application Layer (Django 6.1 + Python 3.13)
│   ├── Business Services (Pricing, Bookings, Haversine, Notifications)
│   ├── REST APIs (Pricing Calculation, Calendar Operations, OTA Sync)
│   └── Multi-Gateway Payment Processors (Stripe, PayPal, Offline)
│
├── Central Operations & Executive Console (Custom Django Admin)
│   ├── Central Departure & Capacity Calendar (FullCalendar 6)
│   ├── OTA Distribution Channel Manager
│   └── Manual Phone Booking Dispatcher
│
└── Data Layer (PostgreSQL 17)
    └── 54 Relational Models across 11 Modular Django Apps
```

### Technology Matrix
| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Language** | Python | `3.13` | Core server runtime |
| **Framework** | Django | `6.1` | Web framework, ORM, Auth & Security |
| **API** | Django REST Framework | `3.18.0` | Internal JSON APIs for calendar & pricing |
| **Database** | PostgreSQL | `17` | Relational persistence & atomic transactions |
| **Interactive UI** | Vue.js | `3.x (CDN)` | Embedded real-time booking calculators |
| **Calendar** | FullCalendar | `6.1.10` | Interactive operations schedule |
| **Styles** | Vanilla CSS | Custom | Bespoke luxury design system & responsive layout |
| **Icons** | Phosphor Icons | `Bold / Fill` | Modern editorial icon set |
| **Reports** | ReportLab | `5.0.1` | Dynamic PDF operations manual generation |
| **Payments** | Stripe & PayPal | Latest | Secure hosted checkout & orders v2 |

---

## 📁 5. Project Directory Structure

```
Nord Velocity/
├── Project Screenshots/                    # Visual showcase, UI architecture & preview assets
│   └── README.md                          # Screenshots index & naming convention guide
│
├── Backend/                                # Django 6 Core Application
│   ├── manage.py                           # Django management CLI
│   ├── requirements.txt                    # Locked Python dependencies
│   ├── .env                                # Local environment variables
│   ├── nordvelocity/                       # Project configuration & root URLs
│   │   ├── settings.py                     # Master Django settings
│   │   ├── urls.py                         # Top-level URL routing & admin overrides
│   │   └── wsgi.py                         # WSGI deployment entrypoint
│   ├── core/                               # Site settings, CMS, testimonials & mega menu
│   ├── accounts/                           # CustomUser, authentication & customer profiles
│   ├── tours/                              # Tours, itineraries, dates, pricing & departures
│   ├── chauffeur/                          # Vehicle classes, VIP fleet & fixed routes
│   ├── bookings/                           # Unified booking engine & calendar views
│   ├── payments/                           # Stripe, PayPal, offline invoices & coupons
│   ├── content/                            # Blog articles, categories & static pages
│   ├── channels/                           # OTA channel manager (Viator, GYG, Bokun)
│   ├── analytics/                          # Funnel events, pageviews & search query logs
│   ├── notifications/                      # Transactional email templates & audit logs
│   ├── seo/                                # Dynamic meta tags, OpenGraph & XML sitemaps
│   ├── test_site_integrity.py              # Automated 22-endpoint verification test
│   └── generate_step_by_step_manual.py     # PDF operations manual generator
│
├── Frontend/                               # Presentation Layer
│   ├── base.html                           # Public portal master layout
│   ├── style.css                           # Global luxury CSS stylesheet
│   ├── admin/                              # Custom Executive Admin Templates
│   │   ├── admin-base.html                 # Executive admin master layout
│   │   ├── base.html                       # Django admin base override
│   │   ├── nav_sidebar.html                # Unified dark sidebar navigation
│   │   ├── departure_calendar.html         # FullCalendar 6 operations console
│   │   ├── manual_booking_form.html        # Admin phone booking creation modal
│   │   └── luxury_admin.css                # Master luxury admin stylesheet
│   ├── tours/                              # Tour catalog & detail templates
│   ├── chauffeur/                          # Fleet listing & chauffeur booking templates
│   ├── bookings/                           # Checkout, summary & confirmation templates
│   ├── accounts/                           # Auth, signup, customer dashboard & vouchers
│   └── images/                             # Brand assets, logos & photography
│
├── Nord_Velocity_Admin_Panel_Operations_Manual.pdf  # Comprehensive operations manual
├── database_architecture.md                # Full 54-model relational database schema
├── Instruction.txt                         # Owner design benchmarks & visual formulas
└── README.md                               # Project documentation & developer guide
```

---

## 🚀 6. Quickstart & Local Setup Guide

### Prerequisites
- **Python 3.12+** or **3.13** installed.
- **PostgreSQL 16+** or **17** running locally.
- **Git** version control.

### Step 1: Clone the Repository
```bash
git clone <repository-url> "Nord Velocity"
cd "Nord Velocity"
```

### Step 2: Create and Activate Virtual Environment
```bash
# On Windows (PowerShell / Command Prompt)
python -m venv Backend\venv
Backend\venv\Scripts\activate

# On macOS / Linux
python3 -m venv Backend/venv
source Backend/venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create or verify `Backend/.env`:
```env
DEBUG=True
SECRET_KEY=django-insecure-nord-velocity-development-key-change-in-prod
DATABASE_URL=postgres://postgres:admin123@127.0.0.1:5432/nordvelocity

# Stripe Sandbox Keys
STRIPE_PUBLIC_KEY=pk_test_placeholder
STRIPE_SECRET_KEY=sk_test_placeholder
STRIPE_WEBHOOK_SECRET=whsec_placeholder

# PayPal Sandbox Keys
PAYPAL_CLIENT_ID=sb
PAYPAL_SECRET=sandbox_secret_placeholder
PAYPAL_MODE=sandbox
```

### Step 5: Database Setup & Migrations
Ensure PostgreSQL has an empty database named `nordvelocity`:
```sql
CREATE DATABASE nordvelocity;
```
Run Django migrations:
```bash
python manage.py migrate
```

### Step 6: Create Administrative Superuser
```bash
python manage.py createsuperuser
```

### Step 7: Start Development Server
```bash
python manage.py runserver
```
The application will be accessible at:
- **Public Website**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Executive Admin Console**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Operations Departure Calendar**: [http://127.0.0.1:8000/admin/operations/calendar/](http://127.0.0.1:8000/admin/operations/calendar/)

---

## 📊 7. Modular Django Applications Reference

| Application | Domain & Key Responsibilities | Primary Models |
|---|---|---|
| **`core`** | Site branding, navigation, homepage CMS, social links, FAQs | `SiteSetting`, `NavbarItem`, `HomeOfferCard`, `FAQItem`, `Testimonial`, `AuditLog` |
| **`accounts`** | Role-based authentication, customer profiles, vouchers | `CustomUser`, `CustomerProfile` |
| **`tours`** | Packages, itineraries, departures, pricing tiers, reviews | `Tour`, `TourDate`, `Departure`, `TourPricing`, `TourItinerary`, `VehicleType` |
| **`chauffeur`** | Fleet categories, vehicles, fixed routes, charter rates | `VehicleClass`, `Vehicle`, `FixedRoute`, `PricingRule`, `ChauffeurBooking` |
| **`bookings`** | Booking engine, state machine, operations calendar | `Booking`, `TourBooking`, `TourBookingGuest`, `BookingStatusLog`, `GuaranteedReattempt` |
| **`payments`** | Gateways, webhooks, offline reconciliations, discount codes | `PaymentIntent`, `Refund`, `Receipt`, `Coupon`, `CouponUsage` |
| **`channels`** | OTA distribution (Viator, GetYourGuide, Bokun) & sync audit | `Channel`, `ChannelSyncLog` |
| **`content`** | Editorial storytelling, travel guides, categories & tags | `BlogPost`, `BlogCategory`, `BlogTag`, `StaticPage` |
| **`notifications`**| Transactional emails, booking confirmations & reminder logs | `NotificationTemplate`, `NotificationLog` |
| **`analytics`** | Anonymous conversion funnels, pageviews & search tracking | `PageView`, `BookingFunnelEvent`, `SearchQueryLog` |
| **`seo`** | Metadata injection, OpenGraph previews & XML sitemaps | `SEOPage`, `SitemapEntry` |

---

## 🧪 8. Automated Testing & Verification Suite

Nord Velocity includes an integrated automated verification script to validate URL routing, dynamic pricing calculations, admin hub endpoints, and live API state toggles.

To run the integrity suite:
```bash
cd Backend
python test_site_integrity.py
```

### What `test_site_integrity.py` Tests:
1. **Public Routes**: Homepage, About, FAQ, Contact, Tour Catalog, Fleet Listing, and Blog (all return `200 OK`).
2. **Detail & Booking Endpoints**: Tour detail view, booking checkout form, and live `/tours/api/<id>/calculate-price/` API.
3. **Admin & Operations Hub**: Admin dashboard, FullCalendar operations view, manual phone booking dispatcher, and channel sync endpoints.
4. **Live API State Manipulation**: Executes a live `POST` request to `/admin/api/departures/<id>/status/` to test status transitions (`ACTIVE` &rarr; `BLOCKED` &rarr; `ACTIVE`) with live database refresh assertions.

---

## 📖 9. Administrative Operations Manuals

A series of comprehensive, illustrated manuals are maintained in the repository for training operations staff and concierge dispatchers:
- **`Nord_Velocity_Admin_Panel_Operations_Manual.pdf`**: Complete step-by-step operational guide covering:
  - Tour package creation, media upload, and pricing tier setup.
  - Fleet management, vehicle attributes, and route pricing.
  - Departure calendar management, live capacity overrides, and status blocking.
  - Booking lifecycle management, cancellations, and customer rebooking.
  - OTA distribution channel monitoring.

To regenerate the manual with updated system models:
```bash
cd Backend
python generate_step_by_step_manual.py
```

---

## 🔒 10. Production Deployment & Security Checklist

When moving from staging to live production:

1. **Environment Security**:
   - Set `DEBUG=False` in `.env`.
   - Configure strong, random `SECRET_KEY`.
   - Update `ALLOWED_HOSTS` with your production domains (e.g., `nordvelocity.com`).
2. **Live Gateways**:
   - Replace Stripe test keys with live `STRIPE_PUBLIC_KEY` and `STRIPE_SECRET_KEY`.
   - Register live Stripe webhook signing secret (`STRIPE_WEBHOOK_SECRET`) pointing to `https://nordvelocity.com/payments/webhook/`.
   - Swap `PAYPAL_MODE=live` with verified live business client credentials.
3. **Web Server & Reverse Proxy**:
   - Run Django via **Gunicorn** or **Uvicorn** WSGI/ASGI workers.
   - Configure **Nginx** reverse proxy with HTTP/2, Gzip/Brotli compression, and automatic Let's Encrypt SSL.
4. **Cloud Media Storage**:
   - Configure `django-storages` with AWS S3, Cloudflare R2, or MinIO for media assets.
5. **Background Workers (Recommended)**:
   - Configure **Celery + Redis** for asynchronous transactional email delivery and scheduled departure reminders.

---

## 👨‍💻 11. Development & Engineering Credits

**Nord Velocity** is designed, architected, and developed by:

### 🚀 **[StradigTech](https://www.stradigtech.com)**
> *Engineering Next-Generation Digital Experiences & Enterprise Travel Platforms*

- 🌐 **Website**: [www.stradigtech.com](https://www.stradigtech.com)
- 💼 **Domain Expertise**:
  - Enterprise Web & Mobile Platform Architecture
  - High-Conversion OTA Travel, Tour Booking & VIP Chauffeur Systems
  - Custom Full-Stack Django 6 & Vue.js Reactive Solutions
  - High-Volume Relational Database Engineering (PostgreSQL 17)
  - Multi-Gateway Payment Infrastructure (Stripe, PayPal, Offline SEPA/Cash)
- ✉️ **Inquiries & Consultation**: Visit [www.stradigtech.com](https://www.stradigtech.com) for bespoke digital transformation and custom software engineering.

---

## 📄 12. Ownership & License

- **Platform & Brand**: Proprietary and confidential to **Nord Velocity**. All rights reserved.
- **Engineering & Implementation**: Developed by **[StradigTech](https://www.stradigtech.com)** (`www.stradigtech.com`).
- Unauthorized reproduction, distribution, or reverse engineering is strictly prohibited under applicable international copyright law.
