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
# TWO-PASS CANVAS WITH NUMBERED PAGES, RUNNING HEADERS & FOOTERS
# ----------------------------------------------------------------------
class StepManualNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(StepManualNumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(StepManualNumberedCanvas, self).showPage()
        super(StepManualNumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress running header/footer on cover page

        self.saveState()
        
        # Running Top Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0F172A"))
        self.drawString(36, 841.89 - 24, "NORD VELOCITY LUXURY TRAVEL & CHAUFFEUR")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(250, 841.89 - 24, "|   Admin Panel Complete Operations & Training Manual")
        self.drawRightString(595.27 - 36, 841.89 - 24, "Standard Operating Procedure (SOP)")

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(36, 841.89 - 28, 595.27 - 36, 841.89 - 28)

        # Running Bottom Footer
        self.line(36, 32, 595.27 - 36, 32)
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#4F46E5"))
        self.drawString(36, 20, "OFFICIAL SYSTEM TRAINING MANUAL")
        
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(185, 20, "— Step-by-Step Instructions: Navigate, View, Create, Edit, Delete & Booking Lifecycle")

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(595.27 - 36, 20, page_str)
        self.restoreState()


def build_manual_pdf(filename="Nord_Velocity_Admin_Panel_Operations_Manual.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    # Color Palette Tokens
    PRIMARY = colors.HexColor("#0F172A")    # Deep Slate Navy
    SECONDARY = colors.HexColor("#4F46E5")  # Brand Indigo Accent
    ACCENT = colors.HexColor("#059669")     # Emerald Green
    WARNING = colors.HexColor("#D97706")    # Deep Amber
    DANGER = colors.HexColor("#DC2626")     # Crimson Red
    MUTED = colors.HexColor("#64748B")      # Slate Grey
    LIGHT_BG = colors.HexColor("#F8FAFC")   # Crisp Background Tint
    BORDER = colors.HexColor("#E2E8F0")     # Subtle Border Grey
    CARD_BG = colors.HexColor("#F1F5F9")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=PRIMARY,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceAfter=15
    )

    sec_header = ParagraphStyle(
        'SecHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    mod_header = ParagraphStyle(
        'ModHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    sub_header = ParagraphStyle(
        'SubHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=PRIMARY,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body_text = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=PRIMARY,
        spaceAfter=4
    )

    step_num_text = ParagraphStyle(
        'StepNumText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=PRIMARY,
        leftIndent=14,
        spaceAfter=3
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=PRIMARY
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white
    )

    def alert_box(text, title="SYSTEM BUSINESS LOGIC & UNDER-THE-HOOD BEHAVIOR", border_col=SECONDARY, bg_col=LIGHT_BG):
        content = [
            Paragraph(f"<b>{title}</b>", ParagraphStyle('ABT', parent=body_text, fontName='Helvetica-Bold', textColor=border_col, spaceAfter=2)),
            Paragraph(text, body_text)
        ]
        t = Table([[content]], colWidths=[523])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_col),
            ('BOX', (0,0), (-1,-1), 1, border_col),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        return t

    def format_table(headers, rows, widths=None):
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
    story.append(Spacer(1, 20))
    story.append(Paragraph("NORD VELOCITY LUXURY TRAVEL & CHAUFFEUR", ParagraphStyle('CoverBrand', fontName='Helvetica-Bold', fontSize=10.5, textColor=SECONDARY, spaceAfter=6)))
    story.append(Paragraph("Admin Panel Complete Operations Manual<br/>Comprehensive Step-by-Step Training Guide", title_style))
    story.append(Paragraph("Standard Operating Procedure for Every Module &bull; Click-by-Click Instructions &bull; Customer Booking & Payment Lifecycles", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2.5, color=SECONDARY, spaceAfter=16))

    meta_info = [
        [Paragraph("<b>Document Title:</b>", table_cell), Paragraph("Nord Velocity Administrative Panel Operating Manual & SOP", table_cell)],
        [Paragraph("<b>Framework / UI:</b>", table_cell), Paragraph("Django 6.1 Enterprise Admin &bull; Custom Nord Velocity Luxury Dark Dashboard Theme", table_cell)],
        [Paragraph("<b>Target Audience:</b>", table_cell), Paragraph("Operations Managers, Tour Dispatchers, Booking Concierges, Fleet Supervisors, Content Staff", table_cell)],
        [Paragraph("<b>Modules Covered:</b>", table_cell), Paragraph("All 22+ Sidebar Modules (Core Operations, Marketing & Content, Platform Settings)", table_cell)],
        [Paragraph("<b>System Core Engines:</b>", table_cell), Paragraph("Departure Capacity Matrix (Private Car/Micro/Bus), Stripe Webhooks, Offline Pay Later, Aurora Guarantees", table_cell)],
        [Paragraph("<b>Publication Version:</b>", table_cell), Paragraph("Version 4.0 &bull; Autumn/Winter Operating Season", table_cell)],
    ]
    t_meta = Table(meta_info, colWidths=[130, 393])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('PADDING', (0,0), (-1,-1), 5.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1"))
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    intro_directive = (
        "<b>HOW TO USE THIS MANUAL:</b><br/>"
        "This training manual is structured specifically to provide clear, actionable, numbered steps for every operation in the admin panel. "
        "For each administrative module, you will find 6 standardized steps:<br/>"
        "&nbsp;&nbsp;&bull; <b>Step 1: Navigate from Left Sidebar:</b> Exactly where to click in the left-hand navigation menu.<br/>"
        "&nbsp;&nbsp;&bull; <b>Step 2: View Existing Records:</b> What is visible on the list table, how to search, sort, and filter.<br/>"
        "&nbsp;&nbsp;&bull; <b>Step 3: Click Add [Item]:</b> How to launch the creation form.<br/>"
        "&nbsp;&nbsp;&bull; <b>Step 4: Fill Up Details (Field-by-Field Breakdown):</b> Exact guidance on what each field means and what to enter.<br/>"
        "&nbsp;&nbsp;&bull; <b>Step 5: How to Edit an Existing Record:</b> How to locate, modify, and save changes safely.<br/>"
        "&nbsp;&nbsp;&bull; <b>Step 6: How to Delete or Deactivate:</b> Distinction between soft deactivation and hard deletion, and foreign key safeguards.<br/>"
        "In addition, <b>Section 4</b> contains a complete technical and commercial breakdown of the customer-side booking lifecycle, "
        "including Paid Online (Stripe) vs Pay Later (Cash/Wire), real-time seat inventory reservation, date availability, and multi-party van sharing."
    )
    story.append(alert_box(intro_directive, title="OPERATIONAL MANDATE & MANUAL STRUCTURE", border_col=PRIMARY, bg_col=CARD_BG))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: CORE OPERATIONS (Modules from Screenshot)
    # =========================================================================
    story.append(Paragraph("SECTION 1: CORE OPERATIONS MODULES", sec_header))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=10))

    # --- 1.1 DASHBOARD ---
    story.append(Paragraph("1. Dashboard", mod_header))
    story.append(Paragraph("<b>Overview & Purpose:</b> High-level command center displaying operational pace, active revenue, upcoming tour departures, and urgent concierge action items.", body_text))
    story.append(Paragraph("1. <b>Navigate from Left Sidebar:</b> Look at the top section labeled <b>CORE OPERATIONS</b> and click the first item, <b>Dashboard</b> (`/admin/`).", step_num_text))
    story.append(Paragraph("2. <b>View Existing Records:</b> You will see 4 KPI metric cards across the top (Total Revenue, Confirmed Bookings, Active Departures, Fleet Status). Below the KPI cards is the <i>Recent Bookings</i> live feed displaying customer names, departure dates, and booking status badges.", step_num_text))
    story.append(Paragraph("3. <b>Quick Actions:</b> In the top header bar, use the omni-search bar to instantly locate any booking reference, customer email, or passenger surname across the system.", step_num_text))
    story.append(Paragraph("4. <b>Navigation Hub:</b> Click on any recent booking reference or upcoming departure row to jump directly into its management screen.", step_num_text))
    story.append(Spacer(1, 8))

    # --- 1.2 BOOKINGS ---
    story.append(Paragraph("2. Bookings", mod_header))
    story.append(Paragraph("<b>Overview & Purpose:</b> Master commercial ledger for all passenger reservations across Arctic tours and VIP chauffeur transfers.", body_text))
    story.append(Paragraph("1. <b>Navigate from Left Sidebar:</b> Under <b>CORE OPERATIONS</b>, click <b>Bookings</b> (`/admin/bookings/booking/`).", step_num_text))
    story.append(Paragraph("2. <b>View Existing Records:</b> You can see all created bookings in the main table with columns: <i>Booking Ref</i> (e.g. `NV-2026-A1B2C3`), <i>Booking Type</i> (Tour / Chauffeur), <i>Channel Source</i> (Direct / OTA / Manual), <i>Customer</i>, <i>Status</i> (Confirmed, Pending, Cancelled), <i>Payment Status</i> (Paid, Unpaid), and <i>Total Amount (€)</i>. In the right filter panel, filter by Status, Payment Status, or Date. Use the top search bar to search references or surnames.", step_num_text))
    story.append(Paragraph("3. <b>Click Add Booking (Manual Phone / Concierge Booking):</b> In the top right corner, click the purple button <b>[+ Manual Booking]</b> (`/admin/bookings/manual-create/`) or <b>[+ Add Booking]</b>.", step_num_text))
    story.append(Paragraph("4. <b>Fill Up Details:</b>", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Departure Selection:</b> Select the scheduled tour and departure slot from the dropdown.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Vehicle Category:</b> Select <i>Private Car (4 seats)</i>, <i>Micro (12 seats)</i>, or <i>Group Bus (54 seats)</i>.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Guest Quantities:</b> Enter number of Adults and Children (system validates available seat capacity in real time).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Customer Details:</b> Search for an existing registered guest or input Full Name, Email, and Mobile Phone.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Payment Method & Status:</b> Select `STRIPE`, `OFFLINE` (Cash to Chauffeur), or `BANK_TRANSFER`. Select `PAID` or `UNPAID`.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Concierge Notes:</b> Enter hotel pickup addresses, flight numbers, or dietary requirements (e.g. Vegetarian, Gluten-free).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; Click <b>[Create Booking & Reserve Seats]</b>. The booking is instantly confirmed and seat inventory decremented.", step_num_text))
    story.append(Paragraph("5. <b>How to Edit an Existing Booking:</b> In the Bookings list, click the blue <b>Booking Reference</b> link. Update the payment status, hotel pickup notes, or dietary constraints. To mark an unpaid booking as settled, change <i>Payment Status</i> from `UNPAID` to `PAID`. Scroll down and click <b>[Save]</b>.", step_num_text))
    story.append(Paragraph("6. <b>How to Cancel or Delete:</b>", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <i>Safe Cancellation (Recommended):</i> Open the booking, change <i>Status</i> to `CANCELLED`, and click <b>Save</b>. The system automatically restores the booked seats back into sellable inventory.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <i>Bulk Cancellation:</i> In the list view, select the checkboxes next to bookings, choose <b>'Cancel booking & release capacity'</b> from the Action dropdown, and click <b>Run</b>.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <i>Deletion Warning:</i> Do NOT use 'Delete selected bookings' on real customer transactions to preserve financial audit history.", step_num_text))
    story.append(Spacer(1, 8))

    # --- 1.3 DEPARTURE CALENDAR ---
    story.append(Paragraph("3. Departure Calendar", mod_header))
    story.append(Paragraph("<b>Overview & Purpose:</b> High-capacity visual dispatch monitor with instant zero-reload toggle between Interactive Month Calendar and Table View.", body_text))
    story.append(Paragraph("1. <b>Navigate from Left Sidebar:</b> Under <b>CORE OPERATIONS</b>, click <b>Departure Calendar</b> (`/admin/operations/calendar/`).", step_num_text))
    story.append(Paragraph("2. <b>View Departures (Calendar Mode):</b> A full-width month calendar displays each scheduled departure as an event block showing: <i>Time</i>, <i>Tour Title</i>, and live vehicle capacity pills (e.g., 🚗 4/4, 🚐 8/12, 🚌 45/54).", step_num_text))
    story.append(Paragraph("3. <b>Switch to Table View (Zero Reload):</b> In the top right header, click <b>[Table View]</b>. The screen switches instantly without page refresh to an operational table with real-time text search and status filters.", step_num_text))
    story.append(Paragraph("4. <b>Inspect & Quick Actions:</b> Click on any departure event in the calendar (or click <b>[Operations]</b> in table view) to open the modal. Review independent vehicle seat breakdowns (Total, Booked, Blocked, Sellable).", step_num_text))
    story.append(Paragraph("5. <b>How to Edit Status from Calendar:</b> Inside the popup modal, click <b>[Open]</b>, <b>[Close]</b>, or <b>[Block]</b>. The status updates via background AJAX and refreshes both calendar and table without reloading.", step_num_text))
    story.append(Paragraph("6. <b>Launch Manual Booking:</b> Click <b>[Manual Booking]</b> inside the modal to immediately open the booking form pre-filled with this departure slot.", step_num_text))
    story.append(PageBreak())

    # --- 1.4 TOUR DEPARTURES ---
    story.append(Paragraph("4. Tour Departures", mod_header))
    story.append(Paragraph("<b>Overview & Purpose:</b> Specific calendar time slots when a tour operates. Each departure maintains independent inventory partitioned by vehicle category.", body_text))
    story.append(Paragraph("1. <b>Navigate from Left Sidebar:</b> Under <b>CORE OPERATIONS</b>, click <b>Tour Departures</b> (`/admin/tours/departure/`).", step_num_text))
    story.append(Paragraph("2. <b>View Existing Records:</b> You can see all created departures in a table showing: <i>Tour Package</i>, <i>Date</i>, <i>Start Time</i>, <i>Status</i> (`OPEN`, `SOLD_OUT`, `CLOSED`, `BLOCKED`), and <i>Capacity Breakdown</i> (Sellable / Total). Filter by status or date on the right.", step_num_text))
    story.append(Paragraph("3. <b>Click Add Tour Departure:</b> Click the purple <b>[+ Add Departure]</b> button at the top right.", step_num_text))
    story.append(Paragraph("4. <b>Fill Up Details:</b>", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Tour:</b> Select the parent Tour Package from the dropdown list (e.g., *'Rovaniemi Arctic Glass Igloo & Aurora'*).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Date & Time:</b> Enter Departure Date (e.g. `2026-12-20`) and Time (e.g. `19:30:00`).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Status:</b> Set to `OPEN` (Bookable online) or `BLOCKED` (Held for maintenance).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Vehicle Capacities Inline (Bottom of Form):</b> Rows are pre-populated for *Private Car*, *Micro*, and *Group Bus*. Customize `Total Capacity` (e.g., if using a 16-seat van instead of 12) and optionally enter `Price Override Adult` or `Price Override Child`.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; Click <b>[Save]</b> at the bottom right. The departure is live and bookable.", step_num_text))
    story.append(Paragraph("5. <b>How to Edit:</b> Click on the Tour Title in the departures list. Update the date, time, or status. To reserve guide seats, scroll down to the Capacities inline and increase `Blocked Seats` by 1 or 2. Click <b>Save</b>.", step_num_text))
    story.append(Paragraph("6. <b>How to Delete:</b> Select the checkbox next to the departure in the list, select 'Delete selected departures' from the Action dropdown, and click Run. Note: Deletion will be rejected by the database if confirmed customer bookings already exist for this departure.", step_num_text))
    story.append(Spacer(1, 8))

    # --- 1.5 VEHICLE TYPES ---
    story.append(Paragraph("5. Vehicle Types", mod_header))
    story.append(Paragraph("<b>Overview & Purpose:</b> Global tour transport categories defining how seat capacity is partitioned across departures (Private Car, Micro, Group Bus).", body_text))
    story.append(Paragraph("1. <b>Navigate from Left Sidebar:</b> Under <b>CORE OPERATIONS</b>, click <b>Vehicle Types</b> (`/admin/tours/vehicletype/`).", step_num_text))
    story.append(Paragraph("2. <b>View Existing Records:</b> Displays all active vehicle types with columns: <i>Name</i>, <i>Slug</i>, <i>Icon</i>, <i>Default Capacity</i>, and <i>Is Active</i>.", step_num_text))
    story.append(Paragraph("3. <b>Click Add Vehicle Type:</b> Click <b>[+ Add Vehicle Type]</b> at the top right.", step_num_text))
    story.append(Paragraph("4. <b>Fill Up Details:</b> Enter Name (e.g., *'Super Jeep 4x4'*), Slug (*'super-jeep'*), Icon emoji (*'🚙'*), Default Capacity (*6*), and Sort Order (*4*). Check 'Is Active' = True. Click <b>Save</b>.", step_num_text))
    story.append(Paragraph("5. <b>How to Edit:</b> Click any vehicle type name. Update the name, icon, or default seat count. Click <b>Save</b>. (Note: Modifying default capacity applies to newly created departures).", step_num_text))
    story.append(Paragraph("6. <b>How to Delete / Deactivate:</b> If departures are already using this vehicle type, uncheck 'Is Active' instead of deleting to preserve database referential integrity.", step_num_text))
    story.append(Spacer(1, 8))

    # --- 1.6 RE-ATTEMPTS (AURORA) ---
    story.append(Paragraph("6. Re-attempts (Aurora)", mod_header))
    story.append(Paragraph("<b>Overview & Purpose:</b> Manages Nord Velocity's 100% Northern Lights Guarantee policy. When an Aurora tour encounters dense cloud cover with no sightings, staff log re-attempts so guests can re-book on subsequent nights at €0.00.", body_text))
    story.append(Paragraph("1. <b>Navigate from Left Sidebar:</b> Under <b>CORE OPERATIONS</b>, click <b>Re-attempts (Aurora)</b> (`/admin/bookings/guaranteedreattempt/`).", step_num_text))
    story.append(Paragraph("2. <b>View Existing Records:</b> Displays all guarantee records showing: <i>Original Booking</i>, <i>Guest Name</i>, <i>Original Departure</i>, <i>Status</i> (`ELIGIBLE`, `REBOOKED`, `DECLINED`, `EXPIRED`), and <i>Re-attempt Departure</i>.", step_num_text))
    story.append(Paragraph("3. <b>Click Add Re-attempt:</b>", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <i>Option A (From Bookings List - Fastest):</i> In <i>Bookings</i>, select the cloudy tour bookings with checkboxes, choose <b>'🌌 Mark as Failed Experience (Create Guaranteed Re-attempt)'</b> from the Action dropdown, and click <b>Run</b>.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <i>Option B (Manual):</i> Click <b>[+ Add Guaranteed Re-attempt]</b> at the top right.", step_num_text))
    story.append(Paragraph("4. <b>Fill Up Details:</b> Select Original Booking, Original Departure, enter Guest Count, Reason (`WEATHER`), and set Status to `ELIGIBLE`. Click <b>Save</b>.", step_num_text))
    story.append(Paragraph("5. <b>How to Rebook Guest on New Date:</b> Open the Re-attempt record when the customer selects their retry date. In <i>Re-attempt Departure</i>, select the new departure slot. Change Status to `REBOOKED`. Click <b>Save</b>. Seats are automatically reserved on the new departure and an e-ticket voucher with €0 balance is issued to the guest.", step_num_text))
    story.append(Paragraph("6. <b>How to Delete:</b> Only delete test entries. For guest records who decline a retry, set Status to `DECLINED` or `EXPIRED`.", step_num_text))
    story.append(PageBreak())

    # --- 1.7 TOUR PACKAGES ---
    story.append(Paragraph("7. Tour Packages", mod_header))
    story.append(Paragraph("<b>Overview & Purpose:</b> The core product catalog defining Arctic experiences (Glass Igloo Safaris, Snowmobile Adventures, Reindeer Sledding).", body_text))
    story.append(Paragraph("1. <b>Navigate from Left Sidebar:</b> Under <b>CORE OPERATIONS</b>, click <b>Tour Packages</b> (`/admin/tours/tour/`).", step_num_text))
    story.append(Paragraph("2. <b>View Existing Records:</b> Displays all tour packages with columns: <i>Title</i>, <i>Destination</i>, <i>Travel Style</i>, <i>Duration</i>, <i>Status</i> (`DRAFT`, `PUBLISHED`, `ARCHIVED`), and <i>Base Price</i>. Filter by Status, Destination, or Season on the right panel.", step_num_text))
    story.append(Paragraph("3. <b>Click Add Tour:</b> Click the purple <b>[+ Add Tour]</b> button in the top right corner.", step_num_text))
    story.append(Paragraph("4. <b>Fill Up Details (Field-by-Field):</b>", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Title:</b> Full commercial package name (e.g., *'Lapland Northern Lights & Glass Igloo Expedition'*).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Slug:</b> URL slug (e.g., `lapland-northern-lights-glass-igloo`). Auto-generated from title.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Destination & Country:</b> Select Destination (*Rovaniemi*) and Country (*Finland*).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Short Summary:</b> 1-2 sentence card preview text (max 200 characters) displayed on search grids.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Overview:</b> Full rich text description detailing the experience, arctic landscapes, and highlights.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Duration Text:</b> User-friendly duration string (e.g. *'3 Days / 2 Nights'* or *'4 Hours'*).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Badge Text:</b> Marketing ribbon (e.g. *'Best Seller'*, *'15% Off'*, *'Aurora Guaranteed'*).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Category Checkboxes:</b> Check `Group Tour`, `Private Tour`, and/or `Family Tour` to control homepage filter tabs.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Aurora Guarantee:</b> Check `Has Guaranteed Reattempt` = True if Northern Lights retry policy applies.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Media Inline (Bottom of Page):</b> Upload photos (16:9 ratio recommended). Check `Is Hero` on the primary cover photo.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Option Pricing Inline:</b> Add pricing rows for *Private Car*, *Micro*, and *Group Bus* with Adult and Child prices.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Inclusions Inline:</b> Add items with text (e.g. *'Thermal Snowsuit & Boots'*, *'Hot Berry Juice'*); set `Is Included` to True or False.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Status:</b> Set to `PUBLISHED` to go live immediately on the public website, or `DRAFT` to keep hidden.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; Click <b>[Save]</b> at the bottom right.", step_num_text))
    story.append(Paragraph("5. <b>How to Edit:</b> Click on any tour title link in the list. Edit text, adjust prices in the pricing inline, upload new gallery photos, or toggle badges. Click <b>Save</b>.", step_num_text))
    story.append(Paragraph("6. <b>How to Delete or Archive:</b>", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <i>Safe Archiving:</i> Open the tour, change Status from `PUBLISHED` to `ARCHIVED`, and click <b>Save</b>. The tour is removed from the public website while all past booking manifests remain intact.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <i>Hard Deletion:</i> Select checkbox in list, choose 'Delete selected tours' from Action dropdown, click Run. (Blocked if departures or bookings exist).", step_num_text))
    story.append(Spacer(1, 8))

    # --- 1.8 to 1.10 ---
    story.append(Paragraph("8. Countries, 9. Tour Places & Cities, 10. Tour Categories", mod_header))
    story.append(Paragraph("<b>8. Countries (`/admin/tours/country/`):</b><br/>"
                           "1. Click <b>Countries</b> in sidebar.<br/>"
                           "2. View existing Nordic nations (Finland, Norway, Sweden, Denmark, Iceland).<br/>"
                           "3. Click <b>[+ Add Country]</b>. Enter Name (e.g. *'Norway'*), Slug (*'norway'*), Region (*'Northern Europe'*), upload Flag SVG icon, and check 'Is Active'.<br/>"
                           "4. Edit: Click country name, update description or flags, click Save.<br/>"
                           "5. Delete: Check box, select Delete, click Run.", step_num_text))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>9. Tour Places & Cities (`/admin/tours/destination/`):</b><br/>"
                           "1. Click <b>Tour Places & Cities</b> in sidebar.<br/>"
                           "2. View cities (Rovaniemi, Tromsø, Reykjavik, Kiruna, Helsinki).<br/>"
                           "3. Click <b>[+ Add Destination]</b>. Enter Name (*'Tromsø'*), select Country (*Norway*), enter Airport Code (*TOS*), upload scenic banner, check 'Is Featured in Nav'. Save.<br/>"
                           "4. Edit/Delete: Click city name to edit coordinates or highlights; delete via action dropdown.", step_num_text))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>10. Tour Categories (`/admin/tours/experiencetype/`):</b><br/>"
                           "1. Click <b>Tour Categories</b> in sidebar.<br/>"
                           "2. View categories (*Northern Lights*, *Winter Safaris*, *Cultural*).<br/>"
                           "3. Click <b>[+ Add Experience Type]</b>. Enter Name, upload circular navigation icon, set sort order, check 'Featured in Nav'. Save.", step_num_text))
    story.append(PageBreak())

    # --- 1.11 TOUR INVENTORY & DATES ---
    story.append(Paragraph("11. Tour Inventory & Dates (Legacy Matrix)", mod_header))
    story.append(Paragraph("<b>Overview & Purpose:</b> Manages simplified calendar blocks and bulk capacity overrides for tours operating on fixed calendar blocks.", body_text))
    story.append(Paragraph("1. <b>Navigate from Left Sidebar:</b> Under <b>CORE OPERATIONS</b>, click <b>Tour Inventory & Dates</b> (`/admin/tours/tourdate/`).", step_num_text))
    story.append(Paragraph("2. <b>View Existing Records:</b> Displays dates with columns: <i>Tour</i>, <i>Start Date</i>, <i>End Date</i>, <i>Total Capacity</i>, <i>Booked Count</i>, <i>Available Spots</i>, and <i>Status</i>.", step_num_text))
    story.append(Paragraph("3. <b>Click Add Tour Date:</b> Click <b>[+ Add Tour Date]</b> at top right.", step_num_text))
    story.append(Paragraph("4. <b>Fill Up Details:</b> Select Tour, Start Date, Total Capacity (e.g. `16`), and Status (`AVAILABLE`). Click <b>Save</b>.", step_num_text))
    story.append(Paragraph("5. <b>How to Edit:</b> Click the tour date link. Adjust total capacity or toggle status to `SOLD_OUT`. Click <b>Save</b>.", step_num_text))
    story.append(Paragraph("6. <b>How to Delete:</b> Select checkbox, choose Delete, click Run.", step_num_text))
    story.append(Spacer(1, 8))

    # --- 1.12 FLEET CLASSES ---
    story.append(Paragraph("12. Fleet Classes (Luxury Fleet)", mod_header))
    story.append(Paragraph("<b>Overview & Purpose:</b> Controls luxury chauffeur service classes displayed on the public fleet showcase (`VIP`, `Business Class`, `Minivan`, `Executive Van`, `Coupe`, `First Class VIP`). Each class contains pricing models and vehicle specifications.", body_text))
    story.append(Paragraph("1. <b>Navigate from Left Sidebar:</b> Under <b>CORE OPERATIONS</b>, click <b>Fleet Classes (Luxury Fleet)</b> (`/admin/chauffeur/vehicleclass/`).", step_num_text))
    story.append(Paragraph("2. <b>View Existing Records:</b> Displays classes with columns: <i>Name</i>, <i>Slug</i>, <i>Thumbnail Preview</i>, <i>Fleet Count</i>, and <i>Is Active</i>.", step_num_text))
    story.append(Paragraph("3. <b>Click Add Vehicle Class:</b> Click <b>[+ Add Vehicle Class]</b> in the top right corner.", step_num_text))
    story.append(Paragraph("4. <b>Fill Up Details:</b>", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Class Name:</b> Name of the luxury tier (e.g., *'First Class VIP'*).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Slug:</b> Canonical identifier (e.g., `first-class-vip`). Auto-filled from name.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Capacities:</b> Max Passengers (*3*), Max Luggage (*2*).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Images:</b> Upload Vehicle Silhouette SVG/PNG icon and representative photograph.", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Pricing Rules Inline (Bottom):</b> Enter Base Fare (e.g. `95.00`), Per KM Rate (`3.50`), and Minimum Total Fare (`120.00`).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; <b>Service Standards Inline:</b> Add bullet points (e.g. *'Complimentary WiFi & Spring Water'*, *'Flight Delay Monitoring'*).", step_num_text))
    story.append(Paragraph("&nbsp;&nbsp;&bull; Check 'Is Active' = True and click <b>[Save]</b>.", step_num_text))
    story.append(Paragraph("5. <b>How to Edit:</b> Click on any class name. Update base fares, per-km rates, or passenger capacities. Click <b>Save</b>. Online quotes update immediately.", step_num_text))
    story.append(Paragraph("6. <b>How to Delete or Deactivate:</b> Uncheck 'Is Active' and save. The class immediately hides from the public Chauffeur grid without breaking past transfer invoices.", step_num_text))
    story.append(Spacer(1, 8))

    # --- 1.13 VIP CHAUFFEUR VEHICLES ---
    story.append(Paragraph("13. VIP Chauffeur Vehicles", mod_header))
    story.append(Paragraph("<b>Overview & Purpose:</b> The physical fleet of chauffeur vehicles (e.g. Mercedes-Benz EQE Electric, Mercedes S-Class 580e, Mercedes V-Class VIP).", body_text))
    story.append(Paragraph("1. <b>Navigate from Left Sidebar:</b> Under <b>CORE OPERATIONS</b>, click <b>VIP Chauffeur Vehicles</b> (`/admin/chauffeur/vehicle/`).", step_num_text))
    story.append(Paragraph("2. <b>View Existing Records:</b> Displays all fleet vehicles with columns: <i>Vehicle Name</i>, <i>Photo</i>, <i>Vehicle Class</i>, <i>License Plate</i>, <i>Passengers</i>, <i>Luggage</i>, and <i>Is Active</i>.", step_num_text))
    story.append(Paragraph("3. <b>Click Add Vehicle:</b> Click <b>[+ Add Vehicle]</b> at top right.", step_num_text))
    story.append(Paragraph("4. <b>Fill Up Details:</b> Enter Name (e.g. *'Mercedes-Benz S-Class 580e'*), select Vehicle Class (*First Class VIP*), enter License Plate (*NORD-007*), Max Passengers (*3*), Luggage (*3*). In the <i>Vehicle Photos Inline</i>, upload high-res photos and check `Is Primary` on the best photo. Check 'Is Active' = True. Click <b>[Save]</b>.", step_num_text))
    story.append(Paragraph("5. <b>How to Edit:</b> Click vehicle name. Update photos, assign to a different class, or log maintenance notes. Click <b>Save</b>.", step_num_text))
    story.append(Paragraph("6. <b>How to Delete / Decommission:</b> Uncheck 'Is Active' and click Save. The vehicle is removed from active booking assignment.", step_num_text))
    story.append(Spacer(1, 8))

    # --- 1.14 FIXED AIRPORT ROUTES & 1.15 GUESTS ---
    story.append(Paragraph("14. Fixed Airport Routes & 15. Guests & Users", mod_header))
    story.append(Paragraph("<b>14. Fixed Airport Routes (`/admin/chauffeur/fixedroute/`):</b><br/>"
                           "1. Click <b>Fixed Airport Routes</b> in sidebar.<br/>"
                           "2. View configured fixed airport transfers.<br/>"
                           "3. Click <b>[+ Add Fixed Route]</b>. Enter Origin (e.g. *'Helsinki-Vantaa Airport [HEL]'*), Destination (*'Helsinki City Center'*), select Vehicle Class (*'Business Class'*), and enter Flat Fare (e.g. `95.00`). Click <b>Save</b>. Overrules per-km rate with a guaranteed flat price.", step_num_text))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>15. Guests & Users (`/admin/accounts/customuser/`):</b><br/>"
                           "1. Click <b>Guests & Users</b> in sidebar.<br/>"
                           "2. View registered travelers, concierges, and admin staff.<br/>"
                           "3. Click <b>[+ Add User]</b> to create staff accounts (check 'Staff Status' to allow admin panel login).<br/>"
                           "4. Inspect Guest Details: Click on a customer email to review their booked trips, passport records, and customer profile.", step_num_text))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 2: MARKETING & CONTENT MODULES
    # =========================================================================
    story.append(Paragraph("SECTION 2: MARKETING & CONTENT MODULES", sec_header))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=10))

    mkt_modules = [
        ("16. Features & Value Props", "/admin/core/valueproposition/",
         "Homepage trust badges ('Certified Arctic Chauffeurs', 'Guaranteed Aurora Sightings', 'Luxury Fleet').",
         "1. Click <b>Features & Value Props</b> under MARKETING & CONTENT.\n"
         "2. View existing value propositions in the list.\n"
         "3. Click <b>[+ Add Value Proposition]</b>.\n"
         "4. Enter Title (*'Certified Arctic Drivers'*), Subtitle (*'Winter skid & ice certified'*), Phosphor icon class (*'ph-shield-check'*), and Sort Order (*1*).\n"
         "5. How to Edit: Click title link, update wording or icon, click Save.\n"
         "6. How to Delete: Select checkbox, choose Delete, click Run."),

        ("17. Discounts & Offers", "/admin/core/homeoffercard/",
         "Homepage promotional banner cards ('Winter Special - Up to 30% Off Arctic Tours').",
         "1. Click <b>Discounts & Offers</b> in sidebar.\n"
         "2. View active promotional banners.\n"
         "3. Click <b>[+ Add Home Offer Card]</b>.\n"
         "4. Enter Badge (*'Limited Winter Offer'*), Title (*'Save 25% on Glass Igloo Packages'*), Description, Button text (*'Explore Packages'*), Target URL (*'/tours/'*), and upload 16:9 Background Image. Check 'Is Active'. Save.\n"
         "5. How to Edit: Click banner title, update dates or discount text, click Save.\n"
         "6. How to Delete: Uncheck 'Is Active' to hide from homepage."),

        ("18. Partner Logos", "/admin/core/partnerlogo/",
         "Corporate partners, luxury hotel chains, airlines, and regional tourism boards.",
         "1. Click <b>Partner Logos</b> in sidebar.\n"
         "2. View partner logo carousel items.\n"
         "3. Click <b>[+ Add Partner Logo]</b>.\n"
         "4. Enter Partner Name (e.g. *'Visit Finland'*), upload transparent PNG logo, enter Website URL, and check 'Is Active'. Save.\n"
         "5. How to Edit/Delete: Click partner name to replace logo; delete via action dropdown."),

        ("19. Promo Coupons", "/admin/payments/coupon/",
         "Checkout promotional discount codes (percentage or fixed cash discount).",
         "1. Click <b>Promo Coupons</b> in sidebar.\n"
         "2. View coupons with columns: Code, Discount Type, Discount Value, Max Uses, Used Count, and Active status.\n"
         "3. Click <b>[+ Add Coupon]</b>.\n"
         "4. Enter Coupon Code (e.g. `AURORA2026`), Discount Type (`PERCENTAGE` or `FIXED`), Value (`15.00` for 15%), Valid From and Valid To dates, and Max Total Uses (`100`). Check 'Is Active'. Click Save.\n"
         "5. How to Edit: Click code, adjust validity date or discount value, click Save.\n"
         "6. How to Delete: Deactivate coupon by unchecking 'Is Active'."),

        ("20. Reviews & Ratings", "/admin/tours/tourreview/",
         "Customer testimonials, ratings (1 to 5 stars), and moderation approval queue.",
         "1. Click <b>Reviews & Ratings</b> in sidebar.\n"
         "2. View submitted reviews. Unapproved reviews have `Is Approved = False`.\n"
         "3. Moderation & Approval: Click on a review, verify the comment text, and check the checkbox <b>Is Approved = True</b>.\n"
         "4. Click <b>Save</b>. The review appears publicly on the tour page and updates the average star rating.\n"
         "5. How to Delete: Select spam or abusive reviews, choose 'Delete selected reviews' from Action dropdown, click Run."),

        ("21. Blog & Stories", "/admin/content/blogpost/",
         "Arctic travel guides, aurora photography tips, and destination articles.",
         "1. Click <b>Blog & Stories</b> in sidebar.\n"
         "2. View all blog posts with Author, Published Date, and Status.\n"
         "3. Click <b>[+ Add Blog Post]</b>.\n"
         "4. Enter Title (*'How to Photograph the Northern Lights in Rovaniemi'*), Slug, Rich Text Body, Author, upload Featured Banner Image, and set Status to `PUBLISHED`.\n"
         "5. Enter SEO Meta Title and Meta Description for Google search ranking. Click Save.\n"
         "6. How to Edit/Delete: Click title to revise content; set Status to Draft to unpublish."),

        ("22. Inquiries & Leads", "/admin/core/contactsubmission/",
         "Inquiries and custom concierge requests submitted through the `/contact/` form.",
         "1. Click <b>Inquiries & Leads</b> in sidebar.\n"
         "2. View incoming leads with Name, Email, Phone, Subject, and Status (`NEW`, `CONTACTED`, `CONVERTED`, `CLOSED`).\n"
         "3. Click on any inquiry row to read the full guest message.\n"
         "4. In <i>Status</i>, change from `NEW` to `CONTACTED`. In <i>Admin Notes</i>, record staff follow-up actions.\n"
         "5. Click <b>Save</b>.")
    ]

    for title, url, desc, steps in mkt_modules:
        story.append(Paragraph(title, mod_header))
        story.append(Paragraph(f"<b>URL:</b> <code>{url}</code> &bull; <i>{desc}</i>", body_text))
        for line in steps.split("\n"):
            story.append(Paragraph(line, step_num_text))
        story.append(Spacer(1, 5))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 3: PLATFORM CONFIGURATION MODULES
    # =========================================================================
    story.append(Paragraph("SECTION 3: PLATFORM CONFIGURATION MODULES", sec_header))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=10))

    cfg_modules = [
        ("23. Site Settings (Mission, Stats & Brand Assets)", "/admin/core/sitesetting/1/change/",
         "Global branding logos, emergency concierge phone, live statistics counters, and company legal info.",
         "1. In the sidebar under PLATFORM SETTINGS, click <b>Site Settings (Mission & Stats)</b>.\n"
         "2. View global settings record.\n"
         "3. <b>Brand & Identity:</b> Update Site Name ('Nord Velocity'), upload Desktop Logo, Dark Admin Logo, and Browser Favicon.\n"
         "4. <b>Statistics Counters:</b> Update numbers shown on homepage: Completed Tours ('26K+'), Experience Years ('5'), Happy Travelers ('15,000+'), Satisfaction Rate ('98%').\n"
         "5. <b>Concierge Contact:</b> Update 24/7 Telephone, Email, and Physical Office Address in Helsinki.\n"
         "6. Click <b>[Save]</b>. Changes immediately apply across all public pages and headers."),

        ("24. Navigation Icons (Navbar Items)", "/admin/core/navbaritem/",
         "Top header navigation bar links (Home, Destinations, Tours, Chauffeur, Contact).",
         "1. Click <b>Navigation Icons</b> in sidebar.\n"
         "2. View navbar links and their sort orders.\n"
         "3. Click on any item to change title, target URL, or Phosphor icon class. Click Save."),

        ("25. Mega Menu Promos & Company Menu Items", "/admin/core/megamenupromo/ & /companymenuitem/",
         "Visual promotional cards displayed inside the dropdown Mega Menus.",
         "1. Click <b>Mega Menu Promos</b> in sidebar. Click [+ Add Mega Menu Promo].\n"
         "2. Select parent dropdown (Destinations or Tours), enter Headline ('Winter Special 30% Off'), upload image, and link to package. Save.\n"
         "3. Click <b>Company Menu Items</b> to add footer links (About, Terms, Privacy Policy, Press)."),

        ("26. FAQs & Testimonials", "/admin/core/faqitem/ & /testimonial/",
         "Frequently asked questions and verified passenger testimonials.",
         "1. Click <b>FAQs</b> in sidebar &rarr; [+ Add FAQ Item]. Select Category (Booking, Chauffeur, Aurora Guarantee), enter Question and detailed Answer. Check 'Is Published' and click Save.\n"
         "2. Click <b>Testimonials</b> in sidebar &rarr; [+ Add Testimonial]. Enter Guest Name, Country, Quote, 5-Star Rating, and upload avatar. Save.")
    ]

    for title, url, desc, steps in cfg_modules:
        story.append(Paragraph(title, mod_header))
        story.append(Paragraph(f"<b>URL:</b> <code>{url}</code> &bull; <i>{desc}</i>", body_text))
        for line in steps.split("\n"):
            story.append(Paragraph(line, step_num_text))
        story.append(Spacer(1, 5))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: CLIENT-SIDE BOOKING LIFECYCLE, SEATS & DATE AVAILABILITY
    # =========================================================================
    story.append(Paragraph("SECTION 4: CLIENT-SIDE BOOKING LIFECYCLE & INVENTORY LOGIC", sec_header))
    story.append(HRFlowable(width="100%", thickness=1.5, color=SECONDARY, spaceAfter=12))

    story.append(Paragraph("4.1 The Complete Customer Booking Journey (Front-to-Back Flow)", mod_header))
    story.append(Paragraph(
        "When a prospective traveler books an Arctic experience on the Nord Velocity public website, the system executes an automated, "
        "multi-step state transition. Here is exactly what happens from customer click to administrative fulfillment:", body_text
    ))

    journey_steps = [
        ("Step 1: Date & Experience Selection",
         "The customer browses to `/tours/` and selects a tour package (e.g. *Lapland Aurora Hunt*). The public booking widget queries all "
         "<code>Departure</code> records for this tour. It evaluates every date: if at least one vehicle category has sellable seats, the date "
         "is highlighted as available in the calendar. If all vehicle categories have zero sellable seats, the date is marked <b>'Sold Out'</b> and disabled."),
        
        ("Step 2: Vehicle Category & Seat Selection",
         "The customer selects their desired transport category: <b>Private Car (4 seats)</b>, <b>Micro (12 seats)</b>, or <b>Group Bus (54 seats)</b>. "
         "The customer inputs guest counts (e.g., 2 Adults, 1 Child). The frontend performs a live AJAX check against "
         "<code>DepartureCapacity.public_sellable</code>. If the requested seats exceed availability, an instant notification prompts them to select another vehicle or date."),

        ("Step 3: Passenger Manifest Details",
         "The customer enters Lead Guest contact details (Name, Email, Mobile Phone) and individual guest details (Full Names, Child/Adult types, "
         "special dietary constraints, and hotel pickup location). If the customer does not have an account, the system automatically provisions a guest profile."),

        ("Step 4: Atomic Capacity Reservation (15-Minute Lock)",
         "Upon clicking <i>'Proceed to Checkout'</i>, Django executes an atomic database transaction using <code>select_for_update()</code> on the "
         "target <code>DepartureCapacity</code> record. It creates a <code>Booking</code> with status <code>HELD</code> and increments <code>booked_count</code> immediately. "
         "This guarantees that no other traveler on the internet can claim those seats while this customer enters payment details.")
    ]

    for step_title_text, step_desc in journey_steps:
        story.append(Paragraph(f"<b>{step_title_text}</b>", sub_header))
        story.append(Paragraph(step_desc, body_text))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 6))

    # --- 4.2 PAID VS PAY LATER ---
    story.append(Paragraph("4.2 Payment Scenarios: Paid Online (Stripe) vs Pay Later (Cash / Wire)", mod_header))
    story.append(Paragraph(
        "Nord Velocity accommodates both international cardholders and VIP corporate travelers who prefer deferred or on-arrival payment. "
        "Here is the precise system behavior and administrative protocol for each scenario:", body_text
    ))

    pay_scenarios_table = [
        ["Attribute / Event", "Scenario A: Paid Online (Stripe / Card)", "Scenario B: Pay Later (Cash / Bank Wire)"],
        ["Customer Action", "Enters credit/debit card on secure Stripe Checkout page.", "Selects 'Pay on Arrival / Cash to Driver' or 'Bank Wire Transfer'."],
        ["System State", "<code>Status = CONFIRMED</code><br/><code>Payment Status = PAID</code>", "<code>Status = CONFIRMED</code> (Seat Held)<br/><code>Payment Status = UNPAID</code>"],
        ["Seat Inventory Impact", "Seats permanently decremented from sellable capacity.", "Seats permanently decremented so customer does NOT lose their spot."],
        ["Automated Notifications", "Instant payment receipt & e-ticket confirmation voucher dispatched.", "Confirmation email dispatched with Bank Wire Details (IBAN/BIC) or Cash Instructions."],
        ["Admin Panel Visibility", "Appears in Bookings list with green <b>PAID</b> badge. No staff intervention required.", "Appears in Bookings list with warning badge: <b>UNPAID / Pending Collection</b>."],
        ["Administrative Protocol", "Verified and finalized. Assign chauffeur and print passenger manifest.", "1. Filter Bookings by <i>Payment: Unpaid</i>.<br/>2. When funds arrive in bank or cash collected by chauffeur: open Booking, change <i>Payment Status</i> to <b>PAID</b>, log reference in notes, click <b>Save</b>."]
    ]
    story.append(format_table(pay_scenarios_table[0], pay_scenarios_table[1:], widths=[110, 206, 207]))
    story.append(Spacer(1, 10))

    # --- 4.3 REAL-WORLD MULTI-PARTY SHARING ---
    story.append(Paragraph("4.3 Real-World Seat Capacity Progression (12-Seat Micro Van Scenario)", mod_header))
    story.append(Paragraph(
        "To understand how shared vehicles operate without overbooking, follow this exact progression for a 12-seat Micro van departure:", body_text
    ))

    cap_rows = [
        ["Progression", "Booking Party", "Party Size", "Remaining Capacity", "System Behavior & Operational Directives"],
        ["Departure Created", "Initial Inventory", "—", "12 of 12 Seats", "Departure Status = OPEN. System displays 12 sellable seats online."],
        ["Booking #1", "Family A", "4 Guests", "8 Seats Left", "Database increments booked_count to 4. 8 seats remain open for public booking."],
        ["Booking #2", "Group B", "5 Guests", "3 Seats Left", "Database increments booked_count to 9. 3 seats remain. Urgency badge triggers online."],
        ["Booking #3", "Couple C", "2 Guests", "1 Seat Left", "Database increments booked_count to 11. Exactly 1 seat remains open."],
        ["Scenario 4A", "Solo Traveler D", "1 Guest", "0 Seats (SOLD OUT)", "Single traveler books the last seat. Status switches to SOLD_OUT. Date disables."],
        ["Scenario 4B", "No Solo Traveler", "0 Guests", "1 Seat Unfilled", "<b>Manager Directive:</b> If 1 seat remains unfilled at 24h cutoff, the tour dispatches safely with 11 passengers. The empty seat remains unoccupied."],
        ["Blocked Attempt", "Party E (2 guests)", "2 Guests", "1 Seat Left", "<b>TRANSACTION REJECTED:</b> Booking engine blocks Party E because 2 > 1. System displays: 'Only 1 seat remaining. Please choose another departure.'"]
    ]
    story.append(format_table(cap_rows[0], cap_rows[1:], widths=[75, 80, 55, 85, 228]))
    story.append(Spacer(1, 10))

    # --- 4.4 CANCELLATION & AUTOMATIC RESTORATION ---
    story.append(Paragraph("4.4 Cancellations, Date Availability & Automatic Capacity Restoration", mod_header))
    story.append(Paragraph(
        "<b>What happens when a booking is cancelled?</b><br/>"
        "1. <b>Status Transition:</b> When an administrator changes a booking's status to <code>CANCELLED</code> or <code>REFUNDED</code>, "
        "the <code>BookingService.transition_status()</code> method executes an atomic release operation.<br/>"
        "2. <b>Seat Restitution:</b> The system automatically decrements <code>DepartureCapacity.booked_count</code> by the cancelled guest count. "
        "The formula <code>public_sellable = total_capacity - booked_count - blocked_seats</code> immediately increases.<br/>"
        "3. <b>Automatic Date Re-opening:</b> If the departure date was previously displayed as <b>'Sold Out'</b> on the public website, "
        "it automatically flips back to <b>'Available'</b> instantly. New customers can immediately reserve the newly liberated seats without any manual developer intervention.<br/>"
        "4. <b>Audit Trail:</b> Every status transition generates an immutable entry in <code>BookingStatusLog</code> recording the timestamp, previous state, new state, user ID, and cancellation reason.", body_text
    ))
    story.append(Spacer(1, 10))

    story.append(alert_box(
        "<b>MASTER RULES FOR OPERATIONAL COMPLIANCE:</b><br/>"
        "&bull; <b>Rule 1: Never Hard Delete Active Records:</b> Always use <code>Status = CANCELLED</code> or <code>ARCHIVED</code>. Hard deletion breaks financial reports and invoice references.<br/>"
        "&bull; <b>Rule 2: Daily Unpaid Audit at 09:00:</b> Review all bookings where Payment Status is <code>UNPAID</code>. Reconcile overnight wire transfers and confirm cash pickups with dispatch.<br/>"
        "&bull; <b>Rule 3: Aurora Guarantee Logging by 23:30:</b> If overcast skies prevent Aurora sightings, log the failed experience before midnight so guests wake up with free re-booking invitations in their email inbox.",
        title="EXECUTIVE OPERATIONAL CHECKLIST", border_col=PRIMARY, bg_col=CARD_BG
    ))

    # Build PDF
    doc.build(story, canvasmaker=StepManualNumberedCanvas)
    print(f"Complete Step-by-Step PDF operations manual generated successfully at: {filename}")
    return filename

if __name__ == "__main__":
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Nord_Velocity_Admin_Panel_Operations_Manual.pdf"))
    build_manual_pdf(out_path)
