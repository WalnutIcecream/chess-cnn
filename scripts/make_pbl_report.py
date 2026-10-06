#!/usr/bin/env python3
"""Generate the PBL-2 project report (docx) for the chess move-explainer project.

The document reproduces the section skeleton, front matter, table and figure numbering of
the submitted PBL-2 report, with content rewritten for the current (moveexp) system.

Run inside the venv::

    .venv\\Scripts\\python.exe scripts/make_pbl_report.py
"""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from docx import Document  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Inches, Pt, RGBColor  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

from moveexp.config import PROJECT_ROOT  # noqa: E402

DOCX_NAME = "PBL_Report_Chess_Move_Intent.docx"
RESULTS_CSV = PROJECT_ROOT / "experiments" / "model_vs_rules.csv"

_FONT = "Calibri"


# --------------------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------------------


def _draw_boxes(ax, boxes, edges):
    """Draw labelled rounded boxes and arrows. ``boxes``: (x, y, w, h, text)."""
    for x, y, w, h, text in boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.06,rounding_size=0.12",
                linewidth=1.1,
                edgecolor="#33415a",
                facecolor="#eef2f8",
            )
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.6, color="#16202e")
    for (x1, y1), (x2, y2) in edges:
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="-|>",
                mutation_scale=11,
                linewidth=1.3,
                color="#2f6b45",
            )
        )


def figure_architecture(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 3.9))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    top = [
        (0.15, 3.0, 2.15, 0.95, "Input\nFEN + move, or PGN"),
        (2.6, 3.0, 2.15, 0.95, "Engine layer\nStockfish 19 over UCI\n+ SQLite cache"),
        (
            5.05,
            3.0,
            2.15,
            0.95,
            "Symbolic layer\nquality, criticality, SEE,\n40 themes, intent tags",
        ),
        (7.5, 3.0, 2.35, 0.95, "MoveReport\n(pydantic: JSON / Parquet)"),
    ]
    bottom = [
        (
            2.6,
            1.0,
            2.6,
            1.0,
            "Explanation layer\nfacts -> render -> verify\n(prose, every claim sourced)",
        ),
        (6.4, 1.0, 3.0, 1.0, "Neural layer\nencode board -> CNN ->\nquality / theme / intent"),
    ]
    edges = [
        ((2.3, 3.47), (2.6, 3.47)),
        ((4.75, 3.47), (5.05, 3.47)),
        ((7.2, 3.47), (7.5, 3.47)),
        ((8.1, 3.0), (4.6, 2.0)),
        ((8.1, 3.0), (7.6, 2.0)),
    ]
    _draw_boxes(ax, top, edges)
    _draw_boxes(ax, bottom, [])
    ax.text(
        0.15,
        2.55,
        "One invariant: evaluation perspective is converted in exactly one module.",
        fontsize=7.6,
        color="#5a6472",
    )
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def figure_flowchart(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 4.1))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    boxes = [
        (0.15, 3.3, 2.0, 0.9, "cli.py\nanalyze-move / explain\n/ batch / vocab"),
        (2.55, 3.3, 2.0, 0.9, "pipeline.py\nanalyse_move\nanalyse_game"),
        (4.95, 3.3, 2.0, 0.9, "engine/\nclient + cache\neval_utils"),
        (
            7.35,
            3.3,
            2.5,
            0.9,
            "analysis/\nmove_quality, criticality,\nsee, features, themes/, intent",
        ),
        (0.15, 1.5, 2.4, 0.95, "explain/\nmodels, facts, render,\nverify, api"),
        (2.95, 1.5, 2.4, 0.95, "model/\nencode, dataset,\nnetwork"),
        (
            5.75,
            1.5,
            4.1,
            0.95,
            "schema.py -> MoveReport / GameReport (the contract every module speaks)",
        ),
    ]
    edges = [
        ((2.15, 3.75), (2.55, 3.75)),
        ((4.55, 3.75), (4.95, 3.75)),
        ((6.95, 3.75), (7.35, 3.75)),
        ((6.0, 3.3), (1.35, 2.45)),
        ((6.0, 3.3), (4.15, 2.45)),
    ]
    _draw_boxes(ax, boxes, edges)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def figure_terminal(path: Path) -> None:
    lines = [
        '$ moveexp explain --fen "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 4 4"',
        '        --move "Qxf7#" --depth 14',
        "",
        "Qxf7# \u2014 a great move.",
        "  The evaluation remains winning by force.",
        "  It was the only move that keeps the position.",
        "  The move is forcing: a check or a forced mate.",
        "  The position was critical: small differences in the evaluation mattered.",
        "  Fork: Q@f7 hits b@f8 and n@g8 and k@e8 at once and does not hang.",
        "  Threat created: the move now attacks the defended b@f8.",
        "  Back rank mate: Qxf7# mates: the king on e8 never left its back rank.",
        "  Capture: takes the p@f7.",
        "  Material: the mover gained 1.00 pawns.",
        "  Intent \u2014 attacks king: Qxf7# gives check.",
        "",
        "# each line above is a claim; --json prints the claim's evidence and source values",
    ]
    height = 0.34 * len(lines) + 0.4
    fig, ax = plt.subplots(figsize=(9.4, height))
    ax.axis("off")
    ax.add_patch(
        FancyBboxPatch(
            (0.005, 0.005),
            0.99,
            0.99,
            transform=ax.transAxes,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            linewidth=1.0,
            edgecolor="#33415a",
            facecolor="#0f141b",
        )
    )
    for index, line in enumerate(lines):
        ax.text(
            0.02,
            0.97 - index * (0.94 / len(lines)),
            line,
            transform=ax.transAxes,
            fontsize=7.6,
            family="monospace",
            color="#d6e2f0",
            va="top",
        )
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def figure_results(path: Path) -> None:
    rows = []
    with RESULTS_CSV.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["variant"] == "with_move":
                rows.append(
                    (
                        row["head"],
                        row["metric"],
                        float(row["model"]),
                        float(row["majority_baseline"]),
                    )
                )
    labels = [f"{head}: {metric}" for head, metric, _, _ in rows]
    model = [r[2] for r in rows]
    base = [r[3] for r in rows]
    y = range(len(labels))
    fig, ax = plt.subplots(figsize=(9.2, 3.6))
    ax.barh([i + 0.2 for i in y], model, height=0.38, color="#3f8f5f", label="CNN model")
    ax.barh([i - 0.2 for i in y], base, height=0.38, color="#9aa6b4", label="majority baseline")
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xlim(0, 1)
    ax.invert_yaxis()
    ax.set_xlabel("score", fontsize=9)
    ax.legend(fontsize=8.5, loc="lower right")
    ax.grid(axis="x", linestyle=":", color="#c9d0da")
    for i, value in enumerate(model):
        ax.text(value + 0.01, i + 0.2, f"{value:.3f}", va="center", fontsize=7.5, color="#25613f")
    for i, value in enumerate(base):
        ax.text(value + 0.01, i - 0.2, f"{value:.3f}", va="center", fontsize=7.5, color="#5a6472")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------------------
# Document helpers
# --------------------------------------------------------------------------------------


def _set_doc_defaults(doc: Document) -> None:
    style = doc.styles["Normal"]
    style.font.name = _FONT
    style.font.size = Pt(11)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), _FONT)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.15


def h(doc: Document, text: str, level: int = 1) -> None:
    sizes = {1: 15, 2: 13, 3: 11.5}
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    paragraph.paragraph_format.space_after = Pt(6)
    run = paragraph.add_run(text)
    run.bold = True
    run.font.size = Pt(sizes[level])
    run.font.color.rgb = RGBColor(0, 0, 0)
    run.font.name = _FONT


def body(doc: Document, text: str, *, justify: bool = True) -> None:
    paragraph = doc.add_paragraph(text)
    if justify:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        paragraph = doc.add_paragraph(item, style="List Bullet")
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def numbered(doc: Document, items: list[str]) -> None:
    for item in items:
        paragraph = doc.add_paragraph(item, style="List Number")
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def centered(doc: Document, text: str, *, size: float = 11, bold: bool = False) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = _FONT


def caption(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.bold = True
    run.font.size = Pt(9.5)


def table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    tbl = doc.add_table(rows=1, cols=len(headers))
    tbl.style = "Table Grid"
    for cell, text in zip(tbl.rows[0].cells, headers, strict=True):
        cell.text = ""
        run = cell.paragraphs[0].add_run(text)
        run.bold = True
        run.font.size = Pt(9.5)
    for row in rows:
        cells = tbl.add_row().cells
        for cell, text in zip(cells, row, strict=True):
            cell.text = ""
            run = cell.paragraphs[0].add_run(text)
            run.font.size = Pt(9.5)
    doc.add_paragraph()


def figure(doc: Document, path: Path, caption_text: str, width: float = 6.3) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(path), width=Inches(width))
    caption(doc, caption_text)


def toc_field(doc: Document, entries: list[tuple[str, str]]) -> None:
    """Insert a Word TOC field with the section list cached until the field is updated."""
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    fld_begin = run._r.makeelement(qn("w:fldChar"), {qn("w:fldCharType"): "begin"})
    instr = run._r.makeelement(qn("w:instrText"), {})
    instr.text = r'TOC \o "1-3" \h \z \u'
    fld_sep = run._r.makeelement(qn("w:fldChar"), {qn("w:fldCharType"): "separate"})
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    for number, title in entries:
        line = paragraph.add_run(f"\n{number}   {title}")
        line.font.size = Pt(11)
    end_run = paragraph.add_run()
    fld_end = end_run._r.makeelement(qn("w:fldChar"), {qn("w:fldCharType"): "end"})
    end_run._r.append(fld_end)


# --------------------------------------------------------------------------------------
# Report content
# --------------------------------------------------------------------------------------

TITLE = "Explaining the Intent Behind Chess Moves: A Verifiable Symbolic-Neural Pipeline"

TOC_ENTRIES = [
    ("1.", "Introduction"),
    ("1.1", "Background"),
    ("1.2", "Purpose of the Document"),
    ("1.3", "Scope of the Project"),
    ("2.", "Literature Review"),
    ("2.1", "Overview of Existing Solutions"),
    ("2.2", "Identified Challenges"),
    ("2.3", "Opportunities for Improvement"),
    ("2.4", "Summary of Findings"),
    ("3.", "Problem Definition"),
    ("3.1", "Project Scope"),
    ("3.2", "Objectives"),
    ("3.3", "Deliverables"),
    ("3.4", "Problem Statement"),
    ("4.", "Proposal Development"),
    ("4.1", "Research Findings"),
    ("4.2", "Project Objectives"),
    ("4.3", "Methodology"),
    ("4.3.1", "Data Collection Methods"),
    ("4.3.2", "Analytical Techniques"),
    ("5.", "Prototype Design"),
    ("5.1", "Design Specifications"),
    ("5.2", "Functionality Requirements"),
    ("5.3", "Feasibility and Scalability Analysis"),
    ("5.4", "Design Validation Criteria"),
    ("6.", "Prototyping"),
    ("6.1", "Proof-of-Concept Development"),
    ("6.2", "Key Functionalities Implementation"),
    ("6.3", "Tools and Technologies Used"),
    ("7.", "Testing and Validation"),
    ("7.1", "Test Plan and Procedures"),
    ("7.2", "Performance Metrics"),
    ("7.3", "Iteration Results"),
    ("8.", "Data Collection and Analysis"),
    ("8.1", "Testing Data Methodology"),
    ("8.2", "Key Findings and Metrics"),
    ("8.3", "Data Visualisation"),
    ("9.", "Patent Search"),
    ("9.1", "Relevant Patents Review"),
    ("9.2", "IP Gap Analysis"),
    ("10.", "Conclusion"),
    ("10.1", "Summary"),
    ("10.2", "Next Steps"),
    ("11.", "References"),
]


def build_report(work_dir: Path) -> Path:
    figures = {
        "arch": work_dir / "fig_4_1.png",
        "flow": work_dir / "fig_5_1.png",
        "term": work_dir / "fig_6_1.png",
        "res": work_dir / "fig_8_1.png",
    }
    figure_architecture(figures["arch"])
    figure_flowchart(figures["flow"])
    figure_terminal(figures["term"])
    figure_results(figures["res"])

    doc = Document()
    _set_doc_defaults(doc)

    # ---- Title page ------------------------------------------------------------------
    for _ in range(3):
        doc.add_paragraph()
    centered(doc, "School of Computer Science and Engineering", size=12, bold=True)
    centered(doc, "Department of Data Science and Engineering", size=12)
    centered(doc, "MANIPAL UNIVERSITY JAIPUR, JAIPUR", size=12, bold=True)
    centered(doc, "RAJASTHAN, INDIA", size=12)
    for _ in range(2):
        doc.add_paragraph()
    centered(doc, "A Project Report", size=13, bold=True)
    centered(doc, "on", size=12)
    centered(doc, TITLE, size=15, bold=True)
    doc.add_paragraph()
    centered(doc, "carried out as part of the Project Based Learning-2 (DSE2270)", size=11)
    centered(doc, "Submitted", size=11)
    centered(doc, "by", size=11)
    centered(doc, "Aditya Pandey (2430010060)", size=12, bold=True)
    doc.add_paragraph()
    centered(doc, "in partial fulfilment for the award of the degree of", size=11)
    centered(
        doc, "Bachelor of Technology in Computer Science and Engineering (Data Science)", size=11
    )
    for _ in range(2):
        doc.add_paragraph()
    centered(doc, "School of Computer Science and Engineering", size=11, bold=True)
    centered(doc, "Department of Data Science and Engineering", size=11)
    centered(doc, "MANIPAL UNIVERSITY JAIPUR, JAIPUR", size=11, bold=True)
    centered(doc, "RAJASTHAN, INDIA", size=11)
    doc.add_paragraph()
    centered(doc, "March 2026", size=11, bold=True)
    doc.add_page_break()

    # ---- Certificate -----------------------------------------------------------------
    centered(doc, "CERTIFICATE", size=14, bold=True)
    doc.add_paragraph()
    body(
        doc,
        (
            "This is to certify that the project-based learning, project titled "
            f"{TITLE} is a record of the bonafide work done by Aditya Pandey (2430010060), "
            "submitted in partial fulfilment of the requirements for the award of the Degree of "
            "Bachelor of Technology in Computer Science and Engineering (Data Science) of Manipal "
            "University Jaipur, Jaipur during the academic year 2025-26."
        ),
    )
    for _ in range(4):
        doc.add_paragraph()
    centered(doc, "Dr. Rekha Chaturvedi", size=11, bold=True)
    centered(doc, "Assistant Professor", size=10)
    centered(doc, "Project Guide, Department of Data Science and Engineering", size=10)
    centered(doc, "Manipal University Jaipur, Jaipur", size=10)
    for _ in range(3):
        doc.add_paragraph()
    centered(doc, "Dr. Pooja Gupta", size=11, bold=True)
    centered(doc, "Associate Professor", size=10)
    centered(doc, "Class Coordinator, Department of Data Science and Engineering", size=10)
    centered(doc, "Manipal University Jaipur, Jaipur", size=10)
    doc.add_page_break()

    # ---- Abstract --------------------------------------------------------------------
    centered(doc, "ABSTRACT", size=14, bold=True)
    doc.add_paragraph()
    body(
        doc,
        (
            "Strong chess engines such as Stockfish and Leela Chess Zero play far better than any "
            "human, but they only report what is good, not why. Their output is a number and a best "
            "move; a learner is expected to infer the idea behind the move, and cannot. This project "
            "builds a pipeline that takes a position and a played move and produces a structured, "
            "auditable explanation of the move: how good it was, what tactics it contained, how it "
            "changed the position, and what intent it plausibly served. The final step turns that "
            "structure into natural language in which every sentence is traceable to a fact in the "
            "underlying report."
        ),
    )
    body(
        doc,
        (
            "The central difficulty is that intent is not observable. A game record contains "
            "positions and moves, and no large dataset of human-labelled intentions exists. The "
            "system therefore treats intent as inferred consequence and works strictly from what can "
            "be measured: an engine layer supplies objective numbers, and hand-written symbolic rules "
            "over the board supply interpretable concepts. These rules are the weak-supervision "
            "source that produces labels at scale. A neural network is added only on top of those "
            "labels and only where it can be compared against the rule baseline."
        ),
    )
    body(
        doc,
        (
            "The current build delivers a working symbolic layer (engine client with caching, static "
            "exchange evaluation, forty theme detectors, intent tags, and a typed MoveReport), a "
            "constrained explanation layer that re-derives every claim against the report and drops "
            "anything unsupported, a command-line interface, self-contained visual demo pages, and a "
            "small CNN trained on self-play labels that predicts move quality, tactical themes and "
            "intent tags from the board alone. On the current corpus the model learns themes and "
            "intents clearly above a trivial baseline but does not learn move quality; both the "
            "result and its causes are reported rather than hidden. The pipeline is reproducible, "
            "runs entirely offline, and is covered by 316 automated tests."
        ),
    )
    doc.add_page_break()

    # ---- List of tables / figures ----------------------------------------------------
    centered(doc, "LIST OF TABLES", size=14, bold=True)
    doc.add_paragraph()
    table(
        doc,
        ["Table No.", "Table Title", "Page No."],
        [
            ["4.1", "Timeline and Milestones", "11"],
            ["6.1", "Tools and Technologies Used", "16"],
            ["7.1", "Test Cases and Results", "18"],
            ["8.1", "Model versus Baseline Metrics", "20"],
            ["9.1", "Patent Summary", "22"],
        ],
    )
    doc.add_page_break()
    centered(doc, "LIST OF FIGURES", size=14, bold=True)
    doc.add_paragraph()
    table(
        doc,
        ["Figure No.", "Figure Title", "Page No."],
        [
            ["4.1", "System Architecture Diagram", "10"],
            ["5.1", "Module Interaction Flowchart", "13"],
            ["6.1", "Sample Terminal Output", "15"],
            ["8.1", "Model versus Baseline Scores", "20"],
        ],
    )
    doc.add_page_break()

    # ---- Table of contents -----------------------------------------------------------
    centered(doc, "TABLE OF CONTENTS", size=14, bold=True)
    doc.add_paragraph()
    toc_field(doc, TOC_ENTRIES)
    doc.add_page_break()

    # ---- 1. Introduction -------------------------------------------------------------
    h(doc, "1. Introduction")
    h(doc, "1.1 Background", 2)
    body(
        doc,
        (
            "Chess engines have been stronger than the best humans for two decades, and the modern "
            "generation is far stronger still. Stockfish evaluates tens of millions of positions per "
            "second using an alpha-beta search over a neural evaluation, and Leela Chess Zero learns "
            "an evaluation from self-play. Both output the same kind of answer: a numerical score, "
            "usually in centipawns, together with a principal variation. That answer is exactly right "
            "for choosing a move and close to useless for teaching one. A student shown that a move "
            "loses 1.4 pawns learns that a mistake happened, not what it was. The engine knows the "
            "move is bad because the search says so; it has no representation of the pawn weakness, "
            "the misplaced knight or the undefended back rank that make it bad."
        ),
    )
    body(
        doc,
        (
            "The obvious fix is to have a language model explain the engine's answer. That is where "
            "most current systems stop, and it is where they go wrong: a language model asked to "
            "explain a chess move will produce fluent commentary that is frequently unverifiable and "
            "sometimes simply false. For a teaching tool the failure mode matters more than the "
            "average case. A confident wrong explanation is worse than no explanation, because the "
            "student cannot tell the difference."
        ),
    )
    body(
        doc,
        (
            "This project takes the opposite constraint as its starting point: nothing may be said "
            "that cannot be checked. It builds a system in which every claim about a move is either "
            "measured by the engine or derived from the board by a rule that can be read and argued "
            "with, and in which the natural-language layer is only allowed to state facts that are "
            "present in the structured report. Where the rules are silent or wrong, the system is "
            "silent too, and that gap is reported as a limitation rather than papered over."
        ),
    )
    body(
        doc,
        (
            "A second consequence follows from the first. If explanation is to be learned rather than "
            "hand-written, the system needs labelled examples, and no dataset of human-labelled chess "
            "intentions exists at scale. The project therefore generates labels with the rules "
            "themselves, treats the rules as the baseline, and asks whether a network can recover "
            "those labels from the board alone. This is weak supervision, with label noise as a known "
            "and measured property of the data rather than an accident."
        ),
    )
    h(doc, "1.2 Purpose of the Document", 2)
    body(
        doc,
        (
            "This document records the project end to end: the problem, the related work, the design "
            "decisions and the reasoning behind them, the implementation, the tests, the measured "
            "results, the failures encountered and how they were resolved, and the limitations that "
            "remain. It is submitted in partial fulfilment of the requirements for the Project Based "
            "Learning-2 (DSE2270) course at Manipal University Jaipur. It is written to be read by "
            "someone who will check the work, so it states where the system is weak as plainly as "
            "where it is strong."
        ),
    )
    h(doc, "1.3 Scope of the Project", 2)
    body(doc, "The project covers per-move analysis and its presentation:")
    bullets(
        doc,
        [
            "Move quality: how much the move cost or gained, from the mover's point of view.",
            "Criticality: whether the move was forced, the only move, or played in a sharp position.",
            "Tactical and positional content: forty hand-written theme detectors over the board "
            "geometry, plus positional change in material, mobility, king safety, pawn structure, "
            "space and activity.",
            "Intent tags: a small vocabulary of plausible aims inferred from what the move does.",
            "A labelled dataset built from a locally generated self-play corpus, and a neural model "
            "that predicts the labels from the board alone.",
            "A constrained explanation layer and self-contained visual demo pages.",
        ],
    )
    body(
        doc,
        (
            "The following are explicitly out of scope: building a stronger engine; long-term "
            "strategic planning of the kind that spans many moves; any claim about the player's "
            "actual psychological intent; and human-written commentary as ground truth. The project "
            "is a research prototype, not a product."
        ),
    )
    doc.add_page_break()

    # ---- 2. Literature Review --------------------------------------------------------
    h(doc, "2. Literature Review")
    h(doc, "2.1 Overview of Existing Solutions", 2)
    body(
        doc,
        (
            "Commercial and open platforms already analyse games well. Lichess and Chess.com both run "
            "Stockfish and present evaluations, move classifications and suggested variations, and "
            "Chess.com sells a coaching layer on top. DecodeChess generates natural-language "
            "commentary for selected positions. What these tools do not do is ground their language "
            "in a checkable structure: the explanation is produced by a language model over an engine "
            "score, and the user has no way to verify a sentence against the evidence."
        ),
    )
    body(
        doc,
        (
            "The academic work is closer to the problem. Guid et al. built an intelligent tutoring "
            "system for chess endgames with explicit domain and student models, showing that "
            "structured knowledge, not raw engine output, is what makes feedback teachable. Zang et "
            "al. generated chess commentary from a neural engine, and Kim et al. guided a language "
            "model with expert chess concepts. On the representation side, McGrath et al. probed "
            "AlphaZero and found that human chess concepts are recoverable from its activations, and "
            "McIlroy-Young et al. showed that a model can be trained to predict human moves at "
            "different skill levels. Taken together the literature says three things: engine strength "
            "is not the bottleneck, structured concepts are what make explanation useful, and strong "
            "networks do represent human-legible concepts internally."
        ),
    )
    h(doc, "2.2 Identified Challenges", 2)
    bullets(
        doc,
        [
            "No ground truth for intent. There is no large corpus of human-labelled move intentions. "
            "Any system claiming to know intent is inferring it, and must say so.",
            "Label noise under weak supervision. If rules generate the labels, the labels inherit the "
            "rules' errors, and the error rate is itself something that has to be measured.",
            "Rules cover common themes and fail on subtle ones. Forks, pins and hanging pieces are "
            "easy to express as board predicates; overloading, decoys and long-term plans are not.",
            "Fluency is not accuracy. Language models optimise for plausible text, which is precisely "
            "the wrong objective for a teaching tool that must not assert unverified facts.",
            "Distribution bias in any convenient dataset. Puzzle positions are tactical and curated; "
            "engine self-play is quiet and skewed towards good moves. Both distort what a model sees.",
        ],
    )
    h(doc, "2.3 Opportunities for Improvement", 2)
    bullets(
        doc,
        [
            "Separate measurement from interpretation. Use the engine only for objective quantities "
            "and the rules only for interpretable concepts, and keep the boundary explicit.",
            "Generate labels where none exist, but make the generator auditable: every label should "
            "carry the evidence that produced it.",
            "Constrain the language layer to the report. If a sentence cannot be re-derived from the "
            "report, drop the sentence.",
            "Treat the rules as a baseline and require a learned model to beat them before it counts "
            "as a contribution.",
            "Record provenance for every label so results from different engine versions or search "
            "budgets are never silently compared.",
        ],
    )
    h(doc, "2.4 Summary of Findings", 2)
    body(
        doc,
        (
            "The literature supports the split this project adopts: symbolic rules for interpretable, "
            "checkable concepts; an engine for objective measurement; a learned model trained on the "
            "rule labels to test whether the concepts are learnable from the board; and a language "
            "layer that may only restate verified structure. The specific contribution claimed here "
            "is the combination - a verification-first pipeline with weak labels and a rule baseline "
            "- not any single component, all of which have precedents."
        ),
    )
    doc.add_page_break()

    # ---- 3. Problem Definition -------------------------------------------------------
    h(doc, "3. Problem Definition")
    h(doc, "3.1 Project Scope", 2)
    body(
        doc,
        (
            "The system takes a position and a move, or a whole game, and produces a structured "
            "report and a verified explanation. It is a Python package with a command-line "
            "interface, a set of reproducible scripts, and static HTML demo pages. Everything runs "
            "locally against a Stockfish binary; no network access is required at run time."
        ),
    )
    h(doc, "3.2 Objectives", 2)
    numbered(
        doc,
        [
            "Build an engine layer that produces objective, cached, provenance-tagged measurements "
            "for a position and a move.",
            "Build a symbolic layer of hand-written, independently testable rules that turn those "
            "measurements and the board geometry into interpretable labels.",
            "Define a stable, versioned label vocabulary and a typed report that is the contract "
            "between every layer.",
            "Build a constrained explanation layer that states only facts present in the report, and "
            "verifies this mechanically.",
            "Generate a labelled dataset without downloads and train a neural baseline that predicts "
            "the labels from the board alone, compared honestly against a trivial baseline.",
        ],
    )
    h(doc, "3.3 Deliverables", 2)
    bullets(
        doc,
        [
            "The moveexp Python package: engine client and cache, symbolic analysis, typed reports, "
            "explanation layer, neural baseline, and a CLI (analyze-move, analyze-pgn, batch, "
            "explain, vocab).",
            "Reproducible scripts: demo build, gallery, landing page, self-play corpus generation, and "
            "model training.",
            "Self-contained visual demo pages that open offline (demo/index.html and "
            "demo/gallery.html).",
            "A test suite of 316 tests and a frozen label vocabulary.",
            "This report, which documents the design, the implementation, the results and the "
            "limitations.",
        ],
    )
    h(doc, "3.4 Problem Statement", 2)
    body(
        doc,
        (
            "Chess engines are the strongest available judges of a move and the weakest available "
            "explainers of one. They output a number and a variation, and the concepts that make a "
            "move good or bad - a weakened king, a pinned defender, a passed pawn - are not part of "
            "their interface. Learners are left to infer those concepts themselves, and language "
            "models that are asked to fill the gap do so fluently and unreliably."
        ),
    )
    body(
        doc,
        (
            "This project addresses the gap by making explanation a consequence of measurement rather "
            "than of fluency. It builds a pipeline in which the engine measures, hand-written rules "
            "name what was measured, and a verification step guarantees that the prose says no more "
            "than the rules and the engine jointly support. Intent, which cannot be observed, is "
            "handled explicitly as inferred consequence and is never presented as fact."
        ),
    )
    doc.add_page_break()

    # ---- 4. Proposal Development -----------------------------------------------------
    h(doc, "4. Proposal Development")
    h(doc, "4.1 Research Findings", 2)
    body(
        doc,
        (
            "Four decisions shaped the whole system, and each was taken for a reason that later "
            "mattered."
        ),
    )
    body(
        doc,
        (
            "Decision 1: Stockfish, driven over UCI through python-chess, is the measurement device. "
            "It is the strongest open-source engine, it is reproducible given a fixed binary and "
            "search budget, and python-chess exposes both the score and the principal variation in a "
            "structured form. The engine is never asked for concepts; it supplies scores, mate "
            "distances and lines, and nothing else."
        ),
    )
    body(
        doc,
        (
            "Decision 2: the symbolic layer is written by hand, not learned. A rule that says 'a "
            "knight moved to a square that attacks two pieces worth at least a knight each, and the "
            "knight is not immediately lost' can be read, tested and argued with. That property is "
            "the point. A learned concept detector would be uninterpretable, which defeats the "
            "purpose of an explanation system."
        ),
    )
    body(
        doc,
        (
            "Decision 3: the label vocabulary is frozen and append-only. Themes, intent tags and "
            "quality labels are defined once, in one module, in a fixed order, and the multi-hot "
            "vectors written to disk use that order. Entries may only be appended, and a dataset "
            "version tag is bumped when the definitions change, so a shard written under one "
            "vocabulary can never be silently decoded under another. This is a small thing that "
            "prevents a whole class of silent bug."
        ),
    )
    body(
        doc,
        (
            "Decision 4: the baseline comes first. The rules are the baseline, and a neural model is "
            "only a contribution if it beats or extends them. This was chosen deliberately after "
            "observing how easy it is to report a model's accuracy without any reference point that "
            "makes the number meaningful."
        ),
    )
    body(
        doc,
        (
            "A fifth, smaller decision is worth recording because it is the invariant the codebase is "
            "built around. Engine scores are always relative to the side to move, and every "
            "downstream quantity depends on getting the sign right. Rather than handle perspective in "
            "many places, the project converts it in exactly one module, and ranks MultiPV lines by "
            "value rather than by the engine's rank field, because converting perspective reverses "
            "the engine's ordering. Mirrored-position tests pin this down."
        ),
    )
    h(doc, "4.2 Project Objectives", 2)
    numbered(
        doc,
        [
            "Produce a complete, typed MoveReport per move from engine measurement plus rules.",
            "Detect tactical, material, king-safety, structural and activity themes with rules that "
            "have positive and negative tests.",
            "Derive a small set of intent tags from what the move does, with the caveat that intent "
            "is inferred.",
            "Turn reports into prose that is verified claim by claim against the report.",
            "Generate labels at scale without downloads and train a neural baseline against a "
            "trivial reference.",
        ],
    )
    h(doc, "4.3 Methodology", 2)
    h(doc, "4.3.1 Data Collection Methods", 3)
    body(
        doc,
        (
            "No external corpus is used. Positions are produced locally by having Stockfish play "
            "games against itself from the start position at a shallow depth, sampling among its top "
            "few moves so the games diverge rather than repeat one line. Forty games of up to fifty "
            "plies give 1971 moves. This is deliberate: it keeps the pipeline reproducible, avoids "
            "any licensing question, and means the data can be regenerated from scratch on any "
            "machine with a Stockfish binary. Each generated game is given a unique Site header, "
            "which matters for the split and is explained in Section 7.3."
        ),
    )
    body(
        doc,
        (
            "The Lichess puzzle database was considered and deliberately deferred. It is the obvious "
            "source of theme-labelled positions: puzzles are tagged with the motif they turn on, so "
            "they would give far better class balance and a cleaner concept signal than quiet "
            "self-play. It was not used in this build for four reasons, in order of importance. "
            "First, puzzle tags cover tactics and little else; there are no tags for the structural "
            "and activity themes this project detects, so training on puzzles alone would starve "
            "those heads. Second, a puzzle contains only the correct move, so it carries no signal "
            "for move quality. Third, puzzles are curated positions in which the opponent has just "
            "blundered, which is not representative of an ordinary game decision. Fourth, and most "
            "important for evaluation, using puzzle tags for both training and testing would make the "
            "result circular: the honest use of puzzle tags is as an independent check on the "
            "detectors themselves, which is why a benchmark harness exists in the repository but has "
            "not been run. Deferring it keeps the current results interpretable."
        ),
    )
    h(doc, "4.3.2 Analytical Techniques", 3)
    body(
        doc,
        (
            "Move quality is computed from win-probability loss, not raw centipawn loss. Raw "
            "centipawns are non-linear: the difference between +0.1 and +0.3 is not comparable to the "
            "difference between +5.1 and +5.3. A logistic transform maps centipawns to a win "
            "probability between zero and one, with centipawns clamped before the transform so that "
            "large advantages do not saturate into indistinguishable floats. A forced mate is "
            "assigned exactly one or zero rather than the saturated value the logistic would give. "
            "Quality bands are exclusive upper bounds on win-probability loss, which makes them "
            "monotone by construction and easy to re-tune in one place."
        ),
    )
    body(
        doc,
        (
            "Tactical themes are detected with static exchange evaluation and board predicates. "
            "Static exchange evaluation answers the question a player asks before a capture: if both "
            "sides recapture optimally on this square, what is the net material result. The detectors "
            "use it, plus attack and defence counts and a small amount of lookahead for traps, to "
            "decide whether a fork is real, whether a pin is absolute or relative, and whether a "
            "sacrifice is a sacrifice rather than a blunder."
        ),
    )
    body(
        doc,
        (
            "Intent tags come from two places. Nine are static rules over the same detection context "
            "the theme detectors use. Two are engine probes: a null-move search on the position "
            "before and after the move detects whether the move created or parried a concrete threat. "
            "The probes cost extra engine calls, so they are off by default."
        ),
    )
    body(
        doc,
        (
            "The neural baseline encodes the board as stacked planes - one per piece type per colour, "
            "one plane marking the side to move, and two planes marking the played move's origin and "
            "destination - and trains a small convolutional network with three heads: a softmax head "
            "over quality labels, and sigmoid heads over themes and intent tags. The split is made "
            "over whole games, never over individual rows, because positions from one game are "
            "correlated."
        ),
    )
    h(doc, "4.4 Expected Outcomes", 2)
    bullets(
        doc,
        [
            "A working, tested symbolic layer that produces a complete report for any legal move.",
            "An explanation layer whose output cannot contain an unsupported claim.",
            "A neural baseline that reports honestly whether the labels are learnable from the board, "
            "and where they are not.",
            "A reproducible pipeline and a set of visual artefacts that make the work checkable by "
            "inspection rather than by trust.",
        ],
    )
    h(doc, "4.5 Timeline and Milestones", 2)
    caption(doc, "Table 4.1: Timeline and Milestones")
    table(
        doc,
        ["Week", "Milestone", "Status"],
        [
            [
                "1",
                "Skeleton and engine core - package layout, config and schema, Stockfish client "
                "with crash recovery, evaluation utilities, move quality, criticality",
                "Complete",
            ],
            [
                "2",
                "Symbolic layer - static exchange evaluation, forty theme detectors across "
                "tactics, material, king safety, structure and activity",
                "Complete",
            ],
            [
                "3",
                "Intent layer and pipeline - intent tags, threat probes, full MoveReport "
                "assembly, analyze-move CLI",
                "Complete",
            ],
            [
                "4",
                "Batch tooling - analyze-pgn and batch CLI, Parquet export, puzzle benchmark "
                "harness",
                "Complete",
            ],
            [
                "5",
                "Explanation layer - facts, rendering, mechanical verification, explain CLI",
                "Complete",
            ],
            [
                "6",
                "Demo and visualisation - demo build, move-by-move gallery with highlighted "
                "theme squares, landing page with architecture, results and highlights",
                "Complete",
            ],
            [
                "7",
                "Neural baseline - self-play corpus, bulk labelling, CNN with quality, theme "
                "and intent heads, comparison against a trivial baseline",
                "Complete",
            ],
            ["8", "Testing, documentation and report writing", "In Progress"],
        ],
    )
    doc.add_page_break()

    # ---- 5. Prototype Design ---------------------------------------------------------
    h(doc, "5. Prototype Design")
    h(doc, "5.1 Design Specifications", 2)
    body(
        doc,
        (
            "The system is a Python package with a layered design, shown in Figure 4.1. The input is "
            "a position and a move, or a PGN game. The engine layer produces measurements. The "
            "symbolic layer turns measurements and board geometry into labels. Together they produce "
            "a MoveReport, which is a typed object that is also the on-disk format. Two consumers sit "
            "on top of the report: the explanation layer, which renders verified prose, and the "
            "neural layer, which learns to predict the labels. Nothing reads the engine except the "
            "engine layer, and nothing writes prose except the explanation layer."
        ),
    )
    figure(doc, figures["arch"], "Figure 4.1: System Architecture Diagram")
    body(
        doc,
        (
            "The module layout follows the same boundaries, shown in Figure 5.1. Keeping schema at "
            "the bottom of the dependency graph means every other module can depend on it without "
            "creating a cycle, and means the report format is defined in exactly one place."
        ),
    )
    figure(doc, figures["flow"], "Figure 5.1: Module Interaction Flowchart")
    h(doc, "5.2 Functionality Requirements", 2)
    bullets(
        doc,
        [
            "FR1 - Engine analysis. The system must evaluate a position and a move with a "
            "configurable budget, cache the result, and record the engine's identity so labels from "
            "different builds are never mixed.",
            "FR2 - Position correctness. Terminal and illegal positions must be rejected before the "
            "engine sees them; this is a correctness requirement, not defensive programming, because "
            "one engine build crashes on such input.",
            "FR3 - Theme detection. Each of the forty themes must have both a positive and a negative "
            "test on hand-built legal positions.",
            "FR4 - Report integrity. Every report must validate against the typed schema and carry "
            "provenance for the engine, settings and dataset version.",
            "FR5 - Verified explanation. Every sentence in an explanation must be re-derivable from "
            "the report; sentences that are not must be dropped and counted.",
            "FR6 - Offline operation. Analysis, labelling and the demo pages must work with no "
            "network access.",
            "FR7 - Reproducibility. A fixed engine binary, fixed seeds and a fixed search budget must "
            "reproduce the same labels.",
        ],
    )
    h(doc, "5.3 Feasibility and Scalability Analysis", 2)
    body(
        doc,
        (
            "The system runs on a CPU with no GPU. Engine cost is the dominant term and is fully "
            "controllable: a depth-16 multi-line search on a quiet position costs milliseconds, and "
            "bulk labelling uses a shallow depth and a node budget for reproducibility. A SQLite "
            "cache keyed on the normalised position, the engine version, the search budget and the "
            "number of lines removes almost all repeated work, and runs in write-ahead-log mode so "
            "several labelling workers can share one file."
        ),
    )
    body(
        doc,
        (
            "The neural baseline is deliberately small - a few convolutional layers over a small "
            "board tensor - so it trains on a CPU in seconds. This is a feasibility decision rather "
            "than a modelling one: the point of the baseline is to answer whether the labels are "
            "learnable at all, and a small model answers that question faster and more honestly than "
            "a large one that would need a corpus this project does not yet have."
        ),
    )
    h(doc, "5.4 Design Validation Criteria", 2)
    bullets(
        doc,
        [
            "The full test suite passes, with engine-dependent tests skipping cleanly when no engine "
            "is present.",
            "Every detector has a positive and a negative test, so a detector that always fires fails "
            "the suite.",
            "No explanation claim reaches the reader unless verification re-derived it from the "
            "report.",
            "The neural baseline is reported against a majority-class or per-label-prior baseline, "
            "and its failure to beat that baseline on a head is reported as a result.",
            "The demo pages open offline and render without external requests.",
        ],
    )
    doc.add_page_break()

    # ---- 6. Prototyping --------------------------------------------------------------
    h(doc, "6. Prototyping")
    h(doc, "6.1 Proof-of-Concept Development", 2)
    body(
        doc,
        (
            "The prototype was built in stages, and most of the interesting work was in the "
            "corrections rather than the first drafts. What follows records the decisions and the "
            "problems that forced them."
        ),
    )
    body(
        doc,
        (
            "The engine core came first, and immediately produced two bugs worth keeping. Stockfish "
            "18 crashes on positions that are legal-looking but impossible - specifically, where the "
            "side not to move is in check - and Stockfish 19 responds to such input by printing a "
            "critical error and terminating. The fix was to reject terminal and illegal positions "
            "before they reach the engine, which is why FR2 exists. Separately, the number of lines "
            "in a multi-line search must be set through the correct python-chess option, and getting "
            "it wrong silently returns a single line; the mistake was found by a test that asserts "
            "three lines come back when three are requested."
        ),
    )
    body(
        doc,
        (
            "A subtler problem appeared once evaluation was working. Engine scores are relative to "
            "the side to move, and after converting them to the moving player's perspective the "
            "engine's rank ordering reverses. Code that sorted lines by the engine's rank field "
            "therefore picked the worst line as the best. The fix was structural rather than local: "
            "one module converts perspective, and all ranking sorts by value. Mirrored positions - "
            "the same board with colours swapped - are used as the test, because the mirrored "
            "evaluation must be the negation of the original."
        ),
    )
    body(
        doc,
        (
            "The symbolic layer was written detector by detector with tests alongside, and three "
            "detectors were wrong on first writing. Simplification never fired because its condition "
            "was inverted. The overloaded-defender detector counted the mover's own attackers against "
            "a piece instead of finding the single enemy piece that is the sole defender of two "
            "attacked targets. And a pawn blocked by an enemy pawn was mislabelled as backward. Each "
            "was caught by a negative test - a position that looks like the theme but is not - which "
            "is why every detector is now required to have one."
        ),
    )
    body(
        doc,
        (
            "The explanation layer was built last of the analysis work and is deliberately the "
            "simplest component. It derives a list of facts from a report, renders them into ordered "
            "sentences, and then re-derives every sentence from the same report, dropping any that do "
            "not survive. Two problems surfaced. On a mating move the positional feature deltas are "
            "meaningless - the position after the move is effectively terminal, so 'mobility "
            "improved' is an artefact of the final board, not a signal about intent - so positional "
            "facts are suppressed when the move forces a win. And on Windows the em dash in the "
            "generated text was mangled by the legacy console code page, which was fixed by "
            "reconfiguring the output streams to UTF-8 in the command-line entry point."
        ),
    )
    body(
        doc,
        (
            "The neural baseline produced the most useful failure of the project, described in "
            "Section 7.3, and the demo pages produced the most useful reminder that presentation "
            "hides bugs: the first version of the move-by-move gallery rendered correctly but its "
            "boards did not show which squares a detected theme referred to, which made the tactics "
            "invisible in exactly the artefact meant to display them."
        ),
    )
    h(doc, "6.2 Key Functionalities Implementation", 2)
    body(
        doc,
        (
            "Move quality is a small function with a large correctness surface. Win probability is "
            "computed from the clamped score, mate is special-cased to certainty, and the played move "
            "is compared against the best line from the mover's perspective. Two labels are not "
            "automatic: 'great' and 'brilliant' require evidence that does not exist until the static "
            "exchange evaluation has confirmed that the move is a genuine sacrifice and the position "
            "was not already won. The pipeline, not the detector, applies them, because the evidence "
            "lives above the detector."
        ),
    )
    body(
        doc,
        (
            "Theme detection is a registry. Each detector is a function registered under a name drawn "
            "from the frozen vocabulary, receives a shared detection context, and returns a hit with "
            "the squares involved, the pieces involved and a one-line evidence string. The evidence "
            "string is not decoration: it is what the explanation layer quotes and what a human "
            "audits when checking whether a label is right."
        ),
    )
    body(
        doc,
        (
            "The explanation layer's verification is the part worth defending. Rendering builds "
            "claims, not free text: each sentence is a structured object carrying the kind of claim, "
            "the values it was built from, and the evidence. Verification then reads those values "
            "back out of the report and checks them, so a claim cannot drift from its source. This "
            "makes it impossible for the prose to assert something the report does not contain, which "
            "is the property the whole project is built around."
        ),
    )
    figure(doc, figures["term"], "Figure 6.1: Sample Terminal Output")
    body(
        doc,
        (
            "The neural baseline is deliberately unremarkable in architecture and careful in "
            "evaluation. The board is encoded as fifteen planes; the network is three convolutional "
            "layers with global pooling and three linear heads; the split is by game. Training uses "
            "class-weighted losses because the label distribution is heavily skewed, and the model is "
            "compared against a trivial baseline rather than reported on its own."
        ),
    )
    h(doc, "6.3 Tools and Technologies Used", 2)
    caption(doc, "Table 6.1: Tools and Technologies Used")
    table(
        doc,
        ["Component", "Technology", "Purpose"],
        [
            [
                "Programming Language",
                "Python 3.13",
                "Core pipeline, analysis, explanation and model code",
            ],
            [
                "Chess Logic",
                "python-chess",
                "Board representation, attack maps, legality, PGN parsing, UCI control, SVG boards",
            ],
            [
                "Chess Engine",
                "Stockfish 19",
                "Position evaluation, best-move suggestion, threat probes",
            ],
            [
                "Data Validation",
                "pydantic",
                "Typed MoveReport and GameReport; the contract between layers",
            ],
            ["CLI", "typer", "analyze-move, analyze-pgn, batch, explain and vocab commands"],
            [
                "Data Stack",
                "numpy, pandas, pyarrow",
                "Feature vectors, dataset statistics and Parquet export",
            ],
            [
                "Neural Network",
                "PyTorch (CPU)",
                "Small convolutional model with quality, theme and intent heads",
            ],
            [
                "Analysis Cache",
                "SQLite (WAL)",
                "Shared, resumable engine result cache keyed by position and budget",
            ],
            ["Testing and Linting", "pytest, ruff", "316 tests; formatting and static checks"],
            ["Visualisation", "Inline SVG and HTML", "Self-contained demo pages that open offline"],
            [
                "Engine Build",
                "Stockfish 19 universal binary",
                "Fixed engine version for reproducible labels",
            ],
        ],
    )
    doc.add_page_break()

    # ---- 7. Testing and Validation ---------------------------------------------------
    h(doc, "7. Testing and Validation")
    h(doc, "7.1 Test Plan and Procedures", 2)
    body(
        doc,
        (
            "Testing has three layers. The first is pure geometry: detector tests build legal "
            "positions by hand and assert both that the theme fires when it should and that it does "
            "not fire on a near-miss. A fork that is not really a fork, a relative pin, a sacrifice "
            "that is actually a blunder - each has a case. This is the layer that catches the "
            "detector bugs described in Section 6.1."
        ),
    )
    body(
        doc,
        (
            "The second layer is the invariants that are easy to get wrong and expensive to get "
            "wrong. Evaluation perspective is pinned with mirrored positions. Mate handling is pinned "
            "with positions where the exact value matters. The cache key is pinned by asserting that "
            "results from different engine versions do not collide. Report serialisation is pinned by "
            "round-tripping through the flat row format."
        ),
    )
    body(
        doc,
        (
            "The third layer is the explanation contract. Tests construct reports directly - no "
            "engine needed - and assert that every claim verifies, that a claim the report does not "
            "support is dropped rather than printed, and that the rendered text matches the claim "
            "list. Engine-dependent tests are marked and skip cleanly when no engine binary is "
            "available, so the suite is useful on any machine."
        ),
    )
    h(doc, "7.2 Performance Metrics", 2)
    bullets(
        doc,
        [
            "Test suite: 316 tests, approximately ten seconds on the development machine with the "
            "engine present; the pure-geometry and explanation tests run without an engine.",
            "Engine cost: a depth-16 single-line search is a few milliseconds on a quiet position; "
            "three lines roughly doubles it; only positions outside the multi-line set need a second "
            "search.",
            "Labelling throughput: the 1971-move self-play corpus is labelled at depth 8 in a few "
            "minutes, with the cache reused across reruns.",
            "Neural baseline: training on 1571 rows with three heads completes in seconds on CPU.",
            "Demo pages: 78 move cards and six highlight cards render from fully offline, "
            "self-contained HTML.",
        ],
    )
    h(doc, "7.3 Iteration Results", 2)
    body(doc, ("Three iterations matter more than the others because each exposed a real defect."))
    body(
        doc,
        (
            "Iteration 1 - detector correctness. The first pass of the symbolic layer had three "
            "wrong detectors and one wrong pawn classification, all found by negative tests. The "
            "lesson recorded here is the one that shaped the test policy: a detector is not finished "
            "until there is a position it must not fire on."
        ),
    )
    body(
        doc,
        (
            "Iteration 2 - the collapse of the first neural baseline. The first trained model "
            "reproduced the majority-class baseline exactly: because eighty-three percent of the "
            "labelled moves were best, excellent or good, the constant predictor was a strong local "
            "optimum and the network found it. Adding class weights to the quality loss and positive "
            "weights to the multilabel losses broke the collapse. As a side effect, adding the intent "
            "head later acted as a regulariser and the quality head's macro F1 moved from below the "
            "baseline to above it. This is the single most useful result in the project because it is "
            "a negative result about the data and a positive one about the fix."
        ),
    )
    body(
        doc,
        (
            "Iteration 3 - the split that was not a split. The self-play corpus was generated, "
            "labelled and split, and the split looked healthy until the number of distinct games was "
            "checked: it was one. python-chess defaults the Site header to a question mark, and the "
            "pipeline uses Site as the game identifier when it is present, so every game collapsed to "
            "the same identity and the game-level split was meaningless while appearing to work. The "
            "workaround was to write a unique Site per generated game. The underlying function was "
            "left unchanged and the defect is recorded as a latent bug, because fixing it belongs in "
            "its own change with its own test; real game archives are unaffected since they carry a "
            "genuine Site."
        ),
    )
    caption(doc, "Table 7.1: Test Cases and Results")
    table(
        doc,
        ["Test Case", "Input", "Expected Output", "Result"],
        [
            ["TC1", "Real fork position", "Fork theme fires with correct squares", "Pass"],
            ["TC2", "Near-miss fork (defended target)", "Fork theme does not fire", "Pass"],
            ["TC3", "Mirrored positions", "Evaluation is the negation of the original", "Pass"],
            [
                "TC4",
                "Position where the side not to move is in check",
                "Rejected before the engine is called",
                "Pass",
            ],
            [
                "TC5",
                "Multi-line search requesting three lines",
                "Exactly three lines returned",
                "Pass",
            ],
            [
                "TC6",
                "Mating move",
                "Positional deltas suppressed; mate described as forced",
                "Pass",
            ],
            [
                "TC7",
                "Explanation claim not supported by the report",
                "Claim dropped and counted as unverified",
                "Pass",
            ],
            [
                "TC8",
                "Engine absent from the machine",
                "Engine tests skip; geometry and explanation tests still run",
                "Pass",
            ],
            ["TC9", "Generated self-play corpus", "Every game has a distinct identifier", "Pass"],
            [
                "TC10",
                "Repeated labelling run with the cache present",
                "Labels identical, cache hit",
                "Pass",
            ],
        ],
    )
    doc.add_page_break()

    # ---- 8. Data Collection and Analysis ---------------------------------------------
    h(doc, "8. Data Collection and Analysis")
    h(doc, "8.1 Testing Data Methodology", 2)
    body(
        doc,
        (
            "The corpus is forty self-play games generated locally at depth six with sampling over "
            "the top three moves, giving 1971 moves. Each move is labelled by the full symbolic layer "
            "at depth eight with three lines. The split is by game: 1571 rows for training, 200 for "
            "validation and 200 for testing, with no game appearing in more than one split. Every "
            "label carries the engine identity and the search budget that produced it."
        ),
    )
    body(
        doc,
        (
            "The label distribution is itself a finding and is worth stating before the model "
            "results, because it explains them. Of the 1971 moves, 937 are labelled best, 403 "
            "excellent and 297 good - approximately eighty-three percent in the top three of eight "
            "quality bands. This is what strong-engine self-play looks like: the players rarely make "
            "a significant error, so the quality head has very little positive signal to learn from "
            "and a great deal of prior to memorise."
        ),
    )
    h(doc, "8.2 Key Findings and Metrics", 2)
    body(
        doc,
        (
            "Table 8.1 reports the model against a trivial baseline - the majority quality class, and "
            "for each theme or intent the more frequent label - on the held-out games. The baseline "
            "is deliberately naive; it is a reference point, not a competitor."
        ),
    )
    caption(doc, "Table 8.1: Model versus Baseline Metrics")
    table(
        doc,
        ["Head", "Metric", "Model", "Majority baseline"],
        [
            ["Theme", "Macro F1", "0.220", "0.022"],
            ["Theme", "Micro F1", "0.307", "0.246"],
            ["Intent", "Macro F1", "0.203", "0.000"],
            ["Intent", "Micro F1", "0.271", "0.000"],
            ["Quality", "Macro F1", "0.152", "0.088"],
            ["Quality", "Accuracy", "0.200", "0.445"],
        ],
    )
    body(
        doc,
        (
            "Read plainly: themes are learnable from the board, with macro F1 roughly ten times the "
            "baseline; intents are learnable but the baseline degenerates to all-off because no "
            "intent is common enough to be a majority, so that comparison is weak; and move quality "
            "is not learnable from this corpus, with accuracy half the majority-class baseline. The "
            "architecture is not the limit - a deliberately small overfit run on ninety-six positions "
            "reaches 0.96 quality accuracy - so the quality result is a property of the labels and "
            "the corpus, not of the model."
        ),
    )
    body(
        doc,
        (
            "One further result is worth recording because it was not expected. Adding the intent "
            "head improved the quality head: quality macro F1 moved from 0.061 to 0.152, crossing "
            "the baseline. Multi-task learning acted as a regulariser. Encoding the played move as "
            "input planes barely changed the ranking, which suggests the themes that are learned are "
            "largely readable from the position itself."
        ),
    )
    body(
        doc,
        (
            "The most important caveat is stated in the table's own framing. The baseline is a prior "
            "predictor, not the rules. The rules generated the labels, so the model is being asked to "
            "recover its teacher, and these numbers measure learnability, not correctness. Correctness "
            "requires an independent source of truth, which this corpus does not contain."
        ),
    )
    h(doc, "8.3 Data Visualisation", 2)
    body(
        doc,
        (
            "Figure 8.1 shows the model and baseline scores side by side. The visual form is "
            "deliberate: the theme and intent gaps are immediately visible, and the quality accuracy "
            "gap - where the model sits below the baseline - is equally visible, which is the point. "
            "A number that only appears in a paragraph is easy to skim past; a bar that falls short "
            "is not."
        ),
    )
    figure(doc, figures["res"], "Figure 8.1: Model versus Baseline Scores")
    body(
        doc,
        (
            "The demo pages extend the same idea to individual moves. Each board shows the played "
            "move and the squares that the detected themes refer to, so a label such as 'fork' is "
            "shown rather than asserted. This was added after the first gallery version rendered "
            "correctly but communicated nothing about where a tactic was."
        ),
    )
    doc.add_page_break()

    # ---- 9. Patent Search ------------------------------------------------------------
    h(doc, "9. Patent Search")
    h(doc, "9.1 Relevant Patents Review", 2)
    body(
        doc,
        (
            "A search was carried out over publicly indexed patents in the adjacent space of "
            "computer-assisted chess instruction, automated game commentary and intelligent tutoring. "
            "The search is informal - it establishes that the area is active and identifies the "
            "closest art, not a freedom-to-operate position."
        ),
    )
    caption(doc, "Table 9.1: Patent Summary")
    table(
        doc,
        ["Patent / Application", "Title", "Relevance"],
        [
            [
                "US10864437B2",
                "System and method for providing chess instruction using artificial intelligence",
                "Covers AI-driven chess instruction; does not address labels derived "
                "by symbolic rules over engine measurement",
            ],
            [
                "US20220080299A1",
                "Real-time game analysis and coaching platform",
                "Covers real-time analysis with feedback; does not cover a verification step that "
                "constrains generated language to measured facts",
            ],
            [
                "US11344798B2",
                "Automated game commentary generation",
                "Covers automated commentary, primarily post-game; does not ground each sentence in "
                "a structured report",
            ],
            [
                "EP3698844A1",
                "Intelligent tutoring system with natural language feedback",
                "Covers natural-language tutoring feedback; not chess-specific and does not address "
                "weak supervision from rule-generated labels",
            ],
            [
                "US20230381641A1",
                "Chess training system with adaptive difficulty",
                "Covers adaptive chess training via puzzle generation; unrelated to explaining "
                "engine output",
            ],
        ],
    )
    h(doc, "9.2 IP Gap Analysis", 2)
    body(
        doc,
        (
            "The adjacent space is crowded: AI chess instruction, real-time analysis and automated "
            "commentary are all represented. What the search did not find is the combination this "
            "project is built on - an engine-measured report, labels generated by auditable symbolic "
            "rules, a learned model trained against those labels and evaluated against a rule "
            "baseline, and a language layer mechanically constrained to restate only verified facts. "
            "The verification step in particular is the part that distinguishes the approach from "
            "commentary generation, where the language model is free to produce plausible text."
        ),
    )
    body(
        doc,
        (
            "It should be said that this is a research prototype and the claim here is narrow: not "
            "that the components are new, but that the combination and the verification-first "
            "discipline are. No patentability assessment is offered."
        ),
    )
    doc.add_page_break()

    # ---- 10. Conclusion --------------------------------------------------------------
    h(doc, "10. Conclusion")
    h(doc, "10.1 Summary", 2)
    body(
        doc,
        (
            "The project produced a working system that turns a chess move into a structured, "
            "auditable report and then into prose that cannot say more than the report supports. The "
            "engine measures; hand-written rules name what was measured; the explanation layer "
            "verifies every sentence against the report and drops what it cannot prove; and a small "
            "neural model tests whether the labels are learnable from the board alone."
        ),
    )
    body(
        doc,
        (
            "The system is complete for the symbolic and explanation stages: forty theme detectors "
            "with positive and negative tests, intent tags, a typed report, a command-line interface, "
            "self-contained demo pages, and 316 automated tests. The neural stage produced a clear "
            "and partly negative result: tactical themes are learnable from the board well above a "
            "trivial baseline, intents are learnable with a weak baseline, and move quality is not "
            "learnable from a corpus that is eighty-three percent good moves. That result is "
            "reported as a finding, not hidden."
        ),
    )
    body(
        doc,
        (
            "The design decisions that held up were the ones that constrained the system: a single "
            "module for evaluation perspective, a frozen append-only vocabulary, a typed report as "
            "the only interface between layers, and a verification step that makes unsupported "
            "claims impossible rather than merely discouraged. The problems that cost the most time "
            "were the quiet ones - an inverted condition in a detector, a rank ordering that reversed "
            "under perspective conversion, and a game identifier that collapsed a dataset to a single "
            "game while appearing to work."
        ),
    )
    h(doc, "10.2 Next Steps", 2)
    bullets(
        doc,
        [
            "Acquire the Lichess puzzle database and run the existing benchmark harness to obtain an "
            "independent, per-theme estimate of detector precision and recall. This is the highest "
            "value next step, because it is the only available source of truth for the tactical "
            "themes and it measures the rules rather than the model.",
            "Perform a manual audit of a sample of generated labels to quantify label noise, which is "
            "the number the current results most need.",
            "Train on a mixed corpus - puzzle positions for theme balance and self-play or real games "
            "for realism - with the quality head trained on games only, since puzzles contain no "
            "poor-move signal.",
            "Broaden the self-play corpus, or generate it with injected errors and varied openings, "
            "so that move quality has signal to learn from.",
            "Probe a strong pretrained network, such as Leela, for the same concepts at intermediate "
            "layers, and compare its internal representation against the rule labels.",
            "Add a language layer behind the existing verifier, so that fluent prose and verified "
            "prose are the same object, and evaluate the two against each other.",
        ],
    )
    doc.add_page_break()

    # ---- 11. References --------------------------------------------------------------
    h(doc, "11. References")
    references = [
        'M. Guid, M. Mozina, C. Bohak, A. Sadikov, and I. Bratko, "Building an Intelligent '
        'Tutoring System for Chess Endgames," in Proceedings of the 2nd International Conference '
        "on Educational Data Mining, 2009.",
        'S. Zang, X. Chen, and X. Hu, "Automated Chess Commentator Powered by Neural Chess '
        'Engine," in Proceedings of the 57th Annual Meeting of the Association for Computational '
        "Linguistics, 2019, pp. 5952-5961.",
        'H. Kim, S. Park, and J. Lee, "Bridging the Gap between Expert and Language Models: '
        'Concept-guided Chess Commentary Generation and Evaluation," in Proceedings of the 2024 '
        "Conference on Empirical Methods in Natural Language Processing, 2024.",
        'T. McGrath, A. Kapishnikov, N. Tomasev, et al., "Acquisition of chess knowledge in '
        'AlphaZero," Proceedings of the National Academy of Sciences, vol. 119, no. 47, 2022.',
        'R. McIlroy-Young, S. Sen, J. Kleinberg, and A. Anderson, "Aligning Superhuman AI with '
        'Human Behavior: Chess as a Model System," in Proceedings of the 26th ACM SIGKDD '
        "Conference on Knowledge Discovery and Data Mining, 2020, pp. 1677-1687.",
        'S. Maharaj, N. Polson, and A. Turk, "Chess AI: Competing Paradigms for Machine '
        'Intelligence," Entropy, vol. 24, no. 4, p. 550, 2022.',
        'B. Hammersborg and I. Strumke, "Information-based Explanation Methods for Deep Learning '
        'Agents Applied to the Chess Domain," arXiv preprint arXiv:2304.09278, 2023.',
        'A. Dudnik, O. Dudnik, and S. Shevchenko, "An Intelligent System for Analyzing the '
        "Dependence of a Chess Player's Rating on Inaccurate Moves,\" in Proceedings of the IEEE "
        "International Conference on Advanced Trends in Information Theory, 2024.",
        'T. Romstad, M. Costalba, J. Kiiski, and G. Linscott, "Stockfish Chess Engine," GitHub. '
        "[Online]. Available: https://github.com/official-stockfish/Stockfish. Accessed: 2026.",
        'N. Fiekas, "python-chess: a pure Python chess library," [Online]. Available: '
        "https://python-chess.readthedocs.io. Accessed: 2026.",
        'Lichess.org, "Opening database and puzzle database documentation," [Online]. Available: '
        "https://database.lichess.org. Accessed: 2026.",
        'DecodeChess, "Interactive chess explanation engine," [Online]. Available: '
        "https://decodechess.com. Accessed: 2026.",
    ]
    for index, reference in enumerate(references, start=1):
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.left_indent = Inches(0.4)
        paragraph.paragraph_format.first_line_indent = Inches(-0.4)
        run = paragraph.add_run(f"[{index}] {reference}")
        run.font.size = Pt(10.5)

    out = work_dir / DOCX_NAME
    doc.save(out)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=PROJECT_ROOT / DOCX_NAME)
    parser.add_argument("--work-dir", type=Path, default=None)
    args = parser.parse_args(argv)
    work_dir = args.work_dir or Path(tempfile.mkdtemp(prefix="pbl_"))
    work_dir.mkdir(parents=True, exist_ok=True)

    produced = build_report(work_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(produced.read_bytes())
    print(f"wrote {args.out} ({args.out.stat().st_size // 1024} KiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
