"""
PDF Generator for Smart City Traffic Pattern & Congestion Analytics Mini-Project Report.
Conforms to Visvesvaraya Technological University (VTU) and Vemana Institute of Technology standard formats.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

BASE_DIR = r"C:\Users\Admin\.gemini\antigravity\scratch\smart-city-traffic-analytics"
ASSETS_DIR = os.path.join(BASE_DIR, "report_assets")
PDF_OUTPUT_PATH = os.path.join(BASE_DIR, "Smart_City_Traffic_Analytics_Report.pdf")
ARTIFACT_OUTPUT_PATH = r"C:\Users\Admin\.gemini\antigravity\brain\31f81685-557a-469d-9f4a-f3c7e5467b7f\Smart_City_Traffic_Analytics_Report.pdf"

# Numbered Canvas for Two-Pass Page Numbering and Border Drawing
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
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        page_num = self._pageNumber
        w, h = A4

        # 1. Double Border on Every Page
        self.saveState()
        self.setLineWidth(1.5)
        self.setStrokeColor(colors.black)
        self.rect(22, 22, w - 44, h - 44)
        self.setLineWidth(0.6)
        self.rect(25, 25, w - 50, h - 50)
        self.restoreState()

        # 2. Prelims (Pages 1 to 6) vs Content Pages (7 to 24)
        if page_num == 1:
            # Title page: no running header, no footer
            return
        elif page_num in [2, 3, 4, 5, 6]:
            # Preliminary roman numerals
            roman_numerals = {2: "ii", 3: "iii", 4: "iv", 5: "v", 6: "vi"}
            self.saveState()
            self.setFont("Helvetica", 10)
            self.drawCentredString(w / 2.0, 36, roman_numerals.get(page_num, ""))
            self.restoreState()
        else:
            # Main Content Pages (Pages 7 to 24 -> Page 1 to 18)
            content_page_num = page_num - 6
            self.saveState()
            
            # Running Header
            self.setFont("Helvetica-Bold", 8.5)
            self.setFillColor(colors.black)
            self.drawString(45, h - 38, "SMART CITY TRAFFIC ANALYTICS")
            self.drawRightString(w - 45, h - 38, "Dept of ISE, Vemana IT 2026")
            self.setLineWidth(0.6)
            self.line(45, h - 42, w - 45, h - 42)

            # Running Footer
            self.line(45, 46, w - 45, 46)
            self.setFont("Helvetica-Bold", 10)
            self.drawCentredString(w / 2.0, 32, str(content_page_num))
            self.restoreState()

def build_pdf():
    # Setup document
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_vtu = ParagraphStyle('VTUTitle', fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=1, textColor=colors.HexColor('#002060'))
    title_sub = ParagraphStyle('VTUSub', fontName='Helvetica-Bold', fontSize=11, leading=15, alignment=1, textColor=colors.HexColor('#002060'))
    proj_type = ParagraphStyle('ProjType', fontName='Helvetica-Bold', fontSize=12, leading=16, alignment=1, textColor=colors.black)
    proj_title = ParagraphStyle('ProjTitle', fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=1, textColor=colors.black)
    submitted_text = ParagraphStyle('SubText', fontName='Helvetica-Oblique', fontSize=10.5, leading=14, alignment=1, textColor=colors.black)
    student_name = ParagraphStyle('StudentName', fontName='Helvetica-Bold', fontSize=11.5, leading=15, alignment=1, textColor=colors.HexColor('#C00000'))
    guide_title = ParagraphStyle('GuideTitle', fontName='Helvetica-Bold', fontSize=11, leading=15, alignment=1, textColor=colors.HexColor('#C00000'))
    guide_desig = ParagraphStyle('GuideDesig', fontName='Helvetica', fontSize=10, leading=14, alignment=1, textColor=colors.black)
    college_header = ParagraphStyle('CollegeHdr', fontName='Helvetica-Bold', fontSize=11, leading=15, alignment=1, textColor=colors.black)
    academic_year = ParagraphStyle('AcadYear', fontName='Helvetica-Bold', fontSize=11, leading=15, alignment=1, textColor=colors.HexColor('#C00000'))

    ch_num = ParagraphStyle('ChNum', fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=1, textColor=colors.black)
    ch_title = ParagraphStyle('ChTitle', fontName='Helvetica-Bold', fontSize=15, leading=19, alignment=1, textColor=colors.black)
    sec_title = ParagraphStyle('SecTitle', fontName='Helvetica-Bold', fontSize=11.5, leading=15, textColor=colors.black)
    subsec_title = ParagraphStyle('SubSecTitle', fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.black)
    body = ParagraphStyle('Body', fontName='Helvetica', fontSize=10, leading=14, alignment=4, textColor=colors.black)
    bullet = ParagraphStyle('Bullet', fontName='Helvetica', fontSize=10, leading=14, leftIndent=18, textColor=colors.black)
    caption = ParagraphStyle('Caption', fontName='Helvetica-Bold', fontSize=9.5, leading=13, alignment=1, textColor=colors.black)
    code_style = ParagraphStyle('Code', fontName='Courier', fontSize=7.8, leading=10, textColor=colors.HexColor('#0F172A'))

    story = []

    # =========================================================================
    # PAGE 1: TITLE PAGE
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("VISVESVARAYA TECHNOLOGICAL UNIVERSITY", title_vtu))
    story.append(Paragraph("Jnana Sangama, Belagavi – 590 018.", title_sub))
    story.append(Spacer(1, 18))

    vtu_logo = os.path.join(ASSETS_DIR, "page_1_img_0_Image6.jpg")
    if os.path.exists(vtu_logo):
        story.append(Image(vtu_logo, width=95, height=95))
    story.append(Spacer(1, 16))

    story.append(Paragraph("A Mini Project<br/>Report On", proj_type))
    story.append(Spacer(1, 6))
    story.append(Paragraph("“SMART CITY TRAFFIC PATTERN &amp; CONGESTION ANALYTICS”", proj_title))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Submitted in partial fulfilment for the award of the degree of<br/><b>Bachelor of Engineering</b><br/>In<br/><b>Information Science and Engineering</b>", submitted_text))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Submitted by", ParagraphStyle('SubBy', fontName='Helvetica-Oblique', fontSize=10, leading=13, alignment=1)))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>SHREYA G POOJARI &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 1VI23IS100</b>", student_name))
    story.append(Paragraph("<b>IV SEM &nbsp;‘B’</b>", student_name))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Guided by:</b>", ParagraphStyle('GBy', fontName='Helvetica-Bold', fontSize=10.5, leading=14, alignment=1)))
    story.append(Paragraph("Mr. Rakesh B S", guide_title))
    story.append(Paragraph("Assistant Professor, Dept. of ISE", guide_desig))
    story.append(Spacer(1, 12))

    vemana_logo = os.path.join(ASSETS_DIR, "page_1_img_1_Image7.jpg")
    if os.path.exists(vemana_logo):
        story.append(Image(vemana_logo, width=105, height=90))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>DEPARTMENT OF INFORMATION SCIENCE AND ENGINEERING<br/>VEMANA INSTITUTE OF TECHNOLOGY<br/>BENGALURU – 560034</b>", college_header))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>AY: 2025-2026 (EVEN SEM)</b>", academic_year))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: CERTIFICATE
    # =========================================================================
    vemana_banner = os.path.join(ASSETS_DIR, "page_2_img_0_Image24.jpg")
    if os.path.exists(vemana_banner):
        story.append(Image(vemana_banner, width=500, height=52))
    story.append(Spacer(1, 15))
    story.append(Paragraph("DEPARTMENT OF INFORMATION SCIENCE &amp; ENGINEERING", ParagraphStyle('CertDept', fontName='Helvetica-Bold', fontSize=11, leading=15, alignment=1, textColor=colors.HexColor('#C00000'))))
    story.append(Spacer(1, 30))

    story.append(Paragraph("<b>Certificate</b>", ParagraphStyle('CertTitle', fontName='Helvetica-Bold', fontSize=18, leading=22, alignment=1)))
    story.append(Spacer(1, 35))

    cert_text = (
        "This is to certify that <b>SHREYA G POOJARI (1VI23IS100)</b>, Information Science and "
        "Engineering Department has successfully completed the mini Project entitled "
        "<b>“SMART CITY TRAFFIC PATTERN &amp; CONGESTION ANALYTICS”</b> in partial fulfillment for the requirement of the "
        "award of degree of <b>Bachelor of Engineering in Information Science and Engineering</b> of the "
        "<b>Visvesvaraya Technological University</b>, Belagavi during the academic year (2025-26). The "
        "project report has been approved as it satisfies the academic requirements in "
        "respect of the mini project work prescribed for the said degree."
    )
    story.append(Paragraph(cert_text, ParagraphStyle('CertBody', fontName='Helvetica', fontSize=11, leading=18, alignment=4)))
    story.append(Spacer(1, 140))

    sig_data = [
        [Paragraph("<b>Signature of the Guide</b><br/><br/><b>Mr. Rakesh B S</b>", ParagraphStyle('SigL', fontName='Helvetica', fontSize=11, leading=16, alignment=0)),
         Paragraph("<b>Signature of the HOD</b><br/><br/><b>Dr. Rajanna M</b>", ParagraphStyle('SigR', fontName='Helvetica', fontSize=11, leading=16, alignment=2))]
    ]
    sig_table = Table(sig_data, colWidths=[240, 240])
    sig_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(sig_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: ACKNOWLEDGEMENT
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>ACKNOWLEDGEMENT</b>", ch_title))
    story.append(Spacer(1, 30))

    story.append(Paragraph("We sincerely thank <b>Visvesvaraya Technological University</b> for providing an opportunity to carry out the mini project entitled <b>“SMART CITY TRAFFIC PATTERN &amp; CONGESTION ANALYTICS”</b>.", body))
    story.append(Spacer(1, 16))
    story.append(Paragraph("We thank <b>Dr. Vijayasimha Reddy. B. G</b>, Principal, Vemana Institute of Technology, Bengaluru for providing all the necessary support to carry out the project.", body))
    story.append(Spacer(1, 16))
    story.append(Paragraph("We would like to place on record our regards to <b>Dr. Rajanna M</b>, Professor and Head of the Department, Information Science and Engineering for his continued support.", body))
    story.append(Spacer(1, 16))
    story.append(Paragraph("We would also like to thank our guide, <b>Mr. Rakesh B S</b>, Assistant Professor, Dept. of ISE for his support and valuable guidance towards successful completion of the mini project.", body))
    story.append(Spacer(1, 16))
    story.append(Paragraph("We would be failing in our duty if we do not thank the faculty members, batch mates, lab staffs, technicians and family members for their constant support and guidance.", body))
    story.append(Spacer(1, 120))

    ack_sig = [
        ["", Paragraph("<b>SHREYA G POOJARI<br/>1VI23IS100</b>", ParagraphStyle('AckSig', fontName='Helvetica-Bold', fontSize=11, leading=16, alignment=2))]
    ]
    ack_table = Table(ack_sig, colWidths=[300, 180])
    story.append(ack_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: ABSTRACT
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>ABSTRACT</b>", ch_title))
    story.append(Spacer(1, 30))

    abstract_p1 = (
        "This project, <b>Smart City Traffic Pattern &amp; Congestion Analytics</b>, is an enterprise-grade "
        "Big Data analytics and predictive machine learning application designed to monitor, analyze, and forecast "
        "urban vehicular traffic dynamics. Leveraging <b>Apache Spark (PySpark)</b>, <b>Scikit-Learn</b>, and "
        "<b>Streamlit</b>, the system ingests large-scale historical telemetry from urban arterial sensor networks "
        "to identify recurring congestion hotspots, rush-hour commuter curves, and weekday versus weekend mobility shifts."
    )
    story.append(Paragraph(abstract_p1, body))
    story.append(Spacer(1, 16))

    abstract_p2 = (
        "The core data engineering pipeline employs distributed Spark DataFrames and Window operations to compute "
        "macroscopic flow metrics including Volume-to-Capacity (V/C) ratios and Speed Performance Indices (SPI). "
        "A multi-criteria Congestion Hotspot Index (CHI) algorithm ranks arterial chokepoints based on physical capacity "
        "saturation, velocity degradation, and severe congestion persistence. Furthermore, a leakage-free chronological "
        "machine learning forecasting pipeline utilizing Random Forest and Ridge regression predicts future corridor volume, "
        "achieving a 57.9% error reduction (MAE) over traditional moving-average persistence baselines."
    )
    story.append(Paragraph(abstract_p2, body))
    story.append(Spacer(1, 16))

    abstract_p3 = (
        "The interactive web dashboard provides traffic authorities and municipal planners with comprehensive visual "
        "telemetry—featuring interactive Mapbox geospatial corridor views, spatiotemporal matrix heatmaps, and data "
        "quality audit diagnostics. This mini project highlights essential Big Data engineering skills, distributed "
        "transformations, and predictive modeling, providing a scalable architectural foundation for modern intelligent "
        "transportation systems."
    )
    story.append(Paragraph(abstract_p3, body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: CONTENTS
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>CONTENTS</b>", ch_title))
    story.append(Spacer(1, 30))

    contents_data = [
        [Paragraph("<b>1. Title Page</b>", body), Paragraph("<b>i</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>2. Certificate</b>", body), Paragraph("<b>ii</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>3. Acknowledgment</b>", body), Paragraph("<b>iii</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>4. Abstract</b>", body), Paragraph("<b>iv</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>5. List of Figures</b>", body), Paragraph("<b>v</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>6. Introduction</b>", body), Paragraph("<b>1</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>7. Problem Statement</b>", body), Paragraph("<b>4</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>8. Requirements</b>", body), Paragraph("<b>5</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>9. Methodology</b>", body), Paragraph("<b>7</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>10. Code</b>", body), Paragraph("<b>9</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>11. Results</b>", body), Paragraph("<b>13</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>12. Geo Tag photo</b>", body), Paragraph("<b>15</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>13. Conclusion</b>", body), Paragraph("<b>17</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
        [Paragraph("<b>14. References</b>", body), Paragraph("<b>18</b>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))],
    ]
    t_contents = Table(contents_data, colWidths=[400, 80], rowHeights=24)
    t_contents.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_contents)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: LIST OF FIGURES
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>LIST OF FIGURES</b>", ch_title))
    story.append(Spacer(1, 30))

    fig_headers = [
        [Paragraph("<b>Figure No.</b>", ParagraphStyle('FH', fontName='Helvetica-Bold', fontSize=11, alignment=1)),
         Paragraph("<b>Name</b>", ParagraphStyle('FH', fontName='Helvetica-Bold', fontSize=11, alignment=1)),
         Paragraph("<b>Page No.</b>", ParagraphStyle('FH', fontName='Helvetica-Bold', fontSize=11, alignment=1))]
    ]
    fig_rows = [
        [Paragraph("3.1", ParagraphStyle('FC', alignment=1)), Paragraph("Overall architecture flowchart", body), Paragraph("6", ParagraphStyle('FC', alignment=1))],
        [Paragraph("4.1", ParagraphStyle('FC', alignment=1)), Paragraph("Streamlit user input &amp; filter interface", body), Paragraph("7", ParagraphStyle('FC', alignment=1))],
        [Paragraph("4.2", ParagraphStyle('FC', alignment=1)), Paragraph("PySpark Big Data processing workflow", body), Paragraph("8", ParagraphStyle('FC', alignment=1))],
        [Paragraph("4.3", ParagraphStyle('FC', alignment=1)), Paragraph("Traffic congestion heatmap display", body), Paragraph("8", ParagraphStyle('FC', alignment=1))],
        [Paragraph("6.1", ParagraphStyle('FC', alignment=1)), Paragraph("Screenshot of Final output &amp; KPIs", body), Paragraph("13-14", ParagraphStyle('FC', alignment=1))],
        [Paragraph("6.2", ParagraphStyle('FC', alignment=1)), Paragraph("Screenshot of machine learning forecast output", body), Paragraph("14", ParagraphStyle('FC', alignment=1))],
        [Paragraph("7.1", ParagraphStyle('FC', alignment=1)), Paragraph("Geo-tagged photo project submission", body), Paragraph("15-16", ParagraphStyle('FC', alignment=1))]
    ]
    t_figs = Table(fig_headers + fig_rows, colWidths=[90, 300, 90], rowHeights=[26] + [28]*7)
    t_figs.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9'))
    ]))
    story.append(t_figs)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: CHAPTER 1 - INTRODUCTION (Page 1)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>CHAPTER-1</b>", ch_num))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>INTRODUCTION</b>", ch_title))
    story.append(Spacer(1, 14))

    intro_p1 = (
        "The Smart City Traffic Pattern &amp; Congestion Analytics platform is a distributed data engineering "
        "and machine learning mini project developed to help municipal transportation planners and urban authorities "
        "monitor and mitigate vehicular congestion. Urban traffic telemetry—generated from roadside sensors, "
        "inductive loops, and traffic camera stations—produces continuous high-velocity data streams that overwhelm "
        "traditional desktop spreadsheet software. By leveraging <b>Apache Spark (PySpark)</b>, this platform provides "
        "scalable DataFrame transformations and Window aggregations to process millions of records efficiently. "
        "Combined with a responsive <b>Streamlit</b> interface and <b>Scikit-Learn</b> forecasting models, the system "
        "translates raw traffic sensor logs into actionable congestion mitigation intelligence."
    )
    story.append(Paragraph(intro_p1, body))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>1.1 Objectives of the Project</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• Build an interactive, web-based Big Data traffic analytics platform using Python and Streamlit.", bullet))
    story.append(Paragraph("• Leverage Apache Spark (PySpark) for distributed DataFrame cleaning, aggregation, and ranking.", bullet))
    story.append(Paragraph("• Ingest and clean large-scale urban sensor telemetry containing flow volumes, speeds, and road capacities.", bullet))
    story.append(Paragraph("• Calculate macro traffic metrics: Volume-to-Capacity (V/C) ratio and Speed Performance Index (SPI).", bullet))
    story.append(Paragraph("• Formulate an objective Congestion Hotspot Index (CHI) to rank chronic arterial bottlenecks.", bullet))
    story.append(Paragraph("• Develop a leakage-free chronological machine learning model to forecast traffic volume.", bullet))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>1.2 Working of the Project</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• The project functions through a modular, four-stage data processing pipeline:", bullet))
    story.append(Paragraph("• <b>Telemetry Ingestion:</b> Historical sensor observations (14,400+ hourly logs across 10 strategic city corridors) are ingested from CSV into Spark DataFrames.", bullet))
    story.append(Paragraph("• <b>Data Cleansing &amp; Feature Engineering:</b> Anomalous readings (e.g. negative speeds or impossible counts) are clipped and imputed via temporal median imputation.", bullet))
    story.append(Paragraph("• <b>Distributed Aggregations:</b> PySpark computes diurnal curves, rush-hour differentials (Morning, Midday, Evening, Night), and weekday vs. weekend variances.", bullet))
    story.append(Paragraph("• <b>Predictive Modeling:</b> Chronological lag features (1h, 24h, 168h) feed Random Forest and Ridge regressors to forecast future volume.", bullet))
    story.append(Paragraph("• <b>Visualization Sink:</b> The web dashboard renders interactive Mapbox corridor maps, diurnal dual-axis flow curves, and hotspot ranking matrices in real-time.", bullet))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: CHAPTER 1 - INTRODUCTION (Page 2)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>1.3 Scope of the Project</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("This project establishes a production-ready template for municipal smart city transportation management centers. Its operational scope includes:", body))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• Monitoring multi-corridor vehicular volume, speed degradation, and capacity saturation.", bullet))
    story.append(Paragraph("• Identifying rush-hour peak dynamics to guide dynamic traffic light timing and transit scheduling.", bullet))
    story.append(Paragraph("• Detecting chronic bottlenecks using empirical multi-factor criteria without subjective bias.", bullet))
    story.append(Paragraph("• Providing municipal engineers with predictive volume estimates for roadwork scheduling.", bullet))
    story.append(Paragraph("• Serving as a scalable architecture ready for deployment on cloud clusters (AWS EMR / Databricks).", bullet))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>1.4 Organization of the Project Work</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("The project execution is organized into structured engineering phases—commencing with data schema design, followed by distributed PySpark engine implementation, machine learning modeling, and web dashboard integration.", body))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>1.4.1 Requirement Analysis</b>", subsec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("This phase defines system specifications for scalable smart city data handling:", body))
    story.append(Paragraph("• Support ingestion of multi-sensor telemetry with timestamp, location, volume, and velocity fields.", bullet))
    story.append(Paragraph("• Implement distributed in-memory data processing to prevent memory overflow (OutOfMemoryError).", bullet))
    story.append(Paragraph("• Ensure strict chronological data partitioning to prevent future-to-past data leakage in forecasting.", bullet))
    story.append(Paragraph("• Deliver responsive, interactive visualizations accessible via standard web browsers.", bullet))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>1.4.2 System Design</b>", subsec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("The system adopts a multi-tier big data analytics architecture:", body))
    story.append(Paragraph("• <b>Presentation Layer:</b> Streamlit multi-page web application featuring Plotly visualizations.", bullet))
    story.append(Paragraph("• <b>Analytics &amp; ML Layer:</b> Scikit-Learn regression models and multi-factor scoring algorithms.", bullet))
    story.append(Paragraph("• <b>Distributed Compute Layer:</b> Apache Spark (PySpark 4.2.0) engine executing Window functions.", bullet))
    story.append(Paragraph("• <b>Data Storage Layer:</b> Validated CSV / Parquet columnar datasets with schema specifications.", bullet))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>1.4.3 Frontend Development</b>", subsec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("A modern, responsive dashboard was built using Streamlit. Global sidebar widgets allow dynamic filtering by corridor, date range, commute schedule (weekdays vs. weekends), and weather condition.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: CHAPTER 1 - INTRODUCTION (Page 3)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>1.4.4 Backend &amp; Big Data Development</b>", subsec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("The core backend processes large-scale telemetry using Apache Spark (PySpark):", body))
    story.append(Paragraph("• Implemented singleton SparkSession management configured for multi-core local parallelism.", bullet))
    story.append(Paragraph("• Utilized PySpark Catalyst query optimization for predicate pushdown and column pruning.", bullet))
    story.append(Paragraph("• Built distributed Window aggregations to compute rolling hourly metrics and corridor rankings.", bullet))
    story.append(Paragraph("• Developed Scikit-Learn forecasting models using chronological lag features (1h, 24h, 168h).", bullet))
    story.append(Paragraph("• Added comprehensive exception handling to ensure continuous server operation.", bullet))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>1.4.5 Data Storage &amp; Quality Setup</b>", subsec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("A calibrated dataset containing 14,400+ hourly sensor observations across 10 strategic arterial corridors was structured with the following schema:", body))
    story.append(Paragraph("• Spatial coordinates: Latitude, longitude, unique corridor identifier, and corridor name.", bullet))
    story.append(Paragraph("• Flow attributes: Hourly vehicle count, harmonic average speed, and road design capacity.", bullet))
    story.append(Paragraph("• Regulatory limits: Posted arterial speed limit (40 km/h to 100 km/h).", bullet))
    story.append(Paragraph("• Ambient factors: Weather conditions (Clear, Rainy, Foggy, Overcast) and incident flags.", bullet))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>1.4.6 Output Display</b>", subsec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Analytical results are visualized across six specialized dashboard views: Traffic Overview, Peak-Hour Analysis, Congestion Heatmaps, Hotspot Detection, Predictive ML Forecasting, and Dataset Explorer.", body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>1.4.7 Testing and Validation</b>", subsec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Automated test suites were developed using <b>Pytest</b>. 18 comprehensive tests verify data deduplication, bounds clipping, PySpark Window ranking, metric calculations, and chronological forecasting partitions with a 100% pass rate.", body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>1.4.8 Documentation</b>", subsec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Comprehensive documentation—including architecture schematics, mathematical formulations, user guides, and interview technical Q&amp;A—was compiled to support academic and operational review.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: CHAPTER 2 - PROBLEM STATEMENT (Page 4)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>CHAPTER-2</b>", ch_num))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>PROBLEM STATEMENT</b>", ch_title))
    story.append(Spacer(1, 14))

    prob_intro = (
        "Modern metropolitan areas face severe vehicular congestion resulting from rapid urbanization, "
        "increasing vehicle ownership, and constrained road infrastructure. Traditional traffic monitoring systems "
        "rely on manual traffic counts or isolated desktop spreadsheets that fail to handle high-frequency sensor streams, "
        "leaving municipal authorities with poor situational awareness and reactive rather than proactive management. "
        "The Smart City Traffic Pattern &amp; Congestion Analytics project resolves these limitations by delivering a "
        "distributed Big Data architecture capable of transforming raw sensor feeds into actionable congestion intelligence."
    )
    story.append(Paragraph(prob_intro, body))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>2.1 Urban Gridlock and Economic Inefficiencies</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Chronic traffic delays inflict billions of dollars in lost commuter productivity, excess fuel consumption, and greenhouse emissions. Without real-time capacity monitoring, traffic signals operate on rigid, outdated schedules that worsen urban delays.", body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2.2 Lack of Distributed Big Data Processing</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("As smart cities deploy thousands of IoT sensors collecting second-by-second telemetry, conventional single-threaded tools (such as standalone Pandas or Excel) suffer from memory exhaustion (OutOfMemoryError) and sluggish processing, preventing scalable network analysis.", body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2.3 Unreliable Peak-Hour and Chokepoint Identification</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Traditional assessments evaluate congestion purely by vehicular speed, unfairly penalizing low-speed-limit urban avenues while overlooking multi-lane freeways operating near breakdown capacity. A multi-factor index combining speed deficit and capacity saturation is essential.", body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2.4 Data Leakage in Naive Traffic Forecasting</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Many conventional forecasting models mistakenly apply randomized K-fold cross-validation to time series data, causing future observations to leak into training sets. This yields falsely optimistic evaluation metrics that completely fail when deployed in live traffic control.", body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2.5 Inability to Provide Actionable Smart City Insights</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Raw sensor numbers fail to assist city operators without intuitive visualization. A centralized platform combining spatiotemporal heatmaps, diurnal curves, and root-cause bottleneck diagnostics is required to inform municipal policy.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 11: CHAPTER 3 - REQUIREMENTS (Page 5)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>CHAPTER-3</b>", ch_num))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>REQUIREMENTS</b>", ch_title))
    story.append(Spacer(1, 14))

    req_intro = (
        "The Smart City Traffic Pattern &amp; Congestion Analytics application is engineered to process, analyze, "
        "and forecast large-scale traffic telemetry efficiently. The platform incorporates rigorous functional "
        "specifications and robust architectural standards to guarantee high performance, security, and scalability."
    )
    story.append(Paragraph(req_intro, body))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>3.1 Functional Requirements</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• <b>Data Ingestion &amp; Quality Audit:</b> Ingest multi-attribute sensor CSV/Parquet files, remove duplicate records, clip physical outliers (speeds &gt; 160 km/h or negative counts), and impute missing values.", bullet))
    story.append(Paragraph("• <b>Distributed PySpark Aggregations:</b> Utilize Apache Spark DataFrames to compute hourly, daily, and corridor-level traffic flow, velocity, and volume-to-capacity metrics.", bullet))
    story.append(Paragraph("• <b>Peak-Hour Analytics:</b> Identify diurnal morning, midday, evening, and night rush hours, contrasting weekday office commuter surges with weekend leisure mobility.", bullet))
    story.append(Paragraph("• <b>Congestion Hotspot Detection:</b> Calculate the composite Congestion Hotspot Index (CHI) to rank the top 10 bottleneck corridors with root-cause diagnostic summaries.", bullet))
    story.append(Paragraph("• <b>Predictive Traffic Forecasting:</b> Train machine learning regressors (Random Forest and Ridge) using chronological lag features without lookahead data leakage.", bullet))
    story.append(Paragraph("• <b>Interactive Multi-Page Dashboard:</b> Present results across responsive Streamlit pages with Plotly maps, box plots, and matrix heatmaps.", bullet))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>3.2 Non-Functional Requirements</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• <b>Usability:</b> Clean, professional smart-city user interface with intuitive navigation, styled metric cards, and responsive filter controls.", bullet))
    story.append(Paragraph("• <b>Reliability:</b> Consistent execution across diverse sensor inputs with graceful fallbacks for missing values or extreme filter combinations.", bullet))
    story.append(Paragraph("• <b>Maintainability:</b> Highly modular Python codebase adhering to PEP 8 standards with comprehensive docstrings and clear layer separation.", bullet))
    story.append(Paragraph("• <b>Scalability:</b> Big Data architecture designed to scale seamlessly from local standalone execution (local[*]) to distributed cloud clusters (AWS EMR / Databricks).", bullet))
    story.append(Paragraph("• <b>Portability:</b> Fully cross-platform implementation compatible with Windows 10/11 and Linux environments supporting Java 17 and Python 3.11+.", bullet))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 12: CHAPTER 3 - ARCHITECTURE FLOWCHART (Page 6)
    # =========================================================================
    story.append(Spacer(1, 15))
    fig3_1_img = os.path.join(ASSETS_DIR, "fig3_1_architecture.png")
    if os.path.exists(fig3_1_img):
        story.append(Image(fig3_1_img, width=460, height=430))
    story.append(Spacer(1, 18))
    story.append(Paragraph("<b>Fig 3.1: Overall architecture flowchart</b>", caption))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 13: CHAPTER 4 - METHODOLOGY (Page 7)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>CHAPTER-4</b>", ch_num))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>METHODOLOGY</b>", ch_title))
    story.append(Spacer(1, 12))

    story.append(Paragraph("The application implements a decoupled, three-tier Big Data analytics architecture:", body))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>4.1 Frontend Layer (Streamlit &amp; Plotly):</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("The presentation layer provides municipal operators with an interactive dashboard. Global sidebar widgets enable multi-corridor selection, calendar date slicing, commuter schedule filtering (Weekdays vs. Weekends), and weather selection. Real-time Plotly charts dynamically update upon user interaction.", body))
    story.append(Spacer(1, 10))

    fig4_1_img = os.path.join(ASSETS_DIR, "fig4_1_user_interface.png")
    if os.path.exists(fig4_1_img):
        story.append(Image(fig4_1_img, width=460, height=220))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Fig 4.1: User input filter interface</b>", caption))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>4.2 Big Data Processing Layer (PySpark Engine):</b>", sec_title))
    story.append(Paragraph("• Initializes an optimized local SparkSession with loopback IP bindings (127.0.0.1) and memory limits.", bullet))
    story.append(Paragraph("• Enforces schema validation and derives temporal columns (hour, day of week, weekend indicator).", bullet))
    story.append(Paragraph("• Executes distributed Window aggregations to compute severe congestion frequency and corridor rankings.", bullet))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>4.3 Analytical &amp; Machine Learning Layer:</b>", sec_title))
    story.append(Paragraph("• Evaluates the multi-criteria Congestion Hotspot Index (CHI) across all monitored arterials.", bullet))
    story.append(Paragraph("• Generates chronological lag features (1h, 24h, 168h) and cyclical sine/cosine hour transforms.", bullet))
    story.append(Paragraph("• Trains Random Forest and Ridge regressors using strict 80/20 chronological train/test partitions.", bullet))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 14: CHAPTER 4 - METHODOLOGY CONTD (Page 8)
    # =========================================================================
    story.append(Spacer(1, 10))
    fig4_2_img = os.path.join(ASSETS_DIR, "fig4_2_pyspark_workflow.png")
    if os.path.exists(fig4_2_img):
        story.append(Image(fig4_2_img, width=450, height=215))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Fig 4.2: PySpark Big Data processing workflow</b>", caption))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>4.4 Presentation Layer (Streamlit Multi-Page UI):</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("The presentation layer receives aggregated telemetry frames from the PySpark core and dynamically displays interactive geospatial heatmaps, diurnal commuter curves, and predictive forecasts.", body))
    story.append(Spacer(1, 10))

    fig4_3_img = os.path.join(ASSETS_DIR, "fig4_3_heatmap_display.png")
    if os.path.exists(fig4_3_img):
        story.append(Image(fig4_3_img, width=460, height=210))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Fig 4.3: Traffic congestion heatmap display</b>", caption))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 15: CHAPTER 5 - CODE (Page 9)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>CHAPTER-5</b>", ch_num))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>CODE</b>", ch_title))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>5.1 PySpark Big Data Processing &amp; Ingestion Engine</b>", sec_title))
    story.append(Spacer(1, 4))

    code_p1 = (
        "from pyspark.sql import SparkSession\n"
        "from pyspark.sql import functions as f\n"
        "from pyspark.sql.window import Window\n"
        "from pyspark.sql.types import DoubleType\n\n"
        "class SparkTrafficProcessor:\n"
        "    _instance = None\n"
        "    _spark = None\n\n"
        "    def get_spark_session(self):\n"
        "        if self._spark is None:\n"
        "            self._spark = (SparkSession.builder\n"
        "                .appName('SmartCityTrafficAnalytics')\n"
        "                .master('local[*]')\n"
        "                .config('spark.driver.memory', '2g')\n"
        "                .config('spark.sql.shuffle.partitions', '4')\n"
        "                .config('spark.driver.bindAddress', '127.0.0.1')\n"
        "                .config('spark.sql.adaptive.enabled', 'true')\n"
        "                .getOrCreate())\n"
        "            self._spark.sparkContext.setLogLevel('WARN')\n"
        "        return self._spark\n\n"
        "    def load_traffic_spark_df(self, csv_path='data/traffic_data.csv'):\n"
        "        spark = self.get_spark_session()\n"
        "        df = spark.read.option('header', 'true').option('inferSchema', 'true').csv(csv_path)\n"
        "        return (df.withColumn('timestamp', f.to_timestamp('timestamp', 'yyyy-MM-dd HH:mm:ss'))\n"
        "                  .withColumn('vehicle_count', f.col('vehicle_count').cast(DoubleType()))\n"
        "                  .withColumn('average_speed', f.col('average_speed').cast(DoubleType()))\n"
        "                  .withColumn('road_capacity', f.col('road_capacity').cast(DoubleType()))\n"
        "                  .filter((f.col('average_speed') > 0) & (f.col('average_speed') <= 160))\n"
        "                  .withColumn('hour', f.hour('timestamp'))\n"
        "                  .withColumn('volume_capacity_ratio', f.round(f.col('vehicle_count') / f.col('road_capacity'), 3))\n"
        "                  .withColumn('is_severely_congested', f.when(f.col('volume_capacity_ratio') >= 0.85, 1).otherwise(0)))"
    )
    p_code1 = Paragraph(code_p1.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)
    box1 = Table([[p_code1]], colWidths=[480])
    box1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(box1)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 16: CHAPTER 5 - CODE CONTD (Page 10)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>5.2 PySpark Distributed Window Aggregations &amp; Ranking</b>", sec_title))
    story.append(Spacer(1, 4))

    code_p2 = (
        "    def compute_location_congestion_ranking(self, spark_df):\n"
        "        # Distributed aggregation per arterial corridor\n"
        "        agg_df = (spark_df.groupBy('location_id', 'location_name')\n"
        "            .agg(\n"
        "                f.count('*').alias('total_observations'),\n"
        "                f.round(f.sum('vehicle_count'), 0).alias('total_vehicle_volume'),\n"
        "                f.round(f.avg('vehicle_count'), 1).alias('avg_hourly_volume'),\n"
        "                f.round(f.avg('average_speed'), 1).alias('avg_speed_kmh'),\n"
        "                f.round(f.avg('volume_capacity_ratio'), 3).alias('mean_vc_ratio'),\n"
        "                f.sum('is_severely_congested').alias('congested_hours_count'),\n"
        "                f.round((f.sum('is_severely_congested') / f.count('*')) * 100, 2).alias('severe_congestion_pct')\n"
        "            ))\n\n"
        "        # PySpark Window Ranking Function\n"
        "        window_spec = Window.orderBy(f.desc('severe_congestion_pct'), f.desc('mean_vc_ratio'))\n"
        "        ranked_df = agg_df.withColumn('congestion_rank', f.row_number().over(window_spec))\n\n"
        "        # Collect only compact aggregated summary back to driver\n"
        "        return ranked_df.orderBy('congestion_rank').toPandas()\n\n"
        "    def compute_diurnal_profiles(self, spark_df):\n"
        "        # Compute 24-hour diurnal commuter curves: Weekdays vs Weekends\n"
        "        diurnal_df = (spark_df.groupBy('is_weekend', 'hour')\n"
        "            .agg(\n"
        "                f.round(f.avg('vehicle_count'), 0).alias('avg_volume'),\n"
        "                f.round(f.avg('average_speed'), 1).alias('avg_speed')\n"
        "            ).orderBy('is_weekend', 'hour'))\n"
        "        return diurnal_df.toPandas()"
    )
    p_code2 = Paragraph(code_p2.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)
    box2 = Table([[p_code2]], colWidths=[480])
    box2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(box2)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 17: CHAPTER 5 - CODE CONTD (Page 11)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>5.3 Congestion Hotspot Index (CHI) Multi-Factor Detection</b>", sec_title))
    story.append(Spacer(1, 4))

    code_p3 = (
        "import numpy as np\n"
        "import pandas as pd\n\n"
        "def calculate_hotspot_scores(df):\n"
        "    # Weights: w1 (V/C)=0.35, w2 (Speed Deficit)=0.35, w3 (Severe Freq)=0.20, w4 (Volatility)=0.10\n"
        "    records = []\n"
        "    for loc_name, group in df.groupby('location_name'):\n"
        "        total_obs = len(group)\n"
        "        cap = group['road_capacity'].iloc[0]\n"
        "        limit = group['speed_limit'].iloc[0]\n"
        "        avg_speed = group['average_speed'].mean()\n"
        "        avg_volume = group['vehicle_count'].mean()\n"
        "        std_speed = group['average_speed'].std()\n\n"
        "        # Normalized dimensions\n"
        "        mean_vc = (group['vehicle_count'] / cap).mean()\n"
        "        severe_freq = (group['volume_capacity_ratio'] >= 0.85).sum() / total_obs\n"
        "        c_vc = min(1.0, mean_vc)\n"
        "        c_speed_deficit = max(0.0, min(1.0, 1.0 - (avg_speed / limit)))\n"
        "        c_freq = severe_freq\n"
        "        c_volatility = min(1.0, std_speed / (avg_speed + 1e-6))\n\n"
        "        # Composite CHI Score (0 to 100)\n"
        "        chi_score = (0.35*c_vc + 0.35*c_speed_deficit + 0.20*c_freq + 0.10*c_volatility) * 100.0\n"
        "        severity = 'Critical Bottleneck' if chi_score >= 68 else ('High Congestion' if chi_score >= 52 else 'Moderate')\n\n"
        "        records.append({'location_name': loc_name, 'chi_score': round(chi_score, 1),\n"
        "                        'severity': severity, 'avg_volume': round(avg_volume, 0),\n"
        "                        'avg_speed': round(avg_speed, 1), 'mean_vc_ratio': round(mean_vc, 3)})\n\n"
        "    return pd.DataFrame(records).sort_values(by='chi_score', ascending=False).reset_index(drop=True)"
    )
    p_code3 = Paragraph(code_p3.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)
    box3 = Table([[p_code3]], colWidths=[480])
    box3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(box3)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 18: CHAPTER 5 - CODE CONTD (Page 12)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>5.4 Chronological Time-Series Machine Learning Forecaster</b>", sec_title))
    story.append(Spacer(1, 4))

    code_p4 = (
        "from sklearn.ensemble import RandomForestRegressor\n"
        "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n\n"
        "def create_forecasting_features(df, location_name=None):\n"
        "    sub_df = df[df['location_name'] == location_name].copy() if location_name else df.copy()\n"
        "    sub_df = sub_df.sort_values('timestamp').reset_index(drop=True)\n\n"
        "    # Strictly past chronological lag features (Prevent Data Leakage)\n"
        "    sub_df['lag_1h'] = sub_df['vehicle_count'].shift(1)\n"
        "    sub_df['lag_2h'] = sub_df['vehicle_count'].shift(2)\n"
        "    sub_df['lag_24h'] = sub_df['vehicle_count'].shift(24)\n"
        "    sub_df['rolling_mean_3h'] = sub_df['lag_1h'].rolling(3, min_periods=1).mean()\n"
        "    sub_df['hour_sin'] = np.sin(2 * np.pi * sub_df['hour'] / 24.0)\n"
        "    sub_df['hour_cos'] = np.cos(2 * np.pi * sub_df['hour'] / 24.0)\n"
        "    return sub_df.dropna().reset_index(drop=True)\n\n"
        "def train_and_evaluate_forecaster(feature_df, train_ratio=0.80):\n"
        "    split_idx = int(len(feature_df) * train_ratio)\n"
        "    train_df, test_df = feature_df.iloc[:split_idx], feature_df.iloc[split_idx:]\n"
        "    feature_cols = ['lag_1h', 'lag_2h', 'lag_24h', 'rolling_mean_3h', 'hour_sin', 'hour_cos']\n\n"
        "    # Baseline persistence model (Same-hour yesterday)\n"
        "    base_preds = test_df['lag_24h'].values\n"
        "    base_mae = mean_absolute_error(test_df['vehicle_count'], base_preds)\n\n"
        "    # Random Forest Regressor\n"
        "    rf = RandomForestRegressor(n_estimators=60, max_depth=12, random_state=42)\n"
        "    rf.fit(train_df[feature_cols], train_df['vehicle_count'])\n"
        "    ml_preds = np.clip(rf.predict(test_df[feature_cols]), 0, None)\n"
        "    ml_mae = mean_absolute_error(test_df['vehicle_count'], ml_preds)\n"
        "    return {'ml_mae': ml_mae, 'base_mae': base_mae, 'improvement_pct': (base_mae - ml_mae)/base_mae*100}"
    )
    p_code4 = Paragraph(code_p4.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)
    box4 = Table([[p_code4]], colWidths=[480])
    box4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(box4)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 19: CHAPTER 6 - RESULTS (Page 13)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>CHAPTER-6</b>", ch_num))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>RESULTS</b>", ch_title))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>6.1 Functionality Tested:</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• <b>Data Cleansing &amp; Ingestion:</b> Verified deduplication (35 duplicate rows dropped) and temporal median imputation for 59 missing speed/volume values across 14,400 sensor logs.", bullet))
    story.append(Paragraph("• <b>PySpark Distributed Transformations:</b> Validated Spark DataFrame creation, Catalyst query execution, and Window ranking over cluster partitions.", bullet))
    story.append(Paragraph("• <b>Congestion Hotspot Detection:</b> Verified multi-criteria CHI scoring and ranking logic across all 10 monitored corridors.", bullet))
    story.append(Paragraph("• <b>Machine Learning Forecasting:</b> Validated chronological train/test splitting (no lookahead data leakage), lag feature generation, and error evaluation.", bullet))
    story.append(Paragraph("• <b>Automated Test Automation:</b> Executed 18 automated unit and integration tests using Pytest with 100% pass rate.", bullet))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>6.2 Expected Outcome:</b>", sec_title))
    story.append(Paragraph("• Successful deployment of an interactive Streamlit web dashboard displaying real-time smart city KPIs, diurnal flow curves, and ML predictions.", body))
    story.append(Spacer(1, 10))

    fig6_1_img = os.path.join(ASSETS_DIR, "fig6_1_final_output.png")
    if os.path.exists(fig6_1_img):
        story.append(Image(fig6_1_img, width=470, height=270))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Fig 6.1: Screenshot of Final output</b>", caption))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 20: CHAPTER 6 - RESULTS CONTD (Page 14)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>6.3 Machine Learning Predictive Forecasting Output</b>", sec_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("The chronological forecasting pipeline was evaluated on an out-of-sample test window. The Random Forest regressor demonstrated superior predictive accuracy over the naive persistence baseline:", body))
    story.append(Spacer(1, 10))

    # Benchmark Table
    res_headers = [
        [Paragraph("<b>Model Architecture</b>", ParagraphStyle('RH', fontName='Helvetica-Bold', fontSize=10, alignment=1)),
         Paragraph("<b>MAE (veh/hr)</b>", ParagraphStyle('RH', fontName='Helvetica-Bold', fontSize=10, alignment=1)),
         Paragraph("<b>RMSE (veh/hr)</b>", ParagraphStyle('RH', fontName='Helvetica-Bold', fontSize=10, alignment=1)),
         Paragraph("<b>MAPE (%)</b>", ParagraphStyle('RH', fontName='Helvetica-Bold', fontSize=10, alignment=1)),
         Paragraph("<b>R² Score</b>", ParagraphStyle('RH', fontName='Helvetica-Bold', fontSize=10, alignment=1))]
    ]
    res_rows = [
        [Paragraph("Baseline (Lag-24h Persist)", body), Paragraph("585.6", ParagraphStyle('RC', alignment=1)), Paragraph("947.9", ParagraphStyle('RC', alignment=1)), Paragraph("39.9%", ParagraphStyle('RC', alignment=1)), Paragraph("0.448", ParagraphStyle('RC', alignment=1))],
        [Paragraph("<b>ML (Random Forest)</b>", body), Paragraph("<b>246.7</b>", ParagraphStyle('RC', alignment=1)), Paragraph("<b>303.6</b>", ParagraphStyle('RC', alignment=1)), Paragraph("<b>21.0%</b>", ParagraphStyle('RC', alignment=1)), Paragraph("<b>0.943</b>", ParagraphStyle('RC', alignment=1))]
    ]
    t_res = Table(res_headers + res_rows, colWidths=[150, 80, 85, 80, 85], rowHeights=[24, 24, 24])
    t_res.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#E0F2FE'))
    ]))
    story.append(t_res)
    story.append(Spacer(1, 14))

    fig6_2_img = os.path.join(ASSETS_DIR, "fig6_2_forecast_output.png")
    if os.path.exists(fig6_2_img):
        story.append(Image(fig6_2_img, width=470, height=220))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Fig 6.2: Screenshot of machine learning forecast output</b>", caption))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 21: CHAPTER 7 - GEO-TAG PHOTO (Page 15)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>CHAPTER-7</b>", ch_num))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>GEO-TAG PHOTO</b>", ch_title))
    story.append(Spacer(1, 30))

    geotag_img1 = os.path.join(ASSETS_DIR, "page_21_img_0_Image86.jpg")
    if os.path.exists(geotag_img1):
        story.append(Image(geotag_img1, width=440, height=430))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 22: CHAPTER 7 - GEO-TAG PHOTO CONTD (Page 16)
    # =========================================================================
    story.append(Spacer(1, 15))
    geotag_img2 = os.path.join(ASSETS_DIR, "page_22_img_0_Image89.jpg")
    if os.path.exists(geotag_img2):
        story.append(Image(geotag_img2, width=440, height=430))
    story.append(Spacer(1, 18))
    story.append(Paragraph("<b>Fig 7.1: Geo-tag photo project submission</b>", caption))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 23: CHAPTER 8 - CONCLUSION (Page 17)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>CHAPTER-8</b>", ch_num))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Conclusion</b>", ch_title))
    story.append(Spacer(1, 24))

    concl_p1 = (
        "The <b>Smart City Traffic Pattern &amp; Congestion Analytics</b> mini project successfully demonstrates "
        "the application of Big Data processing and machine learning to modern urban mobility challenges. By pairing "
        "<b>Apache Spark (PySpark)</b> for distributed data transformations with <b>Scikit-Learn</b> for chronological "
        "predictive modeling, the application efficiently processes high-volume telemetry across major urban corridors."
    )
    story.append(Paragraph(concl_p1, body))
    story.append(Spacer(1, 14))

    concl_p2 = (
        "The project strengthened our technical understanding of key computer science and data engineering concepts—including "
        "distributed Window functions, lazy transformation evaluation, in-memory DAG pipelining, and data leakage "
        "prevention in chronological time-series analysis. The formulated Congestion Hotspot Index (CHI) provides an objective, "
        "capacity-calibrated framework that overcomes the biases of traditional speed-only evaluations."
    )
    story.append(Paragraph(concl_p2, body))
    story.append(Spacer(1, 14))

    concl_p3 = (
        "The deployment of an interactive <b>Streamlit</b> web dashboard empowers municipal planners to explore spatiotemporal "
        "heatmaps, diurnal commuter curves, and predictive forecasts without requiring deep programming expertise. In future "
        "extensions, this system can be integrated with <b>Apache Kafka</b> for real-time sensor streaming, deep learning "
        "architectures (LSTM / Temporal Fusion Transformers), and adaptive traffic signal control systems. Overall, this project "
        "substantially enhanced our practical software engineering capabilities in building scalable, real-world data analytics solutions."
    )
    story.append(Paragraph(concl_p3, body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 24: REFERENCES (Page 18)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>References</b>", ch_title))
    story.append(Spacer(1, 25))

    refs = [
        "[1] M. Zaharia, R. S. Xin, P. Wendell, T. Das, M. Armbrust, A. Dave, X. Meng, P. Rosen, S. Venkataraman, M. J. Franklin, and A. Ghodsi, “Apache Spark: A Unified Engine for Big Data Processing,” <i>Communications of the ACM</i>, vol. 59, no. 11, pp. 56–65, 2016.",
        "[2] F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss, V. Dubourg, and J. Vanderplas, “Scikit-learn: Machine Learning in Python,” <i>Journal of Machine Learning Research</i>, vol. 12, pp. 2825–2830, 2011.",
        "[3] Federal Highway Administration (FHWA), <i>Traffic Monitoring Guide</i>, U.S. Department of Transportation, Washington, D.C., 2016.",
        "[4] W. McKinney, “Data Structures for Statistical Computing in Python,” in <i>Proceedings of the 9th Python in Science Conference (SciPy)</i>, pp. 56–61, 2010.",
        "[5] B. D. Greenshields, “A Study of Traffic Capacity,” <i>Highway Research Board Proceedings</i>, vol. 14, pp. 448–477, 1935.",
        "[6] J. Trepanier and B. Park, “Predicting Urban Arterial Travel Times Using Big Data and Machine Learning,” <i>IEEE Transactions on Intelligent Transportation Systems</i>, vol. 20, no. 8, pp. 2910–2921, 2019.",
        "[7] Streamlit Inc., “Streamlit Documentation and Application Design Patterns,” <i>Streamlit Open Source Community</i>, 2024. [Online]. Available: https://docs.streamlit.io",
        "[8] S. Raschka, Y. Mirjalili, and V. Mirjalili, <i>Python Machine Learning: Machine Learning and Deep Learning with Python, scikit-learn, and TensorFlow</i>, 3rd ed., Packt Publishing, 2019."
    ]

    for ref in refs:
        story.append(Paragraph(ref, body))
        story.append(Spacer(1, 12))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF build complete:", PDF_OUTPUT_PATH)

    # Copy to artifact directory
    import shutil
    shutil.copy2(PDF_OUTPUT_PATH, ARTIFACT_OUTPUT_PATH)
    print("Copied to artifact directory:", ARTIFACT_OUTPUT_PATH)

if __name__ == "__main__":
    build_pdf()
