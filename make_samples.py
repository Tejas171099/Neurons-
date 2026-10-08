"""Regenerates the mock attachments in sample_data/ (run: python make_samples.py)."""
from pathlib import Path

from tests import samples

out = Path(__file__).parent / "sample_data"
out.mkdir(exist_ok=True)
(out / "HDFC_Security_Update.pdf").write_bytes(samples.pdf_with_link("http://hdfc-login-update.xyz"))
(out / "Statement_clean.pdf").write_bytes(samples.pdf_clean())
(out / "Invoice_javascript.pdf").write_bytes(samples.pdf_with_javascript())
(out / "login_update.html").write_bytes(samples.PHISHING_HTML)
(out / "obfuscated_capture.html").write_bytes(samples.OBFUSCATED_HTML)
(out / "newsletter_clean.html").write_bytes(samples.CLEAN_HTML)
print("wrote", *sorted(p.name for p in out.iterdir()), sep="\n  ")
