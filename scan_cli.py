"""Scan files from the command line - the quickest way to feed the code real input.

    python scan_cli.py sample_data/HDFC_Security_Update.pdf
    python scan_cli.py a.pdf b.html --subject "Urgent" --body "Verify your account now"
    python scan_cli.py a.pdf --body-file email.txt --detail      # full evidence + timings
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

from app.nlp import load_analyzer
from app.pipeline import Pipeline


async def main() -> int:
    ap = argparse.ArgumentParser(description="Attachment Risk Sandbox")
    ap.add_argument("files", nargs="*", help=".pdf / .html files to scan")
    ap.add_argument("--subject", default="")
    ap.add_argument("--body", default="")
    ap.add_argument("--body-file", help="read the email body from this text file")
    ap.add_argument("--detail", action="store_true", help="include findings and timings")
    args = ap.parse_args()

    body = args.body
    if args.body_file:
        with open(args.body_file, encoding="utf-8", errors="replace") as fh:
            body = fh.read()
    attachments = []
    for path in args.files:
        if not os.path.isfile(path):
            print(f"error: no such file: {path}", file=sys.stderr)
            return 2
        with open(path, "rb") as fh:
            attachments.append((os.path.basename(path), fh.read()))

    pipeline = Pipeline(load_analyzer())
    try:
        result = await pipeline.run(args.subject, body, attachments)
    finally:
        pipeline.close()
    print((result if args.detail else result.to_contract()).model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
