---
name: adform-bid-landscape
description: >-
  RTB bid-landscape forecast for the Adform FLOW DSP. Shows the CPM-versus-win-rate curve for an RTB line item —
  auction win share at each CPM and the reachable unique cookies and bid requests. Trigger on
  "what CPM do I need to win X percent of auctions", "bid landscape", "win rate at this CPM",
  "is my bid high enough", "how many cookies can this line item reach".
  For plan-level impressions and KPIs use adform-reach-forecast; for observed recent volume use
  adform-past-traffic. Read-only.
---

# Adform bid landscape

The CPM-versus-win-rate curve for an RTB line item: what share of auctions you win at each CPM,
plus reachable cookies and requests. Use this to answer "what CPM do I need to win X%". Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute(query, variables)` to run and
`graphql_validate` to check a query first. Always validate before executing. The queries below are
**illustrative examples** — if a field or input shape isn't shown, or a query fails validation,
discover the current schema with `graphql_search` (lighter, preferred) and fall back to
`graphql_introspect` one call at a time with ≥2s between calls for complex input types, enum
values, or union/interface resolution.

---

## Building the input

`rtbLineItemForecasting(lineItem: ForecastingRtbLineItemInput!)` needs a complete line-item
shape. Build it by reading the live line item first, then mirroring its targeting, inventory,
pricing, periods, and environments into the input.

## Method

1. Read the live line item using `rtbLineItem(id:)` (the `id` is the RTB setup ID from `rtbLineItems()`, not the placement ID) to get current targeting, inventory, and pricing
2. Mirror the complete line item structure into the `ForecastingRtbLineItemInput` payload
3. Run `rtbLineItemForecasting` with the mirrored input
4. Pair `cpms` and `winRates` arrays by index to read the CPM-vs-win-rate curve

## Inline execute examples

### Read the live line item

```graphql
{
  rtbLineItem(id: "99999") {
    id name environments orderId campaignId
    inventories { id buyingType deals { id bidPrice } }
    targetings { id name bidMultiplier }
  }
}
```

### Run the forecast

```graphql
{
  rtbLineItemForecasting(lineItem: {
    name: "Forecast"
    campaignId: "3993873"
    # mirror the full targeting and inventory from the live line item
  }) {
    cpms
    winRates
    reachableCookies
    reachableRequests
  }
}
```

`cpms` and `winRates` are parallel arrays — pair index N of `cpms` with index N of `winRates`
to read the curve.

---

## Presenting

Lead with the actionable answer: the CPM needed to hit the trader's target win rate (interpolate
the curve), then show the full curve as context, and the reachable cookies and requests for
inventory sizing. State that forecasts are estimates and cross-check with adform-past-traffic if
volume looks unexpected.
