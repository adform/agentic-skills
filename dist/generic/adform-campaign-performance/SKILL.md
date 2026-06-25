---
name: adform-campaign-performance
description: >-
  Campaign delivery overview for Adform Flow DSP. Portfolio-level view of campaign delivery
  including spend, pacing, projected delivery, and budget deviation. **Important:** This provides
  delivery metrics only - performance metrics like CTR, viewability, or eCPM are not available
  through this system. For delivery health issues use delivery health checks; for creative details
  use creative performance monitoring.
---

# Campaign Delivery Overview

Portfolio-level campaign delivery metrics including spend, pacing, projected delivery, and budget
deviation across all campaigns for an advertiser.

## ⚠️ Metrics Availability

**Available Metrics:**
- Current spend and budget utilization
- Pacing status and delivery projections  
- Budget deviation and flight progress
- Delivery schedule status

**Not Available:**
- CTR (Click-Through Rate)
- Viewability rate
- eCPM (effective Cost Per Mille)
- Historical performance data
- Period-over-period comparisons

**System Limitation:** The Adform Flow MCP GraphQL gateway provides delivery indications and
entity configuration only. Performance metrics are not queryable for any historical periods.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_search` to
look up field names; use `graphql_introspect` for complex nested types. Keep calls sequential
(~1–2s apart); retry transient errors at most twice.

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

---

## Presenting

Table with one row per campaign: name, goal type, flight dates, budget goal, current spend,
projected spend, deviation %, and status. Include an account totals row. Flag campaigns with
deviation below −20% as under-delivering and above +10% as approaching overspend. Sort by
deviation ascending to surface the largest gaps first.

For dimensional drill-down (by day, geo, domain, deal) use adform-performance-breakdown. For
creative-level numbers use adform-creative-performance.
