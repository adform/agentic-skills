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

> **The introspection cache lags the live endpoint.** `graphql_introspect`,
> `graphql_search` and `graphql_validate` serve a cached schema snapshot.
> Three deployed cost metrics — `rtbBrandSafetyCost`,
> `rtbContextualTargetingCost` and `rtbCrossDeviceCost` — are rejected by
> `graphql_validate` with "type `McpStatsMetrics` does not have a field X",
> but execute correctly against the live endpoint. Verify those three with
> `graphql_execute` only, and never drop them from a query because validate
> rejected them.

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
- **At most 10 metrics per query.** An 11th returns `tooManyMetrics`
  (HTTP 500, "Too many metrics provided"). To pull a wider metric set, split it
  across several queries with identical dimensions and filter, then join the
  results on the dimension columns. This bites hardest on the cost tables
  below — a full RTB fee breakdown does not fit in one call.

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
  cost(costType: rtb)      # state the costType you applied
  ecpm(costType: rtb)
  ecpc(costType: rtb)
  rtbMediaCost             # inventory only — not total cost
  rtbCostInAgencyCurrency
}
```

Pair this with the `campaign { currencyName }` dimension and read the cost
reference below before reporting any figure from it.

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

## Cost metrics — canonical reference

**This is the canonical cost and currency reference for the Adform skill set.**
Other skills link here rather than restating these tables. Add new cost fields
here, not in the skill that happens to need them.

### The `costType` argument — read this before reporting any cost

These metrics accept a `costType` argument that selects which cost calculation
method the figure is drawn from:

`cost`, `costNonView`, `costView`, `costBySales`, `salesByCost`, `roi`,
`ecpa`, `ecpacrossdevice`, `ecpc`, `ecpi`, `ecpm`, `ecpmv`, `ecpp`

The four values are the same everywhere:

| Value | What it selects |
|---|---|
| `rtb` | RTB Budget Spent — the amount actually spent in the auction. Schema descriptions consistently contrast this with "booked or accumulated cost". |
| `maxCost` | A booked/accumulated cost basis. This is what the FLOW Standard Reporting Cost column uses by default, and on a programmatic campaign it resolves to RTB Cost. |
| `fixedCost` | A booked/accumulated cost basis. |
| `fixedPrice` | A booked/accumulated cost basis. |

The schema carries **no per-value description** for `maxCost`, `fixedCost` and
`fixedPrice` beyond their names. Do not assert which one a given line item uses
— confirm against its buying type first (see adform-line-items).

The enum type is **per field**, not shared: `cost` takes
`CostCostTypeSpecEnum`, `ecpm` takes `EcpmCostTypeSpecEnum`, and so on. All of
them carry the same four values, so a `graphql_validate` error naming an
unfamiliar `*CostTypeSpecEnum` is a type-name difference, not a bad value.

**There is no documented default.** No field description and no argument
definition states which method applies when `costType` is omitted; the
argument description is uniformly "Apply selected cost calculation method".

**Rules:**
- Whenever you report a cost or eCP* figure, **state which `costType` was
  applied.** If you omitted the argument, say so and note that the API default
  is undocumented.
- For RTB campaigns, `rtb` is normally the correct value — it reports budget
  actually spent in the auction.
- When reconciling against a FLOW report and the figures disagree, **`costType`
  is the first thing to check** — before date range, timezone, or filters.
- For **eCPM (Reach)**, the schema's own tip is to set `costType: rtb` together
  with `adUniqueness: campaignUnique`. Plain `ecpm` is not eCPM (Reach).
  `adUniqueness` values: `all`, `campaignUnique`, `campaignDayUnique`,
  `mediaUnique`, `lineItemUnique`, `lineItemDayUnique`, `bannerUnique`,
  `notCampaignUnique`.

Several metrics additionally take a data-source argument — `costDataSource` on
`cost` and `roi`, `dataSource` on `ctr`, `ecpc`, `ecpm`, `cov`, `vtr`,
`clicks`, `impressions`. Values are `adform` and `se` (search engine); `se`
pairs with `seAvgCPC`. Same risk as `costType`, lower frequency.

**Observed spread** (two live RTB campaigns, EUR): all four `costType` values
returned an identical figure for each campaign. That is the expected result on
programmatic inventory, not a sign the argument is inert — Standard Reporting
defaults Cost to Max Cost, and on a programmatic campaign Max Cost is RTB Cost,
so the four values converge. A campaign carrying both booked and RTB cost can
still diverge, so keep stating the value used.

To match a FLOW Standard Reporting Cost column exactly, pass
`costType: maxCost`. On programmatic campaigns this ties to the cent.

```graphql
metrics {
  rtb:        cost(costType: rtb)
  maxCost:    cost(costType: maxCost)
  fixedCost:  cost(costType: fixedCost)
  fixedPrice: cost(costType: fixedPrice)
}
```

---

### Currency handling

`McpStats.rows` has **no `currencyCode` argument** — its full signature is
`rows(filter, paging, sort, timeZoneOffset)`. Costs always come back in
campaign currency, and `campaign { currencyName }` is the only way to know
which. Therefore:

- **Always select `campaign { currencyName }`** alongside any cost metric.
- **Always label figures with that currency.** Never print a bare number.
- **Proceed without asking.** Do not ask the user for a currency on every
  query.

For queries that *do* take a `currencyCode` argument, pass nothing, let the API
default apply, and state plainly which currency the result is in:

| Query | Default |
|---|---|
| `inventoryMarketplaceListItems` | EUR — declared in the schema as `currencyCode: CurrencyCode = "EUR"` |
| `audienceMarketplaceListItems` | DKK — declared as `= "DKK"` |
| `mediaPlanForecastingKpis` | EUR — declared as `= "EUR"` |
| `mcpInventoryStats.rows` | DKK — platform default, **not** declared in the schema signature. Confirm against returned values before labelling |
| `brandSafetyFee` / `brandSafetyFees` | none, nullable |
| `contextualTargetingFee` / `contextualTargetingFees` | none, nullable |

`CurrencyCode` is a custom scalar, not an enum — always pass it as a quoted
string (`"EUR"`, not `EUR`).

**Ask the user about currency only in these three cases:**

1. Results span campaigns in **more than one currency**. Never sum across
   currencies — ask whether to report per currency or convert to one.
2. The user signals an **external audience**: client report, invoice
   reconciliation, deck, "send this to the client".
3. The user **names a currency** that differs from the data's currency.

Ask once and reuse the answer for the rest of the session.

**Conversion.** Use `currencyRate(sourceCurrencyCode:, targetCurrencyCode:)` or
`currencyRates(sourceCurrencyCode:)` — see adform-geo-reference. Pass codes as
quoted ISO 4217 strings (`"EUR"`, not `EUR`). Apply the rate explicitly, label
the output as converted, and state the source currency and the rate used.
**Never convert silently.**

---

### Cost variants

| Field | Meaning |
|---|---|
| `cost` | Cost for the selected dimension. Takes `costDataSource`, `costType` |
| `costNonView` | Cost attributed to non-viewable and undetermined impressions. Takes `viewSettings`, `adUniqueness`, `costType` |
| `costView` | Cost attributed to viewable impressions. Takes `viewSettings`, `adUniqueness`, `costType` |
| `costPostClick` | Post-click conversion cost. No arguments |
| `costBySales` | Cost divided by sales value |
| `salesByCost` | Sales value divided by cost |
| `roi` | `(Sales − Cost) / Cost`. Uses RTB Budget Spent in place of Cost for RTB campaigns |

`costView + costNonView` should reconcile to `cost`. On campaigns with no
viewability measurement all of it lands in `costNonView` and `costView`
returns 0 — that is not a delivery fault.

On `roi`, the schema describes the result as a percentage, but a zero-sales
campaign returned `-1` rather than `-100` in testing. Treat the scale as
unconfirmed: check the magnitude against `sales` and `cost` before presenting
`roi` as a percentage.

### RTB fee breakdown

| Field | Meaning |
|---|---|
| `rtbMediaCost` | Inventory cost from exchanges |
| `rtbAdformIncludedFee` | Adform included fee |
| `rtbTradingDeskFee` | Trading desk fee |
| `rtbRichMediaFee` | Rich media fee on heavy, rich media and video banners |
| `rtbThirdPartyVendorCost` | Custom third-party fee |
| `rtbBrandSafetyCost` | Brand safety fee |
| `rtbContextualTargetingCost` | Contextual targeting fee |
| `rtbCrossDeviceCost` | ID Fusion / cross-device cost |
| `rtbCostInAgencyCurrency` | RTB cost in agency currency |

**What RTB Cost comprises.** On a programmatic campaign, RTB Cost is the sum of
RTB Media Cost, RTB Adform Included Fee, RTB Rich Media Fee, DMP Data Cost
(DSP), RTB Brand Safety Cost, RTB Contextual Targeting Cost, RTB Trading Desk
Fee where it applies, RTB ID Fusion Cost, DMP ID Fusion Extension Cost, DMP
Lookalike Extension Cost, RTB Custom Third-Party Fee and RTB DCO Fee.

Three of those are not exposed as separate `mcpStats` metrics: DMP ID Fusion
Extension Cost, DMP Lookalike Extension Cost and RTB DCO Fee. They are still
counted inside `cost`, so on a campaign using DCO creatives or lookalike and
ID Fusion audience extensions the selectable components will sum to slightly
**less** than `cost`. Viewing the breakdown in FLOW requires the RTB Cost
Breakdown account permission.

> **`rtbMediaCost` is inventory cost only — never present it as total cost.**
> Total RTB spend requires the fee components above. On two live RTB campaigns
> the gap was almost entirely `rtbAdformIncludedFee`, and the understatement
> differed between the two — it is not a fixed percentage, so it cannot be
> corrected with a multiplier. Sum the components instead.

**Reconciling against `cost`.** `rtbMediaCost` plus the fee components should
equal `cost(costType: rtb)` for the same filter. Pull them in one query so both
sides come from the same snapshot — these are live campaigns, and figures move
between calls. Expect a near-exact match rather than a guaranteed one: in
testing one campaign reconciled to six decimal places while the other left a
residual under 0.002% of `cost`, with the component sum slightly *exceeding*
`cost`. Treat a residual at that scale as rounding. A sum that falls materially
**short** of `cost` points at one of the three components not exposed as
metrics rather than at a bad query — check whether the campaign runs DCO
creatives or audience extensions before treating it as an error.

**Field-name mapping:** `rtbCrossDeviceCost` is the FLOW report column labelled
**"RTB ID Fusion Cost"**. Do not invent an alias such as `rtbIdFusionCost` —
the field name is `rtbCrossDeviceCost`.

`rtbBrandSafetyCost`, `rtbContextualTargetingCost` and `rtbCrossDeviceCost` are
the three fields the introspection cache rejects. They execute fine. They
return 0 where the corresponding feature is not enabled on the campaign, which
is correct rather than missing data.

### DMP data cost

| Field | Meaning |
|---|---|
| `dmpDspDataCost` | Data cost spent on DMP data to win an RTB impression |
| `dmpRotatorsDataCost` | Data cost spent on DMP data to serve a creative |

### Efficiency metrics

| Field | Meaning |
|---|---|
| `ecpm` | Cost per thousand impressions |
| `ecpc` | Cost per click |
| `ecpi` | Cost per impression |
| `ecpa` | Cost per conversion |
| `ecpacrossdevice` | Cost per conversion, ID Fusion cross-device |
| `ecpp` | Cost per pageview, across all tracking points |
| `ecpmv` | Cost per thousand viewable impressions |
| `ecpmInAgencyCurrency` | eCPM in agency currency. No arguments |
| `ecpcInAgencyCurrency` | eCPC in agency currency. No arguments |
| `ecpmOtsInAgencyCurrency` | Cost per thousand DOOH opportunities, agency currency. No arguments |
| `seAvgCPC` | Average CPC for search engine campaigns. No arguments |

The `*InAgencyCurrency` fields and `seAvgCPC` take no arguments at all — they
cannot be qualified with `costType`. Report them as-is and name the agency
currency separately.

`effectiveFlightTotalCost` and `effectiveFlightDailyCost` are **not** mcpStats
metrics — they belong to the delivery-indication queries. See adform-reporting.

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
        campaign: { ids: ["12345"] }
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

### 6. Full RTB cost breakdown — two calls, joined on campaign

The 10-metric cap means a complete fee breakdown does not fit in one query.
Split it, keeping dimensions and filter identical, then join on campaign ID.
Both halves below were executed against the live endpoint.

Call A — totals and the first fee components:

```graphql
{
  mcpStats {
    columns {
      dimensions { campaign { id currencyName } }
      metrics {
        cost
        costNonView
        costView
        rtbMediaCost
        rtbAdformIncludedFee
        rtbTradingDeskFee
        rtbRichMediaFee
        rtbThirdPartyVendorCost
      }
    }
    rows(filter: {
      date: { from: "2026-09-01", to: "2026-10-06" }
      campaign: { ids: ["12345", "67890"] }
    })
    totals
  }
}
```

Call B — the remaining fee components. `graphql_validate` rejects the first
three fields from the cache; execute anyway:

```graphql
{
  mcpStats {
    columns {
      dimensions { campaign { id currencyName } }
      metrics {
        rtbBrandSafetyCost
        rtbContextualTargetingCost
        rtbCrossDeviceCost
        dmpDspDataCost
        dmpRotatorsDataCost
      }
    }
    rows(filter: {
      date: { from: "2026-09-01", to: "2026-10-06" }
      campaign: { ids: ["12345", "67890"] }
    })
    totals
  }
}
```

Present the sum of the fee components next to `cost`, and label the currency
from `currencyName`.

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

**Cost figures specifically:**
- Label every cost and eCP* figure with its currency, taken from the
  `campaign { currencyName }` column. Never print a bare number.
- State which `costType` was applied, or that the argument was omitted and the
  default is undocumented.
- Never present `rtbMediaCost` as total spend — show the fee components, or
  show `cost` alongside it.
- Never sum costs across campaigns in different currencies.
