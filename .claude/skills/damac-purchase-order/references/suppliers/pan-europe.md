# Pan Europe — agreed terms

> Status: **unverified**
> Last confirmed against: _nothing yet — see "Before the first final PO" below._

Least is known about this supplier of the four. Before anything else, establish
whether Pan Europe is a **manufacturer or a trading/distribution house** — it
changes who carries the warranty and whether the PO needs to name the mill.

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
- Shade / calibre and Origin columns on by default until the supply route is
  confirmed; turn Origin off in `assets/suppliers.json` if they are a UAE
  manufacturer.
- If they are a trader, add a term binding them to the manufacturer's warranty
  and naming the mill.

## History
| PO ref | Project / cluster | Date | Value | Notes |
|---|---|---|---|---|


## Before the first final PO

The tables above are empty on purpose. Nothing in this repository has seen a
signed Pan Europe PO, so filling them in from general knowledge would put invented
commercial terms on a document DAMAC signs.

To populate them:

1. Find previous signed POs: `<Project folder>\<Cluster>\Pan Europe\Signed\`.
2. Run `python3 scripts/learn_terms.py pan-europe <those PDFs>`.
3. Read the candidate wording it prints, confirm it, and record it here **and**
   in `assets/suppliers.json` with `"status": "verified"` and the source PO named.
4. Anything you cannot confirm stays `unverified`. The builder will keep stamping
   DRAFT until it is resolved — which is the correct outcome, not a bug.

### Questions to settle from the signed POs

- Full legal entity name and TRN, and whether they bill from a UAE entity.
- Manufacturer or trader? If a trader: which mill, and does the manufacturer's
  warranty pass through to DAMAC?
- Currency and VAT treatment.
- Delivery basis and lead time.
- Whether previous orders were supply-only or supply-and-fix — this is the
  supplier most likely to vary between the two.

