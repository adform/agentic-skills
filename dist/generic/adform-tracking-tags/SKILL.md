---
name: adform-tracking-tags
description: >-
  Tracking points, tracking filters, tags, and creative inspection for the Adform FLOW DSP.
  List tracking points, inspect filter rules, browse tags, look up creatives by UUID, view
  ad members, list ad sizes, or check published ad versions. Trigger on "tracking points",
  "tracking filters", "tags in campaign", "tag details", "creative by UUID", "ad members",
  "ad sizes", "published ad", "campaign tags". For tag creative audit by exchange use
  adform-line-items. Read-only.
---

# Adform tracking and tags

List tracking points and filters, browse tags, inspect RTB tag settings, look up creatives,
view ad members, and list campaign tags. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_search` to
look up field names; use `graphql_introspect` for nested tag and ad types. Keep calls sequential
(~1–2s apart).

---

## Tracking points

```graphql
{
  trackingPoints(
    campaignId: 3993873
    active: true
    limit: 50
    offset: 0
  ) {
    trackingPoints { id name abbreviation active conversion url }
    totalCount
  }
}
```

## Tracking filters

```graphql
{ trackingFilter(id: 123) { id name } }
```

Use `graphql_introspect` on `TrackingFilter` to discover available fields including rule
expressions.

---

## Tags

### List campaign tags

```graphql
{
  tags(
    filter: { campaignId: "3993873" }
    pagination: { offset: 0, limit: 50 }
  ) {
    tags { id name type status }
    totalCount
  }
}
```

### Get RTB tag

```graphql
{ rtbTag(id: "85543973") { id name type status } }
```

Use `graphql_introspect` on `RtbTag` to discover available fields including destination URLs
and settings.

### Get direct tag

```graphql
{ directTag(id: "85543974") { id name type status } }
```

---

## Creative inspection

### Get ad by UUID

```graphql
{ adByUuid(uuid: "ad-uuid-here") { id { uuid id } name adType commercialType width height publishStatus active } }
```

### Get ad members — sub-creatives of a rotator

```graphql
{ adMembersByUuid(uuid: "ad-uuid-here") { id { uuid id } name adType width height } }
```

### Get published ad — by integer ID and ad type

First get the integer `id` and `adType` from `adByUuid`, then:

```graphql
{ publishedAdById(id: "12345", adType: image) { id { uuid id } name adType width height publishStatus } }
```

### List ad sizes by campaign

```graphql
{
  adSizesByCampaignId(
    campaignId: "3993873"
    pagination: { offset: 0, limit: 50 }
  ) {
    adSizes { id name width height }
    totalCount
  }
}
```

---

## Common workflows

- **Tag audit**: list campaign tags → tag creative audit per tag (adform-line-items) to check
  SSP approval status
- **Creative inspection**: get ad by UUID → get ad members for rotators → get published ad
  for the live version
- **Tracking point discovery**: list tracking points to find conversion points for use in
  targeting or reporting filters

## Presenting

Show tracking points and tags in tables with status, type, and key metadata. For tracking
filters, render the rule set as structured bullet lists.
