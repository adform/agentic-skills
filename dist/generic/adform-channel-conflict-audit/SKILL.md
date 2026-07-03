---
name: adform-channel-conflict-audit
description: >-
  Direct-versus-RTB channel conflict audit for the Adform FLOW DSP.
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
sequential (~1–2s apart).

---

## Step 1 — List RTB line items under the order

```graphql
{
  rtbLineItems(
    orderIds: ["67890"]
    offset: 0
    limit: 20
  ) {
    lineItems { id name environments orderId campaignId paused }
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

The `id` is the RTB setup ID returned by `rtbLineItems()`, not the placement ID.

```graphql
{ rtbLineItem(id: "99999") { id targetings { id name bidMultiplier } inventories { id buyingType } } }
```

Resolve domain targeting list IDs to actual domains:

```graphql
{ rtbTargetingListDomains(id: "12345", pagination: { offset: 0, limit: 100 }) { domains { name bidMultiplier } totalCount } }
```

## Step 4 — Delivery confirmation

Only flag as a conflict when both sides are actively delivering in the same time window. Check
delivery indications for each line item:

```graphql
{ rtbLineItemDeliveryIndications(id: "99999") { status effectiveFlightDailyCost } }
```

## Step 5 — Quantify conflict with mcpStats domain breakdown

Step 4 confirms both sides are live. Use mcpStats to pull actual impression
volume by domain for the RTB line item to measure how much inventory is being
won on the conflicting domains. Validated query:

```graphql
{
  mcpStats {
    totalRowCount
    totals
    columns {
      dimensions { rtbDomain { name } }
      metrics {
        impressions
        clicks
        cost
        ecpm
        rtbBids
        rtbWinRate
      }
    }
    rows(
      filter: {
        date: { from: "2026-06-01", to: "2026-06-30" }
        advertiser: { ids: ["2133936"] }
      }
      paging: { offset: 0, limit: 100 }
      sort: [{ column: 1, direction: desc }]
    )
  }
}
```

Filter the result client-side to only the domains identified as overlapping in
Step 3. The impression volume on those domains is the quantity of inventory
where self-competition is occurring. Include this in the conflict table as
"impressions at risk" alongside the cost figure to communicate business impact.

---

## Method

1. Gather direct and RTB line items under the order; retain only those currently delivering
2. Compare targeting: shared domains (resolve both lists), overlapping audience segment IDs,
   overlapping placements
3. Flag only intersections where both sides show active delivery — that is the real conflict

## Presenting

Conflict table: the direct line item, the RTB line item, the overlap dimension
(domains, audience, or placement), whether both are currently live, impressions
at risk (from mcpStats domain breakdown), and cost at risk. Lead with overlaps
where both sides are delivering. Quantify the scale of self-competition using the
mcpStats impression count on conflicting domains. Recommend de-duplicating
targeting to eliminate self-competition.
