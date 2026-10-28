# Where the PO sits in the DAMAC procurement chain

```
RFP            Request for Procurement raised in PMWeb (e.g. P110-RFP-PN-001)
  │            Procurement L1 → L2 → Construction Department approvals
  ▼
Tender         Formally generated once the RFP workflow is complete
  │            Bids received and levelled
  ▼
RFA            Request for Approval / award recommendation
  │
  ▼
LOA            Letter of Award issued to the successful supplier
  │            Carries the reference the PO number is derived from
  ▼
PO    ◄──── this skill
  │            Raised against the approved LOA, at the awarded rates
  ▼
Signing        Supplier stamps and signs; DAMAC countersigns (often DocuSign)
  │
  ▼
Commitment     PMWeb RFAWO record. At Step 13 of 17 the signed PO replaces the
(RFAWO)        unsigned attachment and the record proceeds to Project QS
  │            (Step 15) for cost upload.
  ▼
Delivery, invoicing, payment per the PO terms
```

## What this means for the PO you prepare

- **The PO must not invent commercial terms.** Rates, scope and the headline
  conditions were fixed at LOA. The PO records them; it does not negotiate them.
  If the PO would differ from the LOA, that is a change to be agreed and
  referenced, not a quiet edit.
- **Reference the LOA explicitly.** PMWeb matches the commitment's LOA Reference
  to the PO number. A PO that does not name its LOA is hard to close out at
  Step 13.
- **The total must agree with the RFA amount.** If it does not, stop: either the
  PO is wrong or the award has moved. Set `budget_amount` in the PO data and the
  validator will block a PO that exceeds it.
- **Supply-only vs. supply-and-fix.** Most tile orders here are supply-only.
  Retention, DLP and LD clauses usually differ between the two — check which one
  the LOA awarded before copying terms from a previous PO.

## Handover to PMWeb

Once signed, the PO is uploaded via the `pmweb-commitment-signed-po-upload`
skill: Document Manager path
`Projects › <project> › <cluster> › Internal › Commercial_Procurement › General › PO`,
then attached to the commitment and the workflow proceeded. That skill owns the
upload; this one owns producing the document.
