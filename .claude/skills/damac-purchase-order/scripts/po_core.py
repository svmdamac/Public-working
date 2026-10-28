"""Shared loading, merging and arithmetic for DAMAC purchase orders.

Everything that touches money lives here so the builder and the validator can
never disagree about a total.
"""
from __future__ import annotations

import json
import os
import re
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")

TERM_ORDER = [
    ("currency", "Currency"),
    ("vat", "VAT"),
    ("payment_terms", "Payment Terms"),
    ("advance_payment", "Advance Payment"),
    ("retention", "Retention"),
    ("delivery_terms", "Delivery Terms"),
    ("lead_time", "Lead Time"),
    ("price_validity", "Price Validity"),
    ("samples_approval", "Samples & Approval"),
    ("breakage_wastage", "Breakage / Wastage"),
    ("packing_marking", "Packing & Marking"),
    ("insurance", "Insurance"),
    ("title_risk", "Title & Risk"),
    ("warranty", "Warranty / DLP"),
    ("ld_clause", "Liquidated Damages"),
    ("special_conditions", "Special Conditions"),
]

# PO reference seen on DAMAC PMWeb commitments, e.g.
# P158.19-NAA-SM-RD-RR-KK-PO-2489-R0
PO_REF_RE = re.compile(r"^[A-Z]{1,4}\d+(?:\.\d+)?-(?:[A-Z]{2,4}-)+PO-\d+", re.I)


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_registry():
    return (
        load_json(os.path.join(ASSETS, "suppliers.json")),
        load_json(os.path.join(ASSETS, "damac.json")),
    )


def term_value(term):
    """A term is either a plain value or {value,status,hint}."""
    if isinstance(term, dict):
        return term.get("value"), term.get("status", "unverified"), term.get("hint")
    return term, "verified", None


def resolve_supplier(po, registry):
    key = po.get("supplier_key")
    suppliers = registry["suppliers"]
    if key not in suppliers:
        raise KeyError(
            "unknown supplier_key %r -- known keys: %s" % (key, ", ".join(sorted(suppliers)))
        )
    supplier = json.loads(json.dumps(suppliers[key]))  # deep copy
    for field, val in (po.get("supplier_override") or {}).items():
        supplier[field] = val
    for field, val in (po.get("terms_overrides") or {}).items():
        # An override is an explicit instruction from the buyer: it counts as verified.
        supplier.setdefault("terms", {})[field] = {
            "value": val,
            "status": "verified",
            "source": "terms_overrides in PO data",
        }
    return key, supplier


def money(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute(po):
    """Return (lines, totals). Each line gains a computed `amount`."""
    lines = []
    for raw in po.get("line_items", []):
        qty = Decimal(str(raw.get("qty", 0)))
        rate = Decimal(str(raw.get("rate", 0)))
        disc = Decimal(str(raw.get("discount_percent", 0) or 0))
        gross = qty * rate
        amount = money(gross * (Decimal(1) - disc / Decimal(100)))
        line = dict(raw)
        line["gross"] = money(gross)
        line["amount"] = amount
        lines.append(line)

    for raw in po.get("lump_sums", []):
        amount = money(raw.get("amount", 0))
        lines.append(
            {
                "description": raw.get("description", ""),
                "spec": raw.get("spec", ""),
                "unit": raw.get("unit", "LS"),
                "qty": raw.get("qty", 1),
                "rate": amount,
                "discount_percent": 0,
                "gross": amount,
                "amount": amount,
                "is_lump_sum": True,
            }
        )

    subtotal = money(sum((l["amount"] for l in lines), Decimal(0)))

    adj = Decimal(0)
    adjustments = []
    for a in po.get("adjustments", []):
        val = money(a.get("amount", 0))
        adjustments.append({"description": a.get("description", ""), "amount": val})
        adj += val
    net = money(subtotal + adj)

    vat_pct = Decimal(str(po.get("vat_percent", 0) or 0))
    vat = money(net * vat_pct / Decimal(100))
    total = money(net + vat)

    return lines, {
        "subtotal": subtotal,
        "adjustments": adjustments,
        "adjustments_total": money(adj),
        "net": net,
        "vat_percent": vat_pct,
        "vat": vat,
        "total": total,
    }


_ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
         "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen",
         "Eighteen", "Nineteen"]
_TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def _under_thousand(n):
    out = []
    if n >= 100:
        out += [_ONES[n // 100], "Hundred"]
        n %= 100
        if n:
            out.append("and")
    if n >= 20:
        out.append(_TENS[n // 10])
        n %= 10
    if n:
        out.append(_ONES[n])
    return out


def amount_in_words(amount, currency="AED", subunit="Fils"):
    """POs are signed on the words, not the figures -- so spell them out."""
    amount = money(amount)
    whole = int(amount)
    frac = int((amount - whole) * 100)
    if whole == 0:
        words = ["Zero"]
    else:
        words = []
        for value, name in ((10 ** 9, "Billion"), (10 ** 6, "Million"), (10 ** 3, "Thousand")):
            if whole >= value:
                words += _under_thousand(whole // value) + [name]
                whole %= value
        if whole:
            if words and whole < 100:
                words.append("and")
            words += _under_thousand(whole)
    text = "%s %s" % (currency, " ".join(words))
    if frac:
        text += " and %s %s" % (" ".join(_under_thousand(frac)), subunit)
    return text + " only"
