---
name: adform-line-items
description: >-
  Line-item inspection for Adform Flow DSP. Covers RTB and direct line items: config, targeting rules,
  delivery indications, creative browsing, and tag creative audit. Trigger on "show me line items",
  "RTB line item config", "deals wired", "targeting on this line item", "publisher name", "creatives in campaign",
  "tag audit status". For delivery health use adform-delivery-health; bid landscape: adform-bid-landscape;
  pacing: adform-pacing-check. Read-only.
---

# Adform line items and wiring

Inspect RTB and direct line items — config, inventory and deal wiring, audience targeting,
delivery, creatives, media search, and tag creative audit. Read-only.

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

## RTB line items

### List RTB line items

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

### Get RTB line item — core config

```graphql
{ rtbLineItem(id: "99999") { id name environments orderId campaignId paused deleted } }
```

For inventory wiring, targeting rules, budget flights, pricing, and impression capping, use
`graphql_introspect` on the relevant nested types before selecting those fields.

### Get RTB line item delivery indications

```graphql
{
  rtbLineItemDeliveryIndications(id: "99999") {
    status goalType
    effectiveFlightTotalGoal effectiveFlightCurrentDelivery
    effectiveFlightProjectedDelivery effectiveFlightDeviationPercentage
    effectiveFlightTotalCost effectiveFlightDailyCost
    effectiveBudgetFlightStartDate effectiveBudgetFlightEndDate
  }
}
```

### Get RTB line item daily delivery — time-series (max 30 days)

```graphql
{
  rtbLineItemDailyDeliveryIndications(
    ids: ["99999"]
    from: "2026-05-13"
    until: "2026-06-12"
  ) {
    id deliveryDate
    deliveryIndications { effectiveFlightDailyCost effectiveFlightDeviationPercentage status }
  }
}
```

### Get RTB line item delivery health — root-cause checks

```graphql
{
  rtbLineItemDeliveryHealth(id: "99999") {
    status updatedAt
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

### Get RTB line item inventory — paginated

```graphql
{
  rtbLineItemInventory(id: "99999", pagination: { offset: 0, limit: 50 }) {
    inventorySources { id name }
    totalCount
  }
}
```

---

## Direct line items

### List direct line items by order

```graphql
{
  directLineItems(
    orderId: "12345"
    pagination: { offset: 0, limit: 50 }
  ) {
    directLineItems { id name status }
    totalCount
  }
}
```

Use `graphql_introspect` on `DirectLineItem` to discover available fields including pricing,
volume, periods, and media UUID.

### Get direct line item

```graphql
{ directLineItem(id: "67890") { id name status } }
```

### Get direct line item delivery indications

```graphql
{
  directLineItemDeliveryIndications(id: "67890") {
    status
  }
}
```

---

## Media and publisher search

Resolve `mediaUuid` from direct line items to publisher names:

```graphql
{
  medias(
    search: { uuids: ["uuid-1", "uuid-2"] }
    pagination: { offset: 0, limit: 50 }
  ) {
    medias { uuid id name active }
    totalCount
  }
}
```

---

## Creatives and ads

```graphql
{
  adsByCampaignId(
    campaignId: "3993873"
    pagination: { offset: 0, limit: 50 }
  ) {
    ads {
      id { uuid id }
      name batch adType commercialType
      size { width height }
      publishStatus active deleted
    }
    totalCount
  }
}
```

---

## Tag creative audit by exchange

`tagId` is the tag entity ID from the tags list, not the ad ID. Returns SSP approval status
per inventory source.

```graphql
{
  tagCreativeAuditInventorySources(
    tagId: "85543973"
    pagination: { offset: 0, limit: 50 }
  ) {
    totalCount
    inventorySources { id name status message }
  }
}
```

Status values: `notSent`, `inProgress`, `approved`, `rejected`, `notSupported`.

---

## Common patterns

- **Line-item drill-down**: list RTB line items by order → get RTB line item for full config
- **Direct plan review**: list direct line items → search media to resolve publisher names
- **Creative audit**: list campaign tags (adform-tracking-tags) → tag creative audit per tag

## Presenting

Show line items in a table with key fields. For targeting, render rules as structured bullet
lists. For direct line items, include financial fields with currency.
