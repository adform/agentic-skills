---
name: adform-deal-health-check
description: >-
  Deal delivery health check for the Adform FLOW DSP. Investigate performance and delivery for deals wired to a campaign
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
look up field names. Keep calls sequential (~1–2s apart).

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
    deals: [{ inventoryId: 42, dealId: "12345" }]
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

## Step 4 — Confirm deal performance via mcpStats

After identifying deals with low delivery in Step 1, pull actual performance
stats per deal ID from mcpStats to get CTR, eCPM, and win rate as reported
metrics (rather than delivery indications). Validated query:

```graphql
{
  mcpStats {
    totalRowCount
    totals
    columns {
      dimensions { rtbDeal { id } campaign { currencyName } }
      metrics {
        impressions
        clicks
        cost(costType: rtb)
        ecpm(costType: rtb)
        rtbBids
        rtbWinRate
        rtbMediaCost
      }
    }
    rows(
      filter: {
        date: { from: "2026-06-01", to: "2026-06-30" }
        advertiser: { ids: ["2133936"] }
      }
      paging: { offset: 0, limit: 50 }
      sort: [{ column: 1, direction: desc }]
    )
  }
}
```

Cross-reference the `rtbDeal.id` values in the result against the deal IDs from
Step 1. A deal present in Step 1 but absent from mcpStats rows (or with zero
impressions after metric post-filtering) confirms zero delivery. Use
`rtbWinRate` to distinguish a pricing problem (low win rate, non-zero bids) from
a supply problem (zero bids).

> **Cost and currency.** `cost` and `ecpm` take a `costType` argument with no
> documented default; `rtb` is used above because deals are RTB buys. State the
> `costType` whenever you report either figure. Costs come back in campaign
> currency only, hence the `campaign { currencyName }` dimension — label every
> figure with it. Note that the deal's own `currencyCode` from Step 1 describes
> the deal's floor price and need not match the buying campaign's currency, so
> do not compare a floor price against an eCPM without checking both. Never
> present `rtbMediaCost` as total spend — it is inventory cost only, excluding
> Adform, trading desk, rich media, brand safety, contextual and ID Fusion
> fees. See adform-stats-performance for the full cost reference.

---

## Reading the results

For each deal, check:
- `deliveryIndications.yesterday.transaction.trackedAds` — impressions yesterday; zero on an
  active deal signals a problem
- `healthIndications.status` — platform health flag
- `deliveryIndications.yesterday.transaction.winRate` — low win rate alongside zero impressions
  suggests pricing is below market; size a fix with adform-bid-landscape
- `assignedToLineItemsCount` — a deal with zero assignments is not yet wired to any line item;
  `deliveryIndications` and `healthIndications` will be null in this case
- Use Step 4 (mcpStats) to confirm zero delivery with actual reported metrics
  rather than relying on delivery indications alone — the two sources together
  provide higher confidence in the diagnosis

---

## Presenting

Lead with deals showing zero or near-zero delivery alongside their status and floor price. Then
show a full table of all deals with impressions, win rate %, and eCPM. Note the likely cause
for each flagged deal and a recommended next step — re-price via adform-bid-landscape, confirm
wiring via adform-line-items, or check supply via adform-past-traffic.

Label floor prices and eCPM figures with their currency, and name the `costType` used for any
cost or eCPM column.
