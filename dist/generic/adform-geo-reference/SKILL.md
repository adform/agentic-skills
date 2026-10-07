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
Read-only. For the full classifier reference (device, network, content, mobile) see
adform-classifier-lookup.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Keep calls sequential
(~1–2s apart).

---

## Geo targeting reference

The geo hierarchy is: Continent → Country → Region → City. Use the returned `id` values in
line-item geo targeting rules.

### Search countries

```graphql
{ countries(search: "Germany", offset: 0, limit: 10) { countries { id name iso2Code iso3Code continentId } totalCount } }
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

`CurrencyCode` is a custom scalar, not an enum — ISO 4217 codes: `EUR`, `USD`,
`DKK`, `GBP`, `SEK`, `NOK`, etc. Always pass them as quoted strings (e.g.
`"EUR"`, not `EUR`).

One target currency — both arguments are required:

```graphql
{ currencyRate(sourceCurrencyCode: "EUR", targetCurrencyCode: "USD") { sourceCurrencyCode targetCurrencyCode rate } }
```

All available targets for one source — `sourceCurrencyCode` is required:

```graphql
{ currencyRates(sourceCurrencyCode: "EUR") { currencyRates { sourceCurrencyCode targetCurrencyCode rate } } }
```

### Using rates in cost reporting

These two queries are the only sanctioned way to convert an Adform cost figure
between currencies. The rules, which apply in every cost-reporting skill:

- **Do not convert by default.** Adform returns costs in campaign currency;
  report them in that currency and label it.
- Convert only when results span more than one currency and the user has asked
  for a single currency, when the figures are going to an external audience
  (client report, invoice reconciliation, deck), or when the user names a
  different currency.
- **Never sum across currencies** without converting first.
- Apply the rate explicitly, label the output as converted, and state the
  source currency and the rate used. **Never convert silently.**

The full cost and currency reference lives in adform-stats-performance.

---

## Label taxonomy

Labels are scoped per advertiser or campaign — there is no global `labelGroups` query.

```graphql
{ advertiserLabels(id: "71883") { labelGroups { id name labels { id name } } } }
```

```graphql
{ campaignLabels(id: "3993873") { labelGroups { id name labels { id name } } } }
```

Label group IDs are used in campaign, advertiser, and line-item label queries.

---

## Common workflows

- **Geo targeting setup**: search countries → search regions by `countryId` → search cities by
  `regionId` → use IDs in line-item geo targeting rules
- **Currency conversion**: get currency rate for cross-currency budget comparisons — state the
  rate and label the result as converted
- **Label resolution**: list label groups to map label IDs from campaigns and line items to names
