---
name: adform-frequency-cap-audit
description: >-
  Frequency cap compliance audit for the Adform Flow DSP. Verify that line-item frequency capping settings match the
  campaign brief or campaign-level constraints, and flag mismatches that risk over-exposure.
  Trigger on "frequency cap audit", "check frequency capping", "do caps match the brief", "flag
  line items with wrong frequency cap", "over-exposure risk". For full line-item config use adform-line-items;
  for campaign config use adform-campaign-management. Read-only.
---

# Adform frequency cap audit

Retrieves frequency and impression capping settings for line items under an order or campaign
and compares them against campaign-level capping or a brief, flagging mismatches that could
cause over-exposure. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_introspect`
on `RtbLineItemCapping`, `RtbLineItemFrequencyCapping`, and `CampaignRtbSettings` to discover
the current field shapes for capping sub-objects. Keep calls sequential (~1–2s apart); retry
transient errors at most twice.

---

## Step 1 — List line items

```graphql
{
  rtbLineItems(
    orderIds: ["67890"]
    offset: 0
    limit: 20
  ) {
    lineItems { id name rtbLineItem { id environments orderId campaignId paused deleted } }
    totalCount
  }
}
```

## Step 2 — Get line item capping detail

```graphql
{ rtbLineItem(id: "99999") { id impressionCappings { frequency { impressions } } } }
```

Use `graphql_introspect` on `RtbLineItemCapping` and `RtbLineItemFrequencyCapping` to confirm
available fields — the `impressions` value is the cap limit.

A line item with an empty `impressionCappings` list has no frequency capping applied.

## Step 3 — Get campaign-level cap for comparison

```graphql
{ campaignRtbSettings(id: "3993873") { capping } }
```

Use `graphql_introspect` on `RtbCappingSettings` and `CampaignCappingViewabilityType` to
expand the capping sub-fields.

---

## Method

1. Read each line item's cap limit from `impressionCappings[].frequency.impressions`
2. Compare each limit against the campaign cap and the brief value (e.g. "3 impressions per user")
3. Flag: missing cap where one is required, a higher limit than the brief specifies, or no
   capping at all where the brief mandates one

## Presenting

Table of line items: name, cap limit (impressions), expected from the brief, and a PASS or FLAG
verdict with the reason. Summarise how many are non-compliant and the over-exposure risk. For
deeper line-item context use adform-line-items; for campaign config use
adform-campaign-management.
