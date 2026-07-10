---
name: adform-viewability-audit
description: >-
  Viewability settings consistency audit for the Adform FLOW DSP.
  Confirm viewability measurement is consistent across an advertiser's campaigns and flag deviations
  that would make reporting inconsistent. Trigger on "viewability audit",
  "are viewability settings consistent", "check measurement standard", "viewability config across
  campaigns", "viewability override check". For general advertiser settings use
  adform-entity-browsing; for campaign config use adform-campaign-management. Read-only.
---

# Adform viewability settings audit

Reads the viewability capping configuration on campaigns and line items, compares it against
the agreed standard, and flags deviations or line-level overrides. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_introspect`
on `CampaignRtbSettings`, `RtbCappingSettings`, and `ViewabilitySettings` to discover the
current field shapes for viewability sub-objects. Keep calls sequential (~1–2s apart).

On this gateway, viewability is modelled as a capping setting — `type` and `duration` in
milliseconds — on `CampaignRtbSettings.capping[]` and on `RtbLineItem.impressionCappings[]`.
If your organisation tracks a viewability provider or percentage threshold separately, use
`graphql_search` with the terms "viewability" and "provider" to discover where those fields live.

---

## Step 1 — List campaigns

```graphql
{
  campaigns(
    advertisers: "71883"
    status: Active
    offset: 0
    limit: 20
  ) {
    campaigns { id name status type subType advertiserId }
    totalCount
  }
}
```

## Step 2 — Get viewability capping per campaign

```graphql
{
  campaignRtbSettings(id: "3993873") {
    capping {
      type
      impressions
      period { type duration }
      viewability { type duration }
    }
  }
}
```

## Step 3 — Spot-check line-level overrides

The `id` is the RTB setup ID returned by `rtbLineItems()`, not the placement ID.

```graphql
{ rtbLineItem(id: "99999") { id impressionCappings { frequency { impressions } } } }
```

Use `graphql_introspect` on `RtbLineItemCapping` to discover viewability-related capping
fields on individual line items.

## Step 4 — Actual viewability metrics via mcpStats

Settings audit (Steps 1–3) confirms what viewability configuration is in place.
Use mcpStats to pull the actual measured viewability numbers for the same
advertiser and period, so the audit report can show both "what is configured"
and "what was actually measured". Validated query:

```graphql
{
  mcpStats {
    totalRowCount
    totals
    columns {
      dimensions { campaign { id } }
      metrics {
        impressions
        viewImpressionsIab
        viewImpressionsPercentIAB
        measurableImpressions
        measurableImpressionsPercent
        undeterminedImpressions
        avgViewabilityTime
      }
    }
    rows(
      filter: {
        date: { from: "2026-06-01", to: "2026-06-30" }
        advertiser: { ids: ["2133936"] }
      }
      paging: { offset: 0, limit: 50 }
      sort: [{ column: 0, direction: desc }]
    )
  }
}
```

Join the mcpStats result to the campaign list from Step 1 using campaign ID. A
campaign with deviating viewability settings (flagged in Step 2) should also
show a materially different `viewImpressionsPercentIAB` in mcpStats — use this
to quantify the reporting impact of the misconfiguration.

---

## Method

1. Establish the baseline `type` and `duration` — from the brief, or the most common
   configuration across campaigns as the de-facto standard
2. For each campaign, read the viewability capping; flag any campaign whose type or duration
   differs from the baseline, or that has no viewability capping where one is expected
3. Spot-check line items for overrides that diverge from the campaign or baseline standard

## Presenting

Consistency table: campaign, viewability type, duration (ms), and a settings
verdict — MATCHES, DEVIATES, or NONE. Below the settings table, include a
measured viewability table from mcpStats: campaign, impressions, viewable
impressions (IAB), viewability rate %, measurable %, and avg viewability time.

Cross-reference the two tables: campaigns with deviating settings should be
expected to show divergent measured rates — flag the delta as the business
impact. Lead with deviations and missing measurement. Note any line-level
overrides separately. Recommend aligning to the agreed standard.
