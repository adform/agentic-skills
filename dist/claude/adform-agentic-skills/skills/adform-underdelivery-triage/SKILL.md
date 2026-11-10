---
name: adform-underdelivery-triage
description: >-
  Account-wide underdelivery triage for the Adform FLOW DSP. Finds every active RTB line item
  underpacing by more than 20%, projects how much of its goal will remain undelivered, ranks
  them by urgency, and gives each one a diagnosis grounded in delivery health and bid data.
  Trigger on "what is underdelivering", "underdelivery report", "which line items are behind",
  "what do I need to fix today", "account-wide pacing problems". Runs across the whole account
  with no advertiser needed. For one entity's pacing verdict use adform-pacing-check; for one
  line item's root cause use adform-delivery-health; for next week's expected spend use
  adform-pipeline-forecast. Read-only.
---

# Adform underdelivery triage

An operational triage list, not a summary. Every active RTB line item underpacing by more than
20%, with the amount projected to go undelivered, the reason, and the items closest to their end
date first. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries and `graphql_validate` to
check them first. Use `graphql_search` to look up field names. Keep calls sequential (~1–2s
apart), never in parallel. To cut the number of calls, put several lookups of the same kind into
one request with aliases, for example five `rtbLineItemDeliveryIndications` lookups named `a:`
to `e:`.

Validation does not catch everything. `filters.fieldName` and `sortBy.fieldName` are free-text
paths, and some `mcpStats` dimension and metric combinations validate but fail at run time. If
the server rejects a filter, drop it and apply the same condition client-side rather than
abandoning the step.

`rtbSetupId` from the sweep is the ID that `rtbLineItemDeliveryIndications(id:)` and
`rtbLineItemDeliveryHealth(id:)` require. The line item `id` is the placement ID, which is what
`mcpStats` takes. Direct line items have a null `rtbSetupId` and are out of scope.

## Default scope

Unless the user overrides it:

| Setting | Default |
|---|---|
| Scope | All advertisers the user can see. Do not ask which advertiser |
| Included | Active RTB line items whose flight includes today |
| Threshold | Underpacing by more than 20%, meaning `deviationPercentage < -20` |
| Excluded | Future line items, completed line items, direct line items, `goalType: Unlimited` |
| Level | Line item. Campaign pacing is context only |

---

## Step 1 — Sweep

One paginated call returns the line items with their campaign, advertiser, flight, currency,
pacing, publisher, deals, pricing and recent performance. Pagination applies to the lowest
level in the selection set, so this pages over line items.

The date filters are required. Line item `status: Active` is a settings flag, not a delivery
state: on a large account it also returns line items whose flights ended years ago, with their
deviation frozen at the value it had when they stopped. Without the date filters, sorting by
end date puts those first and buries the real list.

```graphql
{
  agencyListItems(
    filters: [
      { fieldName: "lineItem.status", operation: eq, values: ["Active"] }
      { fieldName: "lineItem.period.start", operation: lteq, values: ["2026-06-15"] }
      { fieldName: "lineItem.period.end", operation: gteq, values: ["2026-06-15"] }
      { fieldName: "lineItem.deliveryIndications.rtbBudget.deviationPercentage", operation: lt, values: [-20] }
    ]
    sortBy: [{ fieldName: "lineItem.period.end", order: asc }]
    pagination: { offset: 0, limit: 100 }
  ) {
    totalCount
    campaigns {
      id name currencyCode
      advertiser { id name }
      deliveryIndications { rtbBudget { goalType status deviationPercentage spendAmount } }
      orders {
        id name
        lineItems {
          id name type status buyingType channelTypes currencyCode timeZoneId rtbSetupId
          period { start end }
          media { id name }
          rtbSettings {
            setupId
            buying { type price maxBidPrice }
            budget { goalType activeFlight { amount periodType pacingType period { start end } } }
            inventory { dealIds dealGroupIds }
          }
          deliveryIndications {
            rtbBudget { goalType status deviationPercentage spendAmount updatedAt }
            rtbDeliveryHealth { status updatedAt }
            stats {
              yesterday { rtbBids trackedAds costAmount rtbWinRate }
              last7days { rtbBids trackedAds measuredImpressions costAmount rtbWinRate ecpmAmount }
            }
          }
        }
      }
    }
  }
}
```

Put today's date in both period filters. Page with `offset` until you have read `totalCount`
line items. If the server rejects the `deviationPercentage` path, remove that one filter and
apply the −20% threshold yourself as you read the rows.

Drop any line item with a null `rtbSetupId`, and any with `rtbBudget.goalType: Unlimited`, which
has no goal to miss.

## Step 2 — Projected underdelivery per flagged line item

The sweep carries spend and deviation but not the goal or the projection. Pull those for each
flagged line item using `rtbSetupId`, several per request with aliases.

```graphql
{
  a: rtbLineItemDeliveryIndications(id: "99999") {
    status goalType
    effectiveFlightPeriodType
    effectiveFlightTotalGoal
    effectiveFlightCurrentDelivery
    effectiveFlightProjectedDelivery
    effectiveFlightRemainingDelivery
    effectiveFlightDeviationPercentage
    effectiveBudgetFlightStartDate
    effectiveBudgetFlightEndDate
  }
}
```

**Read `effectiveFlightPeriodType` first.** It changes what every other field means:

- **`Total`** — the fields cover the whole budget flight. Expected underdelivery =
  `effectiveFlightTotalGoal − effectiveFlightProjectedDelivery`, only when positive. That is the
  amount projected to remain undelivered at `effectiveBudgetFlightEndDate`
- **`Daily`** — the fields cover today only. `effectiveFlightTotalGoal` is the daily amount and
  `effectiveFlightCurrentDelivery` is today's spend so far, even though
  `effectiveBudgetFlightEndDate` shows the end of the whole flight. Do not read goal minus
  projected as a flight total. Report the daily shortfall instead:
  `activeFlight.amount − (last7days.costAmount ÷ 7)`, when positive. If the user wants a
  flight-end figure, multiply it by the remaining days and label it a run-rate estimate

Expected underdelivery is not the current gap between planned and actual delivery, which
understates an item that has stopped delivering and overstates one that is recovering.

**The unit follows `goalType`.** Only `goalType: Money` gives an amount in the line item's
currency. For `Impressions` or `Clicks` the figure is impressions or clicks — label it with that
unit and never add it to a currency total. If the projection is missing, label the row "no
projection available" and show the goal and delivery to date rather than inventing a number.

`effectiveFlightDailyCost` is today's spend so far, not a daily run rate. Do not use it as one.

Remaining days run from today to `effectiveBudgetFlightEndDate` inclusive, which can be earlier
than the line item's `period.end` when it has several budget flights.

## Step 3 — Delivery health for the diagnosis

For each flagged line item using `rtbSetupId`, several per request with aliases. Every check
carries a `reason` naming the specific fault.

```graphql
{
  a: rtbLineItemDeliveryHealth(id: "99999") {
    status updatedAt
    indications {
      schedule { status reason }
      pricing { status reason }
      budget { status reason }
      bannerAssigned { status reason details { count } }
      tagCreativeAudit {
        status reason
        details {
          count
          rejected { rate }
          notSent { rate }
          notSupported { rate }
          inProgress { rate }
          approved { rate }
        }
      }
      advertiserIndustryVertical { status reason }
    }
  }
}
```

The `details` rates are fractions of `count`. Turn them into a figure worth putting in the
list — "1,752 of 2,960 tags rejected" rather than "creative audit warning".
`bannerAssigned.details.count` of zero confirms a missing creative rather than an unapproved one.

Health is a snapshot and can be days old. Show `updatedAt` when it is older than yesterday, and
treat an old finding as something to confirm rather than as settled.

| Check | `reason` | Severity | What it means |
|---|---|---|---|
| `bannerAssigned` | `NotAssigned` | Fail | No banners are assigned to the line item |
| `tagCreativeAudit` | `NotAssigned` | Fail | No tags exist, or no audits have been created for them |
| `tagCreativeAudit` | `TooManyRejected` | Fail | Too many tags are rejected |
| `tagCreativeAudit` | `TooManyNotApproved` | Fail | Rejected, not sent, not supported and pending audits together exceed the allowed threshold |
| `tagCreativeAudit` | `ManyRejected` | Warn | Many tags are rejected |
| `tagCreativeAudit` | `ManyNotSent` | Warn | Many tags have not been sent for audit |
| `tagCreativeAudit` | `ManyNotSupported` | Warn | Many tags are not supported by the publisher |
| `tagCreativeAudit` | `ManyInProgress` | Warn | Many audits are still pending |
| `tagCreativeAudit` | `ManyNotApproved` | Warn | Not enough approved audits |
| `pricing` | `PriceNotSet` | Fail | The pricing model requires `price` greater than 0 |
| `pricing` | `MaxBidPriceNotSet` | Fail | The pricing model requires `maxBidPrice` greater than 0 |
| `pricing` | `MinPercentNotSet` | Fail | The pricing model requires `minPercent` greater than 0 |
| `budget` | `AmountNotSet` | Fail | The budget flight has no amount greater than 0 |
| `budget` | `AmountGap` | Warn | There is a gap between budget flights, so no amount is available |
| `schedule` | `NotStarted` | Warn | Delivery has not started yet |
| `schedule` | `Gap` | Warn | One budget flight has ended and the next has not started |
| `advertiserIndustryVertical` | `SensitiveIndustryVerticalDetected` | Fail | The advertiser uses a sensitive industry vertical, such as alcohol |

`rtbDeliveryHealth` returns `null` when the last schedule period has ended, which is itself a
finding: the flight is over.

## Step 4 — Bid evidence, only when health is clean

When every health check returns `Ok`, the cause is in the auction rather than the setup. The
sweep's inline `stats` settles most cases on its own:

- `rtbWinRate` is a fraction — 0.0064 means 0.64%
- Stats return 0, not null, for a KPI that is not available. Before reading `rtbBids: 0` as "no
  bids", check that `yesterday` shows the same and that the line item has no spend or tracked
  ads in the same period

An `mcpStats` breakdown by `bidReason` can name the reason behind lost bids, but on some
accounts it fails at run time with "Request dimension/metric combination is not valid", even
though the query validates. Try it once:

```graphql
{
  mcpStats {
    totalRowCount
    columns {
      dimensions { bidReason { name } }
      metrics { rtbBids lostBids bidReasonCount impressions rtbWinRate }
    }
    rows(
      filter: {
        date: { from: "2026-06-08", to: "2026-06-14" }
        lineItem: { ids: ["67890"] }
      }
      paging: { offset: 0, limit: 50 }
    )
  }
}
```

If it fails, do not try variations. Diagnose from the sweep's stats and say the lost-bid reasons
were not available. Adform only receives not-winning reasons from some inventory sources, so an
empty breakdown is not evidence of anything either.

---

## Diagnosis

Work down this table and take the first row whose evidence is present. Never report a reason
the data does not support, and never recommend raising a bid price or opening supply unless the
matching evidence below is actually there.

Two derived values are used below, both for `goalType: Money` only:

- **Required daily spend** — `effectiveFlightRemainingDelivery` ÷ remaining days for a `Total`
  period; `activeFlight.amount` for a `Daily` period
- **Recent daily spend** — `last7days.costAmount` ÷ 7

Adform defines win rate as impressions divided by bids and sets no "low" or "high" threshold, so
the table only uses the patterns Adform Help describes: no bids, bids with a 0% win rate, and a
healthy win rate with limited spend. Do not invent a cut-off. Two expected exceptions:
programmatic guaranteed deals should win close to 100%, and DOOH deals that win impressions in
bulk can exceed 100%.

| Reason to report | Evidence required |
|---|---|
| Flight over | `rtbDeliveryHealth` is null because the last schedule period ended |
| Missing creative assignment | `bannerAssigned.reason: NotAssigned` |
| No tags or audits | `tagCreativeAudit.reason: NotAssigned` |
| Creative rejection | `tagCreativeAudit.reason` is `TooManyRejected` or `ManyRejected` |
| Creative audit incomplete | `tagCreativeAudit.reason` is `TooManyNotApproved`, `ManyNotSent`, `ManyNotSupported`, `ManyInProgress` or `ManyNotApproved` |
| Pricing not configured | `pricing.reason` is `PriceNotSet`, `MaxBidPriceNotSet` or `MinPercentNotSet` |
| Budget not configured | `budget.reason: AmountNotSet` |
| Budget flight gap | `budget.reason: AmountGap` |
| Schedule gap or not started | `schedule.reason` is `Gap` or `NotStarted` |
| Sensitive vertical restriction | `advertiserIndustryVertical.reason: SensitiveIndustryVerticalDetected` |
| No bids on deal supply | Health `Ok`, `inventory.dealIds` or `dealGroupIds` non-empty, and `last7days.rtbBids` is 0 |
| No bids on open supply | Health `Ok`, no deal wiring, and `last7days.rtbBids` is 0 |
| Bidding but not winning | `last7days.rtbBids` above 0 and `last7days.rtbWinRate` is 0 |
| Limited reach despite winning | `last7days.rtbWinRate` above 0, and recent daily spend below required daily spend |
| Historical pacing deficit despite recent recovery | Deviation still below −20%, but `yesterday.costAmount` at or above required daily spend |
| Late start against even pacing | `activeFlight.pacingType: Evenly` and daily delivery indications show no spend for the first days of the flight. See "Reading deviation" below |
| No documented cause found | Health `Ok` and no bid pattern explains it. Say so plainly |

What each auction pattern points at, according to Adform Help (*Fix Common Deal-Related Issues*
and *Troubleshoot Campaigns*). Present these as things to check, not as confirmed causes:

- **No bids on deal supply** — a mismatch between the publisher's deal setup and the deal in
  Adform, such as the seat ID or inventory source, a domain exclusion conflicting with the
  publisher's sites, an unapproved tag, the wrong environment, insufficient budget, or banners
  that are not published or do not match the agreed placements. Hand over to
  adform-deal-health-check for the deal itself
- **No bids on open supply** — targeting rules that leave no matching traffic. Use
  adform-line-items to read the targeting
- **Bidding but not winning** — a bid below the floor (Adform Help suggests adding 15% to a deal
  floor to cover fees), a landing page not allowed by the publisher or not matching the brand,
  or publisher-side filtering
- **Limited reach despite winning** — something restricting bid requests, such as above-the-fold
  only targeting, domain exclusions, contextual or audience targeting that does not overlap the
  supply, brand safety filtering, or a buying strategy that bids below a deal floor

For line items on dynamic CPM, Adform already raises the bid when a line item underdelivers, so
a pricing finding points at the maximum CPM cap rather than the bid price. For any pricing
fault, name the cap that matches the line item's buying type from `rtbSettings.buying.type`
rather than assuming CPM. See the pricing model table in adform-line-items, and size any
increase with adform-bid-landscape.

Keep the reason to one short, specific line naming the evidence — "no banners assigned",
"bidding but 0% win rate on 1,204,332 bids", "recovered yesterday, deficit from the first 9 days
of the flight".

### Reading deviation

Adform Help (*Check Campaign Delivery Deviation*) bands programmatic deviation as on track
between −10% and +10%, falling behind between −10% and −30%, and falling behind significantly
below −30%. The −20% threshold sits inside the falling-behind band. Show the band next to each
row's deviation.

Deviation can overstate a problem:

- A line item with even pacing that started late on purpose shows as underdelivering for its
  whole flight, because deviation is measured against the full schedule
- A change to the schedule or budget can swing deviation sharply overnight — for example from
  −21% to +4,216% after a budget cut — while actual spend stays level. Adform Help recommends
  checking daily spend instead: use `rtbLineItemDailyDeliveryIndications` (see
  adform-pacing-check) and read the daily cost, not the daily deviation

Deviation is not calculated when a line item uses its parent order's budget, or when its budget
flight falls outside the order flight. Those line items cannot appear in this list, so say in
the scope line that line items without their own deviation are not covered.

### Not double-counting

Report amounts at line-item level only. Campaign pacing is a context column, never an addend.
Where several line items sit under one campaign, their expected underdelivery may overlap with a
campaign-level budget: cap the campaign total at the campaign's own
`effectiveFlightTotalGoal − effectiveFlightProjectedDelivery` from `campaignDeliveryIndications`
(for a `Total` period only), present the line-item rows as the breakdown, and note that they
share one campaign budget.

---

## Sorting

1. Remaining days ascending, so the items closest to their end date come first
2. Expected underdelivery descending within the same remaining-days group, money goals before
   impression or click goals

Items sharing an end date may be grouped under a single date heading.

---

## Presenting

Open with the scope, before any table — the filter applied, the date the figures are as at, that
line items without their own deviation are not covered, and how many line items across how many
campaigns were found.

### Triage list

| Column | Source |
|---|---|
| Advertiser | `campaigns.advertiser.name` |
| Campaign name and ID | `campaigns.name`, `campaigns.id` |
| Campaign pacing | campaign `rtbBudget.deviationPercentage` |
| Line item name and ID | `lineItems.name`, `lineItems.id` |
| Start and end date | `period.start`, `period.end` |
| Remaining days | Step 2 |
| Current line item pacing | `rtbBudget.deviationPercentage`, with its band |
| Budget period | `Total` or `Daily` |
| Expected underdelivery | Step 2, with its currency or unit, and "per day" for a daily budget |
| Publisher or inventory source | `media.name`, or the deal wiring from `inventory` |
| Short reason | The diagnosis table |

### Closing summary

- Total expected underdelivery, one line per currency and one per non-money goal unit, never
  pooled. Keep daily-budget shortfalls on their own line, as a per-day figure
- Number of affected advertisers, campaigns and line items
- Number of Critical delivery health findings
- The 3 items with the nearest end date
- The 3 largest projected underdelivery amounts

### Formatting

- Every amount in its own currency, labelled, with at most 2 decimals. Never add different
  currencies into one total. To compare across currencies, convert explicitly with
  `currencyRate` (see adform-geo-reference) and say so
- Pacing as a signed percentage with at most 2 decimals
- Always carry both name and ID
- Unavailable values are labelled "not available" or "no projection available", never
  estimated and never shown as zero

If the result is too large to return in full, keep the most urgent items by the sort order
above, and state exactly how it was limited: how many of how many line items are shown, and the
cut-off used.

This skill reads only. It never changes a line item, budget, creative or flight.
