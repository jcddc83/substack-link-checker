"""Substack Broken Link Checker — async link checker for Substack newsletters."""

from ._cli_check import load_domains_from_file
from .checker import BrokenLinkRecord, LinkCheckResult, SubstackLinkChecker

__version__ = "1.0.0"

__all__ = [
    "BrokenLinkRecord",
    "LinkCheckResult",
    "SubstackLinkChecker",
    "load_domains_from_file",
    "__version__",
]
