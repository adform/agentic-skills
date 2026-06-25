---
name: adform-inventory-availability-forecast
description: >-
  Forward inventory availability sizing for the Adform Flow DSP.
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
    deals: [{ inventorySourceId: "42", dealId: "12345" }]
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

### Step 1 — Search open auctions by geo and format

Must provide `advertiserId` or `campaignId`. Do not pass a sort argument.

```graphql
{
  searchOpenAuctions(
    advertiserId: "71883"
    limit: 20
  ) {
    results { id name inventorySourceId inventorySourceName country channel bannerTypes sizes }
    next previous totalCount
  }
}
```

### Step 2 — Past traffic for the identified inventory sources

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

## Presenting

Deals: table with deal name, status, floor price, baseline daily requests, and projected
30-day available impressions. Open auction: table by publisher category (inventory source)
with addressable cookies and requests. Lead with the headline total and the largest sources.
State that projections extrapolate recent supply and are not guarantees.
