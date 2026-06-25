---
name: adform-inventory-deals
description: >-
  Inventory and deal discovery for Adform Flow DSP. Explore marketplace inventory sources, browse deals
  (private, preferred, open auction), inspect deal groups. Trigger on "what inventory is available",
  "show me deals", "open auctions", "deal groups", "past traffic for domain or deal", "traffic on bild.de".
  For audience marketplace use adform-audience-discovery; line-item wiring: adform-line-items;
  bid landscape: adform-bid-landscape. Read-only.
---

# Adform inventory and deals

Explore marketplace inventory sources, browse and search deals and open auctions, inspect deal
groups, and check past traffic. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_search` to
look up field names; use `graphql_introspect` for complex nested types. Keep calls sequential
(~1–2s apart).

---

## 1. Browse marketplace deals

Always paginate. Do not request `inventorySources` in the same call as `marketplaceDeals`.
The deal `id` is composite: `{inventorySourceId}_{dealId}`.

```graphql
{
  buyerDealListItems(
    pagination: { offset: 0, limit: 50 }
  ) {
    buyerDeals {
      id dealId name type price currencyCode status startDate endDate
      inventorySource { id name }
      advertisers { totalCount allAdvertisers }
      healthIndications { status }
      assignedToLineItemsCount
    }
    totalCount
  }
}
```

### Search deals by keyword

```graphql
{
  buyerDealListItems(
    filters: [{ fieldName: "buyerDeal.searchPhrase", operation: contains, values: ["fashion"] }]
    pagination: { offset: 0, limit: 50 }
  ) {
    buyerDeals {
      id dealId name type price currencyCode status startDate endDate
      inventorySource { id name }
      healthIndications { status }
    }
    totalCount
  }
}
```

---

## 2. Browse inventory sources

Use pagination only — do not pass filters or sortBy on this query.

```graphql
{
  inventoryMarketplaceListItems(
    pagination: { offset: 0, limit: 100 }
  ) {
    inventorySources { id name adExchange { id name } channels environments }
    hasMoreItems totalCount
  }
}
```

---

## 3. Search open auctions

Must provide `advertiserId` or `campaignId`. Do not pass a sort argument.

```graphql
{
  searchOpenAuctions(
    advertiserId: "71883"
    limit: 20
  ) {
    results { id name inventorySourceId inventorySourceName country channel bannerTypes sizes }
    next previous totalCount
  }
}
```

---

## 4. Deal groups

### List buyer deal groups

```graphql
{
  buyerDealGroups(
    filters: { advertiserId: "71883" }
    pagination: { offset: 0, limit: 20 }
  ) {
    dealGroups { id name status dealIds }
    totalCount
  }
}
```

### Get deal group detail

```graphql
{ buyerDealGroup(id: "12345") { id name status dealIds } }
```

---

## 5. Past traffic

### Domain past traffic

```graphql
{
  inventoryMarketplaceDomainPastTraffic(
    domains: ["bild.de", "spiegel.de"]
  ) {
    domain
    trafficCounts { cookies requests }
  }
}
```

### Deal past traffic

```graphql
{
  inventoryMarketplaceDealPastTraffic(
    deals: [{ inventorySourceId: "42", dealId: "12345" }]
  ) {
    dealId
    trafficCounts { cookies requests }
  }
}
```

### Inventory source past traffic

```graphql
{
  inventoryMarketplaceInventoryPastTraffic(inventoryIds: [42, 55]) {
    inventoryId
    trafficCounts { cookies requests }
  }
}
```

### Deal + line item past traffic

```graphql
{
  dealLineItemPastTraffic(inventorySourceId: "42", dealId: "12345", lineItemId: "99999") {
    levels { key name group availableImpressions }
  }
}
```

---

## Common patterns

- **Inventory exploration**: browse inventory sources → search deals → check past traffic →
  note deal IDs for line-item assignment
- **Deal sizing**: past traffic to validate volume before targeting
- **Deal groups**: list groups, then get detail to see which deal IDs are bundled

## Presenting

Show deals in a table with name, type (private/preferred), inventory source, floor price,
currency, and status. For past traffic, show cookies and requests per item and flag thin
inventory where volume may not support the planned budget.
