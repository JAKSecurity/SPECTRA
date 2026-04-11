from .rss import RSSFetcher
from .federal_register import FederalRegisterFetcher
from .cisa_kev import CISAKEVFetcher
from .congress_gov import CongressGovFetcher

FETCHER_TYPES = {
    "rss": RSSFetcher,
    "federal_register": FederalRegisterFetcher,
    "cisa_kev": CISAKEVFetcher,
    "congress_gov": CongressGovFetcher,
}


def get_fetcher(name: str, config: dict):
    """Instantiate a fetcher by its type string from config."""
    fetcher_type = config.get("type", "rss")
    cls = FETCHER_TYPES.get(fetcher_type)
    if cls is None:
        raise ValueError(f"Unknown fetcher type: {fetcher_type}")
    return cls(name, config)
