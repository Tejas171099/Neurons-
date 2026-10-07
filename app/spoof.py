"""Display-name spoofing detector."""
import re
from dataclasses import dataclass

from .auth_checks import aligned

# brand keyword -> legitimate root domains. Extend / load from config or a threat-intel feed.
BRANDS: dict[str, set[str]] = {
    "state bank of india": {"sbi.co.in", "onlinesbi.sbi", "sbi.bank.in"},
    "sbi": {"sbi.co.in", "onlinesbi.sbi", "sbi.bank.in"},
    "netflix": {"netflix.com"},
    "amazon": {"amazon.com", "amazon.in", "amazon.co.uk", "amazonses.com"},
    "paypal": {"paypal.com"},
    "hdfc": {"hdfcbank.com", "hdfcbank.net"},
    "icici": {"icicibank.com"},
    "google": {"google.com", "accounts.google.com"},
    "microsoft": {"microsoft.com", "microsoftonline.com", "outlook.com"},
    "apple": {"apple.com", "id.apple.com"},
}

_LOOKALIKE = str.maketrans({"0": "o", "1": "l", "3": "e", "5": "s", "@": "a", "$": "s"})


@dataclass
class SpoofResult:
    is_spoofed: bool
    brand: str | None = None
    reason: str = ""


def _norm(s: str) -> str:
    return re.sub(r"[^a-z ]", "", s.lower().translate(_LOOKALIKE))


def detect_spoof(display_name: str, sender_domain: str) -> SpoofResult:
    if not display_name or not sender_domain:
        return SpoofResult(False)
    name = f" {_norm(display_name)} "
    for brand, legit in BRANDS.items():
        if f" {brand} " in name or brand in name.replace(" ", "") and len(brand) > 4:
            if not any(aligned(sender_domain, d) or sender_domain == d for d in legit):
                return SpoofResult(
                    True, brand,
                    f"Display name claims '{brand}' but sender domain '{sender_domain}' is not a verified {brand} domain",
                )
    return SpoofResult(False)
