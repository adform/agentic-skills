---
name: adform-segment-governance
description: >-
  First-party segment governance audit for the Adform Flow DSP. Audit DMP and first-party segments for an advertiser — find stale or
  unused segments, review sizes, and validate segment builder. Trigger on "segment governance", "stale segments",
  "unused first-party segments", "segment builder rule validation", "audit our DMP segments". For segment browsing and taxonomy
  use adform-targeting-segments; for marketplace audiences use adform-audience-discovery. Read-only.
---

# Adform segment governance

Two governance jobs over first-party segments: enumerate segments with sizes and flag stale or
unused ones; inspect segment builder rules and flag logic weaknesses. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_introspect`
on `BuyerAudienceListItem` and `BuyerAudience` to discover available fields including size and
composition. Keep calls sequential (~1–2s apart).

---

## Step 1 — List buyer audiences for an advertiser

```graphql
{
  buyerAudienceListItems(
    filters: [{ fieldName: "buyerAudience.advertisers.advertiserIds", operation: intersects, values: ["71883"] }]
    pagination: { offset: 0, limit: 100 }
  ) {
    buyerAudiences {
      id name status
      composition { uidTotalCount }
      stats { campaigns impressions lastImpressionDate }
      createdAt
    }
    totalCount
  }
}
```

## Step 2 — Get audience detail including builder rule

```graphql
{
  buyerAudience(id: "12345") {
    id name status
    ttl frequency idFusion lookalike
    rule { expression recalculable }
    createdAt updatedAt
  }
}
```

---

## Identifying stale and unused segments

- **Zero `uidTotalCount`**: audience has no reach — either the rule is too narrow or data has
  expired
- **`lastImpressionDate` older than 30 days** (or null): segment has not contributed to recent
  delivery — check whether it is referenced in any active line item's targeting
- **`status` inactive**: segment is disabled

To check whether a segment is referenced by active line items, search for its ID in line item
targeting. Cross-reference using adform-line-items.

## Identifying rule weaknesses

Inspect `rule.expression` for:
- No recency window — a segment that includes any historical event with no time limit grows
  stale quickly
- Single broad event trigger with no additional AND conditions
- Missing OR/AND structure that would be needed to build a meaningful audience

---

## Presenting

Two tables. Usage: segment name, status, reach (`uidTotalCount`), last impression date,
referenced in active targeting (yes or no). Rule audit: segment name, rule summary, issue found.
Lead with high-reach segments that are unused, and any segment with an invalid or logic-weak
rule that may be wasting data spend.
