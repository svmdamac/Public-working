#!/usr/bin/env python3
"""Pre-flight checks on DAMAC purchase order data.

Three severities:
  BLOCKER  -- the PO is wrong or unissuable. Never hand it over.
  GATE     -- a term is still `unverified`. Blocks a FINAL PO; a --draft is allowed.
  WARN     -- worth a human glance.

Exit codes: 0 clean, 1 warnings only, 2 gated (draft-only), 3 blockers.
"""
from __future__ import annotations

import argparse
import sys
from decimal import Decimal

from po_core import (PO_REF_RE, TERM_ORDER, compute, load_json, load_registry,
                     resolve_supplier, term_value)

REQUIRED_TOP = ["po_number", "po_date", "project", "supplier_key", "currency"]
REQUIRED_REFS = ["loa", "quotation"]


def validate(po, registry, damac, final=True):
    issues = []

    def add(sev, msg):
        issues.append((sev, msg))

    for field in REQUIRED_TOP:
        if not po.get(field):
            add("BLOCKER", "missing required field: %s" % field)

    ref = po.get("po_reference")
    if not ref:
        add("WARN", "no po_reference -- PMWeb matches the LOA Reference to the PO number, see references/numbering.md")
    elif not PO_REF_RE.match(ref):
        add("WARN", "po_reference %r does not look like the DAMAC pattern "
                    "<PROJECT>-<CODES>-PO-<NNNN>[-R<n>]" % ref)

    try:
        key, supplier = resolve_supplier(po, registry)
    except KeyError as exc:
        add("BLOCKER", str(exc))
        return issues, None, None

    # Identity of both parties must be real, not a placeholder.
    for field in ("legal_name", "address", "trn"):
        val, status, hint = term_value(supplier.get(field))
        if not val:
            add("GATE", "supplier %s: %s is not recorded%s" % (key, field, " (%s)" % hint if hint else ""))

    entity_key = po.get("buyer_entity_key") or damac.get("default_entity_key")
    entity = damac.get("entities", {}).get(entity_key)
    if entity is None:
        add("BLOCKER", "unknown buyer_entity_key %r" % entity_key)
    else:
        for field in ("legal_name", "address", "trn"):
            val, _, hint = term_value(entity.get(field))
            if not val:
                add("GATE", "DAMAC entity %s: %s is not recorded%s"
                    % (entity_key, field, " (%s)" % hint if hint else ""))

    # Commercial terms.
    terms = supplier.get("terms", {})
    for field, label in TERM_ORDER:
        val, status, hint = term_value(terms.get(field))
        if val in (None, ""):
            add("GATE", "term not agreed/recorded for %s: %s%s"
                % (key, label, " -- %s" % hint if hint else ""))
        elif status != "verified":
            add("GATE", "term %s for %s is marked %r, not verified against a signed PO"
                % (label, key, status))

    cur_val, _, _ = term_value(terms.get("currency"))
    if cur_val and po.get("currency") and cur_val.strip().upper()[:3] != po["currency"].strip().upper()[:3]:
        add("BLOCKER", "PO currency %s contradicts the agreed currency for %s (%s)"
            % (po["currency"], key, cur_val))

    if not po.get("line_items") and not po.get("lump_sums"):
        add("BLOCKER", "PO has no line items and no lump sums")

    lines, totals = compute(po)
    for i, line in enumerate(lines, 1):
        if not line.get("description"):
            add("BLOCKER", "line %d has no description" % i)
        if not line.get("is_lump_sum"):
            if Decimal(str(line.get("qty", 0))) <= 0:
                add("BLOCKER", "line %d has a non-positive quantity" % i)
            if Decimal(str(line.get("rate", 0))) <= 0:
                add("BLOCKER", "line %d has a non-positive rate" % i)
        fmt = supplier.get("format", {})
        if line.get("is_lump_sum"):
            continue
        if fmt.get("requires_shade_calibre_column") and not line.get("shade_calibre"):
            add("WARN", "line %d: no shade/calibre recorded -- %s POs normally state it" % (i, key))
        if fmt.get("requires_origin_column") and not line.get("origin"):
            add("WARN", "line %d: no country of origin recorded -- required for imported supply" % i)

    if totals["total"] <= 0:
        add("BLOCKER", "PO total is not positive")

    refs = po.get("references") or {}
    for r in REQUIRED_REFS:
        if not refs.get(r):
            add("WARN", "no %s reference -- a DAMAC PO is raised against the approved LOA/quotation" % r.upper())

    budget = po.get("budget_amount")
    if budget:
        if totals["net"] > Decimal(str(budget)):
            add("BLOCKER", "PO net %s exceeds the stated budget %s" % (totals["net"], budget))
        elif totals["net"] > Decimal(str(budget)) * Decimal("0.95"):
            add("WARN", "PO net is within 5%% of the stated budget (%s of %s)" % (totals["net"], budget))

    if po.get("vat_percent") in (None, ""):
        add("WARN", "vat_percent not set -- state it explicitly even when zero-rated")

    return issues, lines, totals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("po_json")
    ap.add_argument("--draft", action="store_true", help="allow unverified terms (draft output)")
    args = ap.parse_args()

    po = load_json(args.po_json)
    registry, damac = load_registry()
    issues, _, totals = validate(po, registry, damac, final=not args.draft)

    order = {"BLOCKER": 0, "GATE": 1, "WARN": 2}
    for sev, msg in sorted(issues, key=lambda i: order[i[0]]):
        print("%-8s %s" % (sev, msg))

    sevs = {s for s, _ in issues}
    if not issues:
        print("OK -- no issues. Total: %s %s" % (totals["total"], po.get("currency")))
        return 0
    if "BLOCKER" in sevs:
        print("\n=> BLOCKED: fix the blockers above before issuing anything.")
        return 3
    if "GATE" in sevs:
        print("\n=> DRAFT ONLY: %d term(s) still unverified. Confirm them against a signed PO "
              "(scripts/learn_terms.py) before issuing a final PO." % sum(1 for s, _ in issues if s == "GATE"))
        return 2 if not args.draft else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
