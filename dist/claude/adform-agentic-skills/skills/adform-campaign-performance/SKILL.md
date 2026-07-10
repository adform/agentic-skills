---
name: adform-campaign-performance
description: >-
  Campaign performance overview for Adform FLOW DSP. Portfolio-level view of campaigns
  including spend, pacing, projected delivery, budget deviation, and — via mcpStats —
  actual performance metrics such as CTR, viewability rate, video completion, and eCPM.
  For delivery health issues use adform-delivery-health; for full dimensional reporting
  use adform-stats-performance.
---

# Campaign Delivery Overview

Portfolio-level campaign delivery metrics including spend, pacing, projected delivery, and budget
deviation across all campaigns for an advertiser.

## Metrics availability

**Delivery indications** (from `campaignDeliveryIndications`):
- Current spend and budget utilization
- Pacing status and delivery projections
- Budget deviation and flight progress
- Delivery schedule status

**Performance metrics** (from `mcpStats`):
- Impressions, clicks, CTR, eCPM, cost
- Viewability rate (IAB), viewable impressions
- Video completion rate, video starts
- Conversions, eCPA, sales

For a portfolio-level delivery sweep use the delivery indications pattern below.
For performance metrics add an `mcpStats` call scoped to the same advertiser and
date range — see adform-stats-performance for the full query reference.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_search` to
look up field names; use `graphql_introspect` for complex nested types. Keep calls sequential
(~1–2s apart).

## The pattern

1. Resolve the advertiser: `advertisers(search: "name")` → get advertiser ID
2. List campaigns: `campaigns(advertisers: "$advertiserId")` → get all campaign IDs and names
3. Pull delivery per campaign: `campaignDeliveryIndications(id:)` — one call per campaign
4. Assemble, sort, and present client-side

---

## Step 1 — List campaigns

```graphql
{
  campaigns(
    advertisers: "2247935"
    limit: 50
    offset: 0
  ) {
    campaigns { id name status startDate endDate budget currency }
    totalCount
  }
}
```

## Step 2 — Campaign delivery indications

Run once per campaign ID. Returns the active budget flight state.

```graphql
{
  campaignDeliveryIndications(id: "4221341") {
    status
    goalType
    effectiveFlightTotalGoal
    effectiveFlightCurrentDelivery
    effectiveFlightProjectedDelivery
    effectiveFlightRemainingDelivery
    effectiveFlightDeviationPercentage
    effectiveFlightTotalCost
    effectiveFlightDailyCost
    effectiveBudgetFlightStartDate
    effectiveBudgetFlightEndDate
  }
}
```

**Field reference**
- `goalType`: `Money` | `Impressions` | `Clicks` | `Unlimited`
- `status`: `Active` | `ScheduleGap` | `Finished`
- `effectiveFlightDeviationPercentage` — negative = under-delivering; positive = over-delivering
- `effectiveFlightTotalCost` — monetary spend regardless of goalType

## Step 3 — Daily trend (optional)

For a day-by-day spend view across multiple campaigns (max 30-day window):

```graphql
{
  campaignDailyDeliveryIndications(
    ids: ["4221341", "4221349", "4221354"]
    from: "2026-06-01"
    until: "2026-06-11"
  ) {
    id
    deliveryDate
    deliveryIndications {
      effectiveFlightTotalCost
      effectiveFlightDailyCost
      effectiveFlightDeviationPercentage
      status
    }
  }
}
```

## Step 4 — Performance metrics per campaign (mcpStats)

Retrieve CTR, viewability, and cost efficiency metrics for the same campaign
set and date range. Validated query:

```graphql
{
  mcpStats {
    totalRowCount
    totals
    columns {
      dimensions { date { date } campaign { id } }
      metrics {
        impressions
        clicks
        ctr
        cost
        ecpm
        viewImpressionsIab
        viewImpressionsPercentIAB
        videoCompleteCount
        videoCompletionRate
        conversions
      }
    }
    rows(
      filter: {
        date: { from: "2026-06-01", to: "2026-06-30" }
        campaign: { ids: ["4221341"] }
      }
      paging: { offset: 0, limit: 100 }
      sort: [{ column: 0, direction: asc }]
    )
  }
}
```

Merge the mcpStats result with delivery indications client-side using campaign
ID as the join key.

---

## Presenting

Table with one row per campaign: name, goal type, flight dates, budget goal, current spend,
projected spend, deviation %, and status. Include an account totals row. Flag campaigns with
deviation below −20% as under-delivering and above +10% as approaching overspend. Sort by
deviation ascending to surface the largest gaps first.

For creative trafficking checks use adform-creative-discrepancy-audit. For detailed reporting
use adform-reporting.
