# Anatomy of a DAMAC purchase order

The builder renders these blocks in this order. Keep the order — reviewers and
the PMWeb commitment record read them positionally.

| # | Block | Contents | Source |
|---|-------|----------|--------|
| 1 | Letterhead | DAMAC buying entity, address, TRN | `assets/damac.json` |
| 2 | Title | `PURCHASE ORDER`, plus a DRAFT banner when any term is unverified | builder |
| 3 | Order identity | PO No., PO Reference, PO Date, Revision, Project / Cluster | PO data |
| 4 | Source documents | LOA ref + date, RFP / RFA, supplier quotation + date, Currency | PO data `references` |
| 5 | Parties | Supplier legal name, address, TRN, contact / Delivery site, Incoterm, required-on-site date, programme | registry + PO data |
| 6 | Schedule of supply | Priced line items | PO data |
| 7 | Totals | Sub-total, adjustments, net, VAT, total, **amount in words** | computed |
| 8 | Terms | The supplier's agreed terms, in a fixed order | `assets/suppliers.json` |
| 9 | Additional conditions | Order-specific clauses | PO data `additional_terms` |
| 10 | Notes | Non-contractual notes | PO data `notes` |
| 11 | Acceptance | DAMAC signatories + supplier sign & stamp — always on its own page | `assets/damac.json` |

## Rules that are not negotiable

- **The amount in words governs.** It is generated from the computed total, never
  typed. If the figures and the words disagree, the document is wrong.
- **VAT is always shown separately**, as a stated percentage and an amount, even
  when zero-rated. Never fold it into rates.
- **One currency per PO.** Mixing currencies in one schedule breaks the PMWeb
  commitment value. If a supplier quotes in EUR and DAMAC commits in AED, agree
  the conversion, state the rate and date in `additional_terms`, and price the
  schedule in the single PO currency.
- **Every line carries a unit.** `m2` for tiles and slabs, `LM` for skirting and
  trims, `Nos` for sanitaryware and fittings, `LS` for lump sums.
- **The acceptance block never splits across a page.** The builder forces a page
  break before it, so the signature page is always the last page — which is
  where the DocuSign fields get placed.

## Columns in the schedule

The builder shows a column only when the supplier's format calls for it or when
some line carries data for it. Imported supply gets an `Origin` column; tile
supply gets `Shade / Calibre`. This matters: a tile PO without shade and calibre
is the single most common cause of a delivery being rejected on site.

## Revisions

A PO that has been issued is never edited in place. Raise `R1`, `R2`, … in the
`revision` field, keep the same PO number, and state what changed in
`additional_terms`. The superseded PO stays in the project folder; when the new
one is signed it replaces the old attachment on the PMWeb commitment (see
`references/workflow.md`).
