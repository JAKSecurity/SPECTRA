from src.curate.draft import assemble_draft, MAX_ITEMS_PER_SECTION


class TestAssembleDraft:
    def test_produces_markdown_with_title(self, sample_curated_items):
        md = assemble_draft(sample_curated_items, month_label="APRIL 2026")
        assert "# SPECTRA" in md
        assert "APRIL 2026" in md
        assert "Security Policy, Emerging Cyber Threats, Research & AI" in md

    def test_includes_blurb(self, sample_curated_items):
        md = assemble_draft(sample_curated_items, month_label="APRIL 2026")
        assert "monthly digest" in md
        assert "DoD and federal practitioners" in md

    def test_includes_executive_summary(self, sample_curated_items):
        md = assemble_draft(sample_curated_items, month_label="APRIL 2026")
        assert "## Executive Summary" in md
        assert "CISA Releases Emergency Directive" in md

    def test_groups_items_by_section(self, sample_curated_items):
        md = assemble_draft(sample_curated_items, month_label="APRIL 2026")
        assert "## Policy & Compliance Updates" in md
        assert "## Publications & Standards" in md
        assert "## Threats & Incidents" in md

    def test_includes_full_source_url(self, sample_curated_items):
        md = assemble_draft(sample_curated_items, month_label="APRIL 2026")
        assert "[cisa_alerts](https://example.com/cisa-ed-2026-01)" in md
        assert "[nist_csrc](https://example.com/nist-sp-800-207a)" in md

    def test_skips_empty_sections(self):
        items = [
            {
                "id": "a",
                "title": "Only Policy Item",
                "url": "https://example.com",
                "source": "test",
                "section": "policy",
                "summary": "A policy update.",
                "relevance": 8,
            }
        ]
        md = assemble_draft(items, month_label="APRIL 2026")
        assert "## Policy & Compliance Updates" in md
        assert "## Threats & Incidents" not in md
        assert "## AI & Agentic Developments" not in md

    def test_sorts_items_by_relevance_within_section(self):
        items = [
            {
                "id": "low",
                "title": "Low Relevance",
                "url": "https://example.com/low",
                "source": "test",
                "section": "policy",
                "summary": "Low.",
                "relevance": 4,
            },
            {
                "id": "high",
                "title": "High Relevance",
                "url": "https://example.com/high",
                "source": "test",
                "section": "policy",
                "summary": "High.",
                "relevance": 9,
            },
        ]
        md = assemble_draft(items, month_label="APRIL 2026")
        high_pos = md.index("High Relevance")
        low_pos = md.index("Low Relevance")
        assert high_pos < low_pos

    def test_limits_items_per_section(self):
        items = [
            {
                "id": f"item_{i}",
                "title": f"Threat Item {i}",
                "url": f"https://example.com/{i}",
                "source": "test",
                "section": "threats",
                "summary": f"Summary {i}.",
                "relevance": 10 - (i % 5),
            }
            for i in range(30)
        ]
        md = assemble_draft(items, month_label="APRIL 2026")
        # Should only have MAX_ITEMS_PER_SECTION items rendered
        assert md.count("### Threat Item") == MAX_ITEMS_PER_SECTION
        assert f"Showing top {MAX_ITEMS_PER_SECTION} of 30 items" in md
