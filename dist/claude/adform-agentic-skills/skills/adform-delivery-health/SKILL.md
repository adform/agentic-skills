---
name: adform-delivery-health
description: >-
  Delivery health root-cause check for RTB and direct line items on Adform FLOW DSP. Runs structured
  checks on schedule, pricing, budget, banner assignment, creative audits, and advertiser
  vertical sensitivity, rolling up to Ok, Warning, or Critical. When pricing is flagged,
  supplements with mcpStats bid-reason breakdown to identify exact no-bid patterns. For direct
  line items, checks setup, tags, and recorded delivery. Trigger
  on "why isn't my line item delivering", "delivery health", "anything blocking this from
  serving", "no impressions from this line item". For slow pacing use adform-pacing-check;
  for dimensional performance stats use adform-stats-performance. Read-only.
---

# Adform delivery health

Why is this RTB line item not serving? Runs Adform's structured health checks — schedule,
pricing, budget, banner assignment, creative audit, advertiser vertical — and rolls them up to
Ok, Warning, or Critical. Direct line items have no health query, so use the direct line item
check below. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_search` or
`graphql_introspect` to explore nested indication types. Keep calls sequential (~1–2s apart).

The `id` parameter requires the RTB setup ID (returned as `id` from `rtbLineItems(orderIds:)`).
This is the ID in the line item's URL. A line item ID from the user, or shown in the UI, is the
placement ID, so resolve it first (see "Resolve a line item ID" in adform-line-items). Direct line items have no
RTB setup ID (`rtbSetupId` is null in `agencyListItems`), and `rtbLineItemDeliveryHealth` returns
no data for them.

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

This query returns no data once the line item's schedule has ended. Check `period { end }` in
`agencyListItems`, and report "Delivery health is not available because the schedule ended on DATE".
`rtbLineItemDeliveryIndications` still returns data for these line items.

---

## Supplementary: bid reason breakdown via mcpStats

When the `pricing` check returns `Warning` or `Critical`, use `mcpStats` with
the `bidReason` dimension to see the specific no-bid reasons causing lost
auctions. This gives the trader exact signal on whether the loss is price-based,
targeting-based, creative-audit-based, or budget-based.

Validated query:

```graphql
{
  mcpStats {
    totalRowCount
    totals
    columns {
      dimensions { bidReason { name } }
      metrics {
        rtbBids
        lostBids
        bidReasonCount
        impressions
        rtbWinRate
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

Scope the `advertiser` filter (or add `lineItem: { ids: [...] }`) to narrow to
the specific entity under investigation. The `bidReason.name` column will return
the platform's reason label for each no-bid category (e.g. price floor, creative
audit, targeting mismatch). Add this table to the delivery health summary when
pricing or budget is flagged.

---

## Reading the checks

- `bannerAssigned` — no eligible creative assigned to the line item; cannot serve until a
  creative is attached
- `tagCreativeAudit` — creatives not yet approved for the targeted inventory sources
- `pricing` — the primary bid cap is too low to win auctions, or the pricing model is
  misconfigured. Read the line item's buying type to identify which cap is relevant (e.g.
  Max eCPC for CPC buying, Max CPM for dynamic CPM) before recommending a specific increase.
  See the pricing model table in adform-line-items. Size a fix with adform-bid-landscape
- `budget` — budget exhausted or a budget configuration issue. To quantify
  remaining budget use adform-pacing-check; if you add `mcpStats` cost metrics
  to the diagnosis, follow the `costType` and currency rules in
  adform-stats-performance — cost figures there have no documented default
  `costType` and are returned in campaign currency only
- `schedule` — flight has ended, not yet started, or has a gap covering the current time
- `advertiserIndustryVertical` — sensitive-vertical restriction blocking certain inventory

---

## Direct line item check

Use the line item's placement ID (`id` from `agencyListItems { lineItems }`). A direct line item
starts working once an ad is assigned and the resulting tag is on the publisher's side.

```graphql
{
  lineItem: agencyListItems(
    filters: [{ fieldName: "lineItem.id", operation: eq, values: [67890] }]
    pagination: { offset: 0, limit: 1 }
  ) {
    lineItems {
      id name type status onlyForMediaPlanning
      period { start end }
      directSettings { hasTags }
      deliveryIndications {
        stats {
          last30days { trackedAds clicks }
          last13months { trackedAds clicks }
        }
      }
      order { status campaign { status } }
    }
  }
  tagListItems(
    filters: [{ fieldName: "tag.lineItemId", operation: eq, values: [67890] }]
    pagination: { offset: 0, limit: 50 }
  ) {
    tags { id name status }
  }
  directLineItemDeliveryIndications(id: "67890") {
    totalGoal
    totalDelivery { impressions clicks }
  }
}
```

Keep `last13months` in the selection, because `deliveryIndications` can return null when only
`last30days` is selected and has no data. The other fields still return when
`directLineItemDeliveryIndications` has no data.

Adform returns no rollup for direct line items, so apply these rules and use the first that matches:

| What you see | Status | What it means |
|---|---|---|
| `onlyForMediaPlanning: true`, the line item, order, or campaign is not active, or the schedule has ended and `directLineItemDeliveryIndications` has no data | Not expected to deliver | Say which of these explains it |
| `hasTags: false`, or no tag has `status: active` | Critical | Nothing can serve. Assign an ad, or reactivate a paused tag |
| Active tag and no data from `directLineItemDeliveryIndications` | Warning | No delivery recorded in the last 13 months. Check that the publisher has implemented the tag |
| Delivery recorded but `last30days` is null or has no tracked ads or clicks | Warning | It has delivered before but not recently. Check with the publisher |
| `last30days` has tracked ads or clicks | Ok | It is delivering. Use adform-pacing-check for pacing |

- **Schedule:** do not treat dates as a blocker when the line item has delivery data. A direct line
  item's schedule is indicative and does not affect delivery. If the start date is recent or in the
  future, say no delivery may be expected yet.
- **Clicks only:** clicks with no tracked ads still count as delivery. This is normal for tracking
  links.
- **`sentStatus`:** do not use it on tags. Direct tags can show `notSent` while delivering.
- **Cause:** Adform cannot see whether a publisher implemented a tag, so present that as the thing
  to check, not as the confirmed cause.

---

## Presenting

Lead with the rolled-up status, then the specific failing check and a concrete recommended
action for the trader to apply — for example "assign an approved creative", "raise the
relevant bid cap (Max eCPC / Max CPM / etc.) to approximately X", or "the flight ended on
DATE — extend the end date". Always name the correct cap for the line item's buying type.
This skill never changes anything.

If the line item is serving but pacing slowly rather than blocked entirely, use
adform-pacing-check instead.
