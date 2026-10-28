#!/usr/bin/env python3
"""Render a DAMAC purchase order from PO data.

    python3 build_po.py po.json -o out/PO-2489.xlsx [--draft] [--pdf]

Produces the DAMAC PO layout: header block, both parties, references, the
priced schedule, totals with VAT and amount in words, the supplier's agreed
terms, and the signature block. Unverified terms render as a visible
placeholder and force a DRAFT watermark -- a PO never goes out quietly
carrying a guess.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.pagebreak import Break

from po_core import (TERM_ORDER, amount_in_words, compute, load_json,
                     load_registry, resolve_supplier, term_value)
from validate_po import validate

THIN = Side(style="thin", color="A6A6A6")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HDR_FILL = PatternFill("solid", fgColor="1F3864")
SUB_FILL = PatternFill("solid", fgColor="D9E2F3")
WARN_FILL = PatternFill("solid", fgColor="FFF2CC")
TOTAL_FILL = PatternFill("solid", fgColor="EDEDED")
MISSING = "<<< TO BE CONFIRMED >>>"

COLS = [
    ("item", "Item", 7),
    ("description", "Description", 46),
    ("spec", "Specification / Ref.", 24),
    ("shade_calibre", "Shade / Calibre", 15),
    ("origin", "Origin", 13),
    ("unit", "Unit", 8),
    ("qty", "Qty", 11),
    ("rate", "Rate", 13),
    ("discount_percent", "Disc %", 8),
    ("amount", "Amount", 15),
]


def _v(term, default=MISSING):
    val, status, _ = term_value(term)
    if val in (None, ""):
        return default, False
    return val, status == "verified"


class Sheet:
    def __init__(self, ws, ncols):
        self.ws = ws
        self.n = ncols
        self.r = 1

    def span(self, text, *, bold=False, size=11, fill=None, color=None,
             height=None, align="left", border=False, start=1, end=None):
        end = end or self.n
        ws = self.ws
        ws.merge_cells(start_row=self.r, start_column=start, end_row=self.r, end_column=end)
        c = ws.cell(row=self.r, column=start, value=text)
        c.font = Font(bold=bold, size=size, color=color or "000000")
        c.alignment = Alignment(horizontal=align, vertical="center", wrap_text=True)
        if fill:
            for col in range(start, end + 1):
                ws.cell(row=self.r, column=col).fill = fill
        if border:
            for col in range(start, end + 1):
                ws.cell(row=self.r, column=col).border = BOX
        if height:
            ws.row_dimensions[self.r].height = height
        self.r += 1
        return c

    def width_of(self, col, span):
        return sum(self.ws.column_dimensions[get_column_letter(c)].width or 10
                   for c in range(col, col + span))

    def fit(self, text, chars_per_line, *, minimum=14.0, per_line=12.0):
        """Merged cells do not auto-fit, so estimate the height we need."""
        lines = 1
        for para in str(text or "").split("\n"):
            lines = max(lines, 0) + max(1, -(-len(para) // max(8, int(chars_per_line))))
        lines -= 1 if len(str(text or "").split("\n")) > 1 else 0
        return max(minimum, lines * per_line + 3)

    def pair(self, label, value, *, col=1, width=3, flag=False):
        """A label/value pair occupying `width` columns from `col`, one row tall.

        The label claims as many columns as it needs to stay on one line --
        the schedule columns are sized for figures, not for prose labels.
        """
        ws = self.ws
        lspan = 1
        while (lspan + 1 < width and self.width_of(col, lspan) < len(str(label)) * 1.15):
            lspan += 1
        if lspan > 1:
            ws.merge_cells(start_row=self.r, start_column=col,
                           end_row=self.r, end_column=col + lspan - 1)
        lc = ws.cell(row=self.r, column=col, value=label)
        lc.font = Font(bold=True, size=9)
        lc.alignment = Alignment(vertical="top", wrap_text=True)
        ws.merge_cells(start_row=self.r, start_column=col + lspan,
                       end_row=self.r, end_column=col + width - 1)
        vc = ws.cell(row=self.r, column=col + lspan, value=value)
        vc.alignment = Alignment(vertical="top", wrap_text=True)
        vc.font = Font(size=9, color="C00000" if flag else "000000")
        if flag:
            vc.fill = WARN_FILL
        need = self.fit(value, self.width_of(col + lspan, width - lspan) * 1.05,
                        minimum=13.0, per_line=11.0)
        cur = ws.row_dimensions[self.r].height or 0
        ws.row_dimensions[self.r].height = max(cur, need)
        self.r += 1
        return vc

    def blank(self, height=6):
        self.ws.row_dimensions[self.r].height = height
        self.r += 1


def build(po, out_path, draft=False, make_pdf=False):
    registry, damac = load_registry()
    key, supplier = resolve_supplier(po, registry)
    issues, lines, totals = validate(po, registry, damac, final=not draft)

    blockers = [m for s, m in issues if s == "BLOCKER"]
    if blockers:
        raise SystemExit("BLOCKED -- not rendering:\n  - " + "\n  - ".join(blockers))
    gates = [m for s, m in issues if s == "GATE"]
    is_draft = draft or bool(gates)

    entity_key = po.get("buyer_entity_key") or damac["default_entity_key"]
    entity = damac["entities"][entity_key]
    cur = po.get("currency", "AED")

    # Only show columns the supplier's format calls for and that carry data.
    fmt = supplier.get("format", {})
    cols = []
    for field, title, width in COLS:
        if field == "shade_calibre" and not (
                fmt.get("requires_shade_calibre_column") or any(l.get(field) for l in lines)):
            continue
        if field == "origin" and not (
                fmt.get("requires_origin_column") or any(l.get(field) for l in lines)):
            continue
        if field == "spec" and not any(l.get(field) for l in lines):
            continue
        if field == "discount_percent" and not any(l.get(field) for l in lines):
            continue
        cols.append((field, title, width))

    wb = Workbook()
    ws = wb.active
    ws.title = "Purchase Order"
    n = len(cols)
    for i, (_f, _t, w) in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    s = Sheet(ws, n)

    # --- Header -----------------------------------------------------------
    ent_name, ent_ok = _v(entity.get("legal_name"))
    s.span(ent_name, bold=True, size=15, fill=HDR_FILL, color="FFFFFF",
           align="center", height=26)
    ent_addr, _ = _v(entity.get("address"), "")
    ent_trn, _ = _v(entity.get("trn"), "")
    s.span(" | ".join(x for x in (ent_addr, "TRN: %s" % ent_trn if ent_trn else "") if x),
           size=9, align="center")
    s.span("PURCHASE ORDER" + ("  -  DRAFT / NOT FOR ISSUE" if is_draft else ""),
           bold=True, size=14, fill=SUB_FILL, align="center", height=24)
    if is_draft:
        s.span("DRAFT -- contains terms not yet verified against a signed PO. "
               "Do not send to the supplier or attach in PMWeb.",
               size=9, color="C00000", align="center", fill=WARN_FILL)
    s.blank()

    half = max(2, n // 2)
    proj = po.get("project", {})
    proj_label = " / ".join(x for x in (proj.get("code"), proj.get("name"),
                                        proj.get("cluster"), proj.get("building")) if x)
    refs = po.get("references") or {}

    left = [
        ("PO No.", po.get("po_number", MISSING)),
        ("PO Reference", po.get("po_reference", "")),
        ("PO Date", po.get("po_date", MISSING)),
        ("Revision", po.get("revision", "R0")),
        ("Project", proj_label),
    ]
    right = [
        ("LOA Ref.", refs.get("loa", "")),
        ("LOA Date", refs.get("loa_date", "")),
        ("RFP / RFA", " / ".join(x for x in (refs.get("rfp"), refs.get("rfa")) if x)),
        ("Quotation", " / ".join(x for x in (refs.get("quotation"), refs.get("quotation_date")) if x)),
        ("Currency", cur),
    ]
    top = s.r
    for label, val in left:
        s.pair(label, val, col=1, width=half)
    s.r = top
    for label, val in right:
        s.pair(label, val, col=half + 1, width=n - half)
    s.r = top + max(len(left), len(right))
    s.blank()

    # --- Parties ----------------------------------------------------------
    s.span("SUPPLIER", bold=True, size=10, fill=SUB_FILL, border=True, start=1, end=half)
    s.r -= 1
    s.span("DELIVER TO", bold=True, size=10, fill=SUB_FILL, border=True,
           start=half + 1, end=n)
    sup_name, sup_ok = _v(supplier.get("legal_name"), supplier.get("display_name", MISSING))
    sup_addr, sup_addr_ok = _v(supplier.get("address"))
    sup_trn, sup_trn_ok = _v(supplier.get("trn"))
    sup_contact, _ = _v(supplier.get("contact"), "")
    deliv = po.get("delivery", {})

    sup_rows = [("Name", sup_name, not sup_ok), ("Address", sup_addr, not sup_addr_ok),
                ("TRN", sup_trn, not sup_trn_ok), ("Contact", sup_contact, False)]
    del_rows = [("Site", deliv.get("site", MISSING), not deliv.get("site")),
                ("Incoterm / Basis", deliv.get("incoterm", ""), False),
                ("Required On Site", deliv.get("required_on_site", ""), False),
                ("Delivery Programme", deliv.get("programme", ""), False)]
    top = s.r
    for label, val, flag in sup_rows:
        s.pair(label, val, col=1, width=half, flag=flag)
    s.r = top
    for label, val, flag in del_rows:
        s.pair(label, val, col=half + 1, width=n - half, flag=flag)
    s.r = top + max(len(sup_rows), len(del_rows))
    s.blank()

    # --- Priced schedule --------------------------------------------------
    s.span("SCHEDULE OF SUPPLY", bold=True, size=10, fill=SUB_FILL, border=True)
    hdr = s.r
    for i, (_f, title, _w) in enumerate(cols, 1):
        c = ws.cell(row=hdr, column=i, value=title)
        c.font = Font(bold=True, size=9, color="FFFFFF")
        c.fill = HDR_FILL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BOX
    ws.row_dimensions[hdr].height = 28
    s.r += 1

    for idx, line in enumerate(lines, 1):
        for i, (field, _t, _w) in enumerate(cols, 1):
            if field == "item":
                val = line.get("item", idx)
            elif field == "amount":
                val = float(line["amount"])
            elif field in ("rate", "qty"):
                val = float(line.get(field, 0) or 0)
            elif field == "discount_percent":
                val = (line.get(field) or 0) / 100.0
            else:
                val = line.get(field, "")
            c = ws.cell(row=s.r, column=i, value=val)
            c.border = BOX
            c.font = Font(size=9)
            if field in ("rate", "amount"):
                c.number_format = '#,##0.00'
                c.alignment = Alignment(horizontal="right", vertical="top")
            elif field == "qty":
                c.number_format = '#,##0.00'
                c.alignment = Alignment(horizontal="right", vertical="top")
            elif field == "discount_percent":
                c.number_format = '0.0%'
                c.alignment = Alignment(horizontal="center", vertical="top")
            elif field in ("item", "unit", "shade_calibre", "origin"):
                c.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
            else:
                c.alignment = Alignment(vertical="top", wrap_text=True)
        tallest = 15.0
        for field in ("description", "spec"):
            if any(f == field for f, _t, _w in cols):
                i = [f for f, _t, _w in cols].index(field) + 1
                tallest = max(tallest, s.fit(line.get(field, ""),
                                             s.width_of(i, 1) * 1.05,
                                             minimum=15.0, per_line=11.0))
        ws.row_dimensions[s.r].height = tallest
        s.r += 1

    # --- Totals -----------------------------------------------------------
    amt_col = n
    lbl_start = max(1, n - 3)

    def total_row(label, value, *, bold=False, pct=None):
        ws.merge_cells(start_row=s.r, start_column=lbl_start, end_row=s.r, end_column=amt_col - 1)
        lc = ws.cell(row=s.r, column=lbl_start, value=label)
        lc.font = Font(bold=bold or True, size=9)
        lc.alignment = Alignment(horizontal="right", vertical="top")
        lc.fill = TOTAL_FILL
        vc = ws.cell(row=s.r, column=amt_col, value=float(value))
        vc.number_format = '#,##0.00'
        vc.font = Font(bold=bold, size=10 if bold else 9)
        vc.alignment = Alignment(horizontal="right", vertical="top")
        vc.fill = TOTAL_FILL
        vc.border = BOX
        lc.border = BOX
        s.r += 1

    total_row("Sub-total (%s)" % cur, totals["subtotal"])
    for a in totals["adjustments"]:
        total_row(a["description"] or "Adjustment", a["amount"])
    if totals["adjustments"]:
        total_row("Net (%s)" % cur, totals["net"])
    total_row("VAT @ %s%%" % totals["vat_percent"].normalize(), totals["vat"])
    total_row("TOTAL PO VALUE (%s)" % cur, totals["total"], bold=True)

    s.span("Amount in words:  " + amount_in_words(totals["total"], cur),
           bold=True, size=10, border=True, height=20)
    s.blank()

    # --- Agreed terms -----------------------------------------------------
    s.span("TERMS & CONDITIONS -- as agreed with %s" % supplier.get("display_name", key),
           bold=True, size=10, fill=SUB_FILL, border=True)
    terms = supplier.get("terms", {})
    for field, label in TERM_ORDER:
        val, status, hint = term_value(terms.get(field))
        missing = val in (None, "")
        text = MISSING + (" (%s)" % hint if hint else "") if missing else str(val)
        if not missing and status != "verified":
            text += "   [UNVERIFIED]"
        s.pair(label, text, col=1, width=n, flag=missing or status != "verified")

    extra = po.get("additional_terms") or []
    if extra:
        s.blank()
        s.span("ADDITIONAL CONDITIONS FOR THIS ORDER", bold=True, size=10,
               fill=SUB_FILL, border=True)
        for i, t in enumerate(extra, 1):
            s.pair("%d." % i, t, col=1, width=n)

    notes = po.get("notes") or []
    if notes:
        s.blank()
        s.span("NOTES", bold=True, size=10, fill=SUB_FILL, border=True)
        for i, t in enumerate(notes, 1):
            s.pair("%d." % i, t, col=1, width=n)

    # --- Signatures -------------------------------------------------------
    # The acceptance block goes on its own page: it must never split across a
    # page break, and DocuSign fields are placed against a predictable last page.
    ws.row_breaks.append(Break(id=s.r - 1))
    s.span("ACCEPTANCE", bold=True, size=10, fill=SUB_FILL, border=True)
    block = list(entity.get("signatory_block") or [])
    block.append({"role": "Accepted by Supplier (sign & stamp)", "name": None,
                  "title": supplier.get("display_name", key)})
    per = max(1, n // len(block))
    top = s.r
    for i, sig in enumerate(block):
        c0 = 1 + i * per
        c1 = n if i == len(block) - 1 else c0 + per - 1
        ws.merge_cells(start_row=top, start_column=c0, end_row=top, end_column=c1)
        c = ws.cell(row=top, column=c0, value=sig.get("role", ""))
        c.font = Font(bold=True, size=9)
        ws.merge_cells(start_row=top + 1, start_column=c0, end_row=top + 1, end_column=c1)
        nm = ws.cell(row=top + 1, column=c0, value=sig.get("name") or "")
        nm.font = Font(size=9)
        ws.merge_cells(start_row=top + 2, start_column=c0, end_row=top + 2, end_column=c1)
        ti = ws.cell(row=top + 2, column=c0, value=sig.get("title") or "")
        ti.font = Font(size=8, italic=True)
        ws.merge_cells(start_row=top + 4, start_column=c0, end_row=top + 4, end_column=c1)
        for col in range(c0, c1 + 1):
            ws.cell(row=top + 4, column=col).border = Border(top=THIN)
        ws.merge_cells(start_row=top + 5, start_column=c0, end_row=top + 5, end_column=c1)
        sg = ws.cell(row=top + 5, column=c0, value="Signature & Date")
        sg.font = Font(size=8, color="808080")
    s.r = top + 7

    ws.print_area = "A1:%s%d" % (get_column_letter(n), s.r)
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    if len(lines) > 15:
        ws.print_title_rows = "%d:%d" % (hdr, hdr)
    ws.freeze_panes = ws.cell(row=hdr + 1, column=1)
    ws.oddFooter.center.text = "%s  |  Page &P of &N%s" % (
        po.get("po_number", ""), "  |  DRAFT" if is_draft else "")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    wb.save(out_path)

    made = [out_path]
    if make_pdf:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir",
             os.path.dirname(os.path.abspath(out_path)), out_path],
            check=True, capture_output=True, timeout=180)
        made.append(os.path.splitext(out_path)[0] + ".pdf")

    return made, is_draft, issues, totals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("po_json")
    ap.add_argument("-o", "--out", required=True, help="output .xlsx path")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--pdf", action="store_true")
    args = ap.parse_args()

    made, is_draft, issues, totals = build(
        load_json(args.po_json), args.out, draft=args.draft, make_pdf=args.pdf)

    gates = [m for s, m in issues if s == "GATE"]
    warns = [m for s, m in issues if s == "WARN"]
    for m in warns:
        print("WARN     %s" % m)
    for m in gates:
        print("GATE     %s" % m)
    print("\n%s written: %s" % ("DRAFT" if is_draft else "FINAL", ", ".join(made)))
    print("Total: %s %s" % (totals["total"], load_json(args.po_json).get("currency")))
    if is_draft:
        print("\nThis is a DRAFT: %d term(s) unverified. Confirm them against a signed PO, "
              "update assets/suppliers.json, then re-run for a final." % len(gates))
    return 0


if __name__ == "__main__":
    sys.exit(main())
