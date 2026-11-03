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
For RTB line items, the `id` parameter requires the RTB setup ID (returned as `id` from
`rtbLineItems(orderIds:)`), not the placement ID. A line item ID from the user is the placement ID,
so resolve it first (see "Resolve a line item ID" in adform-line-items).

---

## Campaign pacing

```graphql
{
  campaignDeliveryIndications(id: "12345") {
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

## Direct line item pacing

The `id` is the line item's placement ID (`id` from `agencyListItems { lineItems }`).

```graphql
{
  directLineItemDeliveryIndications(id: "67890") {
    bookingType
    totalGoal totalProjected totalRemaining
    totalDelivery { impressions clicks deliveryDeviationPercentage }
  }
}
```

`totalGoal: 0` means there is no booked goal to measure pacing against. `deliveryDeviationPercentage`
also returns 0 in that case, so do not read it as on track.

## Daily trend — when did pacing change?

Max 30-day window. Also available as `orderDailyDeliveryIndications` and
`rtbLineItemDailyDeliveryIndications` with identical argument shapes.

```graphql
{
  campaignDailyDeliveryIndications(
    ids: ["12345"]
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

`effectiveFlightTotalCost` and `effectiveFlightDailyCost` carry **no currency
field** — they are in the campaign's own currency. Resolve it from
`campaigns { currency }` and label every monetary figure, including the
shortfall amount. These fields take no `costType` argument, so a pacing spend
figure will not necessarily match an `mcpStats` `cost` figure for the same
window — that depends on which `costType` the latter used. See
adform-stats-performance before treating a gap between the two as an error.

For the root cause when a line item cannot serve at all (no creative, audit pending, pricing or
budget issue) use adform-delivery-health. To size a bid cap increase that would resolve an
under-pacing pricing issue, use adform-bid-landscape — but check the line item's buying type
first to identify the correct cap to adjust (e.g. Max eCPC for CPC buying, Max CPM for dynamic
CPM). See the pricing model table in adform-line-items.

## When campaign or order delivery returns no data

Campaign and order delivery indications are calculated from programmatic budget settings. Direct
line items have no RTB data and are measured by their buy type instead. So for a campaign or order
with only direct line items, `campaignDeliveryIndications`, `orderDeliveryIndications`, and
`campaignDailyDeliveryIndications` return no data. That does not mean there was no delivery. Check what you can before reporting:

```graphql
{
  campaign(id: "12345") { id }
  rtb: agencyListItems(
    filters: [
      { fieldName: "campaign.id", operation: eq, values: [12345] }
      { fieldName: "lineItem.type", operation: eq, values: ["Rtb"] }
    ]
    skipData: true
  ) { lineItems { id } totalCount }
  direct: agencyListItems(
    filters: [
      { fieldName: "campaign.id", operation: eq, values: [12345] }
      { fieldName: "lineItem.type", operation: eq, values: ["Direct"] }
    ]
    pagination: { offset: 0, limit: 50 }
  ) { lineItems { id name } totalCount }
}
```

If `campaign(id:)` returns no data, the ID is wrong, so resolve it again. If the campaign exists:

- Report **"Campaign-level pacing could not be assessed"**.
- Explain that the delivery lookup returned no usable pacing data, not that the campaign has no
  delivery. Use `mcpStats` (see adform-stats-performance) if you need delivered volume.
- If `rtb` has a `totalCount` of 0 and `direct` has line items, say this is the reason: the campaign
  has only direct line items, and direct line items have no RTB data for these lookups.
- Check the direct line items with `directLineItemDeliveryIndications`. It returns no data for a
  direct line item with no delivery in the last 13 months, while one impression or click is enough
  for it to return data. Report those line items as having no delivery recorded in the last 13
  months, after confirming with `directLineItem(id:)` that the ID exists. Use adform-delivery-health
  to check why.
- Point the user to the **Campaign Delivery Report** in Adform FLOW to assess delivery against
  booked values (Booked, Delivered, Over / Underdelivered).

## Presenting

Lead with the verdict (on track / under-delivering / over-delivering / in a schedule gap / could
not be assessed), then the numbers: spend vs goal, projected vs goal, deviation %. Recommend a
concrete next step.
Label every monetary figure with the campaign currency; never print a bare number.
