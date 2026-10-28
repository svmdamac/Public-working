# PO reference and numbering

## The reference string

DAMAC PMWeb commitments carry a long reference of this shape, observed on live
records:

```
P158.19-NAA-SM-RD-RR-KK-PO-2489-R0
└──┬─┘ └┬┘ └──────┬──────┘ └┬┘ └─┬┘ └┬┘
   │    │         │         │    │   └── revision
   │    │         │         │    └────── sequential PO number
   │    │         │         └─────────── document type (PO / LOA / VO)
   │    │         └───────────────────── routing / approver initials
   │    └─────────────────────────────── package or sub-project segment
   └──────────────────────────────────── project code
```

The LOA for the same package shares everything except the document type and
number, e.g. `P158.19-NAA-SM-RD-RR-KK-LOA-0312`.

**Do not invent a reference.** The initials segment is routing-specific and the
sequential number is issued, not chosen. Take the reference from the approved
LOA / the PMWeb record and change only the `PO` segment and number. If you do not
have it, leave `po_reference` empty and say so — the validator raises a warning
rather than a blocker, precisely so an incomplete reference is visible instead of
fabricated.

`validate_po.py` checks the *shape* only. A reference that is well-formed but
wrong is still wrong; the shape check cannot catch that.

## Project codes seen in PMWeb

| Code | Project |
|------|---------|
| `P158` | Damac Lagoons |
| `P110` | Damac City (Al Safa Park) |
| `P106` | Damac Hills 2 |
| `BDP200.002` | Shoreline |

Extend `assets/damac.json` as you meet more. The builder does not require a
project to be listed — the list is a convenience, not a gate.

## File naming

Signed POs in the project folders follow:

```
YYYY-MM-DD - <date/ref>_<PO no>_<Supplier>.pdf
```

under `<Project folder>\<Cluster>\<Supplier>\Signed\`. Match on the **PO number**,
not on the supplier or the date: an earlier PO for the same supplier and cluster
may exist and have been terminated by the newer one.
