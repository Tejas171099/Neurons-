# Attachment Risk Sandbox & ML Pipeline

Pre-download inspection of `.pdf` / `.html` email attachments for credential-harvesting
threats, merged with the NLP text verdict into one JSON response (budget: 1.5 s).

## Giving it input (3 ways)
**1. Command line - your own files, any path**

    python scan_cli.py sample_data/HDFC_Security_Update.pdf
    python scan_cli.py C:\\Downloads\\invoice.pdf page.html --subject "Urgent" --body "Verify your account"
    python scan_cli.py file.pdf --body-file email.txt --detail     # --detail = evidence + timings

**2. HTTP API** (what Ruchit's backend calls) - `uvicorn app.main:app --port 8000`

    curl -F subject="Urgent" -F body="Verify your account" \
         -F files=@sample_data/HDFC_Security_Update.pdf -F files=@sample_data/login_update.html \
         http://localhost:8000/v1/scan

Or JSON with base64 attachments to `POST /v1/scan/json`. Add `?detail=true` for full evidence.

**3. Python import** - the two modular entry points:

    from app.scanner import scan_attachment, scan_file
    scan_file("invoice.pdf")                      # a file on disk
    scan_attachment("invoice.pdf", raw_bytes)     # bytes straight from the mail parser
    # whole email (text + all attachments, parallel, 1.5 s budget):
    result = await Pipeline(load_analyzer()).run(subject, body, [(name, bytes), ...])

Mock files for testing are in `sample_data/` (regenerate with `python make_samples.py`).

## Output contract (default response)
    {
      "attachment_scanned": true,
      "file_name": "HDFC_Security_Update.pdf",
      "has_malicious_form": true,
      "attachment_risk_level": "HIGH_THREAT",      // SAFE | LOW_RISK | SUSPICIOUS | HIGH_THREAT
      "overall_risk_level": "HIGH_THREAT",
      "text_analysis": {"phishing_probability": 0.4, "risk_level": "SUSPICIOUS", "signals": [...], "error": null}
    }
The first four keys are exactly the brief's example. With several attachments they describe the
riskiest one. The schema lives in `ContractResponse` (`app/models.py`) - change it there only.

## Run / test
    pip install -r requirements.txt
    python -m unittest discover -s tests -t .      # 19 tests

## Plugging in Shruthi's NLP model
Implement `analyze(subject, body) -> TextReport` (see `app/nlp.py`) and set
`NLP_ANALYZER=her_package.module:ClassOrFactory`. Until then a crude keyword stub runs.

## Layout
- `app/urls.py` – URL extraction + reputation heuristics (brand look-alikes, bad TLDs, IP hosts...)
- `app/html_scanner.py`, `app/pdf_scanner.py` – static analysis (BeautifulSoup/lxml, pypdf); nothing is executed or fetched
- `app/scanner.py` – type sniffing (content over extension), size limit, scoring
- `app/risk.py` – score (0-100) and levels: SAFE <10 · LOW_RISK <30 · SUSPICIOUS <60 · HIGH_THREAT
- `app/pipeline.py` – parallel NLP + attachment scans, deadline enforcement, merge
- `app/main.py` – FastAPI

## Behaviour worth knowing
- **Fail closed:** a file that times out, is too big or is encrypted is reported `SUSPICIOUS`, never `SAFE`.
- A crashing/slow NLP model degrades to an `error` field; attachment results still return on time.
- Text + attachment both suspicious ⇒ escalated to `HIGH_THREAT`.
- Thresholds and heuristic lists are plain constants at the top of `urls.py` / `risk.py` for tuning.
