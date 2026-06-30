---
name: adform-geo-reference
description: >-
  Geo reference data, currency rates, and label taxonomy for the Adform FLOW DSP.
  Use when a programmatic trader needs to search countries, regions, or cities for
  geo targeting IDs; look up currency exchange rates; or list label groups and their labels.
  Trigger on "find country ID", "search regions", "search cities", "currency rate EUR to USD",
  "label groups", "what labels are available". For geo targeting on line items use
  adform-line-items. Read-only.
---

# Adform geo reference, currency, and labels

Search geo targeting reference data, look up currency exchange rates, and list label taxonomy.
Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Keep calls sequential
(~1–2s apart).

---

## Geo targeting reference

The geo hierarchy is: Continent → Country → Region → City. Use the returned `id` values in
line-item geo targeting rules.

### Search countries

```graphql
{ countries(search: "Germany", offset: 0, limit: 10) { countries { id name code continentId } totalCount } }
```

### Search regions

```graphql
{ regions(countryId: "276", offset: 0, limit: 20) { regions { id name countryId } totalCount } }
```

### Search cities

```graphql
{ cities(countryId: "276", search: "Berlin", offset: 0, limit: 20) { cities { id name regionId countryId } totalCount } }
```

---

## Currency rates

CurrencyCode is ISO 4217: `EUR`, `USD`, `DKK`, `GBP`, `SEK`, `NOK`, etc.

```graphql
{ currencyRate(sourceCurrencyCode: EUR, targetCurrencyCode: USD) { sourceCurrencyCode targetCurrencyCode rate date } }
```

---

## Label taxonomy

```graphql
{ labelGroups { id name labels { id name } } }
```

Label group IDs are used in campaign, advertiser, and line-item label queries.

---

## Common workflows

- **Geo targeting setup**: search countries → search regions by `countryId` → search cities by
  `regionId` → use IDs in line-item geo targeting rules
- **Currency conversion**: get currency rate for cross-currency budget comparisons
- **Label resolution**: list label groups to map label IDs from campaigns and line items to names
