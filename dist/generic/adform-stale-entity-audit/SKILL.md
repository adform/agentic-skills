---
name: adform-stale-entity-audit
description: >-
  Governance audit for stale and orphaned entities on the Adform Flow DSP.
  Audit governance issues that risk budget leakage —
  campaigns past their end date but still active, and RTB line items whose parent order is inactive
  or ended but the line item is still live. Trigger on "campaigns ended but still active",
  "line items without an active order", "stale entity audit", "budget leakage". For a single pacing use
  adform-pacing-check; for delivery blockers use adform-delivery-health. Read-only.
---

# Adform stale and orphaned entity audit

Two account hygiene sweeps: campaigns whose end date has passed but whose status is still
active, and RTB line items still active under an inactive or ended order. Both present budget
and governance risk. Read-only — remediation (pause or close) is the user's action.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Keep calls sequential
(~1–2s apart); retry transient errors at most twice.

---

## Sweep 1 — Campaigns past their end date

List active campaigns and compare each `endDate` to today:

```graphql
{
  campaigns(
    advertisers: "71883"
    status: Active
    offset: 0
    limit: 50
  ) {
    campaigns { id name status startDate endDate budget currency }
    totalCount
  }
}
```

Flag any campaign where `endDate` is before today. Check whether it is still spending:

```graphql
{
  campaignDeliveryIndications(id: "3993873") {
    status
    effectiveFlightDailyCost
    effectiveFlightTotalCost
  }
}
```

A non-zero `effectiveFlightDailyCost` means the campaign is still spending after its end date.

---

## Sweep 2 — Orphaned RTB line items

Find inactive or ended orders, then check whether any of their line items are still active:

```graphql
{
  orders(
    campaignId: "3993873"
    active: false
    offset: 0
    limit: 20
  ) {
    orders { id name startDate endDate active }
    totalCount
  }
}
```

List line items under those orders:

```graphql
{
  rtbLineItems(
    orderIds: ["67890"]
    paused: false
    offset: 0
    limit: 20
  ) {
    lineItems { id name rtbLineItem { id paused deleted orderId } }
    totalCount
  }
}
```

Check whether any unpaused line item is still spending:

```graphql
{
  rtbLineItemDeliveryIndications(id: "99999") {
    status
    effectiveFlightDailyCost
  }
}
```

---

## Presenting

Two tables. Ghost campaigns: ID, name, end date, days overdue, still spending (daily cost).
Orphaned line items: ID, name, parent order, order status, still spending. Lead with anything
still incurring cost. Frame each row as an action item — pause or close — for the ops owner.
