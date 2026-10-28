#!/usr/bin/env python3
"""Pull candidate terms out of previously signed DAMAC POs.

    python3 learn_terms.py rak-ceramics /path/to/signed/*.pdf

Prints the text around each term we care about so a human can read the real
agreed wording, plus a JSON skeleton to paste into assets/suppliers.json.

This tool never writes the registry itself. Extraction from a scanned or
stamped PDF is approximate, and a wrong payment term on a live PO is a real
commercial problem -- a person confirms the wording, then it is recorded as
`verified` with the source PO named.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

from po_core import ASSETS, TERM_ORDER, load_json

CUES = {
    "payment_terms": ["payment term", "terms of payment", "credit", "days from", "net 30", "net 60", "net 90"],
    "advance_payment": ["advance", "down payment", "mobilisation", "mobilization", "proforma"],
    "retention": ["retention", "retained"],
    "delivery_terms": ["delivery term", "incoterm", "ddp", "dap", "cif", "fob", "exw", "ex-works", "offload"],
    "lead_time": ["lead time", "delivery period", "weeks from", "days from order", "production time"],
    "warranty": ["warranty", "guarantee", "defects liability", "dlp"],
    "ld_clause": ["liquidated damages", "penalty", "ld @", "delay damages"],
    "price_validity": ["price validity", "rates are fixed", "firm price", "valid for", "escalation"],
    "breakage_wastage": ["breakage", "wastage", "wastage allowance", "attic stock"],
    "samples_approval": ["sample", "shade", "calibre", "caliber", "mock-up", "mockup", "approval of sample"],
    "packing_marking": ["packing", "pallet", "crate", "marking", "a-frame"],
    "insurance": ["insurance", "insured", "marine"],
    "title_risk": ["title", "risk shall pass", "ownership"],
    "currency": ["aed", "usd", "eur", "currency"],
    "vat": ["vat", "value added tax", "zero-rated", "reverse charge"],
    "special_conditions": ["country of origin", "certificate of origin", "bill of lading", "letter of credit", "bank guarantee"],
}

LABELS = dict(TERM_ORDER)


def pdf_text(path):
    try:
        import pdfplumber
    except ImportError:
        sys.exit("pdfplumber is required: pip install pdfplumber")
    out = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            out.append((i, page.extract_text() or ""))
    return out


def scan(paths):
    hits = {k: [] for k in CUES}
    empty = []
    for path in paths:
        name = os.path.basename(path)
        pages = pdf_text(path)
        if not any(t.strip() for _p, t in pages):
            empty.append(name)
        for pageno, text in pages:
            lines = [l.strip() for l in text.splitlines()]
            for idx, line in enumerate(lines):
                low = line.lower()
                for field, cues in CUES.items():
                    if any(c in low for c in cues):
                        ctx = " ".join(lines[idx:idx + 3]).strip()
                        hits[field].append((name, pageno, ctx[:400]))
    return hits, empty


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("supplier_key")
    ap.add_argument("pdfs", nargs="+")
    ap.add_argument("--max-per-term", type=int, default=4)
    args = ap.parse_args()

    registry = load_json(os.path.join(ASSETS, "suppliers.json"))
    if args.supplier_key not in registry["suppliers"]:
        sys.exit("unknown supplier_key %r -- known: %s"
                 % (args.supplier_key, ", ".join(sorted(registry["suppliers"]))))

    hits, empty = scan(args.pdfs)

    if empty:
        print("!! No extractable text in: %s" % ", ".join(empty))
        print("   These are probably scans. Run OCR first, or read them by eye.\n")

    print("=" * 78)
    print("CANDIDATE TERMS FOR %s" % args.supplier_key.upper())
    print("=" * 78)
    for field, label in TERM_ORDER:
        found = hits.get(field, [])[: args.max_per_term]
        print("\n### %s" % label)
        if not found:
            print("   (nothing matched -- check the source POs by eye)")
        for name, pageno, ctx in found:
            print("   [%s p.%d] %s" % (name, pageno, ctx))

    skeleton = {
        field: {"value": "<<< paste the confirmed wording >>>", "status": "verified",
                "source": "<<< PO reference + date this came from >>>"}
        for field, _ in TERM_ORDER
    }
    print("\n" + "=" * 78)
    print("Paste into assets/suppliers.json under suppliers.%s.terms, replacing\n"
          "each placeholder with the wording you confirmed above. Delete any term\n"
          "you could not confirm -- leave it unverified rather than guessing."
          % args.supplier_key)
    print("=" * 78)
    print(json.dumps(skeleton, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
