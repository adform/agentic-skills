---
name: adform-delivery-health
description: >-
  Delivery health root-cause check for RTB line items on Adform Flow DSP. Runs structured checks on schedule,
  pricing, budget, banner assignment, creative audits, and advertiser vertical sensitivity, rolling up to Ok,
  Warning, or Critical. Trigger on "why isn't my line item delivering", "delivery health",
  "anything blocking this from serving", "no impressions from this line item". For slow pacing use adform-pacing-check;
  for historical numbers use adform-campaign-performance. Read-only.
---

# Adform delivery health

Why is this RTB line item not serving? Runs Adform's structured health checks — schedule,
pricing, budget, banner assignment, creative audit, advertiser vertical — and rolls them up to
Ok, Warning, or Critical. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_search` or
`graphql_introspect` to explore nested indication types. Keep calls sequential (~1–2s apart).

To resolve a line item ID, use `rtbLineItems(campaignIds:, search:)` or ask the trader to
provide the ID from the Adform platform URL.

## Data Availability

This skill covers real-time delivery indicators for active line items and campaigns only.

---

## Delivery health query

```graphql
{
  rtbLineItemDeliveryHealth(id: "99999") {
    status
    updatedAt
    indications {
      schedule { status }
      pricing { status }
      budget { status }
      bannerAssigned { status }
      tagCreativeAudit { status }
      advertiserIndustryVertical { status }
    }
  }
}
```

Each indication returns `Ok`, `Warning`, or `Critical`. Use `graphql_introspect` on the
specific indication type to retrieve additional detail fields such as `reason`.

---

## Reading the checks

- `bannerAssigned` — no eligible creative assigned to the line item; cannot serve until a
  creative is attached
- `tagCreativeAudit` — creatives not yet approved for the targeted inventory sources
- `pricing` — bid or CPM too low to win auctions, or pricing model misconfigured; size a fix
  with adform-bid-landscape
- `budget` — budget exhausted or a budget configuration issue
- `schedule` — flight has ended, not yet started, or has a gap covering the current time
- `advertiserIndustryVertical` — sensitive-vertical restriction blocking certain inventory

---

## Presenting

Lead with the rolled-up status, then the specific failing check and a concrete recommended
action for the trader to apply — for example "assign an approved creative", "raise CPM to
approximately €X", or "the flight ended on DATE — extend the end date". This skill never
changes anything.

If the line item is serving but pacing slowly rather than blocked entirely, use
adform-pacing-check instead.
