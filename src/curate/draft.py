from collections import defaultdict
from datetime import datetime, timezone

SECTION_ORDER = [
    "policy",
    "publications",
    "threats",
    "ai",
    "legislative",
    "conferences",
]

SECTION_TITLES = {
    "policy": "Policy & Compliance Updates",
    "publications": "Publications & Standards",
    "threats": "Threats & Incidents",
    "ai": "AI & Agentic Developments",
    "legislative": "Legislative Highlights",
    "conferences": "Upcoming Conferences",
}

MAX_ITEMS_PER_SECTION = 20


def _fix_encoding(text: str) -> str:
    """Fix common UTF-8 mojibake artifacts (e.g., em-dash encoded as â€")."""
    replacements = {
        "\u00e2\u20ac\u201c": "\u2014",  # em-dash
        "\u00e2\u20ac\u201d": "\u2014",  # em-dash variant
        "\u00e2\u20ac\u2122": "\u2019",  # right single quote
        "\u00e2\u20ac\u0153": "\u201c",  # left double quote
        "\u00e2\u20ac\u009d": "\u201d",  # right double quote
        "\u00e2\u20ac\u00a6": "\u2026",  # ellipsis
        "\u00c2\u00a0": " ",             # non-breaking space
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def assemble_draft(curated_items: list, month_label: str = None) -> str:
    """Assemble curated items into a SPECTRA markdown draft."""
    if month_label is None:
        month_label = datetime.now(timezone.utc).strftime("%B %Y").upper()

    # Group by section
    sections = defaultdict(list)
    for item in curated_items:
        sections[item["section"]].append(item)

    lines = []

    # Title
    lines.append(f"# SPECTRA \u2014 {month_label}")
    lines.append("")
    lines.append("**Security Policy, Emerging Cyber Threats, Research & AI**")
    lines.append("")
    lines.append("A monthly digest of cybersecurity policy, standards, threats, and AI developments relevant to DoD and federal practitioners. Compiled from public government and industry sources.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Executive summary — top 5 items by relevance
    all_sorted = sorted(
        curated_items, key=lambda x: x.get("relevance", 0), reverse=True
    )
    lines.append("## Executive Summary")
    lines.append("")
    for item in all_sorted[:5]:
        first_sentence = _fix_encoding(item["summary"]).split(".")[0] + "."
        title = _fix_encoding(item["title"])
        lines.append(f"- **{title}** \u2014 {first_sentence}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Each section
    for section_key in SECTION_ORDER:
        items = sections.get(section_key, [])
        if not items:
            continue

        sorted_items = sorted(
            items, key=lambda x: x.get("relevance", 0), reverse=True
        )
        # Limit to top N items
        top_items = sorted_items[:MAX_ITEMS_PER_SECTION]

        lines.append(f"## {SECTION_TITLES[section_key]}")
        lines.append("")

        if len(sorted_items) > MAX_ITEMS_PER_SECTION:
            lines.append(f"*Showing top {MAX_ITEMS_PER_SECTION} of {len(sorted_items)} items by relevance.*")
            lines.append("")

        for item in top_items:
            title = _fix_encoding(item["title"])
            summary = _fix_encoding(item["summary"])
            url = item.get("url", "")
            source = item.get("source", "Unknown")
            lines.append(f"### {title}")
            lines.append(f"*Source: [{source}]({url})*")
            lines.append("")
            lines.append(summary)
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)
