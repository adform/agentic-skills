---
name: adform-past-traffic
description: >-
  Past-traffic lookup for the Adform FLOW DSP. Use when a
  programmatic trader wants to know how much real traffic a piece of inventory recently saw —
  unique cookies and bid requests for specific domains, apps, deals, etc. Trigger on "how much traffic does domain X get",
  "what did this deal or app do recently", "past traffic for this inventory". For a CPM-versus-win-rate forecast use
  adform-bid-landscape; for plan-level reach use adform-reach-forecast. Read-only.
---

# Adform past traffic

How much real traffic did this inventory recently see? Returns unique cookies and bid requests
for domains, apps, deals, inventory sources, or line items. Use this to ground a forecast in
observed reality before targeting. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_introspect`
on `PastTrafficFilterInput` if you need to narrow results by geo or format. Keep calls
sequential (~1–2s apart).

---

## Domain past traffic

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

## App past traffic

```graphql
{
  inventoryMarketplaceAppPastTraffic(
    apps: [{ bundleId: "com.example.app", store: "google" }]
  ) {
    bundleId
    trafficCounts { cookies requests }
  }
}
```

## Deal past traffic

```graphql
{
  inventoryMarketplaceDealPastTraffic(
    deals: [{ inventoryId: 42, dealId: "12345" }]
  ) {
    dealId
    trafficCounts { cookies requests }
  }
}
```

## Inventory source past traffic

```graphql
{
  inventoryMarketplaceInventoryPastTraffic(inventoryIds: [42, 55]) {
    inventoryId
    trafficCounts { cookies requests }
  }
}
```

## RTB line item past traffic

```graphql
{
  rtbLineItemPastTraffic(
    lineItems: [{ lineItemId: "99999", campaignId: "3993873" }]
  ) {
    lineItemId
    trafficCounts { cookies requests }
  }
}
```

## Deal plus line item past traffic

```graphql
{
  dealLineItemPastTraffic(
    inventorySourceId: "42"
    dealId: "12345"
    lineItemId: "99999"
  ) {
    levels { key name group availableImpressions }
  }
}
```

---

## Presenting

Report cookies and requests per inventory item and translate into something actionable: is there
enough volume to support the planned budget and impression target? Flag thin inventory. If the
trader then wants a deliverability or CPM estimate, use adform-reach-forecast or
adform-bid-landscape.
