---
name: adform-inventory-availability-forecast
description: >-
  Forward inventory availability sizing for the Adform FLOW DSP.
  Forecast future supply before launch — how much inventory is available
  given any private auction types, geos, formats, categories. Trigger on "deal availability
  forecast", "size the open auction opportunity", "available impressions by deal".
  For a single line item's reach and KPI forecast use adform-reach-forecast; for an RTB
  CPM-versus-win curve use adform-bid-landscape; for observed-only volume use adform-past-traffic.
  Read-only.
---

# Adform inventory availability forecast

Projects forward supply two ways: across an advertiser's PMP deals using recent traffic as a
baseline, and across open-auction inventory filtered by geo and format. Read-only.

IDs for geo/device/content filters can be resolved via adform-classifier-lookup.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_search` to
look up field names. Keep calls sequential (~1–2s apart).

---

## Deal availability (PMP)

### Step 1 — Find the advertiser's deals

```graphql
{
  buyerDealListItems(
    pagination: { offset: 0, limit: 50 }
  ) {
    buyerDeals {
      id dealId name type price currencyCode status startDate endDate
      inventorySource { id name }
      healthIndications { status }
    }
    totalCount
  }
}
```

### Step 2 — Past traffic baseline per deal

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

Project forward: use mean daily requests from the last 30 days as a baseline for the forecast
horizon. State this is an extrapolation from observed supply.

---

## Open-auction sizing

### Step 1 — Browse available inventory sources

```graphql
{
  inventoryMarketplaceListItems(
    pagination: { offset: 0, limit: 100 }
  ) {
    inventorySources { id name adExchange { id name } channels environments }
    hasMoreItems totalCount
  }
}
```

### Step 2 — Past traffic for identified inventory sources

```graphql
{
  inventoryMarketplaceInventoryPastTraffic(inventoryIds: [42, 55]) {
    inventoryId
    trafficCounts { cookies requests }
  }
}
```

Resolve geo IDs for filtering using adform-geo-reference.

---

## Available impressions and cost via mcpInventoryStats

`mcpInventoryStats` gives publisher-side available impressions alongside cost
efficiency, which is the cheapest way to size supply and price it in one call.
Validated:

```graphql
{
  mcpInventoryStats {
    columns {
      dimensions { deal { inventoryDealId } inventorySource { id } }
      metrics { dealAvailableImpressions ecpmMediaReach ecpm }
    }
    rows(
      filter: { date: { from: "2026-09-01", to: "2026-10-06" } }
      paging: { offset: 0, limit: 50 }
      currencyCode: "EUR"
    )
    totals
  }
}
```

Like `mcpStats`, the `columns` selections return **column indices** into the
`rows` 2D array, not values. The deal dimension field is `inventoryDealId`
(there is no `id`), and `inventorySource` exposes only `id`.

**Available-impression metrics** — each counts publisher offers at a different
grouping level, so pick the one matching your dimension: `dealAvailableImpressions`,
`dealAdTypeAvailableImpressions`, `dealChannelAvailableImpressions`,
`dealEnvironmentAvailableImpressions`, `dealVastVersionAvailableImpressions`.

**Cost metrics:** `ecpm`, `ecpmMediaReach`, `ecpc`, `ecpmv`.
`ecpmMediaReach` is cost per thousand **media unique** impressions and has
**no `mcpStats` equivalent** — it is only available here. Note that none of
these take a `costType` argument, unlike their `mcpStats` namesakes, so they
cannot be qualified to RTB spend.

**Currency:** **Always ask the user which currency to use before running this
query**, unless they have already named one, and pass it as `currencyCode` on
`rows`. Do not omit it: the platform default is DKK, which can make prices look
higher than users expect. Reuse the answer for the rest of the session. Never
print a bare cost figure. See adform-stats-performance for the full currency
rules.

Deals: table with deal name, status, floor price, baseline daily requests, and projected
30-day available impressions. Open auction: table by inventory source with addressable
cookies and requests. Lead with the headline total and the largest sources.
State that projections extrapolate recent supply and are not guarantees.

Label floor prices and any eCPM figure with its currency, and name the currency you passed to
`mcpInventoryStats`. A deal's `currencyCode` need not match the currency the
cost metrics are reported in — do not mix the two in one column.
