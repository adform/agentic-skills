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

Tracking points belong to a tracking setup, which is linked to an advertiser and can be shared
by several advertisers.

Starting from a campaign, get its advertiser ID:

```graphql
{
  agencyListItems(
    filters: [{ fieldName: "campaign.id", operation: eq, values: ["3993873"] }]
  ) {
    campaigns { id advertiser { id } }
  }
}
```

Get the advertiser's tracking setup ID. A `NOT_FOUND` error with `tracking: null` means the
advertiser has no tracking setup:

```graphql
{ tracking(id: "2133350") { trackingSetupId } }
```

Then list the tracking points:

```graphql
{
  trackingPoints(
    trackingSetupId: 2742581
    active: true
    limit: 50
    offset: 0
  ) {
    trackingPoints { id name abbreviation active conversion url }
    totalCount
  }
}
```

### Check for a shared tracking setup

Tracking points have no advertiser field, so results from a shared setup can't be split by
advertiser. Whenever you list tracking points, list the advertisers and compare their
`trackingSetupId` values to find which ones use the same setup:

```graphql
{
  advertisers(limit: 100, offset: 0) {
    advertisers { id name tracking { trackingSetupId } }
    totalCount
  }
}
```

Page through until you reach `totalCount`. Advertisers with no tracking setup return
`tracking: null` with a `NOT_FOUND` error for that entry; the rest of the response is still
valid. This check only covers advertisers the user can access.

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
    tags { id uuid type campaignId active paused createdAt }
    totalCount
  }
}
```

### Get RTB tag

```graphql
{ rtbTag(id: "85543973") { id uuid type campaignId active paused } }
```

Use `graphql_introspect` on `RtbTag` to discover available fields including destination URLs
and settings.

### Get direct tag

```graphql
{ directTag(id: "85543974") { id uuid type campaignId active paused } }
```

---

## Creative inspection

### Get ad by UUID

```graphql
{ adByUuid(uuid: "ad-uuid-here") { id { uuid id } name adType commercialType size { width height } publishStatus active } }
```

### Get ad members — sub-creatives of a rotator

```graphql
{ adMembersByUuid(uuid: "ad-uuid-here") { adId { uuid id } name adType commercialType size { width height } } }
```

### Get published ad — by integer ID and ad type

First get the integer `id` and `adType` from `adByUuid`, then:

```graphql
{ publishedAdById(id: "12345", adType: creative) { id { uuid id } name adType commercialType contentType size { width height } active deleted } }
```

### List ad sizes by campaign

```graphql
{
  adSizesByCampaignId(
    campaignId: "3993873"
    pagination: { offset: 0, limit: 50 }
  ) {
    sizes { width height }
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
- **Tracking point discovery**: resolve the advertiser's tracking setup ID → list tracking
  points to find conversion points for use in targeting or reporting filters → check whether
  the setup is shared

## Presenting

Show tracking points and tags in tables with status, type, and key metadata. For tracking
filters, render the rule set as structured bullet lists.

If the tracking setup is shared, say so above the tracking points table: state that the points
come from a setup shared by other advertisers, name those advertisers, and explain that the
points can't be attributed to a single advertiser.
