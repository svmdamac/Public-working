# RAK Ceramics — agreed terms

> Status: **unverified**
> Last confirmed against: _nothing yet — see "Before the first final PO" below._

RAK Ceramics is a UAE (Ras Al Khaimah) manufacturer, so this is a domestic
supply: AED, local VAT, road delivery, no import clearance. That shapes which
terms matter, but it does **not** tell us what was agreed — fill the tables from
a signed PO before issuing anything final.

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
- Shade / calibre column is required on every tile line.
- Origin column normally omitted (UAE manufacture) — add it if the order mixes
  imported items.
- Check which DAMAC entity their accounts team expects on the PO; a mismatched
  entity name against their TRN records delays invoicing.

## History
| PO ref | Project / cluster | Date | Value | Notes |
|---|---|---|---|---|
### Known previous orders

| PO ref | Project / cluster | Notes |
|---|---|---|
| see PMWeb commitment attachments | P158 Damac Lagoons / Mykonos | A signed PO exists — PMWeb showed an attachment `Mykonos PO RAKCeramics.pdf`. **This is the best source to verify terms from.** |


## Before the first final PO

The tables above are empty on purpose. Nothing in this repository has seen a
signed RAK Ceramics PO, so filling them in from general knowledge would put invented
commercial terms on a document DAMAC signs.

To populate them:

1. Find previous signed POs: `<Project folder>\<Cluster>\RAK Ceramics\Signed\`.
2. Run `python3 scripts/learn_terms.py rak-ceramics <those PDFs>`.
3. Read the candidate wording it prints, confirm it, and record it here **and**
   in `assets/suppliers.json` with `"status": "verified"` and the source PO named.
4. Anything you cannot confirm stays `unverified`. The builder will keep stamping
   DRAFT until it is resolved — which is the correct outcome, not a bug.

### Questions to settle from the signed POs

- Credit period, and whether it runs from invoice date or from delivery/GRN.
- Whether supply-only orders carry retention at all, or nil.
- Delivery basis — is offloading at site theirs or DAMAC's?
- Lead time: from PO, or from approved shade/calibre sample?
- Breakage allowance and how replacements are ordered and priced.

