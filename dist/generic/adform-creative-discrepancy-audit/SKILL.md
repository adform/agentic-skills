---
name: adform-creative-discrepancy-audit
description: >-
  Creative-versus-served discrepancy audit for the Adform Flow DSP.
  Verify that the ads serving in a campaign
  match the setup — catching creative trafficking errors, wrong rotations, or
  unauthorised substitutions. Trigger on "is the served ad the right one",
  "creative vs served mismatch", "trafficking error check", "published ad audit", "ad rotation check".
  For tag and tracking inspection use adform-tracking-tags; for tag-versus-exchange creative audit use adform-line-items. Read-only.
---

# Adform creative-versus-served discrepancy audit

Compares the creatives assigned in campaign setup against the published and served ad state,
surfacing mismatches that indicate trafficking errors. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_introspect`
on `Ad` and `PublishedAd` to discover available fields. Keep calls sequential (~1–2s apart);
retry transient errors at most twice.

---

## Step 1 — List assigned ads on the campaign

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

Each ad's `id` object gives both the UUID and the integer ID. Note `publishStatus` —
`published`, `notPublished`, `publishedButChanged` — and `active` flag.

## Step 2 — Get the published state per ad

The published lookup uses the integer ID and `adType`, not the UUID:

```graphql
{ publishedAdById(id: "12345", adType: image) { id { uuid id } name adType commercialType width height publishStatus } }
```

Compare published name, size, and adType against the assigned values. Flag any divergence,
an active ad with `publishStatus: notPublished`, or `publishedButChanged`.

## Step 3 — Inspect rotation members (for grouped ads)

```graphql
{ adMembersByUuid(uuid: "ad-uuid-here") { id { uuid id } name adType width height } }
```

Confirm that members and their weights match the intended rotation configuration. Flag
unexpected members or active members with zero weight.

---

## Presenting

Discrepancy table: ad name and UUID, assigned values (name, size, type, publish status),
published values, and the mismatch reason. Lead with serving mismatches and any unauthorised
substitutions as these carry the highest risk, then rotation and weight anomalies. Each row
is an action item for the adops owner.
