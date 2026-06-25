---
name: adform-entity-browsing
description: >-
  Entity and ID resolution for Adform Flow DSP. Find, list, or inspect advertisers,
  campaigns, orders, and line items by name or ID. Covers hierarchy browsing with delivery indications,
  name-to-ID lookup, and advertiser detail including labels and domain settings. Trigger on "find advertiser X",
  "ID for campaign Y", "list advertisers", "advertiser settings", "resolve name to ID". For campaign/order
  config use adform-campaign-management; for line-item detail use adform-line-items. Read-only.
---

# Adform entity browsing and ID resolution

Find, list, and resolve Adform entities — advertisers, campaigns, orders, line items — by name
or ID. Browse the full hierarchy with delivery indications, or do quick name-to-ID lookups.
Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute(query, variables)` to run and
`graphql_validate` to check a query first. Always validate before executing. The queries below are
**illustrative examples** — if a field or input shape isn't shown, or a query fails validation,
discover the current schema with `graphql_search` (lighter, preferred) and fall back to
`graphql_introspect` one call at a time with ≥2s between calls for complex input types, enum
values, or union/interface resolution.

## Reliability

Keep calls light and sequential (~1–2s apart). If the backend returns `unexpected server error`,
this is a transient backend issue rather than a query problem — confirm validity with
`graphql_validate`, then retry up to twice before reporting.

---

## 1. Name-to-ID lookup

Convert an entity name to its numeric ID using `agencyListItems` with a search filter. Set the
filter fieldName to the entity type and property you want to match.

```graphql
{
  agencyListItems(
    filters: [{ fieldName: "advertiser.name", operation: eq, values: ["Acme Corp"] }]
  ) {
    advertisers { id name }
  }
}
```

Reverse lookup — ID to name:

```graphql
{
  agencyListItems(
    filters: [{ fieldName: "campaign.id", operation: in, values: ["123456", "789012"] }]
  ) {
    campaigns { id name }
  }
}
```

---

## 2. Hierarchy browser — campaigns by advertiser

```graphql
{
  agencyListItems(
    filters: [{ fieldName: "advertiser.id", operation: eq, values: ["71883"] }]
    pagination: { limit: 20, offset: 0 }
  ) {
    campaigns {
      id name status
      period { start end }
      createdAt billingCode currencyCode type subType
    }
  }
}
```

## 3. Hierarchy browser — line items by order

```graphql
{
  agencyListItems(
    filters: [{ fieldName: "order.id", operation: eq, values: ["456789"] }]
    pagination: { limit: 20, offset: 0 }
  ) {
    lineItems {
      id name type status buyingType channelTypes
      rtbSettings { environments buying { type price maxBidPrice } }
    }
  }
}
```

---

## 4. List advertisers

```graphql
{
  advertisers(
    status: active
    offset: 0
    limit: 20
  ) {
    advertisers { id name status type }
    totalCount
  }
}
```

## 5. Get advertiser detail

```graphql
{
  advertiser(id: "71883") {
    id name status type
    industryVerticalId timeZoneMappingId
    trackingDomain netAmountCalcMethod
  }
}
```

## 6. Get advertiser labels

```graphql
{ advertiserLabels(id: "71883") { labelGroups { id name labels { id name } } } }
```

## 7. Get RTB domain settings

```graphql
{ rtbDomains(id: "71883") { mode domains } }
```

---

## Common patterns

- **Name to ID**: `agencyListItems` with a `searchPhrase` contains filter for the entity level
- **Hierarchy drill-down**: list advertisers → campaigns by advertiser → orders by campaign →
  line items by order
- **ID format**: advertiser, campaign, order, and line item IDs are numeric strings

## Presenting

Show entity name and ID, status, and relevant config fields. For hierarchy views, render as an
indented tree or table. Always include the numeric ID so the trader can cross-reference in the
Adform platform.
