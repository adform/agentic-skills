---
name: adform-reporting
description: >-
  Campaign delivery and spend reporting for Adform FLOW DSP. Monitor current spend, pacing,
  budget flight status, and delivery projections via delivery indications. Also surfaces
  dimensional performance metrics (CTR, viewability, video, conversions, eCPM, domain
  breakdown, bid reasons) via mcpStats. For delivery health root-cause use
  adform-delivery-health; for a dedicated performance reporting workflow use
  adform-stats-performance.
---

# Campaign Delivery Reporting

Monitor campaign delivery, spend, and pacing metrics to track budget utilization and delivery
performance against goals.

## Report Scope

This skill covers two complementary reporting surfaces:

**Delivery indications** (pacing, budget flight, spend):
- Current spend and budget utilization
- Pacing status and delivery projections
- Budget flight progress and completion
- Daily delivery trends (up to 30-day window)
- Line item delivery health indicators

**Performance stats via mcpStats** (CTR, viewability, video, conversions):
- Impressions, clicks, CTR, eCPM, cost — broken down by date, campaign, order,
  line item, banner, domain, deal, bid reason, mobile app, tag, or page
- Viewability metrics: viewable impressions (IAB), viewability %, measurable
  impressions, avg viewability time
- Video metrics: video starts, completions, completion rate, start rate
- Conversion and sales metrics: conversions, eCPA, sales, ROI
- RTB bidding metrics: bids, lost bids, win rate, bid reason breakdown
- Metric post-filtering (e.g. only rows where impressions > 0)

For dimensional performance queries, use `mcpStats` (see adform-stats-performance
skill). For delivery pacing use the delivery indications queries in this skill.

## Technical Operations

The system uses GraphQL operations to process your requests:
- `graphql_validate` - Checks query validity before execution
- `graphql_execute` - Runs delivery reporting queries
- `graphql_search` - Helps discover available report fields
- `graphql_introspect` - Explores complex report structures

This skill covers delivery and spend reporting for active campaigns only.

---

## Available queries

| Need | Query |
|---|---|
| Current spend, pacing, budget flight — campaign | `campaignDeliveryIndications(id)` |
| Current spend, pacing, budget flight — order | `orderDeliveryIndications(id)` |
| Current spend, pacing, budget flight — RTB line item | `rtbLineItemDeliveryIndications(id)` |
| Daily time-series up to 30 days — campaigns | `campaignDailyDeliveryIndications(ids, from, until)` |
| Daily time-series up to 30 days — orders | `orderDailyDeliveryIndications(ids, from, until)` |
| Daily time-series up to 30 days — RTB line items | `rtbLineItemDailyDeliveryIndications(ids, from, until)` |
| Root-cause delivery health — RTB line item | `rtbLineItemDeliveryHealth(id)` |
| Projected delivery plan — campaign | `campaignDeliveryPlan(campaign: {...})` |
| Projected delivery plan — order | `orderDeliveryPlan(order: {...})` |
| Projected delivery plan — line item | `lineItemDeliveryPlan(lineItem: {...})` |

---

## 1. Campaign delivery indications — current pacing snapshot

Returns the active budget flight state: goal, current delivery, projected delivery, deviation %,
total cost, daily cost, and status. Query one campaign at a time.

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
    effectiveFlightPeriodType
  }
}
```

**Field reference**
- `goalType`: `Money` | `Impressions` | `Clicks` | `Unlimited`
- `status`: `Active` | `ScheduleGap` | `Finished`
- `effectiveFlightCurrentDelivery` — spend/impressions/clicks delivered so far in this flight
- `effectiveFlightProjectedDelivery` — model-projected end-of-flight delivery
- `effectiveFlightDeviationPercentage` — negative = under-delivering; positive = over-delivering
- `effectiveFlightTotalCost` — monetary spend regardless of goalType
- `effectiveFlightDailyCost` — spend in the last day

**Pattern — branding report for an advertiser**
1. `advertisers(search: "name")` → get advertiser ID
2. `campaigns(advertisers: "$advertiserId")` → get all campaign IDs and names
3. `campaignDeliveryIndications(id: "$campaignId")` for each campaign, one call at a time
4. Assemble and sort results client-side by spend or deviation

---

## 2. Order delivery indications

Same field shape as campaign. One order at a time.

```graphql
{
  orderDeliveryIndications(id: "99999") {
    status goalType
    effectiveFlightTotalGoal effectiveFlightCurrentDelivery
    effectiveFlightProjectedDelivery effectiveFlightDeviationPercentage
    effectiveFlightTotalCost effectiveFlightDailyCost
    effectiveBudgetFlightStartDate effectiveBudgetFlightEndDate
  }
}
```

---

## 3. RTB line item delivery indications

Same field shape as campaign. One line item at a time. The `id` is the RTB setup ID returned
by `rtbLineItems()`, not the placement ID.

```graphql
{
  rtbLineItemDeliveryIndications(id: "88888") {
    status goalType
    effectiveFlightTotalGoal effectiveFlightCurrentDelivery
    effectiveFlightProjectedDelivery effectiveFlightDeviationPercentage
    effectiveFlightTotalCost effectiveFlightDailyCost
    effectiveBudgetFlightStartDate effectiveBudgetFlightEndDate
  }
}
```

---

## 4. Daily delivery indications — time-series breakdown

One row per entity per day. Maximum window: 30 days. Accepts multiple IDs in one call.

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
      status
      goalType
      effectiveFlightCurrentDelivery
      effectiveFlightTotalCost
      effectiveFlightDailyCost
      effectiveFlightDeviationPercentage
    }
  }
}
```

Use `orderDailyDeliveryIndications` and `rtbLineItemDailyDeliveryIndications` with the same
argument shape for orders and line items respectively.

---

## 5. RTB line item delivery health — structured root-cause check

Returns a health verdict across six checks: schedule, pricing, budget, banner assignment, tag
creative audit, and advertiser industry vertical sensitivity. Each check returns `Ok`, `Warning`,
or `Critical`.

```graphql
{
  rtbLineItemDeliveryHealth(id: "88888") {
    status
    updatedAt
    indications {
      schedule { status }
      pricing { status }
      budget { status }
      bannerAssigned { status }
      tagCreativeAudit { status }
      advertiserIndustryVertical { status }
    }
  }
}
```

---

## 6. Delivery plan projections

Forward-looking projections for a campaign, order, or line item given its current settings.
Use `graphql_introspect` on `DeliveryPlanCampaignSettingsInput`, `DeliveryPlanOrderSettingsInput`,
or `DeliveryPlanLineItemSettingsInput` to discover required fields before calling.

---

## Presenting

For a branding/campaign report: table with campaign name, goal type, flight dates, budget goal,
current spend, projected spend, deviation %, and status. Flag campaigns with deviation below −20%
as under-delivering and above +10% as approaching overspend. Sort by deviation ascending to
surface the largest gaps first.

For daily breakdowns: show a day-by-day spend trend and note any days with zero daily cost as
delivery gaps.
