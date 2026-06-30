---
name: adform-pacing-check
description: >-
  Delivery pacing check for the Adform FLOW DSP. Use whenever a
  programmatic trader wants to know whether a campaign, order, or line item is pacing correctly.
  Trigger on "is campaign X pacing ok", "is this on track to spend its budget", "is it under or
  over delivering", "how much has this spent vs goal", "check pacing", "will it hit budget". For
  the root cause when something is not delivering use adform-delivery-health; for historical
  performance numbers use adform-campaign-performance. Read-only.
---

# Adform pacing check

Is it pacing? Pulls delivery indications — flight goal vs current vs projected vs remaining,
spend, deviation %, and status — at campaign, order, or line-item level. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_search` to
look up field names. Keep calls sequential (~1–2s apart).
Resolve entity IDs using `campaigns(advertisers:, search:)` and `orders(campaignId:, active: true)`.

---

## Campaign pacing

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

## Order pacing

```graphql
{
  orderDeliveryIndications(id: "67890") {
    status goalType
    effectiveFlightTotalGoal effectiveFlightCurrentDelivery
    effectiveFlightProjectedDelivery effectiveFlightDeviationPercentage
    effectiveFlightTotalCost effectiveFlightDailyCost
    effectiveBudgetFlightStartDate effectiveBudgetFlightEndDate
  }
}
```

## RTB line item pacing

```graphql
{
  rtbLineItemDeliveryIndications(id: "99999") {
    status goalType
    effectiveFlightTotalGoal effectiveFlightCurrentDelivery
    effectiveFlightProjectedDelivery effectiveFlightDeviationPercentage
    effectiveFlightTotalCost effectiveFlightDailyCost
    effectiveBudgetFlightStartDate effectiveBudgetFlightEndDate
  }
}
```

## Daily trend — when did pacing change?

Max 30-day window. Also available as `orderDailyDeliveryIndications` and
`rtbLineItemDailyDeliveryIndications` with identical argument shapes.

```graphql
{
  campaignDailyDeliveryIndications(
    ids: ["4221341"]
    from: "2026-05-13"
    until: "2026-06-12"
  ) {
    id deliveryDate
    deliveryIndications {
      effectiveFlightDailyCost
      effectiveFlightDeviationPercentage
      status
    }
  }
}
```

---

## Reading the results

- `status: ScheduleGap` — currently outside an active flight; the most common reason something
  is not delivering at a given moment
- `status: Finished` — flight is over; no further delivery expected
- `goalType: Unlimited` — no pacing target; deviation and period fields will not return
- Strongly negative deviation — under-pacing; shortfall = `totalGoal − projected`
- Strongly positive deviation — front-loading ahead of plan

For the root cause when a line item cannot serve at all (no creative, audit pending, pricing or
budget issue) use adform-delivery-health. For a CPM that would resolve an under-pacing pricing
issue use adform-bid-landscape.

## Presenting

Lead with the verdict — on track / under-delivering / over-delivering / in a schedule gap —
then the numbers: spend vs goal, projected vs goal, deviation %. Recommend a concrete next step.
