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
            return  # Suppress running header/footer on title cover

        self.saveState()
        
        # Running Top Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0F172A"))
        self.drawString(36, 841.89 - 24, "NORD VELOCITY")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(116, 841.89 - 24, "|   Admin Panel Step-by-Step Operations Manual")
        self.drawRightString(595.27 - 36, 841.89 - 24, "Complete Standard Operating Procedure")

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(36, 841.89 - 28, 595.27 - 36, 841.89 - 28)

        # Running Bottom Footer
        self.line(36, 32, 595.27 - 36, 32)
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#4F46E5"))
        self.drawString(36, 20, "OFFICIAL TRAINING MANUAL")
        
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(170, 20, "— Step-by-Step Guide for Creating, Editing, Viewing & Deleting Every Feature")

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

    # Color Tokens
    PRIMARY = colors.HexColor("#0F172A")    # Deep Navy
    SECONDARY = colors.HexColor("#4F46E5")  # Brand Indigo
    ACCENT = colors.HexColor("#10B981")     # Emerald
    WARNING = colors.HexColor("#F59E0B")    # Amber
    DANGER = colors.HexColor("#EF4444")     # Red
    MUTED = colors.HexColor("#64748B")      # Grey
    LIGHT_BG = colors.HexColor("#F8FAFC")   # Light Background
    BORDER = colors.HexColor("#E2E8F0")     # Light Border
    BOX_BORDER = colors.HexColor("#CBD5E1")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=PRIMARY,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceAfter=15
    )

    sec_header = ParagraphStyle(
        'SecHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    mod_header = ParagraphStyle(
        'ModHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    step_title = ParagraphStyle(
        'StepTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=PRIMARY,
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    body_text = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=PRIMARY,
        spaceAfter=4
    )

    step_text = ParagraphStyle(
        'StepText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=PRIMARY,
        leftIndent=12,
        spaceAfter=3
    )

    bullet_text = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=PRIMARY,
        leftIndent=16,
        spaceAfter=2
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

    def alert_box(text, title="HOW IT WORKS BEHIND THE SCENES", border_col=SECONDARY, bg_col=LIGHT_BG):
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
    story.append(Spacer(1, 30))
    story.append(Paragraph("NORD VELOCITY LUXURY TRAVEL & CHAUFFEUR", ParagraphStyle('CoverBrand', fontName='Helvetica-Bold', fontSize=10, textColor=SECONDARY, spaceAfter=8)))
    story.append(Paragraph("Admin Panel Operations Manual<br/>Step-by-Step Training Guide", title_style))
    story.append(Paragraph("Every Module Detailed: Step 1 (Navigate) &bull; Step 2 (View) &bull; Step 3 (Create) &bull; Step 4 (Edit) &bull; Step 5 (Delete)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2.5, color=SECONDARY, spaceAfter=20))

    meta_info = [
        [Paragraph("<b>Manual Type:</b>", table_cell), Paragraph("Click-by-Click Standard Operating Procedure (SOP)", table_cell)],
        [Paragraph("<b>System Core:</b>", table_cell), Paragraph("Django 6.1 Enterprise Admin &bull; Luxury Admin Theme", table_cell)],
        [Paragraph("<b>Target Roles:</b>", table_cell), Paragraph("System Administrators, Tour Dispatchers, Booking Concierges, Content Staff", table_cell)],
        [Paragraph("<b>Scope of Coverage:</b>", table_cell), Paragraph("All 22+ Navigation Sidebar Modules (Core Operations, Marketing, Platform)", table_cell)],
        [Paragraph("<b>Publication Date:</b>", table_cell), Paragraph("September 2026 &bull; Version 3.2", table_cell)],
    ]
    t_meta = Table(meta_info, colWidths=[130, 393])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0"))
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 20))

    intro_box = (
        "<b>HOW TO USE THIS MANUAL:</b><br/>"
        "This manual is formatted as a practical, numbered step-by-step guide for administrative staff. "
        "For each module, simply follow the sequence: <b>(1) How to Navigate & View</b> &rarr; <b>(2) How to Create (Add)</b> "
        "&rarr; <b>(3) How to Edit</b> &rarr; <b>(4) How to Delete or Deactivate</b> &rarr; "
        "<b>(5) How it Works Behind the Scenes</b>. Follow these instructions precisely to ensure data accuracy, "
        "prevent inventory conflicts, and deliver flawless concierge operations."
    )
    story.append(alert_box(intro_box, title="ADMINISTRATIVE OPERATIONAL DIRECTIVE", border_col=PRIMARY, bg_col=colors.HexColor("#F1F5F9")))
    story.append(PageBreak())

    # =========================================================================
    # CORE OPERATIONS - DETAILED STEP-BY-STEP
    # =========================================================================
    story.append(Paragraph("SECTION 1: CORE OPERATIONS MODULES", sec_header))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=12))

    # --- 1.1 DASHBOARD ---
    story.append(Paragraph("1.1 Dashboard", mod_header))
    story.append(Paragraph("<b>What it is and what it does:</b> The mission control center providing instant visibility into today's Arctic operations, revenue metrics, booking pace, and urgent alerts.", body_text))
    story.append(Paragraph("<b>How to Navigate and View:</b>", step_title))
    story.append(Paragraph("1. Log in to the administrative panel at <code>http://127.0.0.1:8000/admin/</code>.", step_text))
    story.append(Paragraph("2. Look at the left sidebar at the top under <b>CORE OPERATIONS</b> and click <b>Dashboard</b>.", step_text))
    story.append(Paragraph("3. You will see the main overview with four key KPI metric cards: Total Revenue, Confirmed Bookings, Upcoming Departures, and Fleet Utilization.", step_text))
    story.append(Paragraph("4. Below the cards, review the <i>Recent Bookings</i> table to see the latest online and manual reservations.", step_text))
    story.append(Paragraph("5. Use the omni-search input in the top header bar to quickly search any booking reference or guest name across the entire platform.", step_text))
    story.append(Spacer(1, 8))

    # --- 1.2 BOOKINGS ---
    story.append(Paragraph("1.2 Bookings", mod_header))
    story.append(Paragraph("<b>What it is and what it does:</b> The commercial ledger storing all tour reservations and VIP chauffeur transfers, guest manifests, payment balances, and pickup details.", body_text))
    
    story.append(Paragraph("<b>A. How to View Bookings:</b>", step_title))
    story.append(Paragraph("1. In the left sidebar under <b>CORE OPERATIONS</b>, click <b>Bookings</b> (`/admin/bookings/booking/`).", step_text))
    story.append(Paragraph("2. You will see the main list table displaying: <i>Booking Ref</i>, <i>Type (Tour / Chauffeur)</i>, <i>Channel Source</i>, <i>Customer</i>, <i>Status</i>, <i>Payment Status</i>, <i>Total Amount</i>, and <i>Created Date</i>.", step_text))
    story.append(Paragraph("3. In the right filter sidebar, click any filter to isolate bookings by Status (*Confirmed*, *Pending*, *Cancelled*, *Completed*), Channel Source (*Direct*, *GetYourGuide*, *Viator*, *Manual*), or Payment Status (*Paid*, *Unpaid*).", step_text))
    story.append(Paragraph("4. Use the search bar at the top of the table to find a booking by typing the Booking Reference (e.g., <code>NV-2026-921</code>) or customer surname.", step_text))

    story.append(Paragraph("<b>B. How to Create (Manual Phone / VIP Booking):</b>", step_title))
    story.append(Paragraph("1. Navigate to <b>Departure Calendar</b> (`/admin/operations/calendar/`) or <b>Bookings</b> (`/admin/bookings/booking/`).", step_text))
    story.append(Paragraph("2. In the top right corner, click the purple button <b>[+ Manual Booking]</b> (`/admin/bookings/manual-create/`).", step_text))
    story.append(Paragraph("3. <b>Select Departure:</b> Choose the target tour and date from the dropdown list.", step_text))
    story.append(Paragraph("4. <b>Select Vehicle Type:</b> Choose either <i>Private Car (4)</i>, <i>Micro (12)</i>, or <i>Group Bus (54)</i>.", step_text))
    story.append(Paragraph("5. <b>Enter Guest Numbers:</b> Enter Adults and Children counts. The system checks capacity in real time.", step_text))
    story.append(Paragraph("6. <b>Guest Account:</b> Search for an existing registered guest or type in a new guest's Name, Email, and Phone number.", step_text))
    story.append(Paragraph("7. <b>Pricing & Notes:</b> Enter any negotiated custom fare override, dietary constraints, and hotel pickup address.", step_text))
    story.append(Paragraph("8. Click <b>[Create Booking & Reserve Seats]</b> at the bottom. The booking is instantly confirmed and seat inventory is atomically decremented.", step_text))

    story.append(Paragraph("<b>C. How to Edit an Existing Booking:</b>", step_title))
    story.append(Paragraph("1. From the Bookings list, click directly on the blue <b>Booking Reference</b> (e.g., <code>NV-2026-1042</code>).", step_text))
    story.append(Paragraph("2. In the edit form, update dietary requirements, special concierge requests, or internal staff notes.", step_text))
    story.append(Paragraph("3. To mark an unpaid booking as settled: change <i>Payment Status</i> to <b>PAID</b> and <i>Status</i> to <b>CONFIRMED</b>.", step_text))
    story.append(Paragraph("4. Scroll to the bottom right and click <b>[Save]</b>.", step_text))

    story.append(Paragraph("<b>D. How to Cancel or Delete a Booking:</b>", step_title))
    story.append(Paragraph("1. <b>Standard Cancellation (Recommended):</b> Open the booking, change <i>Status</i> dropdown from `CONFIRMED` to `CANCELLED`, and click <b>Save</b>. The system automatically releases the reserved seats back into sellable inventory.", step_text))
    story.append(Paragraph("2. <b>Bulk Cancellation Action:</b> In the Bookings list, check the checkboxes next to the bookings, select <b>'🚫 Cancel booking & release capacity back to inventory'</b> from the Action dropdown, and click <b>Run</b>.", step_text))
    story.append(Paragraph("3. <b>Permanent Deletion Warning:</b> Never use 'Delete selected bookings' for genuine customer transactions as it permanently erases financial and invoice history.", step_text))

    story.append(alert_box(
        "<b>Behind the Scenes (Inventory Lock):</b> When a booking is created or confirmed, Django executes an atomic database transaction "
        "with <code>select_for_update()</code> on the specific <code>DepartureCapacity</code>. It increments <code>booked_count</code>, "
        "which immediately reduces <code>public_sellable</code>. When cancelled, <code>booked_count</code> is decremented and seats reappear on the public website.",
        title="HOW IT WORKS: ATOMIC BOOKING INVENTORY", border_col=ACCENT
    ))
    story.append(PageBreak())

    # --- 1.3 DEPARTURE CALENDAR ---
    story.append(Paragraph("1.3 Departure Calendar", mod_header))
    story.append(Paragraph("<b>What it is and what it does:</b> The visual capacity monitoring screen showing all departures across the month with an interactive calendar and an instant table view with zero page reload.", body_text))

    story.append(Paragraph("<b>A. How to View & Switch Modes:</b>", step_title))
    story.append(Paragraph("1. In the left sidebar under <b>CORE OPERATIONS</b>, click <b>Departure Calendar</b> (`/admin/operations/calendar/`).", step_text))
    story.append(Paragraph("2. <b>Calendar View (Default):</b> You see the full-width month grid. Each departure is an event pill displaying: <i>Departure Time</i>, <i>Tour Title</i>, and live vehicle badges (e.g., <code>🚗 2</code>, <code>🚐 8</code>, <code>🚌 45</code>).", step_text))
    story.append(Paragraph("3. <b>Switch to Table View (No Reload):</b> In the top right header, click <b>[Table View]</b>. The calendar seamlessly disappears and a rich operational table appears instantly without refreshing the browser.", step_text))
    story.append(Paragraph("4. <b>Switch back to Calendar:</b> Click <b>[Calendar]</b>. FullCalendar updates its dimensions and returns to the month view instantly.", step_text))
    story.append(Paragraph("5. <b>Quick Search in Table:</b> In Table View, type in the <i>Quick search</i> box. The table rows filter instantly as you type.", step_text))

    story.append(Paragraph("<b>B. How to Inspect & Manage Departures in the Calendar:</b>", step_title))
    story.append(Paragraph("1. Click on any departure pill in the calendar (or click <b>[Operations]</b> in Table View).", step_text))
    story.append(Paragraph("2. A popup modal titled <i>Departure Details</i> appears over the screen.", step_text))
    story.append(Paragraph("3. View the <i>Independent Vehicle Capacities</i> table showing Total, Booked, Blocked, Re-attempt, and Sellable seats.", step_text))
    story.append(Paragraph("4. <b>Quick Status Toggles:</b> Click <b>[Open]</b>, <b>[Close]</b>, or <b>[Block]</b> buttons inside the modal. The system updates the status via AJAX, closes the modal, and refreshes both the calendar and table without reloading the page.", step_text))
    story.append(Paragraph("5. Click <b>[Manual Booking]</b> to immediately launch a manual booking for this exact departure slot.", step_text))
    story.append(Paragraph("6. Click <b>[Close]</b> or the (X) button to exit the modal.", step_text))
    story.append(Spacer(1, 8))

    # --- 1.4 TOUR DEPARTURES ---
    story.append(Paragraph("1.4 Tour Departures", mod_header))
    story.append(Paragraph("<b>What it is and what it does:</b> The specific date/time instances when a tour runs. Every tour package has multiple scheduled departures throughout the winter season.", body_text))

    story.append(Paragraph("<b>A. How to View Tour Departures:</b>", step_title))
    story.append(Paragraph("1. In the left sidebar under <b>CORE OPERATIONS</b>, click <b>Tour Departures</b> (`/admin/tours/departure/`).", step_text))
    story.append(Paragraph("2. You will see columns: <i>Tour</i>, <i>Date</i>, <i>Time</i>, <i>Status</i>, and <i>Capacity (Sellable / Total)</i>.", step_text))
    story.append(Paragraph("3. Use the right sidebar filters to filter departures by Status (*Open*, *Sold Out*, *Blocked*, *Closed*), Date, or Tour.", step_text))

    story.append(Paragraph("<b>B. How to Create (Add) a New Tour Departure:</b>", step_title))
    story.append(Paragraph("1. In the top right corner of the Tour Departures page, click <b>[+ ADD DEPARTURE]</b>.", step_text))
    story.append(Paragraph("2. <b>Tour:</b> Select the parent Tour Package from the dropdown.", step_text))
    story.append(Paragraph("3. <b>Date:</b> Enter the departure date (e.g., `2026-12-15`) or use the calendar picker.", step_text))
    story.append(Paragraph("4. <b>Time:</b> Enter the start time (e.g., `10:00:00`) and optional end time.", step_text))
    story.append(Paragraph("5. <b>Status:</b> Leave as `OPEN` (Bookable).", step_text))
    story.append(Paragraph("6. <b>Vehicle Capacities (Bottom Inlines):</b> The system automatically populates inlines for *Private Car*, *Micro*, and *Group Bus*. You can customize Total Capacity (e.g., if using a 16-seat van instead of 12) or enter Adult/Child price overrides.", step_text))
    story.append(Paragraph("7. Click <b>[Save]</b> at the bottom right. The departure is created and is immediately bookable online.", step_text))

    story.append(Paragraph("<b>C. How to Edit an Existing Departure:</b>", step_title))
    story.append(Paragraph("1. In the Tour Departures list, click on the Tour title link of the departure.", step_text))
    story.append(Paragraph("2. Update the Date, Time, or Status.", step_text))
    story.append(Paragraph("3. To block seats for internal guides or luggage: scroll to the capacities inline and enter a number in <b>Blocked Seats</b>.", step_text))
    story.append(Paragraph("4. Click <b>[Save]</b>.", step_text))

    story.append(Paragraph("<b>D. How to Delete a Departure:</b>", step_title))
    story.append(Paragraph("1. In the list view, select the checkbox next to the departure.", step_text))
    story.append(Paragraph("2. Select 'Delete selected departures' from the Action dropdown and click 'Run'.", step_text))
    story.append(Paragraph("3. <i>Note:</i> If guests have already booked seats on this departure, Django will block deletion. You must first cancel or reassign those bookings before deleting the departure.", step_text))
    story.append(PageBreak())

    # --- 1.5 VEHICLE TYPES ---
    story.append(Paragraph("1.5 Vehicle Types (Tour Fleet Categories)", mod_header))
    story.append(Paragraph("<b>What it is and what it does:</b> Controls the three tour transport categories: <b>Private Car (4)</b>, <b>Micro (12)</b>, and <b>Group Bus (54)</b>. These define how departures partition their seats.", body_text))

    story.append(Paragraph("<b>A. How to View:</b> Click <b>Vehicle Types</b> in the left sidebar (`/admin/tours/vehicletype/`). You will see Name, Slug, Icon, Default Capacity, and Active status.", step_text))
    story.append(Paragraph("<b>B. How to Create:</b> Click <b>[+ ADD VEHICLE TYPE]</b>. Enter Name (e.g., 'Super Jeep'), Slug ('super-jeep'), Icon ('🚙'), Default Capacity (e.g., 6), Sort Order (e.g., 4), and check 'Is Active'. Click <b>Save</b>.", step_text))
    story.append(Paragraph("<b>C. How to Edit:</b> Click any vehicle type name. You can change the icon emoji, name, or default capacity. Click <b>Save</b>. (Note: Changing default capacity affects newly generated departures; existing departures retain their set capacity).", step_text))
    story.append(Paragraph("<b>D. How to Delete:</b> Check the box, select Delete, and click Run. (Recommendation: If departures exist, uncheck 'Is Active' instead of deleting).", step_text))
    story.append(Spacer(1, 8))

    # --- 1.6 RE-ATTEMPTS (AURORA) ---
    story.append(Paragraph("1.6 Re-attempts (Aurora Guarantee)", mod_header))
    story.append(Paragraph("<b>What it is and what it does:</b> Executes Nord Velocity's 100% Northern Lights Sightings Guarantee. When an Aurora tour encounters overcast skies with zero sightings, staff log re-attempts so guests can re-book on subsequent nights at €0.00.", body_text))

    story.append(Paragraph("<b>A. How to View:</b> Click <b>Re-attempts (Aurora)</b> in the sidebar (`/admin/bookings/guaranteedreattempt/`). You will see Original Booking, Reason, Status badge (*ELIGIBLE*, *REBOOKED*, *DECLINED*, *EXPIRED*), Original Departure, and Scheduled Re-attempt Departure.", step_text))
    story.append(Paragraph("<b>B. How to Create a Re-attempt Claim:</b>", step_title))
    story.append(Paragraph("1. Method 1 (Direct from Bookings): In <i>Bookings</i>, select the cloudy tour bookings, choose <b>'🌌 Mark as Failed Experience (Create Guaranteed Re-attempt)'</b> from the Action dropdown, and click <b>Run</b>.", step_text))
    story.append(Paragraph("2. Method 2 (Manual): Click <b>[+ ADD GUARANTEED RE-ATTEMPT]</b>. Select the original booking, enter Guest Count, set Reason = `WEATHER`, and set Status = `ELIGIBLE`.", step_text))
    story.append(Paragraph("<b>C. How to Rebook the Guest on a New Departure:</b>", step_title))
    story.append(Paragraph("1. When the guest requests a retry night: open the Re-attempt record.", step_text))
    story.append(Paragraph("2. In the <b>Re-attempt Departure</b> field, select the new departure slot.", step_text))
    story.append(Paragraph("3. Change <b>Status</b> to `REBOOKED`.", step_text))
    story.append(Paragraph("4. Click <b>Save</b>. The system automatically reserves the seats on the new departure and sends a confirmation voucher at €0 balance.", step_text))
    story.append(Spacer(1, 8))

    # --- 1.7 TOUR PACKAGES ---
    story.append(Paragraph("1.7 Tour Packages", mod_header))
    story.append(Paragraph("<b>What it is and what it does:</b> The master catalog of all Arctic tour experiences (e.g. Glass Igloo Safaris, Reindeer Sledding, Aurora Hunts).", body_text))

    story.append(Paragraph("<b>A. How to View:</b> Click <b>Tour Packages</b> in the sidebar (`/admin/tours/tour/`). Filter by Status (*Published*, *Draft*), Destination, or Travel Style. Search by title.", step_text))
    story.append(Paragraph("<b>B. How to Create a New Tour Package:</b>", step_title))
    story.append(Paragraph("1. Click <b>[+ ADD TOUR]</b> at the top right.", step_text))
    story.append(Paragraph("2. <b>Title:</b> Enter the full tour title (e.g., *'Rovaniemi Arctic Glass Igloo & Aurora Safari'*).", step_text))
    story.append(Paragraph("3. <b>Location:</b> Select Primary Destination (*Rovaniemi*) and Country (*Finland*).", step_text))
    story.append(Paragraph("4. <b>Classification:</b> Select Categories (*Northern Lights*, *Winter Safaris*), Travel Style, and Physical Difficulty (*Easy* / *Moderate*).", step_text))
    story.append(Paragraph("5. <b>Content:</b> Fill in Short Summary, Full Description, Inclusions (what is included), and Exclusions.", step_text))
    story.append(Paragraph("6. <b>Media Inline (Bottom):</b> Upload high-res 16:9 photos, check `Is Hero` on the primary thumbnail.", step_text))
    story.append(Paragraph("7. <b>Option Pricing Inline:</b> Add pricing for *Private Car*, *Micro*, and *Group Bus* with Adult and Child prices.", step_text))
    story.append(Paragraph("8. <b>Status:</b> Select `PUBLISHED` when ready to go live on the website, or `DRAFT` to keep hidden.", step_text))
    story.append(Paragraph("9. Click <b>[Save]</b>.", step_text))
    story.append(Paragraph("<b>C. How to Duplicate a Tour:</b> Select a tour checkbox in the list, choose <b>'📋 Duplicate selected tour(s)'</b> from the Action dropdown, and click Run. Clones all itineraries and pricing instantly.", step_text))
    story.append(Paragraph("<b>D. How to Delete / Archive:</b> To remove a tour without breaking past customer bookings, open the tour, change Status to `ARCHIVED`, and click Save.", step_text))
    story.append(PageBreak())

    # --- 1.8 to 1.10 ---
    story.append(Paragraph("1.8 Countries, 1.9 Tour Places & 1.10 Tour Categories", mod_header))
    story.append(Paragraph("<b>Countries (`/admin/tours/country/`):</b> Click <i>Countries</i>. Click [+ Add Country], enter Name (e.g. 'Finland'), upload Flag Icon, enter Currency code ('EUR'), and check 'Is Active'. Save. Drives destination menus.", step_text))
    story.append(Paragraph("<b>Tour Places & Cities (`/admin/tours/destination/`):</b> Click <i>Tour Places & Cities</i>. Click [+ Add Destination], enter City Name (e.g. 'Rovaniemi'), select Country, enter Airport Code ('RVN'), upload Scenic Banner. Save. Powers search filters and transfer hubs.", step_text))
    story.append(Paragraph("<b>Tour Categories (`/admin/tours/experiencetype/`):</b> Click <i>Tour Categories</i>. Click [+ Add Experience Type], enter Name (e.g. 'Northern Lights'), upload icon/banner, set sort order. Save. Controls category tags across the website.", step_text))
    story.append(Spacer(1, 8))

    # --- 1.11 FLEET CLASSES ---
    story.append(Paragraph("1.11 Fleet Classes (Executive Luxury Fleet)", mod_header))
    story.append(Paragraph("<b>What it is and what it does:</b> Controls the luxury categories displayed on the public Chauffeur hub (VIP, Business Class, Minivan, Micro, Coupe, First Class VIP, Executive Van). Each class contains pricing rules and inclusions.", body_text))

    story.append(Paragraph("<b>A. How to View:</b> In the sidebar under <b>CORE OPERATIONS</b>, click <b>Fleet Classes (Luxury Fleet)</b> (`/admin/chauffeur/vehicleclass/`). You will see Class Name, Thumbnail Preview, Fleet Size count, and Active status.", step_text))
    story.append(Paragraph("<b>B. How to Create a New Fleet Class:</b>", step_title))
    story.append(Paragraph("1. Click <b>[+ ADD VEHICLE CLASS]</b>.", step_text))
    story.append(Paragraph("2. Enter <b>Name</b> (e.g. *'Business Class'*), Slug (*'business-class'*), Max Passengers (*3*), Max Luggage (*2*).", step_text))
    story.append(Paragraph("3. Upload Silhouette Image/Icon.", step_text))
    story.append(Paragraph("4. In the <i>Pricing Rules</i> inline below, enter <b>Base Fare</b> (e.g. `75.00`), <b>Per Km Rate</b> (e.g. `2.80`), and Minimum Fare.", step_text))
    story.append(Paragraph("5. In the <i>Service Standards</i> and <i>Inclusions</i> inlines, add bullet points (*'Armored & Winter Prepared'*, *'Free Cancellation'*).", step_text))
    story.append(Paragraph("6. Check 'Is Active' and click <b>[Save]</b>.", step_text))
    story.append(Paragraph("<b>C. How to Edit Pricing:</b> Click on any class name, update the Base Fare or Per Km Rate in the Pricing Rule inline, and click Save. Public transfer quotes update instantly.", step_text))
    story.append(Paragraph("<b>D. How to Hide a Class:</b> Uncheck 'Is Active' and save. The class disappears from the public fleet grid immediately.", step_text))
    story.append(Spacer(1, 8))

    # --- 1.12 VIP CHAUFFEUR VEHICLES ---
    story.append(Paragraph("1.12 VIP Chauffeur Vehicles", mod_header))
    story.append(Paragraph("<b>What it is and what it does:</b> The physical fleet of luxury vehicles (e.g. Mercedes-Benz EQE Electric, Mercedes S-Class 580e) assigned to fleet classes.", body_text))

    story.append(Paragraph("<b>A. How to View:</b> Click <b>VIP Chauffeur Vehicles</b> in the sidebar (`/admin/chauffeur/vehicle/`). Displays Vehicle Name, Thumbnail, Class, Capacity, and Active status.", step_text))
    story.append(Paragraph("<b>B. How to Create:</b> Click <b>[+ ADD VEHICLE]</b>. Enter Name (e.g. 'Mercedes-Benz EQE Electric'), select Vehicle Class ('Business Class'), input License Plate, seats (3), bags (2). In <i>Vehicle Photos</i> inline, upload high-res photos and check 'Is Primary' on the best one. Click <b>Save</b>.", step_text))
    story.append(Paragraph("<b>C. How to Edit:</b> Click the vehicle name, update details or upload new photos, and click Save.", step_text))
    story.append(Paragraph("<b>D. How to Delete / Decommission:</b> Open vehicle, uncheck 'Is Active', and Save. The public fleet card counter (e.g., '1 Active Vehicle') decrements automatically.", step_text))
    story.append(Spacer(1, 8))

    # --- 1.13 FIXED AIRPORT ROUTES & 1.14 GUESTS ---
    story.append(Paragraph("1.13 Fixed Airport Routes & 1.14 Guests & Users", mod_header))
    story.append(Paragraph("<b>Fixed Airport Routes (`/admin/chauffeur/fixedroute/`):</b> Click <i>Fixed Airport Routes</i>. Click [+ Add Fixed Route]. Enter Origin (e.g. 'Helsinki-Vantaa Airport [HEL]'), Destination ('Helsinki City Center'), select Vehicle Class ('Business Class'), and enter Flat Fare (e.g. `95.00`). Click Save. Overrules distance calculations with flat executive pricing.", step_text))
    story.append(Paragraph("<b>Guests & Users (`/admin/accounts/customuser/`):</b> Click <i>Guests & Users</i>. Click [+ Add User] to create staff or concierge accounts (check 'Staff Status' to allow admin login). To view a customer's passport, dietary preferences, or VIP tier, click their email and inspect the <i>Customer Profile</i> inline.", step_text))
    story.append(PageBreak())

    # =========================================================================
    # MARKETING & CONTENT - STEP-BY-STEP
    # =========================================================================
    story.append(Paragraph("SECTION 2: MARKETING & CONTENT MODULES", sec_header))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=12))

    mkt_items = [
        ("2.1 Features & Value Props", "/admin/core/valueproposition/", "Homepage trust badges ('Certified Arctic Chauffeurs', 'Guaranteed Aurora Sightings').",
         "1. Click 'Features & Value Props' in sidebar.\n2. Click [+ Add Value Proposition].\n3. Enter Title, Subtitle, Phosphor icon name (e.g. 'ph-shield-check'), and Sort Order.\n4. Click Save. Displays live in homepage value ribbon."),
        
        ("2.2 Discounts & Offers", "/admin/core/homeoffercard/", "Homepage promotional banner cards ('Winter offer up to 30% off').",
         "1. Click 'Discounts & Offers' in sidebar.\n2. Click [+ Add Home Offer Card].\n3. Enter Badge ('Special Offer'), Title, Description, Button text ('See Packages'), target URL, and upload background photo.\n4. Check 'Is Active' and Save."),

        ("2.3 Partner Logos", "/admin/core/partnerlogo/", "Partner luxury hotel chains, airlines, and regional tourism boards.",
         "1. Click 'Partner Logos' in sidebar.\n2. Click [+ Add Partner Logo].\n3. Enter Partner Name, upload transparent PNG logo, and enter website URL.\n4. Check 'Is Active' and Save. Displays in homepage trust carousel."),

        ("2.4 Promo Coupons", "/admin/payments/coupon/", "Promotional discount codes for checkout.",
         "1. Click 'Promo Coupons' in sidebar.\n2. Click [+ Add Coupon].\n3. Enter Code (e.g. 'AURORA2026'), select Discount Type (Percentage or Fixed Amount), enter Discount Value (e.g. 15.00 for 15%), set Valid From and Expiration dates, and Max Uses.\n4. Save. System validates code at checkout."),

        ("2.5 Reviews & Ratings", "/admin/tours/tourreview/", "Moderate guest feedback and 1-5 star ratings.",
         "1. Click 'Reviews & Ratings' in sidebar.\n2. Click on a submitted review.\n3. Verify customer name and review text.\n4. Check 'Is Approved' = True.\n5. Click Save. Review immediately appears publicly on the tour page and updates average rating."),

        ("2.6 Blog & Stories", "/admin/content/blogpost/", "Travel reports, Arctic guides, and seasonal insights.",
         "1. Click 'Blog & Stories' in sidebar.\n2. Click [+ Add Blog Post].\n3. Enter Title, Slug, Rich Text Body, Author, Categories, upload Featured Image, and set Status to 'PUBLISHED'.\n4. Enter SEO Meta Title & Meta Description for Google ranking.\n5. Click Save."),

        ("2.7 Inquiries & Leads", "/admin/core/contactsubmission/", "Manage inquiries from the /contact/ form.",
         "1. Click 'Inquiries & Leads' in sidebar.\n2. Click on an inquiry to view guest name, email, phone, and inquiry message.\n3. In 'Status', update to 'CONTACTED' or 'CONVERTED'. Enter internal staff follow-up notes in the notes field.\n4. Click Save.")
    ]

    for title, url, desc, steps in mkt_items:
        story.append(Paragraph(title, mod_header))
        story.append(Paragraph(f"<b>URL:</b> <code>{url}</code> &bull; <i>{desc}</i>", body_text))
        for s in steps.split("\n"):
            story.append(Paragraph(s, step_text))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # =========================================================================
    # PLATFORM CONFIGURATION - STEP-BY-STEP
    # =========================================================================
    story.append(Paragraph("SECTION 3: PLATFORM CONFIGURATION MODULES", sec_header))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=12))

    cfg_items = [
        ("3.1 Site Settings (Mission, Stats & Brand Assets)", "/admin/core/sitesetting/1/change/", "Global branding, emergency telephone, live stats counters, and copyright text.",
         "1. Click 'Site Settings (Mission & Stats)' in sidebar.\n2. <b>Brand & Identity:</b> Update Site Name ('Nord Velocity'), upload Desktop Logo, Dark Admin Logo, and Mobile Favicon.\n3. <b>Statistics:</b> Update live counters: Completed Tours ('26K+'), Experience Years ('5'), Happy Travelers ('15,000+'), Satisfaction Rate ('98%').\n4. <b>Contact:</b> Update Concierge Email, 24/7 Telephone, and Physical Office Address in Helsinki.\n5. Scroll to bottom and click [Save]. Changes propagate immediately across all templates."),

        ("3.2 Navigation Icons (Navbar Items)", "/admin/core/navbaritem/", "Top header navbar links and dropdown menu configurations.",
         "1. Click 'Navigation Icons' in sidebar.\n2. To reorder or rename menu links (Home, Destination, Tour, Transport, Contact): click on the item, update title, URL, or Phosphor icon class.\n3. Click Save."),

        ("3.3 Mega Menu Promos & Company Menu Items", "/admin/core/megamenupromo/ & /companymenuitem/", "Visual promo callout cards in dropdowns.",
         "1. Click 'Mega Menu Promos'. Click [+ Add Mega Menu Promo].\n2. Select parent menu, enter headline ('Winter Offer up to 30%'), upload promo image, and specify target package link.\n3. Save. Appears automatically inside the mega-menu dropdown."),

        ("3.4 FAQs", "/admin/core/faqitem/", "Frequently Asked Questions displayed on /faq/ and tour pages.",
         "1. Click 'FAQs' in sidebar. Click [+ Add FAQ Item].\n2. Select Category (Booking, Chauffeur, Aurora Guarantee, Cancellation).\n3. Enter Question and detailed Answer.\n4. Check 'Is Published' and click Save."),

        ("3.5 Testimonials & Team Leadership", "/admin/core/testimonial/ & /teammember/", "Passenger reviews and guide bios.",
         "1. Click 'Testimonials' &rarr; [+ Add Testimonial]. Enter Guest Name, Country, Quote text, 5-star rating, and upload avatar photo. Save.\n2. Click 'Team Leadership' &rarr; [+ Add Team Member]. Enter Guide Name, Role ('Senior Arctic Chauffeur' / 'Master Aurora Guide'), bio, and photo. Save.")
    ]

    for title, url, desc, steps in cfg_items:
        story.append(Paragraph(title, mod_header))
        story.append(Paragraph(f"<b>URL:</b> <code>{url}</code> &bull; <i>{desc}</i>", body_text))
        for s in steps.split("\n"):
            story.append(Paragraph(s, step_text))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: ADVANCED BUSINESS SCENARIOS
    # =========================================================================
    story.append(Paragraph("SECTION 4: CORE BUSINESS ENGINES & MATH", sec_header))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=12))

    story.append(Paragraph("Scenario A: Multi-Party Shared Micro Van Capacity (Step-by-Step)", mod_header))
    story.append(Paragraph(
        "<b>Real-World Example:</b> A 12-seat Micro van departure is scheduled for a popular Lapland tour. "
        "Here is the exact progression of how independent parties book without overbooking:", body_text
    ))

    scen_rows = [
        ["Step", "Booking Party", "Seats", "Remaining Capacity", "System Behavior & Operational Directives"],
        ["Start", "Initial State", "—", "12 of 12 Seats", "Departure Status = OPEN. System displays 12 available seats on public website."],
        ["1", "Family A", "4 Seats", "8 Seats Left", "Database atomically increments booked_count to 4. 8 seats remain open for public booking."],
        ["2", "Group B", "5 Seats", "3 Seats Left", "Database increments booked_count to 9. 3 seats remain open. Availability badge turns amber."],
        ["3", "Couple C", "2 Seats", "1 Seat Left", "Database increments booked_count to 11. 1 seat remains open. High-demand urgency notice triggers."],
        ["4", "Solo Traveler D", "1 Seat", "0 Seats Left", "Database increments booked_count to 12. Status automatically switches to SOLD_OUT."],
        ["Overbook", "Party E (2 guests)", "2 Seats", "0 Seats Available", "<b>TRANSACTION BLOCKED:</b> Booking engine rejects request and displays alternative departures."]
    ]
    story.append(module_table(scen_rows[0], scen_rows[1:], widths=[55, 95, 60, 95, 218]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Manager Directive:</b> If only 1 seat remains unfilled when booking closes 24 hours prior to departure, the Operations Manager opens the departure and changes Status to <code>CLOSED</code>. The tour dispatches safely with 11 passengers.", body_text))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Scenario B: Chauffeur Point-to-Point vs Fixed Airport Rate Math", mod_header))
    story.append(Paragraph(
        "The Chauffeur pricing service calculates fares using this exact hierarchy:<br/>"
        "1. <b>Fixed Route Check:</b> If pickup and drop match a configured <code>FixedRoute</code> (e.g. Airport to City Center), the flat fee (e.g. €95.00) is applied directly.<br/>"
        "2. <b>Dynamic Point-to-Point:</b> If no fixed route exists:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>Final Fare = Base Rate + (Distance_KM &times; Per_KM_Rate)</code><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>Example:</i> Base €75.00 + (30 KM &times; €2.80) = <b>€159.00</b>.<br/>"
        "3. <b>Round-Trip Multiplier:</b> If the passenger selects Round-Trip, the return journey receives a 15% discount multiplier: <code>Round Trip Total = One Way &times; 1.85</code>.", body_text
    ))
    story.append(Spacer(1, 15))

    story.append(alert_box(
        "<b>ADMINISTRATOR COMPLIANCE CHECKLIST:</b><br/>"
        "&bull; <b>Never Hard Delete:</b> Always set <code>is_active = False</code> or <code>Status = ARCHIVED</code> to preserve audit trails.<br/>"
        "&bull; <b>Daily Calendar Audit:</b> Open <i>Departure Calendar</i> every morning at 08:00 to verify today's manifests and assign chauffeurs.<br/>"
        "&bull; <b>Nightly Weather Logs:</b> Log Aurora guaranteed re-attempts before midnight so affected guests receive re-booking vouchers immediately.",
        title="MANDATORY OPERATIONAL PROTOCOLS", border_col=PRIMARY, bg_col=LIGHT_BG
    ))

    # Build PDF
    doc.build(story, canvasmaker=StepManualNumberedCanvas)
    print(f"Step-by-step PDF manual generated successfully at: {filename}")
    return filename

if __name__ == "__main__":
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Nord_Velocity_Admin_Panel_Operations_Manual.pdf"))
    build_manual_pdf(out_path)
