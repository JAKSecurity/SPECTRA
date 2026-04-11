import re
import sys

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


# --- Color palette ---
NAVY = HexColor("#0b1d3a")
TEAL = HexColor("#1a7a6d")
STEEL = HexColor("#3d5a80")
MUTED = HexColor("#666666")
LIGHT_GRAY = HexColor("#f0f2f5")
DARK_TEXT = HexColor("#1a1a1a")
LINK_COLOR = HexColor("#1a7a6d")

# Section heading colors — each section gets its own accent
SECTION_COLORS = {
    "Executive Summary": NAVY,
    "Policy & Compliance Updates": HexColor("#b5343e"),
    "Publications & Standards": HexColor("#2a6496"),
    "Threats & Incidents": HexColor("#c44900"),
    "AI & Agentic Developments": HexColor("#6a4c93"),
    "Legislative Highlights": HexColor("#3a7d44"),
    "Upcoming Conferences": STEEL,
}


class BannerFlowable(Flowable):
    """A colored banner block for the document header."""

    def __init__(self, width, height, color, title, subtitle, blurb):
        super().__init__()
        self.banner_width = width
        self.banner_height = height
        self.color = color
        self.title = title
        self.subtitle = subtitle
        self.blurb = blurb

    def wrap(self, available_width, available_height):
        return self.banner_width, self.banner_height

    def draw(self):
        self.canv.saveState()
        # Background
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.banner_width, self.banner_height, fill=1, stroke=0)
        # Title
        self.canv.setFillColor(white)
        self.canv.setFont("Helvetica-Bold", 28)
        self.canv.drawString(24, self.banner_height - 40, self.title)
        # Subtitle
        self.canv.setFont("Helvetica", 11)
        self.canv.drawString(24, self.banner_height - 60, self.subtitle)
        # Blurb
        self.canv.setFillColor(HexColor("#c0d0e0"))
        self.canv.setFont("Helvetica", 9)
        # Word-wrap blurb to ~90 chars per line
        words = self.blurb.split()
        line = ""
        y = self.banner_height - 82
        for word in words:
            test = f"{line} {word}".strip()
            if len(test) > 95:
                self.canv.drawString(24, y, line)
                y -= 13
                line = word
            else:
                line = test
        if line:
            self.canv.drawString(24, y, line)
        self.canv.restoreState()


class SectionHeadingFlowable(Flowable):
    """A colored bar behind the section heading text."""

    def __init__(self, width, text, color):
        super().__init__()
        self.bar_width = width
        self.text = text
        self.color = color

    def wrap(self, available_width, available_height):
        return self.bar_width, 28

    def draw(self):
        self.canv.saveState()
        # Colored bar
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.bar_width, 28, fill=1, stroke=0)
        # White text
        self.canv.setFillColor(white)
        self.canv.setFont("Helvetica-Bold", 14)
        self.canv.drawString(10, 8, self.text)
        self.canv.restoreState()


def _fix_encoding(text: str) -> str:
    """Fix common UTF-8 mojibake."""
    replacements = {
        "\u00e2\u20ac\u201c": "\u2014",
        "\u00e2\u20ac\u201d": "\u2014",
        "\u00e2\u20ac\u2122": "\u2019",
        "\u00e2\u20ac\u0153": "\u201c",
        "\u00e2\u20ac\u009d": "\u201d",
        "\u00e2\u20ac\u00a6": "\u2026",
        "\u00c2\u00a0": " ",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def _clean_for_reportlab(text: str) -> str:
    """Escape XML special chars and convert markdown bold to reportlab tags."""
    text = _fix_encoding(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return text


def parse_markdown(md_text: str) -> dict:
    """Parse SPECTRA markdown into a structured dict for rendering."""
    lines = md_text.split("\n")
    title = ""
    subtitle = ""
    blurb = ""
    sections = []
    current_section = None
    current_items = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("# ") and not line.startswith("## "):
            title = line[2:]

        elif line.startswith("**Security Policy"):
            subtitle = line.strip("*")

        elif line.startswith("A monthly digest of"):
            blurb = line

        elif line.startswith("*Showing top"):
            # Section note — skip, handled by item count
            pass

        elif line.startswith("## "):
            if current_section is not None:
                sections.append(
                    {"title": current_section, "items": current_items}
                )
            current_section = line[3:]
            current_items = []

        elif line.startswith("### "):
            item = {"title": line[4:], "source_line": "", "source_url": "", "summary": ""}
            i += 1
            while i < len(lines):
                next_line = lines[i].rstrip()
                if next_line.startswith("### ") or next_line.startswith("## "):
                    i -= 1
                    break
                if next_line == "---":
                    break
                if next_line.startswith("*Source:"):
                    match = re.search(r"\[(.+?)\]\((.+?)\)", next_line)
                    if match:
                        item["source_line"] = match.group(1)
                        item["source_url"] = match.group(2)
                    else:
                        item["source_line"] = next_line.strip("*")
                elif next_line and not next_line.startswith("-"):
                    if item["summary"]:
                        item["summary"] += " " + next_line
                    else:
                        item["summary"] = next_line
                i += 1
            current_items.append(item)

        elif line.startswith("- ") and current_section == "Executive Summary":
            current_items.append({"bullet": line[2:]})

        i += 1

    if current_section is not None:
        sections.append({"title": current_section, "items": current_items})

    return {"title": title, "subtitle": subtitle, "blurb": blurb, "sections": sections}


def _build_styles():
    """Create reportlab paragraph styles for SPECTRA."""
    styles = getSampleStyleSheet()

    return {
        "section": ParagraphStyle(
            "SPSection",
            parent=styles["Heading1"],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=NAVY,
        ),
        "item_title": ParagraphStyle(
            "SPItemTitle",
            parent=styles["Heading2"],
            fontSize=11,
            spaceBefore=12,
            spaceAfter=2,
            textColor=DARK_TEXT,
        ),
        "source": ParagraphStyle(
            "SPSource",
            parent=styles["Normal"],
            fontSize=8,
            textColor=LINK_COLOR,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "SPBody",
            parent=styles["Normal"],
            fontSize=10,
            spaceAfter=8,
            leading=14,
            textColor=DARK_TEXT,
        ),
        "bullet": ParagraphStyle(
            "SPBullet",
            parent=styles["Normal"],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20,
            leading=14,
            textColor=DARK_TEXT,
        ),
    }


def _page_footer(canvas, doc):
    """Draw page number footer on each page."""
    canvas.saveState()
    page_width = letter[0]
    # Footer line
    canvas.setStrokeColor(LIGHT_GRAY)
    canvas.setLineWidth(0.5)
    canvas.line(0.75 * inch, 0.55 * inch, page_width - 0.75 * inch, 0.55 * inch)
    # Left: SPECTRA branding
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.75 * inch, 0.4 * inch, "SPECTRA \u2014 Security Policy, Emerging Cyber Threats, Research & AI")
    # Right: page number
    canvas.drawRightString(page_width - 0.75 * inch, 0.4 * inch, f"Page {doc.page}")
    canvas.restoreState()


def render_pdf(md_text: str, output_path: str) -> str:
    """Render SPECTRA markdown to a PDF file."""
    parsed = parse_markdown(md_text)
    st = _build_styles()

    page_width = letter[0]
    margin = 0.75 * inch
    content_width = page_width - 2 * margin

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=margin,
        bottomMargin=0.75 * inch,
        leftMargin=margin,
        rightMargin=margin,
    )

    story = []

    # Banner
    banner_title = _fix_encoding(parsed["title"])
    banner_subtitle = parsed["subtitle"] or "Security Policy, Emerging Cyber Threats, Research & AI"
    banner_blurb = parsed.get("blurb", "") or "A monthly digest of cybersecurity policy, standards, threats, and AI developments relevant to DoD and federal practitioners."
    story.append(BannerFlowable(
        content_width, 105, NAVY,
        banner_title, banner_subtitle, banner_blurb
    ))
    story.append(Spacer(1, 16))

    # Sections
    for section in parsed["sections"]:
        section_title = section["title"]
        section_color = SECTION_COLORS.get(section_title, NAVY)

        # Section heading — colored bar with white text
        story.append(SectionHeadingFlowable(content_width, section_title, section_color))
        story.append(Spacer(1, 8))

        for item in section["items"]:
            if "bullet" in item:
                text = _clean_for_reportlab(item["bullet"])
                story.append(Paragraph(text, st["bullet"]))
            else:
                story.append(
                    Paragraph(
                        _clean_for_reportlab(item["title"]), st["item_title"]
                    )
                )
                if item.get("source_url"):
                    source_text = f'<link href="{item["source_url"]}">{_clean_for_reportlab(item["source_line"])} \u2014 {_clean_for_reportlab(item["source_url"])}</link>'
                    story.append(Paragraph(source_text, st["source"]))
                elif item.get("source_line"):
                    story.append(
                        Paragraph(
                            _clean_for_reportlab(item["source_line"]),
                            st["source"],
                        )
                    )
                if item.get("summary"):
                    story.append(
                        Paragraph(
                            _clean_for_reportlab(item["summary"]), st["body"]
                        )
                    )

        story.append(Spacer(1, 12))

    doc.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
    return output_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python -m src.render.render <markdown_path> <output_pdf>")
        sys.exit(1)

    md_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(md_path) as f:
        md_text = f.read()

    print(f"SPECTRA Render — {md_path} -> {output_path}")
    render_pdf(md_text, output_path)
    print(f"  Done: {output_path}")


if __name__ == "__main__":
    main()
