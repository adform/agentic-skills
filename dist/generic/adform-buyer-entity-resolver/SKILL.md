---
name: adform-buyer-entity-resolver
description: >-
  Resolve a person's name to their Adform user IDs, and entity names to numeric IDs, on the
  Adform FLOW DSP. The only single-call path from a campaign manager's name to their user IDs -
  `agencyListItems` filters on `managerId` but carries no manager name field. Also a fast path
  for advertiser, campaign, order, and line item name lookup. Trigger on "campaigns managed by
  X", "whose campaigns are these", "find the user ID for Y", "what's the ID for campaign Z", "I
  only have the name". For filtered, sorted, or counted entity lists use adform-entity-browsing.
  Read-only.
---

# Adform buyer entity resolver

Who manages this, and what is the ID for that name? Resolves a person's name to their Adform user
IDs, and advertiser, campaign, order, and line item names to numeric IDs. One call, no GraphQL.
Read-only.

## Connection & tooling

Runs on the Adform MCP. Call `er_buyer_entity_resolver(filters)` directly; there is no validate
step. Issue calls sequentially (~1-2s apart) rather than in parallel. Results are scoped to the
caller's agency seat.

---

## Manager name to user IDs

The primary use. `agencyListItems` exposes and filters `campaign.managerId` and
`campaign.coManagerId`, but carries no manager name field, and the `managers` query takes no
search argument. This tool is the only way to go from a name to an ID in one call.

```json
{ "filters": [ { "field": "campaign.managerId", "operation": "eq", "values": ["Smith"] } ] }
```

```json
[ { "field": "campaign.managerId", "names": [ { "John Smith": [180680, 175704, 149809] } ] } ]
```

A person holds one user ID per client seat, so expect several. Pass the whole set downstream with
`in`, never `eq` on the first one:

```graphql
{
  agencyListItems(
    filters: [{ fieldName: "campaign.managerId", operation: in, values: ["180680", "175704"] }]
    sortBy: [{ fieldName: "campaign.createdAt", order: desc }]
    pagination: { offset: 0, limit: 20 }
  ) {
    totalCount
    campaigns { id name status managerId coManagerId advertiser { name } }
  }
}
```

Only `campaign.managerId` is supported here; `order.managerId` is not. There is no co-manager
field either, but `managerId` and `coManagerId` draw from the same user directory, so the IDs
returned are valid against `coManagerId` too.

---

## Entity name to ID

A fast path when a single named entity needs an ID and completeness does not matter. One filter
object per name; `.name` fields take a single value each.

```json
{
  "filters": [
    { "field": "advertiser.name", "operation": "eq", "values": ["Acme Corp"] },
    { "field": "campaign.name",   "operation": "eq", "values": ["Acme Awareness Q4"] }
  ]
}
```

```json
[
  { "field": "advertiser.name", "names": [ { "Acme Corp": ["2197361"] } ] },
  { "field": "campaign.name",   "names": [ { "Acme Awareness Q4": ["3786678"] } ] }
]
```

Filters resolve independently and return side by side. They are not ANDed, so this cannot answer
"campaigns for advertiser X managed by Y" - resolve each part, then filter in
adform-entity-browsing.

---

## Fields and operations

| Field | Returns | ID type |
|---|---|---|
| `campaign.managerId` | User ID(s) for a person | integer |
| `advertiser.name` | Advertiser ID | string |
| `campaign.name` | Campaign ID | string |
| `order.name` | Order ID | string |
| `lineItem.name` | Line item ID | string |

`eq` is an exact whole-string match; a partial string will not match a longer name. `contains`
matches a substring anywhere in the name. `campaign.managerId` ignores the distinction and always
searches on a name fragment. No other field or entity prefix is supported.

---

## Reading the results

- **Name results are not guaranteed complete.** There is no total count and no pagination, and
  broad searches return a subset. In testing, a `campaign.name` search returned 19 of 31 matching
  campaigns and a `lineItem.name` search returned roughly 62 of 210. An entity that exists can be
  absent from the response. Treat a thin or empty result as unconfirmed and re-run it against
  `agencyListItems` with `totalCount` before telling a trader something does not exist.
- **Names are not unique.** Several IDs under one name is normal. Disambiguate; do not pick the
  first.
- **Manager IDs are integers**, every other field returns ID strings. Cast before using them in
  GraphQL filters expecting strings.
- **The manager directory includes non-human entries** such as API service accounts and internal
  system connections. Filter these out before presenting a list of people.
- **Not a reverse lookup.** An ID passed as a value returns nothing. For ID to name, use
  `agencyListItems` with an `in` filter.

## Common workflows

- **Book of business**: resolve the person here, then filter `campaign.managerId in [...]` in
  adform-entity-browsing for their campaigns with status, dates, and advertiser
- **Ownership check**: resolve the manager, compare against `managerId` and `coManagerId` on the
  campaigns already in hand
- **Single known entity**: resolve the name here, hand the ID to adform-pacing-check,
  adform-delivery-health, adform-stats-performance, or adform-line-items
- **Anything needing all matches**, a count, a sort, or a status filter: skip this tool and go
  straight to adform-entity-browsing

## Presenting

For a manager, state the person and the number of seats their IDs cover before listing campaigns.
For an entity, state the name and ID and move on to what the trader actually asked. On multiple
matches, show a short candidate table and ask which one. Never silently pick the first match, and
never report "not found" from this tool alone.
