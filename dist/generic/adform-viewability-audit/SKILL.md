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

---

## Method

1. Establish the baseline `type` and `duration` — from the brief, or the most common
   configuration across campaigns as the de-facto standard
2. For each campaign, read the viewability capping; flag any campaign whose type or duration
   differs from the baseline, or that has no viewability capping where one is expected
3. Spot-check line items for overrides that diverge from the campaign or baseline standard

## Presenting

Consistency table: campaign, viewability type, duration (ms), and a verdict — MATCHES, DEVIATES,
or NONE. Lead with deviations and missing measurement, as these break cross-campaign reporting
comparability. Note any line-level overrides separately. Recommend aligning to the agreed
standard.
