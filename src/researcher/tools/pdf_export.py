import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))

        # Footer divider line
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 40, letter[0] - 54, 40)

        # Footer text
        left_text = "AI Research & Intelligence Crew | CrewAI"
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawString(54, 26, left_text)
        self.drawRightString(letter[0] - 54, 26, page_text)
        self.restoreState()


def clean_markdown_inline(text: str) -> str:
    """Replaces inline markdown bold/italic with ReportLab XML tags."""
    # Escape XML specials
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Restore tags we want to format
    # Bold **text**
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    # Italic *text* or _text_
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    # Code `code`
    text = re.sub(r"`(.*?)`", r'<font face="Courier" color="#0369a1">\1</font>', text)
    return text


def export_markdown_to_pdf(markdown_content: str, topic: str, output_path: str) -> str:
    """
    Renders structured Markdown text into a professional publication-ready PDF.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6
    )

    meta_style = ParagraphStyle(
        "MetaSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0369a1"),
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        "SectionH3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#334155"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    story = []

    # Title header
    story.append(Paragraph(f"Research Report: {topic}", title_style))
    current_time = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    story.append(Paragraph(f"Generated on {current_time} &bull; Autonomous Intelligence Pipeline", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))

    for line in markdown_content.splitlines():
        line_clean = line.strip()
        if not line_clean:
            story.append(Spacer(1, 4))
            continue

        if line_clean.startswith("# "):
            heading_text = clean_markdown_inline(line_clean[2:])
            story.append(Paragraph(heading_text, h1_style))
        elif line_clean.startswith("## "):
            heading_text = clean_markdown_inline(line_clean[3:])
            story.append(Paragraph(heading_text, h2_style))
        elif line_clean.startswith("### "):
            heading_text = clean_markdown_inline(line_clean[4:])
            story.append(Paragraph(heading_text, h3_style))
        elif line_clean.startswith("- ") or line_clean.startswith("* "):
            bullet_text = clean_markdown_inline(line_clean[2:])
            story.append(Paragraph(f"&bull; {bullet_text}", bullet_style))
        elif re.match(r"^\d+\.\s", line_clean):
            num_content = clean_markdown_inline(re.sub(r"^\d+\.\s", "", line_clean))
            match = re.match(r"^(\d+\.)\s", line_clean)
            num_prefix = match.group(1) if match else "&bull;"
            story.append(Paragraph(f"{num_prefix} {num_content}", bullet_style))
        elif line_clean.startswith("---") or line_clean.startswith("***"):
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceBefore=6, spaceAfter=8))
        else:
            paragraph_text = clean_markdown_inline(line_clean)
            story.append(Paragraph(paragraph_text, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    return output_path
