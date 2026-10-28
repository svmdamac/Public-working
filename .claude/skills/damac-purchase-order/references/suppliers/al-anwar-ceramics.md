# Al Anwar Ceramics — agreed terms

> Status: **unverified**
> Last confirmed against: _nothing yet — see "Before the first final PO" below._

Al Anwar Ceramic Tiles Co. manufactures in Sohar, Oman. Supply into the UAE is
therefore cross-border, which makes the delivery basis, customs clearance and VAT
treatment the terms most likely to differ from a domestic supplier — confirm all
three before issuing.

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
- Shade / calibre column required.
- Origin column required — cross-border supply.
- If contracted through a UAE distributor, the PO should still name the
  manufacturing mill so the warranty is traceable.

## History
| PO ref | Project / cluster | Date | Value | Notes |
|---|---|---|---|---|


## Before the first final PO

The tables above are empty on purpose. Nothing in this repository has seen a
signed Al Anwar PO, so filling them in from general knowledge would put invented
commercial terms on a document DAMAC signs.

To populate them:

1. Find previous signed POs: `<Project folder>\<Cluster>\Al Anwar\Signed\`.
2. Run `python3 scripts/learn_terms.py al-anwar-ceramics <those PDFs>`.
3. Read the candidate wording it prints, confirm it, and record it here **and**
   in `assets/suppliers.json` with `"status": "verified"` and the source PO named.
4. Anything you cannot confirm stays `unverified`. The builder will keep stamping
   DRAFT until it is resolved — which is the correct outcome, not a bug.

### Questions to settle from the signed POs

- Is DAMAC contracting with the Omani manufacturer directly, or through a UAE
  distributor? This decides the TRN, the VAT treatment and who clears customs.
- Delivery basis: DDP site, or delivered to a UAE point with DAMAC clearing?
- Does the lead time quoted include road transit from Sohar, or start on arrival?
- Is a certificate of origin required with each shipment?

