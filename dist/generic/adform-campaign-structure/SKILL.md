---
name: adform-campaign-structure
description: >-
  Campaign structure review for the Adform FLOW DSP. Navigate the hierarchy of advertiser,
  campaign, orders, and RTB line items, with budgets, flight dates, status, and targeting. Trigger
  on "what's in this campaign", "orders and line items under campaign X", "how is this
  campaign structured", "find the campaign for advertiser Y", "what line items
  are in here". For performance numbers use adform-campaign-performance; for optimisation
  suggestions on a plan use adform-media-plan-review. Read-only.
---

# Adform campaign structure

Walk a campaign's setup: advertiser → campaign → orders → RTB line items, with budgets, flight
dates, and status. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_search` to
look up field names; use `graphql_introspect` for complex nested types such as `RtbLineItem`
targeting and inventory. Keep calls sequential (~1–2s apart).
Build the hierarchy one level at a time rather than in a single large query.

---

## Step 1 — Find campaigns for an advertiser

```graphql
{
  campaigns(
    advertisers: "71883"
    status: Active
    offset: 0
    limit: 20
  ) {
    campaigns { id name status type subType advertiserId startDate endDate budget currency billingCode }
    totalCount
  }
}
```

## Step 2 — List orders under a campaign

```graphql
{
  orders(
    campaignId: "3993873"
    active: true
    offset: 0
    limit: 20
  ) {
    orders { id name startDate endDate budget active }
    totalCount
  }
}
```

## Step 3 — List RTB line items under an order

```graphql
{
  rtbLineItems(
    orderIds: ["67890"]
    offset: 0
    limit: 20
  ) {
    lineItems { id name rtbLineItem { id environments orderId campaignId paused deleted } }
    totalCount
  }
}
```

## Step 4 — Get a single line item's full config (optional)

```graphql
{ rtbLineItem(id: "99999") { id name environments orderId campaignId paused deleted } }
```

For full targeting and inventory detail, use `graphql_introspect` on `RtbLineItem`,
`RtbLineItemInventory`, and `RtbLineItemAudience` before selecting deeper fields.

---

## Common patterns

- **Structure review**: run steps 1–3 in sequence to map the full hierarchy
- **Single entity**: use `campaign(id:)`, `order(id:)`, or `rtbLineItem(id:)` for a focused view
- **Targeting inspection**: `rtbLineItems(orderIds:)` returns inventory and targeting inline;
  introspect nested types to select the fields you need

## Presenting

Compact structured summary: the campaign line (status, flight dates, budget, currency), then
orders, then line items grouped by order with paused/active state. Flag anything worth noting
for a setup review — paused line items, missing end dates, line items with no inventory wired.
For performance numbers use adform-campaign-performance.
