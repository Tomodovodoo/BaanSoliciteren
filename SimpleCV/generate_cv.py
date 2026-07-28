"""Generate Tom de Groot's one-page research CV as PDF and PNG.

The document is rendered directly with ReportLab. No HTML or Markdown
source/intermediate files are created.

Run from any directory with:

    python SimpleCV/generate_cv.py
"""

from __future__ import annotations

from pathlib import Path

import fitz
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / "CV.pdf"
PNG_PATH = BASE_DIR / "CV.png"
PROFILE_PATH = BASE_DIR / "Profile_pic.jpg"

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 12 * mm
HEADER_HEIGHT = 56 * mm
BODY_TOP = PAGE_HEIGHT - HEADER_HEIGHT - 8 * mm
BODY_BOTTOM = 11 * mm
COLUMN_GAP = 8 * mm
RAIL_WIDTH = 54 * mm
MAIN_WIDTH = PAGE_WIDTH - 2 * MARGIN - COLUMN_GAP - RAIL_WIDTH
MAIN_X = MARGIN
RAIL_X = MAIN_X + MAIN_WIDTH + COLUMN_GAP

NAVY = colors.HexColor("#0B1F3A")
NAVY_2 = colors.HexColor("#153252")
BLUE = colors.HexColor("#2D63FF")
BLUE_DARK = colors.HexColor("#1746C7")
BLUE_PALE = colors.HexColor("#EAF1FF")
PAGE_BG = colors.HexColor("#F6F8FC")
CARD_BG = colors.white
TEXT = colors.HexColor("#2E3B50")
MUTED = colors.HexColor("#66758C")
RULE = colors.HexColor("#D8E0EC")
SOFT = colors.HexColor("#EEF2F7")
WHITE = colors.white


def _styles() -> dict[str, ParagraphStyle]:
    return {
        "name": ParagraphStyle(
            "Name",
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=28,
            textColor=WHITE,
            alignment=TA_LEFT,
        ),
        "header_title": ParagraphStyle(
            "HeaderTitle",
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=13,
            textColor=colors.HexColor("#78A5FF"),
            alignment=TA_LEFT,
        ),
        "header_focus": ParagraphStyle(
            "HeaderFocus",
            fontName="Helvetica",
            fontSize=8.8,
            leading=10.5,
            textColor=colors.HexColor("#D5E0F0"),
            alignment=TA_LEFT,
        ),
        "header_contact": ParagraphStyle(
            "HeaderContact",
            fontName="Helvetica",
            fontSize=7.8,
            leading=10,
            textColor=colors.HexColor("#D5E0F0"),
            alignment=TA_LEFT,
        ),
        "quote_label": ParagraphStyle(
            "QuoteLabel",
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=8.5,
            textColor=colors.HexColor("#78A5FF"),
            alignment=TA_LEFT,
        ),
        "quote": ParagraphStyle(
            "Quote",
            fontName="Helvetica-Bold",
            fontSize=11.1,
            leading=14,
            textColor=WHITE,
            alignment=TA_LEFT,
        ),
        "quote_source": ParagraphStyle(
            "QuoteSource",
            fontName="Helvetica",
            fontSize=7.7,
            leading=9.5,
            textColor=colors.HexColor("#C7D4E6"),
            alignment=TA_LEFT,
        ),
        "section": ParagraphStyle(
            "Section",
            fontName="Helvetica-Bold",
            fontSize=10.2,
            leading=12,
            textColor=NAVY,
            alignment=TA_LEFT,
        ),
        "rail_section": ParagraphStyle(
            "RailSection",
            fontName="Helvetica-Bold",
            fontSize=8.7,
            leading=10,
            textColor=NAVY,
            alignment=TA_LEFT,
        ),
        "card_tag": ParagraphStyle(
            "CardTag",
            fontName="Helvetica-Bold",
            fontSize=6.8,
            leading=8,
            textColor=BLUE_DARK,
            alignment=TA_LEFT,
        ),
        "card_title": ParagraphStyle(
            "CardTitle",
            fontName="Helvetica-Bold",
            fontSize=10.7,
            leading=12.5,
            textColor=NAVY,
            alignment=TA_LEFT,
        ),
        "card_body": ParagraphStyle(
            "CardBody",
            fontName="Helvetica",
            fontSize=8.9,
            leading=11.7,
            textColor=TEXT,
            alignment=TA_LEFT,
        ),
        "metric_value": ParagraphStyle(
            "MetricValue",
            fontName="Helvetica-Bold",
            fontSize=14.5,
            leading=16,
            textColor=BLUE_DARK,
            alignment=TA_LEFT,
        ),
        "metric_label": ParagraphStyle(
            "MetricLabel",
            fontName="Helvetica",
            fontSize=7.6,
            leading=9.3,
            textColor=TEXT,
            alignment=TA_LEFT,
        ),
        "rail_title": ParagraphStyle(
            "RailTitle",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=10.7,
            textColor=NAVY,
            alignment=TA_LEFT,
        ),
        "rail_body": ParagraphStyle(
            "RailBody",
            fontName="Helvetica",
            fontSize=7.8,
            leading=9.7,
            textColor=TEXT,
            alignment=TA_LEFT,
        ),
        "rail_small": ParagraphStyle(
            "RailSmall",
            fontName="Helvetica",
            fontSize=7.2,
            leading=8.8,
            textColor=MUTED,
            alignment=TA_LEFT,
        ),
        "footer": ParagraphStyle(
            "Footer",
            fontName="Helvetica",
            fontSize=7.2,
            leading=8.5,
            textColor=MUTED,
            alignment=TA_LEFT,
        ),
    }


def _paragraph(
    pdf: canvas.Canvas,
    text: str,
    style: ParagraphStyle,
    x: float,
    y_top: float,
    width: float,
) -> float:
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, PAGE_HEIGHT)
    paragraph.drawOn(pdf, x, y_top - height)
    return y_top - height


def _paragraph_height(
    text: str,
    style: ParagraphStyle,
    width: float,
) -> tuple[Paragraph, float]:
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, PAGE_HEIGHT)
    return paragraph, height


def _draw_profile_photo(
    pdf: canvas.Canvas,
    center_x: float,
    center_y: float,
    radius: float,
) -> None:
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(f"Missing profile image: {PROFILE_PATH}")

    pdf.setFillColor(colors.HexColor("#2A4667"))
    pdf.circle(center_x + 1.2, center_y - 1.2, radius + 2.1, fill=1, stroke=0)
    pdf.setFillColor(WHITE)
    pdf.circle(center_x, center_y, radius + 1.6, fill=1, stroke=0)

    pdf.saveState()
    clip_path = pdf.beginPath()
    clip_path.circle(center_x, center_y, radius)
    pdf.clipPath(clip_path, stroke=0, fill=0)
    pdf.drawImage(
        ImageReader(str(PROFILE_PATH)),
        center_x - radius,
        center_y - radius,
        2 * radius,
        2 * radius,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )
    pdf.restoreState()


def _draw_header(
    pdf: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
) -> None:
    header_bottom = PAGE_HEIGHT - HEADER_HEIGHT
    pdf.setFillColor(NAVY)
    pdf.rect(0, header_bottom, PAGE_WIDTH, HEADER_HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(BLUE)
    pdf.rect(0, header_bottom, 4.5, HEADER_HEIGHT, fill=1, stroke=0)

    photo_x = 22.5 * mm
    photo_y = PAGE_HEIGHT - HEADER_HEIGHT / 2
    _draw_profile_photo(pdf, photo_x, photo_y, 13.2 * mm)

    identity_x = 42 * mm
    identity_width = 84 * mm
    y = PAGE_HEIGHT - 10 * mm
    y = _paragraph(
        pdf,
        "Tom de Groot",
        styles["name"],
        identity_x,
        y,
        identity_width,
    )
    y -= 2
    y = _paragraph(
        pdf,
        "INDEPENDENT RESEARCHER",
        styles["header_title"],
        identity_x,
        y,
        identity_width,
    )
    y -= 2.5
    y = _paragraph(
        pdf,
        "AI-assisted mathematics | formal verification | scientific ML",
        styles["header_focus"],
        identity_x,
        y,
        identity_width,
    )

    contact_y = header_bottom + 17 * mm
    contact_y = _paragraph(
        pdf,
        "Grijpskerk, NL | +31 6 314 90 416 | "
        '<link href="mailto:tomthegreatest04@gmail.com" '
        'color="#D5E0F0">tomthegreatest04@gmail.com</link>',
        styles["header_contact"],
        identity_x,
        contact_y,
        identity_width,
    )
    _paragraph(
        pdf,
        '<link href="https://github.com/Tomodovodoo" '
        'color="#78A5FF">GitHub</link>  |  '
        '<link href="https://x.com/Tomodovodoo" '
        'color="#78A5FF">Research notes</link>  |  '
        '<link href="https://linkedin.com/in/tomodovodoo" '
        'color="#78A5FF">LinkedIn</link>',
        styles["header_contact"],
        identity_x,
        contact_y - 1.5,
        identity_width,
    )

    quote_x = 132 * mm
    quote_width = PAGE_WIDTH - quote_x - MARGIN
    quote_bottom = header_bottom + 10 * mm
    quote_height = 36 * mm
    pdf.setFillColor(NAVY_2)
    pdf.setStrokeColor(colors.HexColor("#2B4E72"))
    pdf.setLineWidth(0.8)
    pdf.roundRect(
        quote_x,
        quote_bottom,
        quote_width,
        quote_height,
        6,
        fill=1,
        stroke=1,
    )
    pdf.setFillColor(BLUE)
    pdf.roundRect(
        quote_x,
        quote_bottom,
        3.2,
        quote_height,
        1.6,
        fill=1,
        stroke=0,
    )
    quote_inner_x = quote_x + 10
    quote_inner_width = quote_width - 18
    quote_y = quote_bottom + quote_height - 9
    quote_y = _paragraph(
        pdf,
        "EXTERNAL VALIDATION",
        styles["quote_label"],
        quote_inner_x,
        quote_y,
        quote_inner_width,
    )
    quote_y -= 7
    quote_y = _paragraph(
        pdf,
        '&quot;the gold standard of LLM-aided mathematics&quot;',
        styles["quote"],
        quote_inner_x,
        quote_y,
        quote_inner_width,
    )
    quote_y -= 7
    _paragraph(
        pdf,
        '<link href="https://www.daniellitt.com/blog/2026/2/20/'
        'mathematics-in-the-library-of-babel" color="#78A5FF">'
        "Daniel Litt</link> on FirstProof Problem 9",
        styles["quote_source"],
        quote_inner_x,
        quote_y,
        quote_inner_width,
    )


def _draw_section_heading(
    pdf: canvas.Canvas,
    title: str,
    x: float,
    y_top: float,
    width: float,
    style: ParagraphStyle,
) -> float:
    pdf.setFillColor(BLUE)
    pdf.roundRect(x, y_top - 9, 3.2, 9, 1.6, fill=1, stroke=0)
    y = _paragraph(pdf, title.upper(), style, x + 8, y_top, width - 8)
    pdf.setStrokeColor(RULE)
    pdf.setLineWidth(0.6)
    pdf.line(x, y - 4, x + width, y - 4)
    return y - 12


def _draw_date_pill(
    pdf: canvas.Canvas,
    label: str,
    x_right: float,
    y_top: float,
) -> float:
    font_name = "Helvetica-Bold"
    font_size = 6.9
    height = 13
    width = stringWidth(label, font_name, font_size) + 10
    x = x_right - width
    y = y_top - height
    pdf.setFillColor(BLUE_PALE)
    pdf.roundRect(x, y, width, height, 4, fill=1, stroke=0)
    pdf.setFillColor(BLUE_DARK)
    pdf.setFont(font_name, font_size)
    pdf.drawCentredString(x + width / 2, y + 3.6, label)
    return width


def _draw_card(
    pdf: canvas.Canvas,
    *,
    tag: str,
    title: str,
    date: str,
    body: str,
    x: float,
    y_top: float,
    width: float,
    styles: dict[str, ParagraphStyle],
    gap_after: float = 7,
) -> float:
    padding_x = 12
    padding_y = 9
    accent_width = 3.2
    content_x = x + padding_x
    content_width = width - 2 * padding_x

    tag_paragraph, tag_height = _paragraph_height(
        tag.upper(),
        styles["card_tag"],
        content_width,
    )
    date_width = stringWidth(date, "Helvetica-Bold", 6.9) + 10 if date else 0
    title_width = content_width - date_width - (7 if date else 0)
    title_paragraph, title_height = _paragraph_height(
        title,
        styles["card_title"],
        title_width,
    )
    body_paragraph, body_height = _paragraph_height(
        body,
        styles["card_body"],
        content_width,
    )

    height = (
        2 * padding_y
        + tag_height
        + 4
        + title_height
        + 5
        + body_height
    )
    y_bottom = y_top - height

    pdf.setFillColor(colors.HexColor("#E4E9F1"))
    pdf.roundRect(x + 1.2, y_bottom - 1.2, width, height, 5, fill=1, stroke=0)
    pdf.setFillColor(CARD_BG)
    pdf.setStrokeColor(RULE)
    pdf.setLineWidth(0.65)
    pdf.roundRect(x, y_bottom, width, height, 5, fill=1, stroke=1)
    pdf.setFillColor(BLUE)
    pdf.roundRect(
        x,
        y_bottom,
        accent_width,
        height,
        accent_width / 2,
        fill=1,
        stroke=0,
    )

    current_y = y_top - padding_y
    tag_paragraph.drawOn(pdf, content_x, current_y - tag_height)
    current_y -= tag_height + 4
    title_paragraph.drawOn(pdf, content_x, current_y - title_height)
    if date:
        _draw_date_pill(pdf, date, x + width - padding_x, current_y)
    current_y -= title_height + 5
    body_paragraph.drawOn(pdf, content_x, current_y - body_height)
    return y_bottom - gap_after


def _draw_metric(
    pdf: canvas.Canvas,
    value: str,
    label: str,
    y_top: float,
    styles: dict[str, ParagraphStyle],
) -> float:
    height = 39
    padding = 8
    pdf.setFillColor(BLUE_PALE)
    pdf.setStrokeColor(colors.HexColor("#C9D8FF"))
    pdf.setLineWidth(0.6)
    pdf.roundRect(
        RAIL_X,
        y_top - height,
        RAIL_WIDTH,
        height,
        5,
        fill=1,
        stroke=1,
    )
    value_y = _paragraph(
        pdf,
        value,
        styles["metric_value"],
        RAIL_X + padding,
        y_top - 5,
        RAIL_WIDTH - 2 * padding,
    )
    _paragraph(
        pdf,
        label,
        styles["metric_label"],
        RAIL_X + padding,
        value_y - 1,
        RAIL_WIDTH - 2 * padding,
    )
    return y_top - height - 6


def _draw_rail_item(
    pdf: canvas.Canvas,
    title: str,
    meta: str,
    body: str,
    y_top: float,
    styles: dict[str, ParagraphStyle],
    *,
    gap_after: float = 7,
) -> float:
    y = _paragraph(
        pdf,
        title,
        styles["rail_title"],
        RAIL_X,
        y_top,
        RAIL_WIDTH,
    )
    if meta:
        y = _paragraph(
            pdf,
            meta,
            styles["rail_small"],
            RAIL_X,
            y - 1,
            RAIL_WIDTH,
        )
    if body:
        y = _paragraph(
            pdf,
            body,
            styles["rail_body"],
            RAIL_X,
            y - 2,
            RAIL_WIDTH,
        )
    return y - gap_after


def _draw_main_column(
    pdf: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
) -> float:
    y = BODY_TOP
    y = _draw_section_heading(
        pdf,
        "Selected Research",
        MAIN_X,
        y,
        MAIN_WIDTH,
        styles["section"],
    )
    y = _draw_card(
        pdf,
        tag="Open problem | Candidate proof",
        title="A Raynaud-Bundle Route",
        date="Jul 2026",
        body=(
            "Steered GPT-5.5 Pro and GPT-5.6 Sol Pro from a partial result to "
            "a complete candidate proof of Daniel Litt's problem. Auditing the "
            "argument with his feedback. "
            '<link href="https://x.com/Tomodovodoo/status/2076027408042573905" '
            'color="#2D63FF">Research note</link>  |  '
            '<link href="https://problemsilike.com/forum/thread/14" '
            'color="#2D63FF">Proof thread</link>'
        ),
        x=MAIN_X,
        y_top=y,
        width=MAIN_WIDTH,
        styles=styles,
    )
    y = _draw_card(
        pdf,
        tag="FirstProof | Lean verified",
        title="Problem 9",
        date="Feb 2026",
        body=(
            "Orchestrated LLM agents from informal search to a Lean 4 proof. "
            "The repository's only solved problem. "
            '<link href="https://github.com/Tomodovodoo/firstproof" '
            'color="#2D63FF">Proof + code</link>'
        ),
        x=MAIN_X,
        y_top=y,
        width=MAIN_WIDTH,
        styles=styles,
    )
    y = _draw_card(
        pdf,
        tag="Open-source formalization",
        title="Prime Number Theorem And (PNT+)",
        date="2025 - Present",
        body=(
            "Merged Lean proofs; compilation and adversarial review as hard "
            "checks on model-generated mathematics. "
            '<link href="https://github.com/AlexKontorovich/'
            'PrimeNumberTheoremAnd/pulls?q=is%3Apr+author%3ATomodovodoo" '
            'color="#2D63FF">Merged PRs</link>'
        ),
        x=MAIN_X,
        y_top=y,
        width=MAIN_WIDTH,
        styles=styles,
        gap_after=11,
    )

    y = _draw_section_heading(
        pdf,
        "Scientific & Agent Systems",
        MAIN_X,
        y,
        MAIN_WIDTH,
        styles["section"],
    )
    y = _draw_card(
        pdf,
        tag="Simulation | Certification | RL",
        title="Bazaar_ML",
        date="2026 - Present",
        body=(
            "<b>49,248</b> executable evaluation cases; <b>99.85%</b> "
            "sampling-pool coverage; deterministic traces, provenance, and "
            "agent-training hooks."
        ),
        x=MAIN_X,
        y_top=y,
        width=MAIN_WIDTH,
        styles=styles,
    )
    y = _draw_card(
        pdf,
        tag="Chemistry | Graph neural networks",
        title="NMR Prediction",
        date="2024 - 2025",
        body=(
            "Curated molecular/NMR data and benchmarked GNNs on HPC under "
            "controlled splits and evaluation."
        ),
        x=MAIN_X,
        y_top=y,
        width=MAIN_WIDTH,
        styles=styles,
    )
    y = _draw_card(
        pdf,
        tag="Agentic engineering",
        title="BaanSoliciteren",
        date="2025 - 2026",
        body=(
            "Auditable pipeline for vacancy ingestion, fit scoring, and state "
            "tracking. "
            '<link href="https://github.com/Tomodovodoo/BaanSoliciteren" '
            'color="#2D63FF">GitHub</link>'
        ),
        x=MAIN_X,
        y_top=y,
        width=MAIN_WIDTH,
        styles=styles,
        gap_after=0,
    )
    return y


def _draw_rail(
    pdf: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
) -> float:
    y = BODY_TOP
    y = _draw_section_heading(
        pdf,
        "At a Glance",
        RAIL_X,
        y,
        RAIL_WIDTH,
        styles["rail_section"],
    )
    y = _draw_metric(
        pdf,
        "LEAN 4",
        "Machine-checked FirstProof solution",
        y,
        styles,
    )
    y = _draw_metric(
        pdf,
        "49,248",
        "Executable evaluation cases",
        y,
        styles,
    )
    y = _draw_metric(
        pdf,
        "99.85%",
        "Sampling-pool coverage",
        y,
        styles,
    )

    y -= 5
    y = _draw_section_heading(
        pdf,
        "Experience",
        RAIL_X,
        y,
        RAIL_WIDTH,
        styles["rail_section"],
    )
    y = _draw_rail_item(
        pdf,
        "AI Engineer",
        "SoundImports | Present",
        "Prediction systems, AI automation, and containerized AWS services.",
        y,
        styles,
    )
    y = _draw_rail_item(
        pdf,
        "Earlier",
        "Teamspot | Transcom | Chess.com",
        "Regional direction, QA, support, and international events.",
        y,
        styles,
    )

    y -= 3
    y = _draw_section_heading(
        pdf,
        "Methods & Tools",
        RAIL_X,
        y,
        RAIL_WIDTH,
        styles["rail_section"],
    )
    y = _draw_rail_item(
        pdf,
        "Research",
        "",
        "Agent workflows, evaluation design, formal verification",
        y,
        styles,
        gap_after=5,
    )
    y = _draw_rail_item(
        pdf,
        "Code",
        "",
        "Python, Lean 4, PyTorch, SQL, RDKit",
        y,
        styles,
        gap_after=5,
    )
    y = _draw_rail_item(
        pdf,
        "Systems",
        "",
        "Linux/HPC, AWS, Docker, Git",
        y,
        styles,
    )

    y -= 3
    y = _draw_section_heading(
        pdf,
        "Education",
        RAIL_X,
        y,
        RAIL_WIDTH,
        styles["rail_section"],
    )
    y = _draw_rail_item(
        pdf,
        "BSc Chemistry",
        "University of Groningen | 2021 - 2025",
        "Chemistry of Life. Thesis: GNN evaluation for NMR prediction.",
        y,
        styles,
    )

    y -= 3
    y = _draw_section_heading(
        pdf,
        "Recognition",
        RAIL_X,
        y,
        RAIL_WIDTH,
        styles["rail_section"],
    )
    y = _draw_rail_item(
        pdf,
        '<link href="https://harmonic.fun/news/mathematician-sponsorships/" '
        'color="#2D63FF">Harmonic Rising Mathematician</link>',
        "",
        "",
        y,
        styles,
        gap_after=5,
    )
    y = _draw_rail_item(
        pdf,
        '<link href="https://www.chess.com/news/view/'
        '2021-chesscom-awards-winners#member" color="#2D63FF">'
        "Chess.com Member of the Year 2021</link>",
        "",
        "",
        y,
        styles,
        gap_after=0,
    )
    return y


def _draw_footer(
    pdf: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
) -> None:
    pdf.setStrokeColor(RULE)
    pdf.setLineWidth(0.6)
    pdf.line(MARGIN, 8.5 * mm, PAGE_WIDTH - MARGIN, 8.5 * mm)
    _paragraph(
        pdf,
        "Research artifacts: "
        '<link href="https://github.com/Tomodovodoo" '
        'color="#2D63FF">github.com/Tomodovodoo</link>  |  '
        '<link href="https://x.com/Tomodovodoo" '
        'color="#2D63FF">x.com/Tomodovodoo</link>',
        styles["footer"],
        MARGIN,
        7.5 * mm,
        PAGE_WIDTH - 2 * MARGIN,
    )


def build_pdf() -> None:
    styles = _styles()
    pdf = canvas.Canvas(str(PDF_PATH), pagesize=A4, pageCompression=1)
    pdf.setTitle("Tom de Groot - Independent Researcher")
    pdf.setAuthor("Tom de Groot")
    pdf.setSubject("AI-assisted mathematics, formal verification, and scientific ML")

    pdf.setFillColor(PAGE_BG)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    _draw_header(pdf, styles)
    main_bottom = _draw_main_column(pdf, styles)
    rail_bottom = _draw_rail(pdf, styles)
    _draw_footer(pdf, styles)

    if min(main_bottom, rail_bottom) < BODY_BOTTOM:
        raise RuntimeError(
            "CV content crossed the safe bottom margin: "
            f"main={main_bottom / mm:.1f} mm, rail={rail_bottom / mm:.1f} mm."
        )

    pdf.showPage()
    pdf.save()


def render_png() -> None:
    with fitz.open(PDF_PATH) as document:
        if document.page_count != 1:
            raise RuntimeError(
                f"Expected a one-page CV, generated {document.page_count} pages."
            )
        pixmap = document[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        pixmap.save(PNG_PATH)


def validate_outputs() -> None:
    reader = PdfReader(str(PDF_PATH))
    if len(reader.pages) != 1:
        raise RuntimeError(f"Expected one PDF page, found {len(reader.pages)}.")

    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    required_phrases = (
        "Tom de Groot",
        "INDEPENDENT RESEARCHER",
        "Raynaud-Bundle",
        "FirstProof",
        "LEAN 4",
        "49,248",
        "GRAPH NEURAL NETWORKS",
        "SoundImports",
        "BaanSoliciteren",
    )
    missing = [phrase for phrase in required_phrases if phrase not in text]
    if missing:
        raise RuntimeError(f"Generated PDF is missing required text: {missing}")

    annotations = reader.pages[0].get("/Annots", [])
    if len(annotations) < 8:
        raise RuntimeError(
            f"Expected at least 8 embedded links, found {len(annotations)}."
        )

    if not PNG_PATH.exists() or PNG_PATH.stat().st_size == 0:
        raise RuntimeError("PNG preview was not generated.")


def generate_cv() -> None:
    build_pdf()
    render_png()
    validate_outputs()
    print(f"Generated {PDF_PATH}")
    print(f"Generated {PNG_PATH}")


if __name__ == "__main__":
    generate_cv()
