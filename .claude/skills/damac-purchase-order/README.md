# DAMAC Purchase Order agent

A Claude Code skill that prepares DAMAC-format purchase orders and applies the
commercial terms agreed with each supplier.

Start with [`SKILL.md`](SKILL.md). Quick run:

```bash
cd .claude/skills/damac-purchase-order/scripts
python3 validate_po.py ../examples/sample-po.json
python3 build_po.py   ../examples/sample-po.json -o /tmp/PO-2489.xlsx --pdf
```

**It ships with no agreed terms recorded.** The four supplier profiles —
RAK Ceramics, Al Anwar Ceramics, Graniti, Pan Europe — carry the correct fields,
the questions each supplier's supply route raises, and `unverified` placeholders.
Every PO therefore comes out as a watermarked DRAFT until the real terms are read
off previous signed POs with `scripts/learn_terms.py` and recorded.

That is the design, not an omission: the terms were agreed in documents this
repository has never seen, and a guessed payment term or LD rate on a PO DAMAC
signs is a commercial problem, not a formatting one.

Requires Python 3 with `openpyxl` (and `pdfplumber` for `learn_terms.py`);
`soffice` for `--pdf`.
