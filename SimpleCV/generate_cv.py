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
            fontSize=12,
            leading=13.4,
            textColor=NAVY,
            alignment=TA_LEFT,
        ),
        "main_body": ParagraphStyle(
            "MainBody",
            fontName="Helvetica",
            fontSize=9.15,
            leading=11.7,
            textColor=TEXT,
            alignment=TA_LEFT,
        ),
        "item_title": ParagraphStyle(
            "ItemTitle",
            fontName="Helvetica-Bold",
            fontSize=10.2,
            leading=11.7,
            textColor=NAVY,
            alignment=TA_LEFT,
        ),
        "item_body": ParagraphStyle(
            "ItemBody",
            fontName="Helvetica",
            fontSize=8.95,
            leading=11.35,
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
        "Chemistry - Math - AI",
        styles["subtitle"],
        x,
        y,
        width,
    )
    y -= 7

    contact_lines = [
        "Grijpskerk, NL",
        '<link href="tel:+31631490416" color="#334155">+31 6 314 90 416</link>',
        '<link href="mailto:tomthegreatest04@gmail.com" '
        'color="#334155">tomthegreatest04@gmail.com</link>',
        '<link href="https://github.com/Tomodovodoo" '
        'color="#334155">github.com/Tomodovodoo</link>',
        '<link href="https://linkedin.com/in/tomodovodoo" '
        'color="#334155">linkedin.com/in/tomodovodoo</link>',
    ]
    for line in contact_lines:
        y = _draw_paragraph(pdf, line, styles["contact"], x, y, width)
        y -= 1.2

    y -= 6
    y = _draw_sidebar_heading(pdf, "Technical Stack", y, styles)
    skill_groups = [
        "<b>AI/Evaluation:</b> PyTorch, TensorFlow, agentic workflows, "
        "RL environments, benchmark design",
        "<b>Data:</b> pandas, NumPy, SQL, RDKit, scientific data quality, "
        "provenance, versioning",
        "<b>Formal:</b> Lean 4, mathlib, Lake, CI/CD for proofs",
        "<b>Tools:</b> Git, AWS, Docker, Linux/HPC, APIs",
        "<b>Languages:</b> Python, Lean, JavaScript<br/>"
        "<b>Spoken:</b> Dutch, English",
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
        "<b>Thesis:</b> Evaluating and Optimizing NMR Prediction with "
        "Graph Neural Networks",
        styles["sidebar_small"],
        x,
        y,
        width,
    )

    y -= 12
    y = _draw_sidebar_heading(pdf, "Awards", y, styles)
    y = _draw_paragraph(
        pdf,
        '<link href="https://www.chess.com/news/view/2021-chesscom-awards-winners#member" '
        'color="#245BFF">Chess.com Member of the Year 2021</link>',
        styles["sidebar_body"],
        x,
        y,
        width,
    )
    y -= 6
    _draw_paragraph(
        pdf,
        '<link href="https://harmonic.fun/news/mathematician-sponsorships/" '
        'color="#245BFF">Harmonic Rising Mathematician Award</link>',
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

    y = _draw_main_heading(pdf, "About Me", y, styles)
    y = _draw_paragraph(
        pdf,
        "AI engineer at <b>SoundImports</b> and BSc Chemistry graduate from "
        "the University of Groningen. My thesis in the Pollice Group focused "
        "on evaluating and optimizing graph neural networks for NMR prediction, "
        "including molecular-data cleaning, HPC training, and controlled model "
        "comparison.",
        styles["main_body"],
        MAIN_X,
        y,
        MAIN_WIDTH,
    )
    y -= 4
    y = _draw_paragraph(
        pdf,
        "I build scientific-AI and agentic systems around explicit data lineage, "
        "reproducible environments, hard evaluations, and failure-driven "
        "iteration - from production prediction systems to deterministic "
        "simulators and Lean-verified mathematics.",
        styles["main_body"],
        MAIN_X,
        y,
        MAIN_WIDTH,
    )

    y -= 10
    y = _draw_main_heading(
        pdf,
        "Scientific AI, Evaluation & Data",
        y,
        styles,
    )
    y = _draw_item(
        pdf,
        "Bazaar_ML - Simulator, Certification & RL Environment",
        "2026 - Present",
        [
            "Built a simulator-first ML stack that ingests versioned public "
            "source data, compiles heterogeneous mechanics into executable "
            "records, simulates complete trajectories, emits deterministic "
            "traces, and exposes agent-training hooks.",
            "Designed schema-frozen certification and provenance. The committed "
            "matrix contains <b>49,248 cases</b>, <b>99.85%</b> executable "
            "sampling-pool coverage, explicit parser/content hashes and "
            "unsupported primitives, and zero recorded execution failures.",
        ],
        y,
        styles,
    )
    y = _draw_item(
        pdf,
        "NMR Prediction with Graph Neural Networks",
        "2024 - 2025",
        [
            "Curated molecular and NMR data and ran controlled GNN experiments "
            "on HPC. Compared architectures and outcomes through a "
            "hypothesis-test-measure-iterate workflow, with attention to "
            "identifiers, scientific context, split design, and evaluation quality.",
        ],
        y,
        styles,
    )

    y -= 2
    y = _draw_main_heading(
        pdf,
        "Research & Formalization",
        y,
        styles,
    )
    y = _draw_item(
        pdf,
        "FirstProof Problem 9 - Lean-Verified Agent Workflow",
        "Feb 2026",
        [
            "Orchestrated multiple LLM agents to find an informal solution and "
            "formalize it in Lean 4. Lean compilation provided a hard evaluator "
            "for every accepted step; the pinned workspace contains the only "
            "solved problem in that repository. "
            '<link href="https://github.com/Tomodovodoo/firstproof" '
            'color="#245BFF">Repository</link>',
        ],
        y,
        styles,
    )
    y = _draw_item(
        pdf,
        "Prime Number Theorem And (PNT+)",
        "Late 2025 - Present",
        [
            "Co-authored multiple merged Lean proofs in the open-source PNT+ "
            "project and use compilation, tests, and adversarial review to "
            "evaluate model-generated mathematics. "
            '<link href="https://github.com/AlexKontorovich/PrimeNumberTheoremAnd/pulls'
            '?q=is%3Apr+author%3ATomodovodoo" color="#245BFF">Merged PRs</link>',
        ],
        y,
        styles,
    )

    y -= 2
    y = _draw_main_heading(pdf, "Engineering Projects", y, styles)
    y = _draw_item(
        pdf,
        "BaanSoliciteren - Agentic Job Automation",
        "2025 - 2026",
        [
            "Built a Python/Gmail MCP pipeline to ingest vacancy pages and "
            "email, normalize them into JSON, score fit, track state, and "
            "archive outcomes with an auditable workflow. "
            '<link href="https://github.com/Tomodovodoo/BaanSoliciteren" '
            'color="#245BFF">GitHub</link>',
        ],
        y,
        styles,
    )

    y -= 1
    y = _draw_main_heading(pdf, "Professional Experience", y, styles)
    y = _draw_item(
        pdf,
        "AI Engineer - SoundImports",
        "Present",
        [
            "Develop prediction algorithms and AI automations; deploy "
            "containerized services on AWS and build full-stack applications "
            "across data, model, API, and production layers.",
        ],
        y,
        styles,
        gap_after=2,
    )
    y = _draw_item(
        pdf,
        "Teamspot - Regional Director / QA",
        "2022 - 2024",
        [
            "Coordinated regional school projects, trained users, and "
            "bug-tested web, app, API, and integration workflows in Jira.",
        ],
        y,
        styles,
        gap_after=2,
    )
    y = _draw_item(
        pdf,
        "Transcom (for Odido)",
        "2024",
        [
            "Maintained consistently strong customer-satisfaction results and "
            "learned to explain technical and operational issues clearly.",
        ],
        y,
        styles,
        gap_after=2,
    )
    y = _draw_item(
        pdf,
        "Chess.com",
        "2022",
        [
            "Moderated and proctored international chess events; recognized as "
            "Member of the Year 2021 for community ownership and coaching.",
        ],
        y,
        styles,
        gap_after=0,
    )
    return y


def build_pdf() -> None:
    styles = _styles()
    pdf = canvas.Canvas(str(PDF_PATH), pagesize=A4, pageCompression=1)
    pdf.setTitle("Tom de Groot - Scientific AI, Evaluation and Data")
    pdf.setAuthor("Tom de Groot")
    pdf.setSubject("CV tailored to scientific AI evaluation and data roles")
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
