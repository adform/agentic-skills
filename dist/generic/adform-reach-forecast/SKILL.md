---
name: adform-reach-forecast
description: >-
  Media plan forecasting for Adform Flow DSP. Project campaign performance before launch including
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

**Technical Operations:**
The system uses GraphQL operations to process your requests:
- `graphql_validate` - Checks query validity before execution
- `graphql_execute` - Runs the forecasting queries with your parameters
- `graphql_search` - Helps discover available fields and options
- `graphql_introspect` - Explores complex data structures when needed

**Processing Time:** Complex forecasts may require 5-15 seconds to complete. Please allow the
system to finish processing before making additional requests.

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

For geographic targeting, use ISO 3166-1 numeric country codes:
- Germany: 276
- United States: 840
- United Kingdom: 826
- France: 250
- Netherlands: 528

You can combine location targeting with audience criteria for more precise forecasting.

---

## Setting Up Your Forecast

**Required Information:**
- **Advertiser ID:** Your unique advertiser identifier
- **Campaign Schedule:** Start and end dates for your campaign
- **Budget Details:** Total budget amount and currency
- **Performance Targets:** Your desired KPI goals (e.g., click-through rate)
- **Targeting Criteria:** Geographic locations and advertising channels

**Targeting Options:**
- **Geographic:** Select countries using ISO country codes (see list above)
- **Channels:** Choose from display, native, video, or other available formats
- **Audience:** Combine with specific audience segments for precise targeting

> **Important Note:** When configuring domain or app targeting, use the format `{ "targetingMode": "includeAll" }`. The `excludeUnknown` property is not supported.

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
