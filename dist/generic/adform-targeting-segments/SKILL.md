---
name: adform-targeting-segments
description: >-
  Targeting lists, segments, DMP, brand safety, and contextual data for Adform FLOW DSP.
  Inspect domain/app targeting lists, browse segments and data providers, explore DMP taxonomy,
  and check brand safety and contextual providers, categories, and per-advertiser CPM fee rates.
  Trigger on "domain targeting list",
  "app targeting list", "segments", "DMP taxonomy", "brand safety", "contextual targeting",
  "brand safety fee", "contextual targeting fee". For audience discovery use
  adform-audience-discovery; for line-item targeting use adform-line-items. Read-only.
---

# Adform targeting and segments

Inspect domain and app targeting lists, browse segments and DMP taxonomy, and explore brand
safety and contextual targeting providers and categories. Read-only.

IDs for geo/device/content filters can be resolved via adform-classifier-lookup.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute(query, variables)` to run and
`graphql_validate` to check a query first. Always validate before executing. The queries below are
**illustrative examples** — if a field or input shape isn't shown, or a query fails validation,
discover the current schema with `graphql_search` (lighter, preferred) and fall back to
`graphql_introspect` one call at a time with ≥2s between calls for complex input types, enum
values, or union/interface resolution.


> **Warning: domains and apps field format**
> When configuring domain or app targeting in line items, the correct structure is `{ "targetingMode": "includeAll" }`. Do NOT include `excludeUnknown: false` as this property doesn't exist in the schema.

---

## Domain and app targeting lists

### Get domain targeting list

```graphql
{ rtbDomainTargetingList(id: "12345") { id createdAt updatedAt itemCount version } }
```

### Get domains in a targeting list

```graphql
{ rtbTargetingListDomains(id: "12345", pagination: { offset: 0, limit: 100 }) { domains { name bidMultiplier } totalCount } }
```

### Get app targeting list

```graphql
{ rtbAppTargetingList(id: "12345") { id createdAt updatedAt itemCount version } }
```

### Get apps in a targeting list

```graphql
{ rtbTargetingListApps(id: "12345", pagination: { offset: 0, limit: 100 }) { apps { id name storeType developerName bidMultiplier } totalCount } }
```

---

## Brand safety

### List brand safety providers

```graphql
{ brandSafetyProviders { providers { id name } } }
```

### Get brand safety categories

```graphql
{ brandSafetyCategories(providerId: "1") { categories { id name parentId } } }
```

### Brand safety fees — per-advertiser rate card

`brandSafetyFee` returns the fee for one provider/feature/advertiser
combination; `brandSafetyFees` lists them. The fee type is **CPM** — the
`BrandSafetyFeeType` enum has `cpm` as its only value, so the amount always
sits under `cpm`.

```graphql
{
  brandSafetyFees(providerId: "1", advertiserId: "71883", currencyCode: "EUR") {
    fees {
      providerId featureId advertiserId
      fee { type cpm { currencyCode amount } }
    }
    totalCount
  }
}
```

`currencyCode` is optional with **no default** — the returned
`cpm.currencyCode` tells you which currency the amount is in, so read it rather
than assuming. Pass codes as quoted strings (`"EUR"`). On the singular
`brandSafetyFee`, `providerId`, `featureId` and `advertiserId` are all
required; on the plural all arguments are optional.

These are rate-card fees, not spend. Actual brand safety spend on a campaign is
the `rtbBrandSafetyCost` metric in adform-stats-performance.

---

## Contextual targeting

### List contextual providers

```graphql
{ contextualTargetingProviders { providers { id name } } }
```

### Get contextual categories

```graphql
{ contextualTargetingCategories(providerId: "1") { categories { id name parentId } } }
```

### Contextual targeting fees

Structurally identical to brand safety fees, including the CPM-only fee type
and the optional, defaultless `currencyCode`.

```graphql
{
  contextualTargetingFees(providerId: "1", advertiserId: "71883", currencyCode: "EUR") {
    fees {
      providerId featureId advertiserId
      fee { type cpm { currencyCode amount } }
    }
    totalCount
  }
}
```

Actual contextual spend on a campaign is the `rtbContextualTargetingCost`
metric in adform-stats-performance.

---

## Common workflows

- **Domain list audit**: get domain targeting list → get domains to see all entries
- **Brand safety review**: list brand safety providers → get categories by provider →
  compare with campaign's blocked categories (adform-campaign-management)
- **Contextual setup**: list contextual providers → get categories → configure targeting on
  the line item (adform-line-items)
- **Fee check**: list providers → read the per-advertiser CPM fee → compare against actual
  spend via `rtbBrandSafetyCost` / `rtbContextualTargetingCost` (adform-stats-performance)

## Presenting

Show targeting lists and segments in tables. For brand safety and contextual, show provider
name and available categories. Always include IDs so they can be referenced in targeting
configuration.

For fees, state the amount, the currency from `cpm.currencyCode`, and that the basis is CPM.
Never present a rate-card fee as spend.
