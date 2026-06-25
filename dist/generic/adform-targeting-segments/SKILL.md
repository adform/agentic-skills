---
name: adform-targeting-segments
description: >-
  Targeting lists, segments, DMP, brand safety, and contextual data for Adform Flow DSP.
  Inspect domain/app targeting lists, browse segments and data providers, explore DMP taxonomy,
  and check brand safety and contextual providers and categories. Trigger on "domain targeting list",
  "app targeting list", "segments", "DMP taxonomy", "brand safety", "contextual targeting". For audience discovery use
  adform-audience-discovery; for line-item targeting use adform-line-items. Read-only.
---

# Adform targeting and segments

Inspect domain and app targeting lists, browse segments and DMP taxonomy, and explore brand
safety and contextual targeting providers and categories. Read-only.

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
{ rtbDomainTargetingList(id: "12345") { id name } }
```

### Get domains in a targeting list

```graphql
{ rtbTargetingListDomains(id: "12345", pagination: { offset: 0, limit: 100 }) { domains { domain } totalCount } }
```

### Get app targeting list

```graphql
{ rtbAppTargetingList(id: "12345") { id name } }
```

### Get apps in a targeting list

```graphql
{ rtbTargetingListApps(id: "12345", pagination: { offset: 0, limit: 100 }) { apps { bundleId name } totalCount } }
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

---

## Common workflows

- **Domain list audit**: get domain targeting list → get domains to see all entries
- **Brand safety review**: list brand safety providers → get categories by provider →
  compare with campaign's blocked categories (adform-campaign-management)
- **Contextual setup**: list contextual providers → get categories → configure targeting on
  the line item (adform-line-items)

## Presenting

Show targeting lists and segments in tables. For brand safety and contextual, show provider
name and available categories. Always include IDs so they can be referenced in targeting
configuration.
