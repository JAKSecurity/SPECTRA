import os

from src.render.render import parse_markdown, render_pdf


SAMPLE_MARKDOWN = """# SPECTRA \u2014 APRIL 2026

**Security Policy, Emerging Cyber Threats, Research & AI**

A monthly digest of cybersecurity policy, standards, threats, and AI developments relevant to DoD and federal practitioners. Compiled from public government and industry sources.

---

## Executive Summary

- **CISA Emergency Directive** \u2014 CISA issued ED 26-01 requiring immediate patching.
- **NIST Zero Trust Guide** \u2014 NIST released updated zero trust guidance.

---

## Policy & Compliance Updates

### CISA Releases Emergency Directive on Critical Vulnerability
*Source: [cisa_alerts](https://example.com/cisa-ed-2026-01)*

CISA issued Emergency Directive 26-01 requiring all federal civilian agencies to patch CVE-2026-XXXX within 72 hours. The directive applies to a critical vulnerability in widely deployed network infrastructure that is under active exploitation.

---

## Publications & Standards

### NIST Publishes Updated Zero Trust Architecture Guide
*Source: [nist_csrc](https://example.com/nist-sp-800-207a)*

NIST released SP 800-207A providing updated implementation guidance for zero trust architecture in federal environments. The publication expands on the original SP 800-207 with practical deployment patterns.

---

## Threats & Incidents

### Major Ransomware Campaign Targets Healthcare Sector
*Source: [dark_reading](https://example.com/ransomware-healthcare)*

A ransomware group is actively targeting US healthcare organizations using a novel phishing vector. Multiple hospital systems have reported incidents affecting patient care operations.

---
"""


class TestParseMarkdown:
    def test_extracts_title(self):
        parsed = parse_markdown(SAMPLE_MARKDOWN)
        assert "APRIL 2026" in parsed["title"]

    def test_extracts_blurb(self):
        parsed = parse_markdown(SAMPLE_MARKDOWN)
        assert "monthly digest" in parsed["blurb"]

    def test_extracts_sections(self):
        parsed = parse_markdown(SAMPLE_MARKDOWN)
        section_titles = [s["title"] for s in parsed["sections"]]
        assert "Executive Summary" in section_titles
        assert "Policy & Compliance Updates" in section_titles
        assert "Publications & Standards" in section_titles
        assert "Threats & Incidents" in section_titles

    def test_extracts_items_within_sections(self):
        parsed = parse_markdown(SAMPLE_MARKDOWN)
        policy_section = next(
            s for s in parsed["sections"] if s["title"] == "Policy & Compliance Updates"
        )
        assert len(policy_section["items"]) == 1
        assert "Emergency Directive" in policy_section["items"][0]["title"]

    def test_extracts_source_url(self):
        parsed = parse_markdown(SAMPLE_MARKDOWN)
        policy_section = next(
            s for s in parsed["sections"] if s["title"] == "Policy & Compliance Updates"
        )
        item = policy_section["items"][0]
        assert item["source_line"] == "cisa_alerts"
        assert item["source_url"] == "https://example.com/cisa-ed-2026-01"


class TestRenderPdf:
    def test_creates_pdf_file(self, tmp_path):
        output_path = str(tmp_path / "test_output.pdf")
        render_pdf(SAMPLE_MARKDOWN, output_path)
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_pdf_starts_with_pdf_header(self, tmp_path):
        output_path = str(tmp_path / "test_output.pdf")
        render_pdf(SAMPLE_MARKDOWN, output_path)
        with open(output_path, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"
