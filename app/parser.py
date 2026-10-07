"""Raw email -> structured header data. Pure in-memory; nothing is written to disk."""
import ipaddress
import re
from dataclasses import dataclass, field
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr


@dataclass
class ParsedEmail:
    raw: bytes
    subject: str = ""
    display_name: str = ""
    sender_email: str = ""
    sender_domain: str = ""
    return_path_domain: str = ""
    client_ip: str | None = None
    dkim_domains: list[str] = field(default_factory=list)
    auth_results: str = ""  # Authentication-Results added by the receiving MTA


def _domain(addr: str) -> str:
    return addr.rsplit("@", 1)[-1].strip().lower().rstrip(".") if "@" in addr else ""


def _origin_ip(received_headers: list[str]) -> str | None:
    """Bottom-most Received header holding a public IP = closest to original sender."""
    for hdr in reversed(received_headers):
        for cand in re.findall(r"\[?((?:\d{1,3}\.){3}\d{1,3}|[0-9a-fA-F:]{6,})\]?", hdr):
            try:
                ip = ipaddress.ip_address(cand)
            except ValueError:
                continue
            if ip.is_global:
                return str(ip)
    return None


def parse_email(raw: bytes) -> ParsedEmail:
    msg = BytesParser(policy=policy.default).parsebytes(raw, headersonly=True)
    name, addr = parseaddr(str(msg.get("From", "")))
    rp = parseaddr(str(msg.get("Return-Path", "")))[1] or addr

    dkim_domains = []
    for sig in msg.get_all("DKIM-Signature", []):
        m = re.search(r"\bd=([^;\s]+)", str(sig))
        if m:
            dkim_domains.append(m.group(1).lower())

    return ParsedEmail(
        raw=raw,
        subject=str(msg.get("Subject", "")),
        display_name=name.strip(),
        sender_email=addr.lower(),
        sender_domain=_domain(addr),
        return_path_domain=_domain(rp),
        client_ip=_origin_ip([str(h) for h in msg.get_all("Received", [])]),
        dkim_domains=dkim_domains,
        auth_results=" ".join(str(h) for h in msg.get_all("Authentication-Results", [])),
    )
