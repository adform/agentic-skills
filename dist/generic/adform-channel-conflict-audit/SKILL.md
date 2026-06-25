---
name: adform-channel-conflict-audit
description: >-
  Direct-versus-RTB channel conflict audit for the Adform Flow DSP.
  Detect overlapping inventory between direct line items and RTB line items under the
  same campaign. Trigger on "channel conflict", "direct vs RTB overlap", "are direct and programmatic
  competing", "same inventory targeted twice", "internal auction conflict", "direct and RTB
  targeting the same domains". For full line-item config use adform-line-items. Read-only.
---

# Adform direct-versus-RTB channel conflict audit

Compares the targeting of direct and RTB line items under a campaign to surface overlap on the
same domains, audiences, or placements where both types are delivering simultaneously. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_introspect`
on `RtbLineItemAudience` and `DirectLineItem` to discover targeting field shapes. Keep calls
sequential (~1–2s apart); retry transient errors at most twice.

---

## Step 1 — List RTB line items under the order

```graphql
{
  rtbLineItems(
    orderIds: ["67890"]
    offset: 0
    limit: 20
  ) {
    lineItems { id name rtbLineItem { id environments orderId campaignId paused } }
    totalCount
  }
}
```

## Step 2 — List direct line items under the order

```graphql
{
  directLineItems(
    orderId: "67890"
    pagination: { offset: 0, limit: 20 }
  ) {
    directLineItems { id name status }
    totalCount
  }
}
```

## Step 3 — Get targeting detail for each

For RTB line items, use `graphql_introspect` on `RtbLineItemAudience` to select targeting
rules including domains, audience segments, and locations:

```graphql
{ rtbLineItem(id: "99999") { id targetings { id name bidMultiplier } inventories { id buyingType } } }
```

Resolve domain targeting list IDs to actual domains using adform-targeting-segments.

## Step 4 — Delivery confirmation

Only flag as a conflict when both sides are actively delivering in the same time window. Check
delivery indications for each line item:

```graphql
{ rtbLineItemDeliveryIndications(id: "99999") { status effectiveFlightDailyCost } }
```

---

## Method

1. Gather direct and RTB line items under the order; retain only those currently delivering
2. Compare targeting: shared domains (resolve both lists), overlapping audience segment IDs,
   overlapping placements
3. Flag only intersections where both sides show active delivery — that is the real conflict

## Presenting

Conflict table: the direct line item, the RTB line item, the overlap dimension (domains,
audience, or placement), and whether both are currently live. Lead with overlaps where both
sides are delivering. Recommend de-duplicating targeting to eliminate self-competition.
