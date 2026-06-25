---
name: adform-deal-health-check
description: >-
  Deal delivery health check for the Adform Flow DSP. Investigate performance and delivery for deals wired to a campaign
  and flag any deal with zero or near-zero impressions caused by deal setup, pricing, or
  publisher supply problems. Trigger on "deal health check", "which deals aren't delivering",
  "deals with zero impressions", "deal delivery problems", "are my PMP deals serving". For
  deal discovery use adform-inventory-deals; for bid-versus-win curve use adform-bid-landscape.
  Read-only.
---

# Adform deal health check

Retrieves deals attached to a campaign or advertiser, pulls recent delivery metrics, and surfaces
deals with low or zero delivery alongside likely causes. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_search` to
look up field names. Keep calls sequential (~1–2s apart); retry transient errors at most twice.

---

## Step 1 — Find deals

Search deals by advertiser:

```graphql
{
  buyerDealListItems(
    filters: [{ fieldName: "buyerDeal.searchPhrase", operation: contains, values: [""] }]
    pagination: { offset: 0, limit: 50 }
  ) {
    buyerDeals {
      id dealId name type price currencyCode status startDate endDate
      inventorySource { id name }
      healthIndications { status }
      deliveryIndications {
        yesterday { transaction { bids winRate trackedAds clicks ctr ecpm } }
        last7Days { transaction { bids winRate trackedAds clicks ctr ecpm } }
      }
      assignedToLineItemsCount
    }
    totalCount
  }
}
```

## Step 2 — Check past traffic per deal

```graphql
{
  inventoryMarketplaceDealPastTraffic(
    deals: [{ inventorySourceId: "42", dealId: "12345" }]
  ) {
    dealId
    trafficCounts { cookies requests }
  }
}
```

## Step 3 — Deal group context (if applicable)

```graphql
{ buyerDealGroup(id: "12345") { id name status dealIds } }
```

---

## Reading the results

For each deal, check:
- `deliveryIndications.yesterday.transaction.trackedAds` — impressions yesterday; zero on an
  active deal signals a problem
- `healthIndications.status` — platform health flag
- `deliveryIndications.yesterday.transaction.winRate` — low win rate alongside zero impressions
  suggests pricing is below market; size a fix with adform-bid-landscape
- `assignedToLineItemsCount` — a deal with zero assignments is not yet wired to any line item

---

## Presenting

Lead with deals showing zero or near-zero delivery alongside their status and floor price. Then
show a full table of all deals with impressions, win rate %, and eCPM. Note the likely cause
for each flagged deal and a recommended next step — re-price via adform-bid-landscape, confirm
wiring via adform-line-items, or check supply via adform-past-traffic.
