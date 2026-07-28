"""Generate Tom de Groot's one-page CV as PDF and PNG.

The generator intentionally keeps no HTML or Markdown intermediate files.
Run from any directory with:

    python SimpleCV/generate_cv.py
"""

from __future__ import annotations

from pathlib import Path

import fitz
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / "CV.pdf"
PNG_PATH = BASE_DIR / "CV.png"

NAVY = colors.HexColor("#0F172A")
SLATE = colors.HexColor("#334155")
MUTED = colors.HexColor("#64748B")
ACCENT = colors.HexColor("#0F766E")
RULE = colors.HexColor("#CBD5E1")
PALE = colors.HexColor("#F0FDFA")


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "Name",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=27,
            leading=29,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=1.5,
        ),
        "headline": ParagraphStyle(
            "Headline",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=ACCENT,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "contact": ParagraphStyle(
            "Contact",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.4,
            leading=10,
            textColor=SLATE,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10.1,
            leading=11.8,
            textColor=ACCENT,
            spaceBefore=4.5,
            spaceAfter=2,
            uppercase=True,
        ),
        "summary": ParagraphStyle(
            "Summary",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.15,
            leading=11.5,
            textColor=SLATE,
            alignment=TA_LEFT,
            spaceAfter=1,
        ),
        "item_title": ParagraphStyle(
            "ItemTitle",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.7,
            leading=11.5,
            textColor=NAVY,
        ),
        "item_meta": ParagraphStyle(
            "ItemMeta",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.35,
            leading=10.2,
            textColor=MUTED,
            alignment=TA_RIGHT,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.85,
            leading=11,
            textColor=SLATE,
            leftIndent=8,
            firstLineIndent=-6,
            bulletIndent=0,
            spaceAfter=0.9,
        ),
        "compact": ParagraphStyle(
            "Compact",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.7,
            leading=10.8,
            textColor=SLATE,
            spaceAfter=0.8,
        ),
    }


def _section(title: str, styles: dict[str, ParagraphStyle]) -> list:
    return [
        Paragraph(title.upper(), styles["section"]),
        HRFlowable(
            width="100%",
            thickness=0.65,
            color=RULE,
            spaceBefore=0,
            spaceAfter=3,
        ),
    ]


def _item_header(
    title: str,
    meta: str,
    styles: dict[str, ParagraphStyle],
) -> Table:
    table = Table(
        [
            [
                Paragraph(title, styles["item_title"]),
                Paragraph(meta, styles["item_meta"]),
            ]
        ],
        colWidths=[138 * mm, 40 * mm],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0.4),
            ]
        )
    )
    return table


def _bullet(text: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(f"&bull;&nbsp; {text}", styles["bullet"])


def _project(
    title: str,
    meta: str,
    bullets: list[str],
    styles: dict[str, ParagraphStyle],
) -> KeepTogether:
    flowables = [_item_header(title, meta, styles)]
    flowables.extend(_bullet(text, styles) for text in bullets)
    flowables.append(Spacer(1, 2))
    return KeepTogether(flowables)


def _on_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setTitle("Tom de Groot - Scientific AI, Evaluation and Data")
    canvas.setAuthor("Tom de Groot")
    canvas.setSubject("Resume tailored to scientific AI evaluation and data roles")
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(2.2)
    canvas.line(doc.leftMargin, A4[1] - 7 * mm, A4[0] - doc.rightMargin, A4[1] - 7 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawRightString(
        A4[0] - doc.rightMargin,
        6.5 * mm,
        "GitHub: Tomodovodoo",
    )
    canvas.restoreState()


def build_pdf() -> None:
    styles = _styles()
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=10.5 * mm,
        bottomMargin=10 * mm,
        title="Tom de Groot - Scientific AI, Evaluation and Data",
        author="Tom de Groot",
        subject="Resume tailored to scientific AI evaluation and data roles",
    )

    story = [
        Paragraph("Tom de Groot", styles["name"]),
        Paragraph(
            "AI Engineer | Scientific AI, Evaluation &amp; Data",
            styles["headline"],
        ),
        Paragraph(
            "Groningen, Netherlands &nbsp;|&nbsp; +31 6 314 90 416 "
            "&nbsp;|&nbsp; "
            '<link href="mailto:tomthegreatest04@gmail.com" '
            'color="#334155">tomthegreatest04@gmail.com</link>'
            "<br/>"
            '<link href="https://github.com/Tomodovodoo" '
            'color="#0F766E">github.com/Tomodovodoo</link>'
            "&nbsp;|&nbsp;"
            '<link href="https://linkedin.com/in/tomodovodoo" '
            'color="#0F766E">linkedin.com/in/tomodovodoo</link>'
            "&nbsp;|&nbsp;"
            '<link href="https://x.com/Tomodovodoo" '
            'color="#0F766E">x.com/Tomodovodoo</link>',
            styles["contact"],
        ),
    ]

    story.extend(_section("Profile", styles))
    story.append(
        Paragraph(
            "AI engineer and chemistry-trained researcher building evaluation, "
            "data, and agentic systems. Production work spans prediction "
            "algorithms, AI automation, AWS/container deployment, and full-stack "
            "applications. Research includes GNN-based NMR prediction, molecular "
            "data cleaning, HPC training, and controlled model evaluation. "
            "Open-source work combines simulator-first RL infrastructure with "
            "Lean-verified evaluation of LLM-generated mathematics.",
            styles["summary"],
        )
    )

    story.extend(_section("Experience", styles))
    story.append(
        _project(
            "AI Engineer - SoundImports",
            "Present",
            [
                "Develop prediction algorithms and AI automations; deploy "
                "containerized services on AWS and build full-stack applications.",
                "Work across data, model, API, and deployment layers to turn "
                "operational workflows into reliable production systems.",
            ],
            styles,
        )
    )
    story.append(
        _project(
            "Chemistry Research - University of Groningen, Pollice Group",
            "2024 - 2025",
            [
                "<b>BSc thesis:</b> Evaluating and Optimizing NMR Prediction "
                "with Graph Neural Networks.",
                "Curated molecular/NMR data and ran controlled GNN experiments "
                "on HPC, comparing architectures and model outcomes through a "
                "hypothesis-test-measure-iterate workflow.",
            ],
            styles,
        )
    )
    story.append(
        _project(
            "Regional Director / QA - Teamspot",
            "2022 - 2024",
            [
                "Coordinated regional school projects, trained users, and "
                "bug-tested web, app, API, and integration workflows in Jira.",
            ],
            styles,
        )
    )

    story.extend(_section("Selected Evaluation, Data & AI Work", styles))
    story.append(
        _project(
            "Bazaar_ML - Simulator, Certification & RL Environment",
            "2026 - Present",
            [
                "Built a simulator-first ML stack that ingests versioned public "
                "data, compiles heterogeneous mechanics into executable records, "
                "emits deterministic traces, and exposes agent-training hooks.",
                "Designed schema-frozen certification and provenance. The current "
                "committed matrix contains <b>49,248 cases</b>, <b>99.85%</b> "
                "executable sampling-pool coverage, content/parser hashes, explicit "
                "unsupported primitives, and zero recorded execution failures.",
            ],
            styles,
        )
    )
    story.append(
        _project(
            "LLM-Aided Formal Mathematics - Lean 4",
            "2025 - Present",
            [
                "Orchestrated multiple agents to solve FirstProof Problem 9 "
                "informally and formalize it in Lean; the repository pins a "
                "reproducible toolchain and contains the only solved problem in "
                "that workspace.",
                "Co-authored multiple merged PNT+ proofs and use Lean compilation, "
                "tests, and adversarial review as hard evaluations for model output.",
            ],
            styles,
        )
    )
    story.append(
        _project(
            "BaanSoliciteren - Agentic Data Pipeline",
            "2025 - 2026",
            [
                "Built a Python/Gmail MCP workflow to ingest vacancy pages and "
                "email, normalize them into JSON, score fit, track state, and "
                "archive outcomes with a reproducible audit trail.",
            ],
            styles,
        )
    )

    story.extend(_section("Education & Recognition", styles))
    story.append(
        Paragraph(
            "<b>BSc Chemistry, University of Groningen</b> - Chemistry of Life "
            "track, 2021 - 2025 &nbsp;|&nbsp; "
            "<b>Harmonic Rising Mathematician Award</b>, 2026 &nbsp;|&nbsp; "
            "<b>Chess.com Member of the Year</b>, 2021",
            styles["compact"],
        )
    )

    story.extend(_section("Technical Skills", styles))
    story.extend(
        [
            Paragraph(
                "<b>Evaluation &amp; data:</b> benchmark/certification design, "
                "data quality and provenance, dataset versioning, deterministic "
                "replay, failure analysis, scientific experimentation",
                styles["compact"],
            ),
            Paragraph(
                "<b>AI &amp; engineering:</b> Python, PyTorch, TensorFlow, "
                "scikit-learn, pandas, NumPy, SQL, RDKit, JavaScript, APIs, AWS, "
                "Docker, Linux/HPC, Git",
                styles["compact"],
            ),
            Paragraph(
                "<b>Formal methods:</b> Lean 4, mathlib, Lake, CI &nbsp;|&nbsp; "
                "<b>Science:</b> analytical chemistry, biochemistry, NMR, BSL-2, "
                "molecular data &nbsp;|&nbsp; "
                "<b>Languages:</b> Dutch (native), English (fluent)",
                styles["compact"],
            ),
        ]
    )

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)


def render_png() -> None:
    with fitz.open(PDF_PATH) as document:
        if document.page_count != 1:
            raise RuntimeError(
                f"Expected a one-page CV, generated {document.page_count} pages."
            )
        page = document[0]
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        pixmap.save(PNG_PATH)


def validate_outputs() -> None:
    reader = PdfReader(str(PDF_PATH))
    if len(reader.pages) != 1:
        raise RuntimeError(f"Expected one PDF page, found {len(reader.pages)}.")

    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    required_phrases = (
        "Tom de Groot",
        "Scientific AI",
        "49,248 cases",
        "Graph Neural Networks",
        "Lean 4",
        "SoundImports",
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
