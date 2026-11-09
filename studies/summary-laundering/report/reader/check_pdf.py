#!/usr/bin/env python3
"""Check the built reader PDF with existing Poppler tools; no network or writes."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata

import evidence


def normalized(text):
    return " ".join(unicodedata.normalize("NFKC", text).split())


def main():
    pdf = evidence.HERE / "who-said-that.pdf"
    meta = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    pages = int(re.search(r"^Pages:\s+(\d+)", meta, re.M).group(1))
    assert pages < 8, "the whole report, including appendix, must be under eight pages"
    text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
    first = text.split("\f")[0]
    repo = "https://github.com/RuslansAleksejevs/boundary-conditions"
    assert first.index(repo) < first.index("Abstract")
    urls = subprocess.check_output(["pdfinfo", "-url", str(pdf)], text=True)
    assert re.search(r"^\s*1\s+Annotation\s+" + re.escape(repo), urls, re.M), "first-page repository URL must be clickable"
    source = (evidence.HERE / "who-said-that.tex").read_text()
    abstract = source.split(r"\reportsection{Abstract}")[1].split(r"\reportsection{1.")[0]
    words = len(abstract.split())
    assert 150 <= words <= 250
    lower = text.lower()
    for term in ("wrong-goal", "verified, but what", "companion", "other study", "study b", "combined budget", "combined campaign"):
        assert term not in lower, term
    for term in ("/Users/", "happy-file://", "sk-or-v1-", "OPENROUTER_API_KEY", "authorization_reference"):
        assert term not in text, term
    assert "Limitations and Dual-Use / Ethical Considerations" in text
    assert "LLM Usage Statement" in text and "human author review" in lower
    data = evidence.derive()
    body = normalized(text)
    for quote in (data["examples"][0]["record_paragraph_verbatim"],
                  data["examples"][0]["summary_excerpt_verbatim"],
                  data["examples"][1]["response_verbatim"]):
        assert normalized(quote) in body, "a quoted example changed in PDF rendering"
    print(json.dumps({"pdf_checks_passed": True, "total_pages": pages, "abstract_words": words,
                      "first_page_repository_link": True, "exact_quotes_checked": 3,
                      "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
                      "bytes": pdf.stat().st_size, "new_api_requests": 0}, indent=2))


if __name__ == "__main__":
    main()