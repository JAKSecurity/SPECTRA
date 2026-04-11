import pytest
import os
import json
import tempfile

SAMPLE_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Cyber Feed</title>
    <link>https://example.com</link>
    <description>Test feed</description>
    <item>
      <title>CISA Releases Emergency Directive on Critical Vulnerability</title>
      <link>https://example.com/cisa-ed-2026-01</link>
      <description>CISA has issued Emergency Directive 26-01 requiring federal agencies to patch a critical vulnerability.</description>
      <pubDate>Mon, 06 Apr 2026 12:00:00 GMT</pubDate>
    </item>
    <item>
      <title>NIST Publishes Updated Zero Trust Architecture Guide</title>
      <link>https://example.com/nist-sp-800-207a</link>
      <description>NIST has released SP 800-207A with updated zero trust guidance for federal agencies.</description>
      <pubDate>Tue, 07 Apr 2026 12:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Major Ransomware Campaign Targets Healthcare Sector</title>
      <link>https://example.com/ransomware-healthcare</link>
      <description>A new ransomware campaign is actively targeting US healthcare organizations using a novel initial access vector.</description>
      <pubDate>Wed, 08 Apr 2026 12:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""


SAMPLE_FETCHED_ITEMS = [
    {
        "id": "a1b2c3",
        "title": "CISA Releases Emergency Directive on Critical Vulnerability",
        "url": "https://example.com/cisa-ed-2026-01",
        "published": "2026-04-06",
        "summary": "CISA has issued Emergency Directive 26-01 requiring federal agencies to patch a critical vulnerability.",
        "category_hint": "policy"
    },
    {
        "id": "d4e5f6",
        "title": "NIST Publishes Updated Zero Trust Architecture Guide",
        "url": "https://example.com/nist-sp-800-207a",
        "published": "2026-04-07",
        "summary": "NIST has released SP 800-207A with updated zero trust guidance for federal agencies.",
        "category_hint": "publication"
    },
    {
        "id": "g7h8i9",
        "title": "Major Ransomware Campaign Targets Healthcare Sector",
        "url": "https://example.com/ransomware-healthcare",
        "published": "2026-04-08",
        "summary": "A new ransomware campaign is actively targeting US healthcare organizations.",
        "category_hint": "news"
    },
]


SAMPLE_CURATED_ITEMS = [
    {
        "id": "a1b2c3",
        "title": "CISA Releases Emergency Directive on Critical Vulnerability",
        "url": "https://example.com/cisa-ed-2026-01",
        "source": "cisa_alerts",
        "section": "policy",
        "summary": "CISA issued Emergency Directive 26-01 requiring all federal civilian agencies to patch CVE-2026-XXXX within 72 hours. The directive applies to a critical vulnerability in widely deployed network infrastructure that is under active exploitation.",
        "relevance": 9
    },
    {
        "id": "d4e5f6",
        "title": "NIST Publishes Updated Zero Trust Architecture Guide",
        "url": "https://example.com/nist-sp-800-207a",
        "source": "nist_csrc",
        "section": "publications",
        "summary": "NIST released SP 800-207A providing updated implementation guidance for zero trust architecture in federal environments. The publication expands on the original SP 800-207 with practical deployment patterns and assessment criteria.",
        "relevance": 8
    },
    {
        "id": "g7h8i9",
        "title": "Major Ransomware Campaign Targets Healthcare Sector",
        "url": "https://example.com/ransomware-healthcare",
        "source": "dark_reading",
        "section": "threats",
        "summary": "A ransomware group is actively targeting US healthcare organizations using a novel phishing vector that exploits trust in health information exchanges. Multiple hospital systems have reported incidents affecting patient care operations.",
        "relevance": 7
    },
]


@pytest.fixture
def sample_rss_xml():
    return SAMPLE_RSS_XML


@pytest.fixture
def sample_fetched_items():
    return SAMPLE_FETCHED_ITEMS


@pytest.fixture
def sample_curated_items():
    return SAMPLE_CURATED_ITEMS


@pytest.fixture
def tmp_output_dir(tmp_path):
    output_dir = tmp_path / "sources" / "2026-04"
    output_dir.mkdir(parents=True)
    return str(output_dir)


@pytest.fixture
def tmp_sources_with_data(tmp_path, sample_fetched_items):
    """Creates a tmp sources dir with two JSON files containing sample items."""
    source_dir = tmp_path / "sources" / "2026-04"
    source_dir.mkdir(parents=True)

    file1 = {
        "source": "cisa_alerts",
        "fetched_at": "2026-04-07T09:00:00Z",
        "items": [sample_fetched_items[0]]
    }
    file2 = {
        "source": "nist_csrc",
        "fetched_at": "2026-04-07T09:00:00Z",
        "items": [sample_fetched_items[1], sample_fetched_items[2]]
    }

    with open(source_dir / "cisa_alerts_20260407.json", "w") as f:
        json.dump(file1, f)
    with open(source_dir / "nist_csrc_20260407.json", "w") as f:
        json.dump(file2, f)

    return str(source_dir)
