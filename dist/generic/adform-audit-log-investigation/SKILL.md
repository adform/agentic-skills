---
name: adform-audit-log-investigation
description: >-
  Change history investigation for the Adform Flow DSP. Reconstruct who changed what and when on any
  entity — campaign, targeting, budget, creative, status — to support incident investigation.
  Trigger on "audit log", "who changed X", "change history", "who modified the budget or targeting", "incident investigation",
  "trace a change". For label and config current-state inspection use adform-campaign-management;
  for entity resolution use adform-entity-browsing. Read-only.
---

# Adform audit log investigation

Pulls the platform change-audit log for an entity over a date range to reconstruct who changed
what and when, and pairs it with current state for an incident timeline. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_introspect`
on the audit log type to discover available filter fields and enum values. Keep calls sequential
(~1–2s apart).

---

## Audit log query

```graphql
{
  auditLog(
    dateFrom: "2026-06-05"
    dateTo: "2026-06-12"
    limit: 50
    offset: 0
  ) {
    id type product correlationId
    user { userFullName }
    entities { id }
    changes { propertyName }
  }
}
```

**Field notes**
- `user` exposes `userFullName` only — no userId or login
- `entities` is a list; each entry exposes `id` only — resolve entity names via
  adform-entity-browsing
- `changes` exposes `propertyName` only — no before/after values inline
- `product` identifies the area: `Dsp` covers campaigns, orders, and line items;
  `AdvertiserManagement` covers advertisers
- Group events by `correlationId` to reconstruct before-and-after state across a single action

---

## Current state for comparison

Pull the current config alongside the audit log to compare what changed against what is live now:

```graphql
{ campaign(id: "3993873") { id name status type subType advertiserId startDate endDate budget currency } }
```

---

## Method

1. Pull audit entries for the entity and date window; order chronologically
2. Group by `user.userFullName` and `changes.propertyName` to identify who touched budget,
   targeting, or status
3. Resolve entity IDs to names via adform-entity-browsing
4. Compare against current state to tie a change to the present configuration

## Presenting

A timeline table: timestamp, user, change type, property changed, entity ID. Lead with the
changes most relevant to the investigation — budget, targeting, status, creative. Summarise
who made the most impactful edits and when. Attribute precisely based on the log data.
