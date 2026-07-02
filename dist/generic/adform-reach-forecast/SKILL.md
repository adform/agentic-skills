---
name: adform-reach-forecast
description: >-
  Media plan forecasting for Adform FLOW DSP. Project campaign performance before launch including
  impressions, reach, spend, and optimal bid pricing to achieve your KPI targets. Ideal for
  campaign planning, budget allocation, and scenario analysis. For detailed line item bidding
  analysis, see bid landscape forecasting; for historical performance data, see past traffic analysis.
---

# Media Plan Reach Forecast

Forecast campaign performance metrics including projected impressions, unique reach, estimated spend,
and maximum bid prices required to achieve specific KPI targets. This enables data-driven campaign
planning and budget optimization.

## Overview

This forecasting tool analyzes your media plan parameters to predict campaign performance. The system
processes targeting criteria, budget allocations, and schedule information to generate accurate
performance projections.

**Processing Time:** Complex forecasts may require 5-15 seconds to complete. Allow time for the
response before retrying.

---

## CRITICAL: Query execution pattern

The `mediaPlanForecastingKpis` endpoint **requires the named-variable pattern exclusively**.
The inline pattern (inputs baked directly into the query body) validates against the schema but
returns a 500 server error at execution time due to MCP layer serialisation. Do not use it.

**Always call `graphql_execute` with `query` and `variables` as separate arguments:**

```graphql
query ForecastScenario($mediaPlan: ForecastingKpisMediaPlanInput!, $currencyCode: CurrencyCode) {
  mediaPlanForecastingKpis(mediaPlan: $mediaPlan, currencyCode: $currencyCode) {
    ctr { kpi impressions spend maxPrice }
    forecast { impressions cookies }
  }
}
```

```json
{
  "currencyCode": "GBP",
  "mediaPlan": {
    "advertiserId": "2133936",
    "timeZoneId": "Europe/London",
    "name": "UK Retail – Display – July 2026",
    "schedules": [
      { "startDateTime": "2026-07-01T00:00:00", "endDateTime": "2026-07-31T23:59:59" }
    ],
    "budget": {
      "currency": "GBP",
      "amount": 25000,
      "frequencyCappingRules": []
    },
    "goals": {
      "kpis": [{ "performance": { "ctr": { "rate": 0.003 } } }]
    },
    "targeting": {
      "idFusionEnabled": true,
      "inventory": { "channels": ["display", "native"] },
      "targetingRuleGroups": [{
        "locations": [{
          "targetingMode": "include",
          "locations": { "countryIds": ["826"] }
        }]
      }]
    }
  }
}
```

**Rules for the variables JSON:**
- All enum values **must be quoted strings**: `"display"`, `"native"`, `"video"`, `"include"`, `"EUR"`, `"GBP"` etc.
- `frequencyCappingRules` must be an explicit empty array `[]` — never omitted.
- `currencyCode` lives at the **top level** of the variables object, not inside `mediaPlan`.
- Channel values: `"display"`, `"native"`, `"video"`, `"tv"`, `"audio"`, `"dooh"`.
- Always validate the query string with `graphql_validate` before executing.

**Result fields under `ctr`:** `kpi`, `impressions`, `spend`, `maxPrice`
**Result fields under `forecast`:** `impressions`, `cookies`

---

## Forecast Parameters

The forecasting system requires the following parameters to generate accurate projections:

**Required Information:**
- **Advertiser ID:** Your unique advertiser identifier
- **Time Zone:** Campaign time zone (e.g., "Europe/Berlin")
- **Campaign Schedule:** Start and end dates for the forecast period
- **Budget:** Total budget amount and currency
- **Performance Goals:** Target KPIs (e.g., click-through rate)
- **Targeting Criteria:** Geographic locations, channels, and audience segments

**Example Configuration:**
```
Campaign: April 1-14, 2026
Budget: €10,000
Target: Germany
Channels: Display, Native
Goal: 0.5% CTR
```

## Location Targeting

For geographic targeting, use country IDs from the Adform geo reference. Look up the correct
ID using `countries(search: "Germany")` via adform-geo-reference rather than hardcoding values.

Common ISO 3166-1 numeric codes (verify via adform-geo-reference before use):
- Germany: 276
- United States: 840
- United Kingdom: 826
- France: 250
- Netherlands: 528

You can combine location targeting with audience criteria for more precise forecasting.

---

## Using Existing Campaigns

To forecast performance for an existing campaign:
1. Retrieve your current campaign settings
2. Adjust parameters you want to test (budget, dates, targeting)
3. Generate new forecast with updated parameters
4. Compare results to make informed decisions

This approach allows you to test different scenarios before committing to changes.

---

## Understanding Your Results

**Performance Metrics:**
- **Target KPI:** The performance goal you set (e.g., click-through rate)
- **Projected Impressions:** Expected ad deliveries at your target KPI
- **Estimated Spend:** Projected campaign cost in your budget currency
- **Maximum Bid Price:** Highest bid needed to achieve your KPI target
- **Total Reach:** Forecasted unique audience reach
- **Total Impressions:** Overall projected ad deliveries

**Key Insights:**
The forecast shows how different bid levels affect campaign performance. Higher bids typically
deliver more impressions but increase costs, while lower bids may reduce reach but improve efficiency.

## Making Decisions

**Presenting Results:**
Focus on the key metrics that matter for your campaign:
- "To achieve a 0.5% CTR, you can expect approximately 2.5 million impressions with an estimated spend of €8,500 at a maximum bid of €3.40"

**Important Considerations:**
- Forecasts are projections based on current market conditions
- Actual performance may vary due to competition and market changes
- Use forecasts as planning tools, not guarantees
- Consider testing different scenarios to find optimal settings

**Next Steps:**
- Compare different budget scenarios
- Test various targeting combinations
- Adjust KPI targets to balance reach and efficiency
- Monitor actual performance against forecasts once live
