---
name: "damac-purchase-order"
description: "Prepare DAMAC purchase orders in the standard format, applying the terms agreed with each supplier (RAK Ceramics, Al Anwar Ceramics, Graniti, Pan Europe). Use when asked to raise, draft, revise or check a PO against an LOA/award, or to record a supplier's agreed PO terms."
---

# DAMAC Purchase Order Preparation

Produces a DAMAC-format PO (Excel + PDF) from the awarded scope and rates,
applying the commercial terms agreed with that supplier, and checks it before it
goes anywhere.

A PO is a document DAMAC signs. The central rule of this skill is therefore:
**never put a commercial term on a PO that has not been confirmed.** The tooling
enforces it — any unconfirmed term forces a watermarked DRAFT.

## When to use

- "Raise a PO for RAK Ceramics on the Mykonos tiles"
- "Prepare the PO for the Graniti slabs against LOA-0312"
- "Revise PO-2489 — quantities changed"
- "Check this PO before I send it"
- "Record what we agreed with Al Anwar so the next PO picks it up"

For uploading a *signed* PO into PMWeb, use `pmweb-commitment-signed-po-upload`.
For finding the RFP/RFA/LOA the PO is raised against, use
`pmweb-procurement-lookup`.

## Before anything else: read the supplier file

`references/suppliers/<supplier>.md` — one per supplier, holding the agreed terms
and the open questions. `assets/suppliers.json` is the machine-readable version
the builder reads.

**All four suppliers currently ship `unverified`.** Nothing here has seen a signed
DAMAC PO, so no agreed terms are recorded. Until they are filled in from real
previous POs, every PO produced will be a DRAFT. Resolve that with
`scripts/learn_terms.py` (below) — not by guessing the terms.

## Workflow

### 1. Gather the award

Get the LOA (or RFA) the PO is raised against, the supplier quotation, and the
awarded rates and quantities. The PO records what was awarded — it does not
re-negotiate it. See `references/workflow.md`.

If an LOA reference is not available, say so rather than inventing one; the PO
reference is derived from it (`references/numbering.md`).

### 2. Write the PO data file

Copy `examples/sample-po.json` and edit. Fields are documented in
`references/po-format.md`. The important ones:

- `supplier_key` — one of `rak-ceramics`, `al-anwar-ceramics`, `graniti`, `pan-europe`
- `references.loa` / `loa_date` — what the PO is raised against
- `budget_amount` — the awarded RFA amount; the validator blocks a PO above it
- `line_items[]` — `description`, `unit`, `qty`, `rate`, plus `shade_calibre`
  and `origin` for tile and imported supply
- `terms_overrides` — only for a term genuinely agreed differently **on this
  order**. An override counts as verified, so use it for real instructions, never
  to silence the draft gate.

### 3. Validate

```bash
python3 scripts/validate_po.py po.json
```

- `BLOCKER` — the PO is wrong. Nothing renders until it is fixed.
- `GATE` — a term is unverified. Draft only.
- `WARN` — worth a look (missing shade/calibre, no LOA reference, near budget).

### 4. Build

```bash
python3 scripts/build_po.py po.json -o out/PO-2489.xlsx --pdf
```

Renders the full DAMAC layout and converts to PDF. If any term is unverified the
output is stamped **DRAFT / NOT FOR ISSUE** and footer-marked, with each
unconfirmed term shown as `<<< TO BE CONFIRMED >>>` in red. That is deliberate:
an incomplete PO should be obviously incomplete, not quietly plausible.

### 5. Report back

Tell the user: the total, whether it came out FINAL or DRAFT, and — if DRAFT —
exactly which terms are outstanding and where to get them. Do not describe a
draft as ready.

## Recording a supplier's terms

This is what turns drafts into final POs.

```bash
python3 scripts/learn_terms.py rak-ceramics "/path/to/Signed/"*.pdf
```

It prints the wording around every term of interest, cited by file and page, then
a JSON skeleton. **A person confirms the wording**; then record it in
`assets/suppliers.json` with `"status": "verified"` and the source PO named, and
in the supplier's `.md` file. The script never writes the registry itself.

Signed POs live at `<Project folder>\<Cluster>\<Supplier>\Signed\` on the user's
PC — reachable through Remote Control / desktop file access, not from a cloud
session. Match on PO number, not supplier name: an older superseded PO for the
same supplier may sit in the same folder.

Anything that cannot be confirmed stays `unverified`. A permanent draft is a
better outcome than a confident wrong number.

## Guardrails

- **Never invent a commercial term** — payment days, retention, LD rate, warranty
  period, Incoterm. If it is not confirmed, it renders as `<<< TO BE CONFIRMED >>>`.
- **Never invent a PO or LOA reference.** Leave it blank and flag it.
- **Never exceed the awarded amount.** The validator blocks it; do not work around
  it by removing `budget_amount`.
- **Never edit an issued PO in place** — raise a revision (`R1`, `R2`).
- **The amount in words is generated, never typed.**
- Do not send a PO to a supplier or attach it in PMWeb from this skill. Produce
  the document; the user issues it.

## Layout

```
SKILL.md
assets/
  suppliers.json     agreed terms per supplier — the builder reads this
  damac.json         DAMAC buying entity, signatories, project codes
scripts/
  po_core.py         loading, merging, money arithmetic, amount-in-words
  validate_po.py     pre-flight checks (BLOCKER / GATE / WARN)
  build_po.py        renders the PO to .xlsx, optionally .pdf
  learn_terms.py     mines previous signed POs for candidate terms
references/
  po-format.md       block-by-block anatomy of the document
  numbering.md       PO/LOA reference convention and file naming
  workflow.md        RFP → Tender → RFA → LOA → PO → PMWeb commitment
  suppliers/*.md     per-supplier agreed terms and open questions
examples/
  sample-po.json     worked example — P158 Mykonos tiles, RAK Ceramics
```

## Setting up (one-time)

Three things must be filled in before any PO can be FINAL:

1. `assets/damac.json` — the DAMAC entity's legal name, address, TRN and the
   signatory names. Take them from a previous signed PO.
2. `assets/suppliers.json` — each supplier's identity and agreed terms, via
   `learn_terms.py`.
3. Confirm the PO reference convention for the project in hand.

Until then the skill works end to end and produces correct, fully-priced DRAFTs.
