---
name: adform-media-plan-review
description: >-
  Media plan review for the Adform FLOW DSP. Inspect a pre-launch media plan: budgets, schedule, goals, and targeting,
  or review the candidate campaign tree it would generate. Trigger on "look at my media plan", "review the plan",
  "what optimisation recommendations does Adform suggest", "what's in plan X", "find my media plans". For the live
  campaign hierarchy use adform-campaign-structure; to forecast a plan's reach use
  adform-reach-forecast. Read-only.
---

# Adform media plan review

Inspect a pre-launch media plan — budget, schedule, goals, targeting — its candidate campaign
tree, and Adform's optimisation recommendations. Read-only.

## Connection & tooling

Runs on the Adform GraphQL MCP. Use `graphql_execute` to run queries. Use `graphql_introspect`
on `MediaPlan`, `MediaPlanContent`, and `MediaPlanRecommendationsFilterInput` to discover
available fields. Keep calls sequential (~1–2s apart).

---

## List media plans

```graphql
{
  mediaPlans(
    advertiserIds: ["71883"]
    pagination: { offset: 0, limit: 20 }
  ) {
    mediaPlans { id name advertiserId comment schedule { startDate endDate timeZoneId } budget { currency amount } }
    totalCount
  }
}
```

## Get plan detail

```graphql
{ mediaPlan(id: "b2d428ae-0000-0000-0000-000000000000") { id name advertiserId comment schedule { startDate endDate timeZoneId } budget { currency amount } } }
```

Use `graphql_introspect` on `MediaPlan` to expand goals, KPIs, targeting, schedules, and line
items.

## Get candidate campaign tree

```graphql
{ mediaPlanContent(id: "b2d428ae-0000-0000-0000-000000000000") { id } }
```

Use `graphql_introspect` on `MediaPlanContent` to discover the full tree structure —
campaigns, orders, and line items the plan would generate.

## Get optimisation recommendations

The `mediaPlan` input requires `advertiserId` and `goals` at minimum. Fetch the plan first,
then pass its parameters. The filter field is `recommendationTypes`.

```graphql
{
  mediaPlanRecommendations(
    mediaPlan: {
      advertiserId: "71883"
      goals: { kpis: [{ performance: { ctr: { rate: 0.005 } } }] }
      schedule: { startDate: "2026-07-01", endDate: "2026-07-31", timeZoneId: "Europe/Berlin" }
    }
    filter: { recommendationTypes: [] }
  ) {
    recommendationGroup
    recommendationType
  }
}
```

Use `graphql_introspect` on `MediaPlanRecommendationsMediaPlanInput` and
`MediaPlanRecommendationsFilterInput` to discover available recommendation types and input
fields.

---

## Presenting

Summarise the plan: advertiser, flight dates, budget, currency, KPI goals, and key targeting.
Present recommendations as a prioritised list explaining what each would change and why a trader
might apply or skip it. To estimate what the plan would deliver, use adform-reach-forecast.
