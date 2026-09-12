import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# ----------------------------------------------------------------------
# TWO-PASS CANVAS WITH RUNNING HEADERS, FOOTERS & PAGE NUMBERS
# ----------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress running header/footer on title cover

        self.saveState()
        
        # Running Top Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0F172A"))
        self.drawString(36, 841.89 - 24, "NORD VELOCITY")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(116, 841.89 - 24, "|   Executive Admin Panel Operations Manual")
        self.drawRightString(595.27 - 36, 841.89 - 24, "Platform v3.2 (Production)")

        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(36, 841.89 - 28, 595.27 - 36, 841.89 - 28)

        # Running Bottom Footer
        self.line(36, 32, 595.27 - 36, 32)
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#4F46E5"))
        self.drawString(36, 20, "CONFIDENTIAL & PROPRIETARY")
        
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(175, 20, "— Internal Operations, Booking Dispatch & Concierge Desk Reference")

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(595.27 - 36, 20, page_str)
        self.restoreState()


# ----------------------------------------------------------------------
# MAIN GENERATOR FUNCTION
# ----------------------------------------------------------------------
def build_pdf(filename="Nord_Velocity_Admin_Panel_Operations_Manual.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#0F172A")    # Deep Slate / Navy
    SECONDARY = colors.HexColor("#4F46E5")  # Luxury Indigo
    ACCENT = colors.HexColor("#10B981")     # Emerald Green
    WARNING = colors.HexColor("#F59E0B")    # Amber
    DANGER = colors.HexColor("#EF4444")     # Crimson Red
    MUTED = colors.HexColor("#64748B")      # Slate Grey
    LIGHT_BG = colors.HexColor("#F8FAFC")   # Ice White / Slate 50
    CARD_BG = colors.HexColor("#F1F5F9")    # Slate 100
    BORDER = colors.HexColor("#CBD5E1")     # Slate 300

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=PRIMARY,
        alignment=0,
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=SECONDARY,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=SECONDARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Header3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=PRIMARY,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=PRIMARY,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'DocBodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=PRIMARY
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=PRIMARY
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold'
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.white
    )

    def callout_box(text, title="OPERATIONAL BEST PRACTICE", border_color=SECONDARY, bg_color=LIGHT_BG):
        content = [
            Paragraph(f"<b>{title}</b>", ParagraphStyle('CT', parent=callout_style, fontName='Helvetica-Bold', textColor=border_color, spaceAfter=3)),
            Paragraph(text, callout_style)
        ]
        t = Table([[content]], colWidths=[523])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('BOX', (0,0), (-1,-1), 1, border_color),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        return t

    def module_table(headers, rows, widths=None):
        data = [[Paragraph(h, table_header) for h in headers]]
        for r in rows:
            formatted_row = []
            for cell in r:
                if isinstance(cell, str):
                    formatted_row.append(Paragraph(cell, table_cell))
                else:
                    formatted_row.append(cell)
            data.append(formatted_row)
        
        if not widths:
            widths = [523 / len(headers)] * len(headers)

        t = Table(data, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ]))
        return t

    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("NORD VELOCITY LUXURY TRAVEL & CHAUFFEUR", ParagraphStyle('BrandKicker', fontName='Helvetica-Bold', fontSize=10, textColor=SECONDARY, leading=14, spaceAfter=10)))
    story.append(Paragraph("Executive Admin Panel<br/>Complete Operations Manual", title_style))
    story.append(Paragraph("A Complete Guide to Every Module: Viewing, Creating, Editing, Deleting, and Core System Architectures", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=3, color=SECONDARY, spaceAfter=25))

    overview_meta = [
        [Paragraph("<b>Document Version:</b>", table_cell), Paragraph("v3.2 Enterprise Production Release", table_cell)],
        [Paragraph("<b>Target Audience:</b>", table_cell), Paragraph("Operations Managers, Concierge Staff, System Admins, Tour Dispatchers", table_cell)],
        [Paragraph("<b>System Core:</b>", table_cell), Paragraph("Django 6.1 Enterprise Core + Decoupled Executive Admin + FullCalendar 6 Engine", table_cell)],
        [Paragraph("<b>Inventory Architecture:</b>", table_cell), Paragraph("Multi-Capacity Vehicle Partitioning (Private Car, Micro, Group Bus) & Atomic Locking", table_cell)],
        [Paragraph("<b>Chauffeur Engine:</b>", table_cell), Paragraph("Dynamic Distance & Route-Based Point-to-Point Pricing Service", table_cell)],
        [Paragraph("<b>Publication Date:</b>", table_cell), Paragraph("September 2026", table_cell)],
    ]
    t_meta = Table(overview_meta, colWidths=[140, 383])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('PADDING', (0,0), (-1,-1), 7),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0"))
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 30))

    exec_summary_text = (
        "This operations manual is the comprehensive reference for managing the Nord Velocity executive platform. "
        "It covers every administrative module shown on the navigation sidebar across <b>Core Operations</b>, "
        "<b>Marketing & Content</b>, and <b>Platform Configuration</b>. For every single module, clear operational procedures "
        "are detailed for <b>Viewing & Filtering</b>, <b>Creating Records</b>, <b>Editing Attributes & Capacities</b>, and "
        "<b>Deleting or Deactivating</b> entries. Critical background engines—including multi-party shared vehicle capacity, "
        "the 100% Aurora Sightings Guarantee re-attempt workflow, and dynamic chauffeur point-to-point pricing—are thoroughly explained."
    )
    story.append(callout_box(exec_summary_text, title="EXECUTIVE SUMMARY & OPERATIONAL MANDATE", border_color=PRIMARY, bg_color=CARD_BG))
    story.append(PageBreak())

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=15))

    toc_data = [
        ("1. System Architecture & Administrative Security", "Core Django backend, role permissions, CSRF & URL protection"),
        ("2. Core Operations Modules", "Dashboard, Bookings, Departure Calendar, Tour Departures, Vehicle Types"),
        ("   2.1 Dashboard & Central KPI Monitoring", "Live revenue, booking volume, departure load, and fleet alerts"),
        ("   2.2 Bookings Management & Manual Booking", "Reservation lifecycle, customer records, payment status, refunds"),
        ("   2.3 Central Departure & Capacity Calendar", "Interactive calendar vs. zero-reload table view, multi-vehicle seat badges"),
        ("   2.4 Tour Departures & Capacity Engine", "Scheduling date/time slots, vehicle seat partitioning, adult/child price overrides"),
        ("   2.5 Vehicle Types (Group Tours)", "Private Car (4), Micro (12), Group Bus (54) fleet categories and defaults"),
        ("   2.6 Aurora Sightings Guaranteed Re-attempts", "100% Sightings Guarantee lifecycle, weather cancellations, zero-cost holds"),
        ("   2.7 Tour Packages & Itineraries", "Creating Arctic safaris, glass igloo packages, physical difficulty, duration bands"),
        ("   2.8 Countries & Tour Places / Cities", "Destination hubs (Rovaniemi, Tromsø, Helsinki, Levi) and airport mappings"),
        ("   2.9 Tour Categories & Seasonal Tags", "Northern Lights, Winter Safaris, Lakeland, Icebreaker categorization"),
        ("   2.10 Tour Inventory & Dates (Legacy)", "Calendar block management, seasonal date tiers, blackout dates"),
        ("   2.11 Fleet Classes (Executive Luxury Fleet)", "VIP, Business Class, First Class VIP, Executive Van chauffeur tiers"),
        ("   2.12 VIP Chauffeur Vehicles", "Individual vehicle fleet (Mercedes EQE, S-Class), specs, photo galleries"),
        ("   2.13 Fixed Airport Routes", "Fixed flat fares (HEL Airport to City Center, RVN to Santa Claus Village)"),
        ("   2.14 Guests & User Accounts", "Customer profiles, VIP concierge levels, passport records, staff permissions"),
        ("3. Marketing & Content Modules", "Value props, promotional offers, partner logos, coupons, reviews, blog, leads"),
        ("4. Platform Configuration Modules", "Site settings, mission, stats, navigation icons, FAQs, testimonials, team"),
        ("5. In-Depth Operational Workflows", "Shared capacity math, Aurora re-attempt vouchers, dynamic point-to-point fares"),
        ("6. Security, Backups & Maintenance Checklist", "Audit trails, database integrity, image optimization, cache clearing")
    ]
    
    toc_rows = []
    for section, desc in toc_data:
        toc_rows.append([Paragraph(f"<b>{section}</b>", table_cell), Paragraph(desc, table_cell)])
    
    t_toc = Table(toc_rows, colWidths=[200, 323])
    t_toc.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#F1F5F9")),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: ARCHITECTURE & SECURITY
    # =========================================================================
    story.append(Paragraph("1. System Architecture & Administrative Security", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=12))

    story.append(Paragraph(
        "The Nord Velocity platform runs on an enterprise-grade Django 6.1 monolith, powering two distinct business verticals: "
        "<b>(1) Curated Arctic Tour & Safari Packages</b> and <b>(2) Executive VIP Chauffeur & Airport Transfers</b>. "
        "The administration interface is fully customized with the proprietary <i>Luxury Admin Theme</i>, featuring a full-height sticky "
        "dark navigation sidebar, global live search, and real-time operational widgets.", body_style
    ))

    story.append(Paragraph("User Roles & Permission Boundaries", h2_style))
    role_data = [
        ["Role Level", "Access Scope", "Capabilities & Constraints"],
        ["Superuser (Admin)", "Entire System (/admin/*)", "Full Create, Read, Update, Delete (CRUD) across all models, system configuration, staff creation, API keys, and database maintenance."],
        ["Operations Manager", "Core Operations & Bookings", "Can manage Bookings, Departures, Calendar allocations, Aurora re-attempts, Manual bookings, and Customer Profiles."],
        ["Content Editor", "Marketing & Content", "Can create and edit Blog stories, Reviews, Homepage value props, Partner logos, and FAQs. Cannot modify pricing rules or bookings."],
        ["Chauffeur Concierge", "Chauffeur & Fleet", "Can update Vehicle availability, review route assignments, and create manual transfer bookings."],
        ["Customer / Guest", "Public Web & Portal (/accounts/*)", "Can view published tours/vehicles, reserve seats via Stripe checkout, and download booking confirmation vouchers."]
    ]
    story.append(module_table(role_data[0], role_data[1:], widths=[110, 130, 283]))
    story.append(Spacer(1, 10))

    story.append(callout_box(
        "<b>Security Protection Against Unauthorized Scanning:</b> The admin panel is shielded by Django's native authentication "
        "system, CSRF session verification on all mutating requests (POST/PUT/DELETE), and rate-limited login endpoints. "
        "To safeguard production deployments against brute-force attacks, superusers can alter the administration root path "
        "or restrict admin IP ranges in web server configurations (e.g., Nginx / Cloudflare WAF).",
        title="SECURITY NOTICE & BEST PRACTICES", border_color=DANGER, bg_color=LIGHT_BG
    ))
    story.append(Spacer(1, 15))

    # =========================================================================
    # SECTION 2: CORE OPERATIONS MODULES
    # =========================================================================
    story.append(Paragraph("2. Core Operations Modules", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=12))

    # -------------------------------------------------------------------------
    # 2.1 Dashboard
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.1 Executive Operations Dashboard", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/</code>", body_style))
    story.append(Paragraph(
        "<b>Module Purpose:</b> The central mission control for Nord Velocity. Provides executive staff with a real-time overview "
        "of ongoing operations without running complex database queries. It displays primary revenue KPIs, current day departure counts, "
        "active fleet utilization, and quick shortcuts to critical workflows.", body_style
    ))
    dash_actions = [
        ["Action", "Operational Guide"],
        ["View", "Access the main landing screen upon login. Key metric cards summarize Total Monthly Revenue (€), Confirmed Reservations, Upcoming Arctic Departures, and Fleet Utilization Rate."],
        ["Quick Search", "Use the omni-search input at the top of the header. Typing booking references, guest surnames, or tour titles navigates directly to matching records."],
        ["Fast Dispatch", "Click on direct widget links to launch <i>Manual Booking</i>, jump to <i>Departure Calendar</i>, or inspect unconfirmed holds."]
    ]
    story.append(module_table(dash_actions[0], dash_actions[1:], widths=[120, 403]))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 2.2 Bookings
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.2 Bookings Management", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/bookings/booking/</code> | <b>Manual Booking:</b> <code>/admin/bookings/manual-create/</code>", body_style))
    story.append(Paragraph(
        "<b>Module Purpose:</b> Represents the commercial core of Nord Velocity. Every booking record links a customer to either a "
        "<b>Tour Departure</b> (with multi-vehicle seat reservation) or a <b>VIP Chauffeur Transfer</b> (with point-to-point vehicle reservation).", body_style
    ))
    booking_actions = [
        ["CRUD Action", "Step-by-Step Procedure", "Business Rules & Logic"],
        ["VIEW", "Navigate to <i>Bookings</i>. Use the right sidebar filters to isolate bookings by Status (Pending, Confirmed, Cancelled, Completed), Payment Status, or Booking Date. Search by Booking Reference (e.g. <code>NV-2026-XXXX</code>) or Customer Name.", "Displays booking summary, guest count, total cost, balance due, and channel source (Direct vs OTA)."],
        ["CREATE (Manual)", "Click <b>[+ Manual Booking]</b> button. Select an active Tour Departure, choose Vehicle Category (Private Car, Micro, Group Bus), enter adult/child counts, select or create guest account, specify pricing overrides, and submit.", "Atomically decrements public sellable capacity in database. Prevents overbooking across concurrent online bookings."],
        ["EDIT", "Click any Booking Reference. You can update dietary requirements, pickup addresses, internal staff notes, payment status (UNPAID -> PAID), or assign concierge staff.", "Modifying guest seats on a confirmed booking automatically recalculates and adjusts the departure's available capacity."],
        ["DELETE / CANCEL", "Select 'CANCELLED' status rather than hard deleting. If an admin deletes a booking, Django prompts for confirmation.", "<b>CRITICAL:</b> Cancelling releases reserved vehicle seats back to inventory. Hard deletion removes the historical booking log forever."]
    ]
    story.append(module_table(booking_actions[0], booking_actions[1:], widths=[90, 240, 193]))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 2.3 Departure Calendar
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.3 Central Departure & Capacity Calendar", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/operations/calendar/</code>", body_style))
    story.append(Paragraph(
        "<b>Module Purpose:</b> Visual command center for dispatchers. Provides a unified 100% full-width view of all tour departures, "
        "enabling instant inspection of available capacity across all three vehicle types (Private Car, Micro, Group Bus) with a zero-reload "
        "switch between FullCalendar and interactive Tabular views.", body_style
    ))
    cal_actions = [
        ["Feature / Mode", "Operational Usage", "Under-The-Hood Mechanics"],
        ["Calendar View", "Default interactive FullCalendar. Shows days of the month with departure pills. Each pill displays start time, tour title, and live vehicle badges: <code>🚗 Car</code>, <code>🚐 Micro</code>, <code>🚌 Bus</code>.", "Pills are color-coded: Emerald Green (Open), Orange (Sold Out), Red (Blocked/Closed), Purple (Reserved)."],
        ["Table View Switch", "Click <b>[Table View]</b> tab in the upper-right. Toggles instantly <i>without page reload</i>. Displays a high-density operational table with real-time quick search input and row counts.", "Uses JavaScript DOM caching and FullCalendar <code>updateSize()</code> for instantaneous switching with zero server reloads."],
        ["Quick Filters", "Use the top filter bar to filter by Tour Package or by Status (Open, Sold Out, Blocked, Closed).", "Filters dynamically synchronize both the Calendar and Table view via <code>/admin/api/departures/calendar/</code>."],
        ["Operations Modal", "Click any departure pill in the calendar, or click <b>[Operations]</b> in the table. Opens modal showing independent vehicle capacities (Total, Booked, Blocked, Re-attempt, Sellable).", "Provides one-click admin buttons to <b>Open</b>, <b>Close</b>, or <b>Block</b> the departure instantly via AJAX, automatically refreshing both views."]
    ]
    story.append(module_table(cal_actions[0], cal_actions[1:], widths=[110, 220, 193]))
    story.append(Spacer(1, 10))

    story.append(callout_box(
        "<b>Mathematical Formula for Sellable Capacity:</b><br/>"
        "<code>Public Sellable = Total Capacity − Confirmed Bookings − Blocked Seats − Re-attempt Holds</code><br/>"
        "This formula guarantees that even if 10 guests book via online channels while an admin is creating a manual reservation, "
        "the database enforces atomicity and will never exceed the physical capacity of the allocated vehicle.",
        title="CENTRAL CAPACITY FORMULA", border_color=ACCENT, bg_color=LIGHT_BG
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 2.4 Tour Departures
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.4 Tour Departures & Multi-Capacity Breakdown", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/tours/departure/</code>", body_style))
    story.append(Paragraph(
        "<b>Module Purpose:</b> Defines individual departures (date, time, tour) and manages per-vehicle capacity allocations. "
        "Whenever a tour departure is scheduled, the system creates child <code>DepartureCapacity</code> records for each active vehicle type.", body_style
    ))
    dep_actions = [
        ["CRUD Action", "Operational Instructions"],
        ["VIEW", "Go to <i>Tour Departures</i>. The list shows Date, Time, Tour Title, Status badge, Total Booked, and Total Sellable seats. Use date filters to see departures for the upcoming week or month."],
        ["CREATE", "Click <b>[+ Add Departure]</b>. Select the Tour, enter Departure Date (YYYY-MM-DD), Start Time (HH:MM), and End Time. Choose status (OPEN). In the inlines at the bottom, customize capacities for Private Car, Micro, or Group Bus if they deviate from system defaults. Click <b>Save</b>."],
        ["EDIT", "Open any departure. You can override Adult Price, Child Price, adjust Blocked Seats (e.g., hold 2 seats for equipment), or set Re-attempt Reserved seats. Modifying status to 'CLOSED' immediately stops public booking."],
        ["DELETE", "Select departure checkbox and choose 'Delete selected departures'. <i>Note:</i> If active bookings exist, Django will raise a protected foreign-key warning. Always reassign or cancel existing bookings first."]
    ]
    story.append(module_table(dep_actions[0], dep_actions[1:], widths=[100, 423]))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 2.5 Vehicle Types (Tours)
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.5 Vehicle Types (Tour Capacity Categories)", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/tours/vehicletype/</code>", body_style))
    story.append(Paragraph(
        "<b>Module Purpose:</b> Controls the three tour transport categories: <b>Private Car (4 seats)</b>, <b>Micro (12 seats)</b>, "
        "and <b>Group Bus (54 seats)</b>. These define how departures partition their seats.", body_style
    ))
    vt_actions = [
        ["CRUD Action", "Operational Instructions & Impact"],
        ["VIEW", "Displays all active vehicle categories, their slug identifier, default passenger capacity, and display icon emoji."],
        ["CREATE", "Click <b>[+ Add Vehicle Type]</b>. Enter Name (e.g., 'Super Jeep'), Slug ('super-jeep'), Icon ('🚙'), Default Capacity (e.g., 6 seats), and Sort Order. Check 'Is Active'."],
        ["EDIT", "Edit existing vehicle type to modify icon, default seat capacity, or display order. <i>Note:</i> Changing default capacity applies to newly created departures; existing departures retain their locked capacities."],
        ["DELETE", "Deletion is restricted if historical departure capacity records reference this vehicle type. Deactivate using 'Is Active = False' instead of hard deleting."]
    ]
    story.append(module_table(vt_actions[0], vt_actions[1:], widths=[100, 423]))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 2.6 Aurora Guaranteed Re-attempts
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.6 Aurora Guaranteed Re-attempts", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/bookings/guaranteedreattempt/</code>", body_style))
    story.append(Paragraph(
        "<b>Module Purpose:</b> Executes Nord Velocity's 100% Northern Lights Sightings Guarantee. When an Aurora tour departs on a cloudy "
        "night with zero sightings, staff log re-attempts so guests can re-book on subsequent nights free of charge.", body_style
    ))
    aurora_actions = [
        ["Action", "Procedure & System Behavior"],
        ["VIEW", "Lists all guest guarantee claims, original tour date, customer details, status (PENDING, REATTEMPTED, EXPIRED, CANCELLED), and scheduled reattempt departure."],
        ["CREATE (Claim)", "Click <b>[+ Add Guaranteed Re-attempt]</b>. Select original Tour Booking, customer, set status to 'PENDING', and set expiration date (typically 12 months from original tour date)."],
        ["SCHEDULE", "When the guest selects their desired retry date: Open the claim record, select the new <b>Target Departure</b>, set status to 'REATTEMPTED', and save. The system allocates seats without generating an invoice."],
        ["DELETE / EXPIRE", "If a guest exhausts their travel window without re-booking, update status to 'EXPIRED'. Do not delete records to maintain audit compliance."]
    ]
    story.append(module_table(aurora_actions[0], aurora_actions[1:], widths=[110, 413]))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 2.7 Tour Packages
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.7 Tour Packages & Curated Itineraries", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/tours/tour/</code>", body_style))
    story.append(Paragraph(
        "<b>Module Purpose:</b> Comprehensive catalog of Arctic experiences, including glass igloo safaris, reindeer sledding, "
        "and icebreaker expeditions.", body_style
    ))
    tour_actions = [
        ["CRUD Action", "Operational Instructions"],
        ["VIEW", "Displays Title, Country, Primary Destination, Experience Category, Physical Difficulty, Base Adult Fare (€), and Publishing Status (Draft, Published, Archived). Filter by country or experience type."],
        ["CREATE", "Click <b>[+ Add Tour]</b>. Complete: Title, Slug (auto-generated), Country, Primary Destination, Category, Duration (Days/Hours), Physical Rating (Easy/Moderate/Challenging). Add Rich Text Itinerary, Inclusions ('What's included'), Exclusions, and upload high-res featured images. Set status to 'PUBLISHED' when ready to go live."],
        ["EDIT", "Update tour descriptions, highlights, or seasonal pricing rules. You can also reorder itinerary days or update pickup instructions."],
        ["DELETE", "To remove a tour from public discovery without breaking historical guest booking records, set Status = 'ARCHIVED'. Never hard delete a tour that has existing bookings."]
    ]
    story.append(module_table(tour_actions[0], tour_actions[1:], widths=[100, 423]))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 2.8 Countries & Tour Places
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.8 Countries & Tour Places / Cities", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/tours/country/</code> & <code>/admin/tours/destination/</code>", body_style))
    dest_actions = [
        ["Entity", "Field Configuration & Procedures"],
        ["Countries (/country/)", "<b>Fields:</b> Name (Finland, Norway, Sweden, Denmark), Slug, Flag Icon image, Description, Currency code (EUR, NOK, SEK), Capital city.<br/><b>Usage:</b> Drives navigation mega-menus, destination filtering, and regional marketing tags."],
        ["Places / Cities (/destination/)", "<b>Fields:</b> City Name (Rovaniemi, Tromsø, Helsinki, Levi, Kiruna), Country foreign key, Airport Code (RVN, TOS, HEL), Scenic banner photo, Coordinates.<br/><b>Usage:</b> Links tours to geographic hubs; powers airport pickup auto-fill suggestions."]
    ]
    story.append(module_table(dest_actions[0], dest_actions[1:], widths=[140, 383]))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 2.9 Tour Categories & 2.10 Inventory
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.9 Tour Categories & 2.10 Tour Inventory Dates", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/tours/experiencetype/</code> & <code>/admin/tours/tourdate/</code>", body_style))
    cat_actions = [
        ["Module", "Operational Scope"],
        ["Tour Categories (Experience Types)", "Defines marketing buckets: <i>Northern Lights</i>, <i>Winter Safaris</i>, <i>Luxury Chauffeur</i>, <i>Lakeland</i>, <i>Icebreaker</i>, <i>Family</i>. Admins can create new tags, upload category hero banners, and configure display sort order."],
        ["Tour Inventory & Dates", "Manages seasonal booking windows, cutoff advance booking rules (e.g. minimum 24 hours prior), and legacy date-tier pricing links. Linked dynamically to active Departures."]
    ]
    story.append(module_table(cat_actions[0], cat_actions[1:], widths=[150, 373]))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 2.11 Fleet Classes (Executive Luxury Fleet)
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.11 Fleet Classes (Our Executive Luxury Fleet)", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/chauffeur/vehicleclass/</code>", body_style))
    story.append(Paragraph(
        "<b>Module Purpose:</b> Controls the luxury categories displayed on the public Chauffeur hub (<b>VIP</b>, <b>Business Class</b>, "
        "<b>Minivan</b>, <b>Micro</b>, <b>Coupe</b>, <b>First Class VIP</b>, <b>Executive Van</b>). Each class contains pricing rules, "
        "service standards, inclusions, and safety guarantees.", body_style
    ))
    fc_actions = [
        ["CRUD Action", "Operational Instructions & Business Logic"],
        ["VIEW", "Displays all luxury fleet classes with preview thumbnails, active vehicle count, sort order, and active status."],
        ["CREATE", "Click <b>[+ Add Vehicle Class]</b>. Enter Name (e.g. 'Business Class'), Slug ('business-class'), Max Passengers, Max Luggage, and upload representative silhouette icon. Configure child inlines: Pricing Rules (Base Fare, Per Km Rate), Service Standards, Inclusions, and Safety Standards. Save."],
        ["EDIT", "Update base fare (e.g. €75.00), per km rate (€2.80/km), or minimum transfer fare. Changes instantly reflect in dynamic point-to-point transfer quotes on the frontend."],
        ["DELETE / TOGGLE", "Toggle 'Is Active = False' to temporarily remove a class from public display without deleting assigned cars."]
    ]
    story.append(module_table(fc_actions[0], fc_actions[1:], widths=[110, 413]))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 2.12 VIP Chauffeur Vehicles
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.12 VIP Chauffeur Vehicles & Photo Galleries", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/chauffeur/vehicle/</code>", body_style))
    story.append(Paragraph(
        "<b>Module Purpose:</b> Represents the physical motor fleet. Each vehicle belongs to a <code>VehicleClass</code> and has "
        "specific license plate registration, passenger capacity, luggage capacity, and dedicated photo gallery.", body_style
    ))
    veh_actions = [
        ["CRUD Action", "Operational Instructions"],
        ["VIEW", "Lists all physical vehicles with photo preview, vehicle class, passenger capacity, and active status."],
        ["CREATE", "Click <b>[+ Add Vehicle]</b>. Enter Vehicle Name (e.g. 'Mercedes-Benz EQE Electric'), select Vehicle Class ('Business Class'), input License Plate, passenger seats (3), luggage bags (2). In the <i>Vehicle Photos</i> inline, upload high-res exterior and interior shots, marking one as 'Is Primary'. Save."],
        ["EDIT", "Update vehicle specs, add seasonal winter tire notes ('Armored & Winter Prepared'), or upload fresh interior photos."],
        ["DELETE", "If a car is decommissioned or sold, toggle 'Is Active = False'. The public card counter automatically decrements."]
    ]
    story.append(module_table(veh_actions[0], veh_actions[1:], widths=[100, 423]))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 2.13 Fixed Airport Routes
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.13 Fixed Airport Routes & Flat Fares", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/chauffeur/fixedroute/</code>", body_style))
    story.append(Paragraph(
        "<b>Module Purpose:</b> Configures fixed point-to-point flat rates for major Arctic airport and hotel transfers "
        "(e.g. Helsinki-Vantaa Airport to Helsinki City Center, Rovaniemi Airport to Santa Claus Village).", body_style
    ))
    route_actions = [
        ["Field / Action", "Operational Description"],
        ["Origin & Destination", "Pickup hub (e.g. 'Helsinki-Vantaa Airport [HEL]') and drop destination (e.g. 'Helsinki City Center')."],
        ["Vehicle Class", "Assigns flat rate specifically to a Vehicle Class (e.g. VIP vs Business Class vs Executive Van)."],
        ["Flat Fare (€)", "Overrules distance calculations with a fixed pre-agreed executive rate (e.g. €95.00 flat)."],
        ["Estimated Minutes", "Typical journey duration (e.g. 30 mins), displayed to guest on booking confirmation."]
    ]
    story.append(module_table(route_actions[0], route_actions[1:], widths=[130, 393]))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # 2.14 Guests & Users
    # -------------------------------------------------------------------------
    story.append(Paragraph("2.14 Guests & User Accounts", h2_style))
    story.append(Paragraph("<b>URL:</b> <code>/admin/accounts/customuser/</code>", body_style))
    story.append(Paragraph(
        "<b>Module Purpose:</b> Central identity directory managing staff administrative logins, concierge credentials, and guest "
        "profiles including nationality, passport numbers, dietary constraints, and VIP concierge tiers.", body_style
    ))
    user_actions = [
        ["CRUD Action", "Operational Instructions"],
        ["VIEW", "Filter users by Staff Status, Superuser Status, or Active Status. Search by email, full name, or phone number."],
        ["CREATE", "Click <b>[+ Add User]</b>. Specify Email, Password, and Personal Information. Check 'Staff Status' to grant admin panel access; assign appropriate user permissions."],
        ["EDIT", "In the <i>Customer Profile</i> inline, update passport numbers, emergency contacts, VIP tier (Standard, VIP, Black Card), and customer notes."],
        ["DELETE / BAN", "Toggle 'Active = False' to revoke login permissions immediately without breaking associated booking history."]
    ]
    story.append(module_table(user_actions[0], user_actions[1:], widths=[100, 423]))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 3: MARKETING & CONTENT MODULES
    # =========================================================================
    story.append(Paragraph("3. Marketing & Content Modules", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=12))

    mkt_modules = [
        ["Module Name", "Admin URL", "Management Guide & Purpose"],
        ["Features & Value Props", "/admin/core/valueproposition/", "Controls homepage value pills (e.g., 'Certified Arctic Chauffeurs', 'Guaranteed Aurora Sightings', 'All-Inclusive Pricing'). Edit title, subtitle, icon, and sort order."],
        ["Discounts & Offers", "/admin/core/homeoffercard/", "Manages promotional banners across homepage & tours (e.g. 'Winter offer for Lapland & Helsinki up to 30% off'). Configure badge text, discount %, destination link, and promo image."],
        ["Partner Logos", "/admin/core/partnerlogo/", "Upload partner hotel logos, luxury travel consortium badges, and airline partner icons shown in the homepage trust carousel."],
        ["Promo Coupons", "/admin/payments/coupon/", "Create coupon discount codes (e.g. <code>AURORA2026</code>). Configure discount type (Percentage or Fixed Amount), minimum spend, expiration date, and max redemption count."],
        ["Reviews & Ratings", "/admin/tours/tourreview/", "Moderate guest reviews. Approve verified traveler testimonials, verify 1-5 star ratings, and edit customer feedback before it appears publicly on tour cards."],
        ["Blog & Stories", "/admin/content/blogpost/", "Publish travel insights and Nordic destination guides (e.g. '2026 Travel Report'). Add SEO meta titles, meta descriptions, cover images, and publish dates."],
        ["Inquiries & Leads", "/admin/core/contactsubmission/", "Review inquiries submitted via the <code>/contact/</code> form. Track lead status (New, Contacted, Converted, Closed), view guest message, and record internal follow-up notes."]
    ]
    story.append(module_table(mkt_modules[0], mkt_modules[1:], widths=[120, 150, 253]))
    story.append(Spacer(1, 15))

    # =========================================================================
    # SECTION 4: PLATFORM CONFIGURATION MODULES
    # =========================================================================
    story.append(Paragraph("4. Platform Configuration Modules", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=12))

    cfg_modules = [
        ["Configuration Item", "Admin URL", "Key Settings & Impact"],
        ["Site Settings (Global)", "/admin/core/sitesetting/1/change/", "Central brand assets: Site Name, Desktop Logo, Dark Admin Logo, Mobile Favicon, Concierge Email, 24/7 Telephone, Live Statistics (26K+ completed tours, 98% satisfaction), and Legal Copyright."],
        ["Navigation Icons", "/admin/core/navbaritem/", "Controls main navigation header links, display labels, target URLs, and associated Phosphor icon classes."],
        ["Mega Menu Promos", "/admin/core/megamenupromo/", "Visual promo cards nested inside the Destination and Tour mega-menus (e.g., seasonal Lapland discount callout)."],
        ["Company Menu Items", "/admin/core/companymenuitem/", "Dropdown links under the 'Company' header menu (About Us, Services, FAQ, Contact, Blog)."],
        ["FAQs", "/admin/core/faqitem/", "Frequently asked questions displayed on <code>/faq/</code> and detail pages. Categorized by Booking, Chauffeur, Aurora, and Cancellation."],
        ["Testimonials", "/admin/core/testimonial/", "Verified guest quotes, passenger headshots, and review snippets displayed across the homepage."],
        ["Team Leadership", "/admin/core/teammember/", "Executive concierges, master guides, and chauffeur captains displayed on the About Us page with bios and photos."]
    ]
    story.append(module_table(cfg_modules[0], cfg_modules[1:], widths=[120, 150, 253]))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 5: IN-DEPTH OPERATIONAL WORKFLOWS
    # =========================================================================
    story.append(Paragraph("5. Advanced Operational Workflows & Business Logic", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=12))

    # Workflow A
    story.append(Paragraph("Workflow A: Multi-Party Shared Vehicle Capacity Engine", h2_style))
    story.append(Paragraph(
        "A critical capability of Nord Velocity is allowing multiple independent parties to share a single vehicle "
        "(e.g., a 12-seat Micro van) on a tour departure without seat fragmentation or overbooking.", body_style
    ))
    
    cap_scenario_data = [
        ["Sequence", "Booking Party", "Seats Requested", "Remaining Micro Seats", "System Status"],
        ["Initial", "System Seed", "—", "12 of 12 Available", "Departure Status = OPEN"],
        ["Step 1", "Family A", "4 passengers", "8 seats remaining", "Atomic decrement; hold confirmed"],
        ["Step 2", "Group B", "5 passengers", "3 seats remaining", "Atomic decrement; hold confirmed"],
        ["Step 3", "Couple C", "2 passengers", "1 seat remaining", "Atomic decrement; departure approaching capacity"],
        ["Step 4", "Solo Traveler D", "1 passenger", "0 seats remaining", "Atomic decrement; Status -> SOLD_OUT"],
        ["Overbook Attempt", "Party E", "2 passengers", "0 seats available", "<b>REJECTED:</b> Booking engine prevents transaction"]
    ]
    story.append(module_table(cap_scenario_data[0], cap_scenario_data[1:], widths=[85, 100, 100, 118, 120]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<i>Operational Rule:</i> If 1 seat remains and no solo traveler books prior to departure cutoff, the Admin Manager can "
        "dispatch the tour with 11 passengers by simply updating status to 'CLOSED' without modifying vehicle allocations.", body_style
    ))
    story.append(Spacer(1, 10))

    # Workflow B
    story.append(Paragraph("Workflow B: Aurora Guarantee Voucher & Re-attempt Lifecycle", h2_style))
    story.append(Paragraph(
        "Nord Velocity guarantees that guests booking Northern Lights tours will witness the Aurora Borealis. "
        "If heavy cloud cover prevents sightings, the operations desk follows this exact workflow:", body_style
    ))
    aurora_steps = [
        ["Phase", "Responsible Staff", "Action & System Behavior"],
        ["1. Trip Sighting Report", "Lead Guide", "Upon tour conclusion, guide confirms zero visibility via operations SMS/radio."],
        ["2. Claim Registration", "Concierge Desk", "Navigate to <code>/admin/bookings/guaranteedreattempt/</code>. Click <b>Add Guaranteed Re-attempt</b>, select original booking, and set status to <b>PENDING</b>."],
        ["3. Guest Rescheduling", "Guest / Concierge", "Guest contacts desk or logs into portal. Desk selects next available departure with open seats, attaches it to the claim, and sets status to <b>REATTEMPTED</b>."],
        ["4. Inventory Hold", "Automated Engine", "The target departure locks 1 seat per guest in <code>reattempt_reserved</code>. Public sellable capacity decrements automatically at <b>€0.00 zero-balance invoice</b>."]
    ]
    story.append(module_table(aurora_steps[0], aurora_steps[1:], widths=[110, 110, 303]))
    story.append(Spacer(1, 10))

    # Workflow C
    story.append(Paragraph("Workflow C: Dynamic Chauffeur Fare Calculation", h2_style))
    story.append(Paragraph(
        "Transfer fares are calculated via <code>ChauffeurPricingService</code> based on vehicle class, route type, and distance:", body_style
    ))
    pricing_math = [
        ["Route Type", "Calculation Logic & Formula", "Example (Business Class)"],
        ["Fixed Route", "Matches exact pickup & drop pair against <code>FixedRoute</code> table. Flat fee takes complete precedence.", "HEL Airport -> City Center = <b>€95.00 Flat</b>"],
        ["Point-to-Point (One-Way)", "<code>Fare = Base Rate + (Distance_KM × Per_KM_Rate)</code><br/>Enforces Minimum Fare if calculated total is lower.", "Base €75 + (25 km × €2.80/km) = <b>€145.00</b>"],
        ["Round Trip Transfer", "Applies discounted return multiplier: <code>Round_Trip = One_Way × 1.85</code>", "€145.00 × 1.85 = <b>€268.25 Total</b>"]
    ]
    story.append(module_table(pricing_math[0], pricing_math[1:], widths=[120, 240, 163]))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 6: SYSTEM MAINTENANCE & BEST PRACTICES
    # =========================================================================
    story.append(Paragraph("6. Maintenance, Backups & Staff Operational Checklist", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=12))

    story.append(Paragraph("Daily Operations Routine Checklist", h2_style))
    checklist_data = [
        ["Time", "Operational Responsibility", "Target Module & Action"],
        ["07:30 Morning", "Day Dispatcher", "Open <b>Departure Calendar</b>. Verify today's departures. Check passenger manifests, luggage totals, and assign licensed Arctic chauffeurs."],
        ["12:00 Midday", "Bookings Concierge", "Review <b>Bookings</b>. Filter for 'Pending / Unpaid'. Reconcile wire transfers or manual bank receipts. Follow up with guests on pickup times."],
        ["17:00 Evening", "Marketing & Content", "Review <b>Inquiries & Leads</b>. Ensure all corporate custom quote inquiries received within 4 hours are addressed. Check new <b>Reviews & Ratings</b> for moderation."],
        ["23:30 Night", "Night Guide / Concierge", "Process weather logs. If an Aurora expedition encountered total cloud cover, log <b>Guaranteed Re-attempts</b> before midnight."]
    ]
    story.append(module_table(checklist_data[0], checklist_data[1:], widths=[85, 120, 318]))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Database Maintenance & Safety Directives", h2_style))
    rules_data = [
        ["Directive", "Mandatory Operational Procedure"],
        ["Safe Deletion Protocol", "<b>NEVER</b> hard delete Tours, Vehicles, or Vehicle Types that possess historical bookings. Deleting parent records will trigger cascade deletion warnings or orphan financial records. Always use <code>is_active = False</code> or set Status to <code>ARCHIVED</code>."],
        ["Image Optimization", "Upload photos in WebP or PNG format at 1920x1080 (16:9) or 1200x800 for vehicles. ImageKit automatically compresses previews, but keeping source files under 2.5 MB maintains optimal site speed."],
        ["Automated Nightly Backups", "Database snapshots (PostgreSQL/SQLite) are scheduled every 24 hours. Retain 30 rolling daily backups and 12 end-of-month archive snapshots in cold cloud storage."],
        ["Cache Invalidation", "When updating global pricing rules, fleet classes, or site settings, changes take effect immediately on next page load without restarting Gunicorn/Django processes."]
    ]
    story.append(module_table(rules_data[0], rules_data[1:], widths=[140, 383]))
    story.append(Spacer(1, 25))

    # Sign-off Box
    signoff_text = (
        "<b>AUTHORIZED SIGN-OFF & OPERATIONAL COMPLIANCE:</b><br/>"
        "This document constitutes the official operating standard for Nord Velocity luxury travel and chauffeur services. "
        "All administrative staff, dispatchers, and concierge team members must adhere to the data integrity and booking "
        "workflows defined herein. Direct technical inquiries or enhancement requests to the Chief Technology Officer."
    )
    story.append(callout_box(signoff_text, title="DOCUMENT APPROVAL & COMPLIANCE", border_color=PRIMARY, bg_color=CARD_BG))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {filename}")
    return filename

if __name__ == "__main__":
    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Nord_Velocity_Admin_Panel_Operations_Manual.pdf"))
    build_pdf(out_file)
