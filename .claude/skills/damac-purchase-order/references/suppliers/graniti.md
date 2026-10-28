# Graniti — agreed terms

> Status: **unverified**
> Last confirmed against: _nothing yet — see "Before the first final PO" below._

Imported porcelain / large-format slabs, Italian origin. **Confirm the exact
contracting entity first** — several suppliers trade under similar "Graniti"
names and the one on the LOA is the one the PO must name.

Imported supply changes the shape of the PO itself, not just the numbers: the
Incoterm drives who pays freight, duty and insurance; the currency may not be
AED; and shipping documents become a contractual deliverable.

## Identity
| Field | Value | Source |
|---|---|---|
| Legal name | | |
| Address | | |
| TRN | | |
| Contact | | |
| Manufacturer or trader? | | |

## Agreed terms
| Term | Agreed wording | Confirmed from | Date |
|---|---|---|---|
| Currency | | | |
| VAT | | | |
| Payment terms | | | |
| Advance payment | | | |
| Retention | | | |
| Delivery terms / Incoterm | | | |
| Lead time | | | |
| Price validity | | | |
| Samples & approval | | | |
| Breakage / wastage | | | |
| Packing & marking | | | |
| Insurance | | | |
| Title & risk | | | |
| Warranty / DLP | | | |
| Liquidated damages | | | |
| Special conditions | | | |

## Format notes
- Shade / calibre **and** Origin columns required.
- The PO needs a shipping-documents clause: commercial invoice, packing list,
  bill of lading, certificate of origin — state who sends what, to whom, and when.
- State the Incoterm in the header delivery block, not buried in the terms.
- Slab packing (A-frame / crate) should be an explicit term, not an assumption.

## History
| PO ref | Project / cluster | Date | Value | Notes |
|---|---|---|---|---|


## Before the first final PO

The tables above are empty on purpose. Nothing in this repository has seen a
signed Graniti PO, so filling them in from general knowledge would put invented
commercial terms on a document DAMAC signs.

To populate them:

1. Find previous signed POs: `<Project folder>\<Cluster>\Graniti\Signed\`.
2. Run `python3 scripts/learn_terms.py graniti <those PDFs>`.
3. Read the candidate wording it prints, confirm it, and record it here **and**
   in `assets/suppliers.json` with `"status": "verified"` and the source PO named.
4. Anything you cannot confirm stays `unverified`. The builder will keep stamping
   DRAFT until it is resolved — which is the correct outcome, not a bug.

### Questions to settle from the signed POs

- **Exact legal entity** on the previous POs.
- Currency. If EUR, how is the AED commitment value in PMWeb derived — fixed rate
  stated on the PO, or rate at payment date? State it in `additional_terms`.
- Incoterm (EXW / FOB / CIF Jebel Ali / DDP site) — everything else follows this.
- Payment: LC, advance against proforma, or credit? If an advance, is an advance
  payment bank guarantee required?
- Lead time broken into production / sea freight / clearance.
- Breakage allowance for slabs and the replacement route — a cracked slab from
  Italy is a 10-week problem, not a 2-day one.

