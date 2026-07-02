---
name: adform-taxonomy-governance
description: >-
   Naming convention and label taxonomy governance audit for Adform FLOW DSP. Audits campaign, order,
   or line-item names against a naming pattern, detects duplicates, and checks campaigns carry required
   labels. Trigger on "naming convention audit", "do campaign names follow the pattern",
   "flag non-compliant names", "label taxonomy audit", "duplicate names". For ID and name resolution
   use adform-entity-browsing; for campaign label config use adform-campaign-management. Read-only.
---

# Adform naming and label taxonomy governance

Validates entity names against a convention pattern and flags missing or wrong label taxonomy
across campaigns. Read-only — it reports; the trafficker fixes.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Keep calls sequential
(~1–2s apart).

---

## Naming convention audit

### List campaigns to audit

```graphql
{
  campaigns(
    advertisers: "71883"
    status: Active
    offset: 0
    limit: 50
  ) {
    campaigns { id name status type subType advertiserId startDate endDate }
    totalCount
  }
}
```

Apply the naming convention as a regex client-side — for example
`^[A-Za-z]+_\d{4}_Q[1-4]_[A-Za-z]+$` for a `Brand_Year_Quarter_Objective` pattern. Flag any
name that does not match and any case-insensitive duplicate within the advertiser scope.

---

## Label taxonomy audit

### Get label group definitions for an advertiser

```graphql
{ advertiserLabels(id: "71883") { labelGroups { id name labels { id name } } } }
```

### Get labels applied to a campaign

```graphql
{ campaignLabels(id: "3993873") { labelGroups { id name labels { id name } } } }
```

For each campaign, compare the applied label groups against the required set (e.g. Market,
Product, Funnel Stage) and flag any campaign missing a required group.

---

## Method

1. Pull the entity list for the advertiser in scope
2. Names: apply the agreed regex; collect mismatches and duplicates; suggest a corrected name
   where the intent is clear from the existing name
3. Labels: for each campaign, list which required label groups have no value applied

## Presenting

Two compliance tables. Naming: entity type, ID, name, PASS or FLAG, reason, suggested fix.
Labels: campaign, missing required label groups. Lead with the non-compliant count and the
items that need the most immediate attention. Every flagged row should be a clear action item
for the trafficking or operations owner.
