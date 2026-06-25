---
name: adform-budget-risk-monitor
description: >-
  Budget delivery risk monitor for the Adform Flow DSP. Identify budget at risk across a campaign —
  orders likely to under-deliver or over-spend. Trigger on
  "budget risk", "which orders will under-deliver", "budget overspend alert", "projected final
  spend", "am I going to over or under spend", "budget pacing".
  For a single entity's pacing verdict use adform-pacing-check; for why something is not
  delivering use adform-delivery-health. Read-only.
---

# Adform budget risk monitor

Sweeps orders under a campaign, compares planned vs current vs projected delivery, and flags
two risks: under-delivery (budget left on the table) and overspend (on track to exceed budget
before the end date). Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Keep calls sequential
(~1–2s apart).

---

## Step 1 — List orders

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

## Step 2 — Delivery indications per order

Run once per order ID:

```graphql
{
  orderDeliveryIndications(id: "67890") {
    status goalType
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

## Step 3 — Campaign-level view (optional)

```graphql
{
  campaignDeliveryIndications(id: "3993873") {
    status goalType
    effectiveFlightTotalGoal effectiveFlightCurrentDelivery
    effectiveFlightProjectedDelivery effectiveFlightDeviationPercentage
    effectiveFlightTotalCost effectiveFlightDailyCost
  }
}
```

## Step 4 — Daily trend for at-risk entities (optional)

Max 30-day window per call:

```graphql
{
  orderDailyDeliveryIndications(
    ids: ["67890", "67891"]
    from: "2026-05-13"
    until: "2026-06-12"
  ) {
    id deliveryDate
    deliveryIndications { effectiveFlightDailyCost effectiveFlightDeviationPercentage status }
  }
}
```

---

## Reading the results

- **Under-delivery risk**: `effectiveFlightProjectedDelivery` materially below
  `effectiveFlightTotalGoal` (negative deviation beyond your threshold, e.g. −10%) while
  the flight is active — reallocation candidate
- **Overspend risk**: deviation strongly positive, or daily cost trend implies budget exhaustion
  before end date
- **Schedule gap**: `status: ScheduleGap` — currently outside an active flight, not a risk in
  itself unless the gap is unexpected

---

## Presenting

Risk table: entity (order or campaign), budget goal, current spend, projected spend, deviation
%, and a verdict — UNDER-DELIVERING, OVER-DELIVERING, or ON TRACK. Lead with at-risk entities
and the monetary amount in play. Suggest reallocating from under-delivering to over-delivering
orders where it fits the plan. For a single entity's detailed pacing use adform-pacing-check;
for a blocked entity use adform-delivery-health.
