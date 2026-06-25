---
name: adform-media-plans
description: >-
  Media plan inspection, forecasting, and AI recommendations for the Adform Flow DSP.
  List media plans, inspect a plan's line items, settings, forecast, or get optimisation
  recommendations. Trigger on "show me plan X", "forecast for this plan",
  "projected CTR or impressions or cookies", "budget scenario". For line-item
  detail use adform-line-items; for bid landscape on individual line items use adform-bid-landscape;
  for reach forecasting use adform-reach-forecast. Read-only.
---

# Adform media plans and forecasting

List, inspect, forecast, and get AI recommendations for media plans. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_search` to
look up field names; use `graphql_introspect` for complex nested types. Keep calls sequential
(~1–2s apart).

Forecast KPI queries can take 5–15 seconds on complex inputs — allow time for the response.

---

## 1. List media plans

```graphql
{
  mediaPlans(
    advertiserIds: ["71883"]
    pagination: { offset: 0, limit: 20 }
  ) {
    mediaPlans { id name advertiserId status createdBy createdAt modifiedAt }
    totalCount
  }
}
```

## 2. Get media plan — full detail

```graphql
{
  mediaPlan(id: "12345") {
    id name advertiserId status createdBy createdAt modifiedAt
    budget { amount }
  }
}
```

Use `graphql_introspect` on `MediaPlan` to discover available sub-fields for goals, targeting,
schedules, and line items.

## 3. Forecast KPIs — projected CTR, impressions, cookies, spend

Build a `ForecastingKpisMediaPlanInput` from an existing plan or from scratch. If referencing
an existing plan, fetch it first and apply only the overrides the trader asked for.

```graphql
{
  mediaPlanForecastingKpis(mediaPlan: {
    advertiserId: "71883"
    timeZoneId: "Europe/Berlin"
    name: "Forecast scenario"
    schedules: [{ startDateTime: "2026-04-01T00:00:00", endDateTime: "2026-04-14T23:59:59" }]
    budget: { currency: EUR, amount: 10000, frequencyCappingRules: [] }
    goals: { kpis: [{ performance: { ctr: { rate: 0.005 } } }] }
    targeting: {
      idFusionEnabled: true
      inventory: { channels: [display, native] }
      targetingRuleGroups: [{
        locations: [{
          targetingMode: include
          locations: { countryIds: ["276"] }
        }]
      }]
    }
  }) {
    ctr { kpi impressions spend maxPrice }
    forecast { impressions cookies }
  }
}
```

Enum values (`EUR`, `display`, `native`, `include`) are unquoted. Omit `inventorySources`
unless the trader explicitly names specific sources.

## 4. Get AI optimisation recommendations

```graphql
{
  mediaPlanRecommendations(
    mediaPlan: { id: "12345" }
    filter: { types: [] }
  ) {
    recommendationGroup
    recommendationType
  }
}
```

Use `graphql_introspect` on `MediaPlanRecommendationsFilterInput` to discover available filter
types before calling.

---

## Common workflows

- **Plan review**: list plans → get plan detail → forecast KPIs to project outcomes →
  get recommendations for optimisation tips
- **Budget scenario**: fetch plan → modify budget in the forecast input → compare results
- **Geo scenario**: change `targetingRuleGroups.locations` in the forecast input → see how
  reach changes

## Presenting

Show plan summary with name, status, and key settings. For forecasts, present projected
impressions, unique cookies, CTR, and spend clearly. For recommendations, list type and
description. State that forecasts are estimates.
