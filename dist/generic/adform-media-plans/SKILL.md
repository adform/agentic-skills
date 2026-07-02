---
name: adform-media-plans
description: >-
  Media plan inspection, forecasting, and AI recommendations for the Adform FLOW DSP.
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
    mediaPlans { id name advertiserId comment schedule { startDate endDate timeZoneId } budget { currency amount } }
    totalCount
  }
}
```

## 2. Get media plan — full detail

```graphql
{
  mediaPlan(id: "12345") {
    id name advertiserId comment
    schedule { startDate endDate timeZoneId }
    budget { currency amount }
  }
}
```

Use `graphql_introspect` on `MediaPlan` to discover available sub-fields for goals, targeting,
schedules, and line items.

## 3. Forecast KPIs — projected CTR, impressions, cookies, spend

Build a `ForecastingKpisMediaPlanInput` from an existing plan or from scratch. If referencing
an existing plan, fetch it first and apply only the overrides the trader asked for.

> **CRITICAL: Use the named-variable pattern only.** The inline pattern (inputs baked into the
> query body with unquoted enum literals) validates against the schema but returns a 500 server
> error at execution due to MCP layer serialisation. Always pass `query` and `variables` as
> separate arguments to `graphql_execute`.

**Query string (pass as `query`):**
```graphql
query ForecastScenario($mediaPlan: ForecastingKpisMediaPlanInput!, $currencyCode: CurrencyCode) {
  mediaPlanForecastingKpis(mediaPlan: $mediaPlan, currencyCode: $currencyCode) {
    ctr { kpi impressions spend maxPrice }
    forecast { impressions cookies }
  }
}
```

**Variables (pass as `variables`, JSON):**
```json
{
  "currencyCode": "EUR",
  "mediaPlan": {
    "advertiserId": "71883",
    "timeZoneId": "Europe/Berlin",
    "name": "Forecast scenario",
    "schedules": [
      { "startDateTime": "2026-04-01T00:00:00", "endDateTime": "2026-04-14T23:59:59" }
    ],
    "budget": {
      "currency": "EUR",
      "amount": 10000,
      "frequencyCappingRules": []
    },
    "goals": {
      "kpis": [{ "performance": { "ctr": { "rate": 0.005 } } }]
    },
    "targeting": {
      "idFusionEnabled": true,
      "inventory": { "channels": ["display", "native"] },
      "targetingRuleGroups": [{
        "locations": [{
          "targetingMode": "include",
          "locations": { "countryIds": ["276"] }
        }]
      }]
    }
  }
}
```

All enum values are **quoted strings** in the variables JSON: `"EUR"`, `"display"`, `"native"`,
`"include"` etc. `currencyCode` is at the top level of variables, not inside `mediaPlan`.
`frequencyCappingRules` must always be an explicit empty array `[]`. Omit `inventorySources`
unless the trader explicitly names specific sources.

## 4. Get AI optimisation recommendations

The `mediaPlan` input requires `advertiserId` and `goals` at minimum. Fetch the plan first,
then pass its parameters. The filter field is `recommendationTypes`.

```graphql
{
  mediaPlanRecommendations(
    mediaPlan: {
      advertiserId: "71883"
      goals: { kpis: [{ performance: { ctr: { rate: 0.005 } } }] }
      schedule: { startDate: "2026-07-01", endDate: "2026-07-31", timeZoneId: "Europe/Berlin" }
    }
    filter: { recommendationTypes: [] }
  ) {
    recommendationGroup
    recommendationType
  }
}
```

Use `graphql_introspect` on `MediaPlanRecommendationsMediaPlanInput` and
`MediaPlanRecommendationsFilterInput` to discover available recommendation types.

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
