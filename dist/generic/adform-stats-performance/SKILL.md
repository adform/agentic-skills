---
name: adform-stats-performance
description: >-
  Dimensional performance reporting for Adform FLOW DSP using mcpStats. Query
  actual ad serving metrics — impressions, clicks, CTR, eCPM, cost, viewability,
  video completion, conversions, RTB win rate, bid reasons — broken down by date,
  campaign, line item, advertiser, domain, deal, banner, order, tag, page, mobile
  app, or bid reason. Supports pagination, sorting, and metric post-filtering.
  date filter is always required. Trigger on "show me performance", "CTR by
  campaign", "viewability metrics", "domain breakdown", "bid reason analysis",
  "what was eCPM last month", "video completion rate", "impressions by date",
  "deal performance stats", "how many bids did we lose and why". For delivery
  pacing and budget flight use adform-pacing-check or adform-reporting; for
  forward-looking forecasts use adform-reach-forecast. Read-only.
---

# Adform stats performance reporting (mcpStats)

Dimensional ad-serving metrics via the `mcpStats` GraphQL query. Returns a
paginated rows result with any combination of dimensions and metrics. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_validate` to check every query
before `graphql_execute`. Use `graphql_introspect` on `McpStatsFilterInput`,
`McpStatsDimensions`, or `McpStatsMetrics` to discover fields. Keep calls
sequential (~1–2s apart).

---

## Query structure

```graphql
{
  mcpStats {
    totalRowCount          # total rows matching the filter (before paging)
    totals                 # aggregate totals across all rows (JSONType)
    columns {
      dimensions { ... }   # declare which dimension columns to include
      metrics { ... }      # declare which metric columns to include
    }
    rows(
      filter: McpStatsFilterInput!   # date is required
      paging: { offset: Int!, limit: Int! }
      sort: [{ column: Int!, direction: asc|desc }]
      timeZoneOffset: Int            # optional; minutes offset from UTC
    )
  }
}
```

**Key rules:**
- `date` inside `filter` is always required. Use `from`/`to` (ISO date strings).
  `DatePreset` enum values exist but are deprecated — always use `from`/`to`.
- `DateFilterKind` can be `utc` or `campaign` (default is campaign time).
- `sort.column` is a zero-based index into the columns declared in `columns {}`.
- `rows` returns `[[JSONType]]` — a 2D array; each inner array is one row, values
  align positionally with the declared columns (dimensions first, then metrics).
- `totals` returns `JSONType` — a flat object with the same column keys summed.
- `paging.limit` is typed as `Limit` scalar — use integers up to a reasonable
  page size (50–200); paginate with `offset` for large result sets.

---

## Dimension reference

Declare only the sub-fields you need. Each sub-field corresponds to one column
in the result rows.

```graphql
columns {
  dimensions {
    date        { date }           # transaction date (YYYY-MM-DD)
    date        { utc }            # date in UTC timezone
    date        { hour }           # hour of day (0–23)
    date        { weekday }        # weekday name
    advertiser  { id }
    campaign    { id }
    campaign    { currencyName }   # campaign currency
    order       { id }
    lineItem    { id }
    lineItem    { name }
    banner      { id }
    banner      { name }
    tag         { id }
    tag         { name }
    page        { id }
    page        { name }
    rtbDomain   { name }           # 2nd-level domain (e.g. cnn.com)
    rtbDeal     { id }
    bidReason   { name }           # DSP no-bid reason or successful bid reason
    mobileApp   { id }
    mobileApp   { name }
    mobileAppStore { name }
  }
}
```

---

## Commonly used metric combinations

### Core delivery + cost
```graphql
metrics {
  impressions
  clicks
  ctr
  cost
  ecpm
  ecpc
  rtbMediaCost
  rtbCostInAgencyCurrency
}
```

### Viewability
```graphql
metrics {
  impressions
  viewImpressionsIab        # viewable impressions (IAB standard)
  viewImpressionsPercentIAB # viewability rate %
  measurableImpressions
  measurableImpressionsPercent
  undeterminedImpressions
  avgViewabilityTime
}
```

### Video
```graphql
metrics {
  impressions
  videoPlayStartCount
  videoCompleteCount
  videoCompletionRate       # videoCompleted / videoPlayStarted * 100%
  videoStartRate            # videoPlayStarted / impressions * 100%
  avgVideoPlayTime
}
```

### RTB bidding
```graphql
metrics {
  rtbBids
  lostBids
  bidReasonCount
  impressions
  rtbWinRate               # impressions / bids %
  rtbMediaCost
}
```

### Conversions & sales
```graphql
metrics {
  impressions
  clicks
  conversions
  cov                      # conversion rate (conversions / clicks %)
  ecpa                     # cost per conversion
  sales
  roi
}
```

---

## Example queries (all validated)

### 1. Campaign daily trend — impressions, CTR, eCPM, viewability

```graphql
{
  mcpStats {
    totalRowCount
    totals
    columns {
      dimensions { date { date } campaign { id } }
      metrics {
        impressions
        clicks
        ctr
        cost
        ecpm
        viewImpressionsIab
        viewImpressionsPercentIAB
        videoCompleteCount
        videoCompletionRate
        conversions
      }
    }
    rows(
      filter: {
        date: { from: "2026-06-01", to: "2026-06-30" }
        campaign: { ids: ["4221341"] }
      }
      paging: { offset: 0, limit: 100 }
      sort: [{ column: 0, direction: asc }]
    )
  }
}
```

### 2. Domain breakdown — where are impressions and cost going?

```graphql
{
  mcpStats {
    totalRowCount
    totals
    columns {
      dimensions { rtbDomain { name } }
      metrics {
        impressions
        clicks
        cost
        ecpm
        rtbBids
        rtbWinRate
      }
    }
    rows(
      filter: {
        date: { from: "2026-06-01", to: "2026-06-30" }
        advertiser: { ids: ["2133936"] }
      }
      paging: { offset: 0, limit: 100 }
      sort: [{ column: 1, direction: desc }]
    )
  }
}
```

### 3. Bid reason analysis — why are we losing auctions?

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

### 4. Deal-level performance stats

```graphql
{
  mcpStats {
    totalRowCount
    totals
    columns {
      dimensions { rtbDeal { id } }
      metrics {
        impressions
        clicks
        cost
        ecpm
        rtbBids
        rtbWinRate
        rtbMediaCost
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

### 5. Advertiser-level summary — all metrics, no dimension breakdown

```graphql
{
  mcpStats {
    totalRowCount
    totals
    columns {
      dimensions { advertiser { id } }
      metrics {
        impressions
        clicks
        ctr
        cost
        ecpm
        viewImpressionsIab
        viewImpressionsPercentIAB
        rtbBids
        rtbWinRate
        conversions
      }
    }
    rows(
      filter: {
        date: { from: "2026-06-01", to: "2026-06-30" }
        advertiser: { ids: ["2133936"] }
      }
      paging: { offset: 0, limit: 10 }
      sort: [{ column: 1, direction: desc }]
    )
  }
}
```

---

## Filter reference

| Filter field | Type | Notes |
|---|---|---|
| `date` | `DateFilterInput` | **Required.** Use `from`/`to` ISO date strings. `kind` is `utc` or `campaign`. |
| `advertiser` | `AdvertiserFilterInput` | Filter by `ids: [ID!]` or `names: [String!]` |
| `campaign` | `CampaignFilterInput` | Filter by `ids`, `names`, `types`, `subtypes`, `active` |
| `order` | `OrderFilterInput` | Filter by `ids`, `names`, `status` |
| `lineItem` | `LineItemFilterInput` | Filter by `ids`, `names`, `buyTypes`, `status` |
| `banner` | `BannerFilterInput` | Filter by `ids`, `names`, `types`, `sizes` |
| `tag` | `TagFilterInput` | Filter by `ids` |
| `rtbDomain` | `RtbDomainFilterInput` | Filter by `names` |
| `rtbDeal` | `RtbDealFilterInput` | Filter by `ids` |
| `country` | `CountryFilterInput` | Filter by `ids` or `names` |
| `continent` | `ContinentFilterInput` | Filter by `ids` or `names` |
| `region` | `RegionFilterInput` | Filter by `ids` or `names` |
| `mobileApp` | `MobileAppFilterInput` | Filter by `names` |
| `bidReason` | `BidReasonFilterInput` | Filter by `names` |
| `trackingPoint` | `TrackingPointFilterInput` | Filter by `ids`, `names`, `preset` |
| `referrerTypes` | `[ReferrerType!]` | `directTraffic`, `referringSite`, `naturalSearch`, `campaign`, `socialMedia` |
| `metrics` | `[FilterInput!]` | Post-aggregate row filter. e.g. `{ fieldName: "impressions", operation: gt, values: [0] }` |

---

## Reading rows results

`rows` is a 2D array `[[JSONType]]`. The column order matches exactly the order
in which dimensions and metrics were declared inside `columns {}` — dimensions
come first in declaration order, then metrics in declaration order.

```
Example columns declared:
  dimensions: { date { date }, campaign { id } }
  metrics: { impressions, ctr, ecpm }

Row layout: [date_value, campaign_id, impressions_value, ctr_value, ecpm_value]
```

`totals` is a flat JSONType object with the same column keys summed across all
rows (not just the current page). Use it for account-level totals without
iterating all pages.

---

## Presenting

- **Date trends**: time-series table sorted by date ascending; flag days with
  zero impressions as delivery gaps.
- **Domain breakdown**: ranked table by impressions or cost descending; flag
  domains with anomalous eCPM (very high or very low vs account average).
- **Bid reason analysis**: table of reason names, bid count, lost bid count,
  win rate; frame each reason as an actionable problem (pricing, targeting,
  creative audit, budget).
- **Deal breakdown**: table of deal IDs with impressions, win rate, eCPM;
  cross-reference with adform-deal-health-check for deals with zero impressions.
- For large result sets, paginate using `offset` and use `totalRowCount` to
  determine how many pages are needed.
- Always show `totals` as a summary row at the top or bottom of the table.
