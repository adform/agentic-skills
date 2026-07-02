---
name: adform-campaign-management
description: >-
  Campaign and order configuration for Adform FLOW DSP. Inspect campaign or order settings: full config,
  RTB budget and capping, labels, brand safety, delivery indications, daily delivery trends, and projected
  delivery plans. Trigger on "campaign config", "labels on this campaign", "brand safety settings",
  "campaign RTB budget", "order details", "order delivery plan", "daily delivery for campaign".
  For entity browsing use adform-entity-browsing; for pacing use adform-pacing-check. Read-only.
---

# Adform campaign and order management

Inspect campaign and order configuration, RTB settings, labels, brand safety, delivery
indications, daily trends, and projected delivery plans. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_search` to
look up field names; use `graphql_introspect` for complex nested types. Keep calls sequential
(~1–2s apart).

---

## Campaign queries

### List campaigns

```graphql
{
  campaigns(
    advertisers: "71883"
    status: Active
    offset: 0
    limit: 20
  ) {
    campaigns { id name status type subType advertiserId startDate endDate budget currency billingCode }
    totalCount
  }
}
```

### Get campaign — full config

```graphql
{ campaign(id: "3993873") { id name status type subType advertiserId startDate endDate budget currency } }
```

### Get campaign RTB settings

```graphql
{
  campaignRtbSettings(id: "3993873") {
    capping {
      type
      impressions
      period { type duration }
      viewability { type duration }
    }
    dsaTransparency { advertiserLegalName }
    budget { budget amount goalType periodType pacingType }
  }
}
```

### Get campaign labels

```graphql
{ campaignLabels(id: "3993873") { labelGroups { id name labels { id name } } } }
```

### Get campaign brand safety

```graphql
{ campaignBrandSafety(id: "3993873") { enabled providerId blockedCategories blockUncategorized } }
```

### Get campaign delivery indications — current pacing snapshot

```graphql
{
  campaignDeliveryIndications(id: "3993873") {
    status goalType
    effectiveFlightTotalGoal effectiveFlightCurrentDelivery
    effectiveFlightProjectedDelivery effectiveFlightDeviationPercentage
    effectiveFlightTotalCost effectiveFlightDailyCost
    effectiveBudgetFlightStartDate effectiveBudgetFlightEndDate
  }
}
```

### Get campaign daily delivery — time-series (max 30 days)

```graphql
{
  campaignDailyDeliveryIndications(
    ids: ["3993873"]
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

## Order queries

### List orders

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

### Get order

```graphql
{ order(id: "67890") { id name startDate endDate budget campaignId active } }
```

### Get order delivery indications

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

### Get order daily delivery — time-series (max 30 days)

```graphql
{
  orderDailyDeliveryIndications(
    ids: ["67890"]
    from: "2026-05-13"
    until: "2026-06-12"
  ) {
    id deliveryDate
    deliveryIndications { effectiveFlightDailyCost effectiveFlightDeviationPercentage status }
  }
}
```

### Get order delivery plan — forward projection

Use `graphql_introspect` on `DeliveryPlanOrderSettingsInput` to discover required fields before
calling `orderDeliveryPlan`.

---

## Common patterns

- **Hierarchy navigation**: list campaigns → list orders (`campaignId`) → list line items
  (see adform-line-items)
- **Name enrichment**: delivery queries return IDs — use `campaigns(advertisers:)` or
  adform-entity-browsing to map ID to name
- **Delivery monitoring**: use the delivery indications query for a point-in-time snapshot;
  use the daily variant for trends over the last 30 days

## Presenting

Lead with status and key config fields. For delivery, show goal vs current vs projected vs
deviation %. For daily trends, present chronologically and call out drops or gaps. Always
include the numeric entity ID.
