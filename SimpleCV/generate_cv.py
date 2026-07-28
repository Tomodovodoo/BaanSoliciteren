"""Generate Tom de Groot's one-page CV as PDF and PNG.

The original two-column visual identity is rendered directly with ReportLab.
No HTML or Markdown source/intermediate files are created.

Run from any directory with:

    python SimpleCV/generate_cv.py
"""

from __future__ import annotations

from pathlib import Path

import fitz
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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
SIDEBAR_WIDTH = 70 * mm
SIDEBAR_PADDING = 4 * mm
MAIN_X = 78 * mm
MAIN_WIDTH = PAGE_WIDTH - MAIN_X - 8 * mm

NAVY = colors.HexColor("#11213B")
TEXT = colors.HexColor("#334155")
MUTED = colors.HexColor("#64748B")
BLUE = colors.HexColor("#245BFF")
SIDEBAR_BG = colors.HexColor("#F8FAFC")
RULE = colors.HexColor("#CBD5E1")
DATE_BG = colors.HexColor("#F1F5F9")
CALLOUT_BG = colors.HexColor("#EEF4FF")
CALLOUT_BORDER = colors.HexColor("#BFD0FF")
WHITE = colors.white


def _styles() -> dict[str, ParagraphStyle]:
    return {
        "name": ParagraphStyle(
            "Name",
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=26,
            textColor=NAVY,
            alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=12.8,
            textColor=BLUE,
            alignment=TA_CENTER,
        ),
        "contact": ParagraphStyle(
            "Contact",
            fontName="Helvetica",
            fontSize=8.8,
            leading=11,
            textColor=TEXT,
            alignment=TA_LEFT,
        ),
        "sidebar_heading": ParagraphStyle(
            "SidebarHeading",
            fontName="Helvetica-Bold",
            fontSize=9.8,
            leading=11.2,
            textColor=MUTED,
            alignment=TA_LEFT,
        ),
        "sidebar_body": ParagraphStyle(
            "SidebarBody",
            fontName="Helvetica",
            fontSize=8.5,
            leading=10.4,
            textColor=TEXT,
            alignment=TA_LEFT,
        ),
        "sidebar_small": ParagraphStyle(
            "SidebarSmall",
            fontName="Helvetica",
            fontSize=7.8,
            leading=9.5,
            textColor=TEXT,
            alignment=TA_LEFT,
        ),
        "main_heading": ParagraphStyle(
            "MainHeading",
            fontName="Helvetica-Bold",
            fontSize=11.2,
            leading=12.6,
            textColor=NAVY,
            alignment=TA_LEFT,
        ),
        "hero_title": ParagraphStyle(
            "HeroTitle",
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=18,
            textColor=NAVY,
            alignment=TA_LEFT,
        ),
        "hero_kicker": ParagraphStyle(
            "HeroKicker",
            fontName="Helvetica-Bold",
            fontSize=8.7,
            leading=10.5,
            textColor=BLUE,
            alignment=TA_LEFT,
        ),
        "hero_body": ParagraphStyle(
            "HeroBody",
            fontName="Helvetica",
            fontSize=10.2,
            leading=13.2,
            textColor=TEXT,
            alignment=TA_LEFT,
        ),
        "quote": ParagraphStyle(
            "Quote",
            fontName="Helvetica-Bold",
            fontSize=11.2,
            leading=13.8,
            textColor=NAVY,
            alignment=TA_LEFT,
        ),
        "quote_attribution": ParagraphStyle(
            "QuoteAttribution",
            fontName="Helvetica",
            fontSize=8.2,
            leading=10,
            textColor=MUTED,
            alignment=TA_LEFT,
        ),
        "item_title": ParagraphStyle(
            "ItemTitle",
            fontName="Helvetica-Bold",
            fontSize=10.4,
            leading=12,
            textColor=NAVY,
            alignment=TA_LEFT,
        ),
        "item_body": ParagraphStyle(
            "ItemBody",
            fontName="Helvetica",
            fontSize=9.15,
            leading=11.8,
            textColor=TEXT,
            alignment=TA_LEFT,
        ),
    }


def _draw_paragraph(
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


def _draw_sidebar_heading(
    pdf: canvas.Canvas,
    title: str,
    y_top: float,
    styles: dict[str, ParagraphStyle],
) -> float:
    x = SIDEBAR_PADDING
    width = SIDEBAR_WIDTH - 2 * SIDEBAR_PADDING
    y = _draw_paragraph(
        pdf,
        title.upper(),
        styles["sidebar_heading"],
        x,
        y_top,
        width,
    )
    pdf.setStrokeColor(RULE)
    pdf.setLineWidth(1)
    pdf.line(x, y - 2.2, x + width, y - 2.2)
    return y - 7


def _draw_main_heading(
    pdf: canvas.Canvas,
    title: str,
    y_top: float,
    styles: dict[str, ParagraphStyle],
) -> float:
    y = _draw_paragraph(
        pdf,
        title.upper(),
        styles["main_heading"],
        MAIN_X,
        y_top,
        MAIN_WIDTH,
    )
    pdf.setStrokeColor(RULE)
    pdf.setLineWidth(0.55)
    pdf.line(MAIN_X, y - 1.8, MAIN_X + MAIN_WIDTH, y - 1.8)
    return y - 5


def _draw_date_pill(
    pdf: canvas.Canvas,
    label: str,
    x_right: float,
    y_top: float,
) -> float:
    font_name = "Helvetica"
    font_size = 7.5
    height = 12
    width = stringWidth(label, font_name, font_size) + 8
    x = x_right - width
    y = y_top - 10.5
    pdf.setFillColor(DATE_BG)
    pdf.roundRect(x, y, width, height, 3, fill=1, stroke=0)
    pdf.setFillColor(MUTED)
    pdf.setFont(font_name, font_size)
    pdf.drawCentredString(x + width / 2, y + 3.1, label)
    return width


def _draw_callout(
    pdf: canvas.Canvas,
    quote: str,
    attribution: str,
    y_top: float,
    styles: dict[str, ParagraphStyle],
) -> float:
    padding_x = 9
    padding_y = 7
    inner_width = MAIN_WIDTH - 2 * padding_x
    quote_paragraph = Paragraph(quote, styles["quote"])
    attribution_paragraph = Paragraph(attribution, styles["quote_attribution"])
    _, quote_height = quote_paragraph.wrap(inner_width, PAGE_HEIGHT)
    _, attribution_height = attribution_paragraph.wrap(inner_width, PAGE_HEIGHT)
    height = 2 * padding_y + quote_height + attribution_height + 3
    y_bottom = y_top - height

    pdf.setFillColor(CALLOUT_BG)
    pdf.setStrokeColor(CALLOUT_BORDER)
    pdf.setLineWidth(0.7)
    pdf.roundRect(
        MAIN_X,
        y_bottom,
        MAIN_WIDTH,
        height,
        5,
        fill=1,
        stroke=1,
    )
    quote_y = y_top - padding_y
    quote_paragraph.drawOn(
        pdf,
        MAIN_X + padding_x,
        quote_y - quote_height,
    )
    attribution_paragraph.drawOn(
        pdf,
        MAIN_X + padding_x,
        quote_y - quote_height - 3 - attribution_height,
    )
    return y_bottom - 9


def _draw_item(
    pdf: canvas.Canvas,
    title: str,
    date: str,
    paragraphs: list[str],
    y_top: float,
    styles: dict[str, ParagraphStyle],
    *,
    gap_after: float = 3,
) -> float:
    date_width = _draw_date_pill(
        pdf,
        date,
        MAIN_X + MAIN_WIDTH,
        y_top,
    ) if date else 0
    title_width = MAIN_WIDTH - date_width - (4 if date else 0)
    y = _draw_paragraph(
        pdf,
        title,
        styles["item_title"],
        MAIN_X,
        y_top,
        title_width,
    )
    y -= 0.8
    for paragraph in paragraphs:
        y = _draw_paragraph(
            pdf,
            paragraph,
            styles["item_body"],
            MAIN_X,
            y,
            MAIN_WIDTH,
        )
        y -= 1
    return y - gap_after


def _draw_profile_photo(pdf: canvas.Canvas) -> None:
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(f"Missing profile image: {PROFILE_PATH}")

    center_x = SIDEBAR_WIDTH / 2
    center_y = PAGE_HEIGHT - 17 * mm
    radius = 11.8 * mm

    pdf.setFillColor(colors.HexColor("#E2E8F0"))
    pdf.circle(center_x + 1.1, center_y - 1.1, radius + 1.6, fill=1, stroke=0)
    pdf.setFillColor(WHITE)
    pdf.circle(center_x, center_y, radius + 1.4, fill=1, stroke=0)

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


def _draw_sidebar(
    pdf: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
) -> None:
    pdf.setFillColor(SIDEBAR_BG)
    pdf.rect(0, 0, SIDEBAR_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
    pdf.setLineWidth(0.6)
    pdf.line(SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, PAGE_HEIGHT)

    _draw_profile_photo(pdf)

    x = SIDEBAR_PADDING
    width = SIDEBAR_WIDTH - 2 * SIDEBAR_PADDING
    y = PAGE_HEIGHT - 34 * mm
    y = _draw_paragraph(pdf, "Tom de Groot", styles["name"], x, y, width)
    y -= 4
    y = _draw_paragraph(
        pdf,
        "Independent Researcher<br/>AI for Math &amp; Science",
        styles["subtitle"],
        x,
        y,
        width,
    )
    y -= 7

    contact_lines = [
        "Grijpskerk, NL  |  +31 6 314 90 416",
        '<link href="mailto:tomthegreatest04@gmail.com" '
        'color="#334155">tomthegreatest04@gmail.com</link>',
        '<link href="https://github.com/Tomodovodoo" '
        'color="#334155">github.com/Tomodovodoo</link>',
        '<link href="https://x.com/Tomodovodoo" '
        'color="#334155">x.com/Tomodovodoo</link>',
        '<link href="https://linkedin.com/in/tomodovodoo" '
        'color="#334155">linkedin.com/in/tomodovodoo</link>',
    ]
    for line in contact_lines:
        y = _draw_paragraph(pdf, line, styles["contact"], x, y, width)
        y -= 1.2

    y -= 6
    y = _draw_sidebar_heading(pdf, "Methods & Tools", y, styles)
    skill_groups = [
        "<b>Research:</b> agentic workflows, evaluations, formal verification",
        "<b>Code:</b> Python, Lean 4, PyTorch, SQL, RDKit",
        "<b>Systems:</b> Linux/HPC, AWS, Docker, Git",
        "<b>Languages:</b> Dutch, English",
    ]
    for group in skill_groups:
        y = _draw_paragraph(
            pdf,
            group,
            styles["sidebar_body"],
            x,
            y,
            width,
        )
        y -= 4

    y -= 1
    y = _draw_sidebar_heading(pdf, "Education", y, styles)
    y = _draw_paragraph(
        pdf,
        "<b><font size='10'>BSc Chemistry</font></b><br/>"
        "University of Groningen<br/>"
        "<font color='#64748B'>2021 - 2025</font><br/>"
        "<i>Track: Chemistry of Life</i>",
        styles["sidebar_body"],
        x,
        y,
        width,
    )
    y -= 5
    y = _draw_paragraph(
        pdf,
        "<b>Thesis:</b> GNN evaluation for NMR prediction",
        styles["sidebar_small"],
        x,
        y,
        width,
    )

    y -= 12
    y = _draw_sidebar_heading(pdf, "Recognition", y, styles)
    y = _draw_paragraph(
        pdf,
        '<link href="https://harmonic.fun/news/mathematician-sponsorships/" '
        'color="#245BFF">Harmonic Rising Mathematician</link>',
        styles["sidebar_body"],
        x,
        y,
        width,
    )
    y -= 6
    _draw_paragraph(
        pdf,
        '<link href="https://www.chess.com/news/view/2021-chesscom-awards-winners#member" '
        'color="#245BFF">Chess.com Member of the Year 2021</link>',
        styles["sidebar_body"],
        x,
        y,
        width,
    )


def _draw_main(
    pdf: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
) -> float:
    y = PAGE_HEIGHT - 9 * mm

    y = _draw_paragraph(
        pdf,
        "INDEPENDENT RESEARCHER",
        styles["hero_title"],
        MAIN_X,
        y,
        MAIN_WIDTH,
    )
    y -= 2
    y = _draw_paragraph(
        pdf,
        "AI-ASSISTED MATHEMATICS  |  FORMAL VERIFICATION  |  SCIENTIFIC ML",
        styles["hero_kicker"],
        MAIN_X,
        y,
        MAIN_WIDTH,
    )
    y -= 4
    y = _draw_paragraph(
        pdf,
        "I use frontier models to attack open problems, then make the result "
        "inspectable: expert review, formal proof, and reproducible code.",
        styles["hero_body"],
        MAIN_X,
        y,
        MAIN_WIDTH,
    )

    y -= 9
    y = _draw_callout(
        pdf,
        '&quot;the gold standard of LLM-aided mathematics&quot;',
        '<link href="https://www.daniellitt.com/blog/2026/2/20/'
        'mathematics-in-the-library-of-babel" color="#245BFF">'
        "Daniel Litt</link> on Tom's Lean-verified FirstProof solution",
        y,
        styles,
    )

    y = _draw_main_heading(pdf, "Selected Research", y, styles)
    y = _draw_item(
        pdf,
        "Daniel Litt Open Problem - Raynaud Bundles",
        "Jul 2026",
        [
            "Steered GPT-5.5 Pro and GPT-5.6 Sol Pro from a partial result to a "
            "complete candidate proof using Raynaud bundles. Now auditing the "
            "argument with Daniel Litt's feedback. "
            '<link href="https://x.com/Tomodovodoo/status/2076027408042573905" '
            'color="#245BFF">Research note</link> | '
            '<link href="https://problemsilike.com/forum/thread/14" '
            'color="#245BFF">Proof thread</link>',
        ],
        y,
        styles,
    )
    y = _draw_item(
        pdf,
        "FirstProof Problem 9 - Lean-Verified",
        "Feb 2026",
        [
            "Orchestrated LLM agents from informal search to Lean 4 verification. "
            "The repository's only solved problem. "
            '<link href="https://github.com/Tomodovodoo/firstproof" '
            'color="#245BFF">Proof + code</link>',
        ],
        y,
        styles,
    )
    y = _draw_item(
        pdf,
        "Prime Number Theorem And (PNT+)",
        "2025 - Present",
        [
            "Contributed merged Lean proofs; use compilation and adversarial "
            "review to test model-generated mathematics. "
            '<link href="https://github.com/AlexKontorovich/'
            'PrimeNumberTheoremAnd/pulls?q=is%3Apr+author%3ATomodovodoo" '
            'color="#245BFF">Merged PRs</link>',
        ],
        y,
        styles,
    )

    y -= 2
    y = _draw_main_heading(pdf, "Scientific AI Systems", y, styles)
    y = _draw_item(
        pdf,
        "Bazaar_ML - Simulator, Certification & RL",
        "2026 - Present",
        [
            "<b>49,248-case</b> executable certification matrix; <b>99.85%</b> "
            "sampling-pool coverage; deterministic traces, provenance, and "
            "agent-training hooks.",
        ],
        y,
        styles,
    )
    y = _draw_item(
        pdf,
        "NMR Prediction with Graph Neural Networks",
        "2024 - 2025",
        [
            "Curated molecular/NMR data and benchmarked GNNs on HPC under "
            "controlled splits and evaluation.",
        ],
        y,
        styles,
    )

    y -= 2
    y = _draw_main_heading(pdf, "Engineering", y, styles)
    y = _draw_item(
        pdf,
        "AI Engineer - SoundImports",
        "Present",
        [
            "Ship prediction algorithms, AI automation, and containerized AWS "
            "services.",
        ],
        y,
        styles,
        gap_after=2,
    )
    y = _draw_item(
        pdf,
        "BaanSoliciteren - Agentic Job Automation",
        "2025 - 2026",
        [
            "Auditable pipeline for vacancy ingestion, fit scoring, and "
            "application-state tracking. "
            '<link href="https://github.com/Tomodovodoo/BaanSoliciteren" '
            'color="#245BFF">GitHub</link>',
        ],
        y,
        styles,
        gap_after=2,
    )
    y = _draw_item(
        pdf,
        "Earlier: Teamspot (Regional Director / QA), Transcom, Chess.com",
        "2022 - 2024",
        [],
        y,
        styles,
        gap_after=0,
    )
    return y


def build_pdf() -> None:
    styles = _styles()
    pdf = canvas.Canvas(str(PDF_PATH), pagesize=A4, pageCompression=1)
    pdf.setTitle("Tom de Groot - Independent Researcher")
    pdf.setAuthor("Tom de Groot")
    pdf.setSubject("Independent research in AI-assisted mathematics and science")
    _draw_sidebar(pdf, styles)
    main_bottom = _draw_main(pdf, styles)
    if main_bottom < 7 * mm:
        raise RuntimeError(
            "Main-column content is too close to the page edge: "
            f"{main_bottom / mm:.1f} mm."
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
        "Raynaud bundles",
        "SoundImports",
        "49,248",
        "Graph Neural Networks",
        "FirstProof Problem 9",
        "BaanSoliciteren",
    )
    missing = [phrase for phrase in required_phrases if phrase not in text]
    if missing:
        raise RuntimeError(f"Generated PDF is missing required text: {missing}")

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
