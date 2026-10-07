"""SPF / DKIM / DMARC validation (sync, dnspython). Run inside a thread with a hard timeout."""
import ipaddress
import re

import dns.exception
import dns.resolver

from .parser import ParsedEmail

_resolver = dns.resolver.Resolver()
_resolver.lifetime = 1.5
_resolver.timeout = 0.75


def _txt(name: str) -> list[str]:
    try:
        return [b"".join(r.strings).decode() for r in _resolver.resolve(name, "TXT")]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return []


def _addrs(name: str, rtype: str) -> list[str]:
    try:
        return [r.to_text() for r in _resolver.resolve(name, rtype)]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return []


def org_domain(domain: str) -> str:
    # Naive; use `tldextract` / the Public Suffix List in production (handles .co.uk etc.)
    return ".".join(domain.split(".")[-2:])


def aligned(a: str, b: str) -> bool:  # relaxed alignment
    return bool(a and b) and org_domain(a) == org_domain(b)


# ---------------- SPF ----------------
def check_spf(ip: str | None, domain: str) -> str:
    """Returns pass | fail | softfail | neutral | none | permerror | temperror"""
    if not ip or not domain:
        return "none"
    try:
        return _spf(ipaddress.ip_address(ip), domain, [0])
    except dns.exception.Timeout:
        return "temperror"
    except Exception:
        return "permerror"


def _spf(ip, domain: str, lookups: list[int], depth: int = 0) -> str:
    if depth > 5 or lookups[0] > 10:
        return "permerror"
    recs = [t for t in _txt(domain) if t.lower().startswith("v=spf1")]
    if not recs:
        return "none"
    quals = {"+": "pass", "-": "fail", "~": "softfail", "?": "neutral"}
    for term in recs[0].split()[1:]:
        q = "+"
        if term[0] in quals:
            q, term = term[0], term[1:]
        low = term.lower()
        hit = False
        if low == "all":
            hit = True
        elif low.startswith(("ip4:", "ip6:")):
            try:
                hit = ip in ipaddress.ip_network(term[4:], strict=False)
            except ValueError:
                pass
        elif low.startswith("include:"):
            lookups[0] += 1
            if _spf(ip, term[8:], lookups, depth + 1) == "pass":
                hit = True
        elif low == "a" or low.startswith("a:") or low.startswith("a/"):
            lookups[0] += 1
            target = term[2:].split("/")[0] if low.startswith("a:") else domain
            rt = "AAAA" if ip.version == 6 else "A"
            hit = str(ip) in _addrs(target, rt)
        elif low == "mx" or low.startswith("mx:"):
            lookups[0] += 1
            target = term[3:] if low.startswith("mx:") else domain
            rt = "AAAA" if ip.version == 6 else "A"
            for mx in _addrs(target, "MX"):
                host = mx.split()[-1].rstrip(".")
                if str(ip) in _addrs(host, rt):
                    hit = True
                    break
        elif low.startswith("redirect="):
            lookups[0] += 1
            return _spf(ip, term[9:], lookups, depth + 1)
        if hit:
            return quals[q]
    return "neutral"


# ---------------- DKIM ----------------
def check_dkim(raw: bytes) -> str:
    """pass | fail | none"""
    if b"dkim-signature:" not in raw[:20000].lower():
        return "none"
    try:
        import dkim
        return "pass" if dkim.verify(raw) else "fail"
    except Exception:
        return "fail"


# ---------------- DMARC ----------------
def check_dmarc(email: ParsedEmail, spf: str, dkim_res: str) -> tuple[str, str]:
    """Returns (result, policy). result: pass | fail | none"""
    dom = email.sender_domain
    if not dom:
        return "fail", "none"
    rec = next((t for t in _txt(f"_dmarc.{dom}") if t.lower().startswith("v=dmarc1")), None) \
        or next((t for t in _txt(f"_dmarc.{org_domain(dom)}") if t.lower().startswith("v=dmarc1")), None)
    if not rec:
        return "none", "none"
    m = re.search(r"\bp=(\w+)", rec)
    pol = m.group(1).lower() if m else "none"
    spf_ok = spf == "pass" and aligned(email.return_path_domain, dom)
    dkim_ok = dkim_res == "pass" and any(aligned(d, dom) for d in email.dkim_domains)
    return ("pass" if (spf_ok or dkim_ok) else "fail"), pol


def from_auth_results(ar: str) -> dict:
    """Trust results the receiving mailbox provider already computed (best for forwarded mail)."""
    out = {}
    for key in ("spf", "dkim", "dmarc"):
        m = re.search(rf"\b{key}=(\w+)", ar, re.I)
        if m:
            out[key] = m.group(1).lower()
    return out


def run_all(email: ParsedEmail) -> dict:
    hdr = from_auth_results(email.auth_results)
    spf = hdr.get("spf") or check_spf(email.client_ip, email.return_path_domain)
    dkim_res = hdr.get("dkim") or check_dkim(email.raw)
    dmarc_res, pol = ((hdr["dmarc"], "unknown") if "dmarc" in hdr
                      else check_dmarc(email, spf, dkim_res))
    return {"spf": spf, "dkim": dkim_res, "dmarc": dmarc_res, "dmarc_policy": pol,
            "source": "authentication-results" if hdr else "live-dns"}
