---
name: adform-pipeline-forecast
description: >-
  Account-wide forward spend forecast for the Adform FLOW DSP. Projects expected daily RTB spend
  from the upcoming Monday, explains the change against the last 7 complete days, and breaks it
  into campaigns ending, campaigns starting, and budgets running out or at risk on continuing
  campaigns. Trigger on "what will we spend next week", "expected daily spend from Monday",
  "what is starting and ending next week", "spend pipeline", "how does next week look". Runs
  across the whole account with no advertiser needed. For a single entity's pacing verdict use
  adform-pacing-check; for underdelivering line items ranked and diagnosed use
  adform-underdelivery-triage. Read-only.
---

# Adform pipeline forecast

Account-wide forecast of expected daily RTB spend from the upcoming Monday, with the reasons it
differs from the last 7 complete days. Campaigns commonly end on a Sunday and start on a Monday,
so this answers what that transition does to daily spend. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries and `graphql_validate` to
check them first. Use `graphql_search` to look up field names. Keep calls sequential (~1–2s
apart), never in parallel. To cut the number of calls, put several lookups of the same kind into
one request with aliases, for example five `campaignDeliveryIndications` lookups named `a:` to
`e:`.

Validation does not catch everything. `filters.fieldName` and `sortBy.fieldName` are free-text
paths, and the server rejects the `between` filter operation even though the schema lists it —
use a `gteq` and an `lteq` filter on the same field instead. If the server rejects a filter,
drop it and apply the same condition client-side rather than abandoning the step.

## Default scope

Unless the user overrides it:

| Setting | Default |
|---|---|
| Scope | All advertisers the user can see. Do not ask which advertiser |
| Spend | RTB spend only. Direct line items have no RTB budget |
| Baseline | The last 7 complete calendar days, ending yesterday |
| Forecast start | The upcoming Monday |
| Forecast window | That Monday through the following Sunday |
| Second week | Flagged for major changes only, not fully forecast |
| Currency | The campaign's own currency, never converted or pooled |

State the resolved dates and the scope before any figures.

## Start from spending campaigns, not from every active campaign

On a large account, thousands of campaigns can carry `status: Active`, because status is a
settings flag rather than a delivery state. Most of them ended long ago or never spend, and RTB
spend is usually concentrated in a few dozen campaigns. So the forecast is built from two short
lists — campaigns that spent in the baseline (Step 2) and campaigns starting from today onwards
(Step 4). Never sweep every active campaign.

---

## Step 1 — Resolve the window

Work out these dates before querying, and reuse them everywhere:

- `baselineFrom` / `baselineTo` — the last 7 complete calendar days, ending yesterday
- `forecastStart` — the next Monday strictly after today. If today is Monday, use today only when
  the user says "this week", otherwise the following Monday
- `forecastEnd` — `forecastStart` + 6 days (the Sunday)
- `week2End` — `forecastEnd` + 7 days
- `daysBeforeWindow` — the days from today up to the day before `forecastStart`, inclusive

## Step 2 — Baseline spend per campaign

Account-wide RTB spend over the baseline, one row per campaign. No advertiser filter means every
advertiser the user can see.

```graphql
{
  mcpStats {
    totalRowCount
    totals
    columns {
      dimensions { campaign { id } campaign { currencyName } }
      metrics { cost(costType: rtb) }
    }
    rows(
      filter: { date: { from: "2026-06-08", to: "2026-06-14" } }
      paging: { offset: 0, limit: 100 }
      sort: [{ column: 2, direction: desc }]
    )
  }
}
```

Rows come back sorted by spend, highest first. Page with `offset` only until the first row with
a cost of 0 — everything after it is a campaign that did not spend. Those rows often carry the
currency `-`.

`costType: rtb` reports RTB budget spent, the same basis as the budgets and delivery indications
used below, so both sides of the forecast match. Say in the output that the baseline is RTB cost.
See adform-stats-performance for the full `costType` and currency rules.

Each spending campaign's **run rate** is its baseline cost ÷ 7. The campaign dimension carries no
name; names come from Step 3.

## Step 3 — Budgets and flights for the spending campaigns

One request per 100 spending campaigns, filtered by their IDs. There is no status filter, so
campaigns that ended during the baseline still come back.

```graphql
{
  agencyListItems(
    filters: [{ fieldName: "campaign.id", operation: in, values: [12345, 12346] }]
    pagination: { offset: 0, limit: 100 }
  ) {
    campaigns {
      id name status currencyCode
      period { start end }
      advertiser { id name }
      rtbSettings {
        budget {
          goalType
          activeFlight { amount periodType pacingType period { start end } }
          nextFlight { amount periodType period { start end } }
        }
      }
      deliveryIndications {
        rtbBudget { goalType status deviationPercentage spendAmount }
      }
    }
  }
}
```

### Where the budget lives

A campaign's own budget is often 0 or `goalType: Unlimited`, even when it spends heavily, because
the budget is set on its orders or line items instead. Use the first level that holds a non-zero
amount:

1. The campaign — `rtbSettings.budget.activeFlight.amount`, or `nextFlight.amount` before the
   flight has begun
2. Its orders — sum `rtbSettings.budget` across `orders` (see the query in Step 4)
3. Its line items — sum `rtbSettings.budget` across `lineItems`, the same way

For a continuing campaign, the remaining budget is only easy to read at campaign level, where
remaining = `activeFlight.amount − deliveryIndications.rtbBudget.spendAmount`. When the budget
sits lower down, do not try to rebuild a remaining figure: forecast it on run rate alone and
label it "budget held below campaign level, not capped".

## Step 4 — Campaigns starting from today

Campaigns that start from today onwards spent nothing in the baseline but may spend in the
window. Most are already `status: Active` before their start date and a few are `Inactive`, so
include both.

```graphql
{
  agencyListItems(
    filters: [
      { fieldName: "campaign.status", operation: in, values: ["Active", "Inactive"] }
      { fieldName: "campaign.period.start", operation: gteq, values: ["2026-06-15"] }
      { fieldName: "campaign.period.start", operation: lteq, values: ["2026-07-05"] }
    ]
    sortBy: [{ fieldName: "campaign.period.start", order: asc }]
    pagination: { offset: 0, limit: 100 }
  ) {
    totalCount
    campaigns {
      id name status currencyCode
      period { start end }
      advertiser { id name }
      rtbSettings {
        budget {
          goalType
          activeFlight { amount periodType period { start end } }
          nextFlight { amount periodType period { start end } }
        }
      }
    }
  }
}
```

Use today for the first date and `week2End` for the second. For every starting campaign whose
own budget is 0, pull its orders' budgets in one request:

```graphql
{
  agencyListItems(
    filters: [{ fieldName: "campaign.id", operation: in, values: [12347, 12348] }]
    pagination: { offset: 0, limit: 100 }
  ) {
    campaigns {
      id
      orders {
        id status period { start end }
        rtbSettings {
          budget {
            goalType
            activeFlight { amount periodType period { start end } }
            nextFlight { amount periodType period { start end } }
          }
        }
      }
    }
  }
}
```

If the orders are 0 as well, repeat one level down with `lineItems` inside `orders`. A starting
campaign whose budget is 0 at every level, or whose goal is impressions or clicks, has no money
amount to spread — list it with "no money budget set" rather than a contribution.

---

## Calculating expected daily spend

Never divide total budget by total flight length. That ignores what has already been spent and
ignores pacing.

Do not forecast next week's spend from the projection fields (`effectiveFlightProjectedDelivery`
and related) either. They mislead in two ways:

- When the budget period is `Daily`, every `effectiveFlight*` field covers today only, not the
  flight
- After a budget change, deviation and projection can swing sharply — for example from −21% to
  +4,216% deviation overnight after a budget cut — while actual spend stays level. Spreading the
  remaining budget across the remaining months can then predict a fraction of what the campaign
  actually goes on to spend each day until its budget runs out

Recent actual spend is the more reliable guide. Classify every campaign, then apply the matching
rule:

| Class | Test | Expected daily contribution in the window |
|---|---|---|
| Already ended | Spent in the baseline, `period.end` before today | Zero. All its run rate is outgoing |
| Ending before the window | `period.end` from today up to the day before `forecastStart` | Zero. All its run rate is outgoing |
| Ending inside the window | `period.end` inside the window | Run rate × days it runs in the window ÷ 7 |
| Continuing | `period.end` after `forecastEnd` | Run rate, capped by its remaining budget (below) |
| Starting | `period.start` inside the window | Flight budget ÷ flight days × days it runs in the window ÷ 7, labelled plan-based |
| Starting this week | `period.start` from today up to the day before `forecastStart` | Same as Starting, counting all 7 window days |
| Starting in week 2 | `period.start` after `forecastEnd` | Not in the window. Report under "Next expected change" |

### Capping a continuing campaign by its remaining budget

Only when the budget is a campaign-level money amount with `periodType: Total`:

- Budget left at the start of the window = remaining − (run rate × `daysBeforeWindow`)
- If that covers 7 days at the run rate, the contribution is the run rate
- If not, the contribution is the budget left ÷ 7 (or 0 if none is left), and the campaign is
  flagged as running out of budget, with the date: today + remaining ÷ run rate

With `periodType: Daily`, cap the run rate at `activeFlight.amount`. With `goalType: Unlimited`,
or a budget held below campaign level, use the run rate uncapped and label it so.

Report run-out dates that fall after the window under "Next expected change". A campaign that
spends heavily but runs out mid-window is often one of the main causes of a drop.

### Budget at risk

Projected underdelivery is a risk measure, not part of the spend forecast. Pull it only for
continuing campaigns with a campaign-level money budget, `periodType: Total` and a negative
deviation in Step 3, several per request with aliases:

```graphql
{
  a: campaignDeliveryIndications(id: "12345") {
    status goalType
    effectiveFlightPeriodType
    effectiveFlightTotalGoal
    effectiveFlightCurrentDelivery
    effectiveFlightProjectedDelivery
    effectiveFlightDeviationPercentage
    effectiveBudgetFlightEndDate
  }
}
```

- Projected underdelivery = `effectiveFlightTotalGoal − effectiveFlightProjectedDelivery`, when
  positive and only when `effectiveFlightPeriodType` is `Total`
- `status: ScheduleGap` means the campaign is between flights. Check `nextFlight` before
  treating it as ending
- When a large shortfall coincides with a sudden swing in deviation, check daily cost with
  `campaignDailyDeliveryIndications` (see adform-pacing-check) before reporting it as a risk — it
  may be a budget change rather than a delivery problem
- No data from `campaignDeliveryIndications` does not mean the campaign has no delivery. See
  "When campaign or order delivery returns no data" in adform-pacing-check

### Adding it up

Per currency:

- **Outgoing** — run rate of already ended and ending campaigns, plus the part of an
  ending-inside-the-window campaign's run rate that stops
- **Change on continuing campaigns** — their contributions minus their run rates (negative when
  budgets run out)
- **Incoming** — starting campaigns' contributions
- **Expected daily spend** — baseline daily average − outgoing + change on continuing + incoming

These lines reconcile exactly to the baseline. Never add two currencies together. If the account
runs several currencies, produce one summary and one key figures table per currency and say so
in the scope line.

---

## Presenting

Lead with a two or three sentence executive summary: the expected daily spend from the upcoming
Monday, the change against the baseline average in absolute and percentage terms, and the main
cause. For example: "Expected RTB spend from Monday is about EUR 17,560 per day, EUR 7,115 per day
lower (−28.84%) than the 7-day average of EUR 24,675. Most of the drop comes from campaigns ending
on Sunday. The 11 campaigns starting on Monday add about EUR 6,752 per day, which does not cover
the outgoing spend."

Then the causes, in order of size: spend disappearing as campaigns end, budgets running out on
continuing campaigns, contribution from new campaigns, and any major change expected in week 2.

### Key figures

| Metric | Value |
|---|---|
| Average actual daily RTB spend, last 7 complete days | |
| Expected daily spend from the upcoming Monday | |
| Expected change, absolute and percentage | |
| Daily spend leaving with campaigns that end | |
| Change on continuing campaigns (budgets running out) | |
| New budget starting this week and in the window | |
| Expected daily contribution from new campaigns | |
| New budget starting in the following week | |
| Projected underdelivery on continuing campaigns | |
| Continuing spend that is uncapped run rate | |

### New campaigns starting

Columns: campaign name, campaign ID, start date, end date, budget, where the budget is held
(campaign, orders or line items), expected daily contribution. List the largest incoming budgets
individually and collapse the tail into a single "Other campaigns (n)" row carrying the combined
budget and contribution.

### Main downward risks

Columns: campaign name, campaign ID, end date, run rate, remaining budget, run-out date or
projected underdelivery, short reason. Sort by the daily spend at stake, largest first. The
reason comes from the data — budget running out, deviation and status — not from assumption. For
a line item level diagnosis of why a campaign is underdelivering, use adform-underdelivery-triage.

### Next expected change

Large campaigns ending after the first week, budgets that run out after the window, and campaigns
starting in week 2 with their estimated daily contribution.

### Formatting

- Every amount in its campaign's own currency, labelled, with at most 2 decimals. To compare
  across currencies, convert explicitly with `currencyRate` (see adform-geo-reference) and say so
- Percentages with a sign and at most 2 decimals
- Always carry both campaign name and campaign ID
- Label actual spend, run-rate spend, plan-based spend and budget distinctly. Never present a
  forecast as actual
- Unavailable values are labelled "not available" or "no money budget set", never estimated and
  never shown as zero
- If the result was limited, say exactly how and what share of baseline spend it covers

This skill reads only. It never changes a campaign, budget or flight.
