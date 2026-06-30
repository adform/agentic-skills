---
name: adform-audience-discovery
description: >-
  Audience discovery and exploration for Adform FLOW DSP. Find and evaluate available audience segments
  including third-party marketplace audiences, first-party data segments, and audience categories.
  Ideal for campaign planning, audience research, and targeting strategy development. For inventory
  and deal opportunities, see inventory discovery; for line item targeting setup, see targeting
  configuration.
---

# Audience Discovery

Explore and evaluate available audience segments to enhance your campaign targeting. This tool
provides access to third-party marketplace audiences, first-party data segments, audience categories,
and deal items to help you make informed targeting decisions.

## Overview

This audience discovery tool helps you find and evaluate targeting options for your campaigns. You can
browse third-party audience marketplaces, explore your first-party data segments, and research audience
categories to build effective targeting strategies.

**Technical Operations:**
The system uses GraphQL operations to process your requests:
- `graphql_validate` - Checks query validity before execution
- `graphql_execute` - Runs audience discovery queries with your filters
- `graphql_search` - Helps find available audience fields and filter options
- `graphql_introspect` - Explores complex audience data structures

**Best Practices:**
- Use specific search terms for better results
- Limit searches to 25 results for faster response times
- Combine multiple criteria to narrow down audience options
- Review audience size and composition before targeting

---

## Marketplace Audiences

Explore third-party audience segments available for targeting. These audiences are provided by
specialized data companies and cover various interests, demographics, and behaviors.

**Available Filters:**
- **Provider:** Search by specific data provider
- **Category:** Browse by audience category or interest
- **Name:** Find audiences by specific keywords
- **Status:** Filter by active/inactive audiences

**Key Information:**
- Audience size and reach estimates
- Pricing information (CPM rates)
- Data provider details
- Audience composition and demographics

### Finding Marketplace Audiences

**Search Methods:**
- **By Audience ID:** Look up specific audiences you already know
- **By Data Provider:** Find audiences from specific companies
- **By Name/Keywords:** Search for audiences related to topics or interests
- **By Status:** Filter for currently active audiences

**What You'll See:**
- Audience name and unique identifier
- Estimated audience size and reach
- Data provider information
- Pricing details (CPM rates)
- Audience availability status

**Example Use Cases:**
- "Find automotive enthusiast audiences"
- "Show me audiences from Provider X"
- "Look up audience ID 12345"
- "List all active audiences in the technology category"

---

**Filter field names for `audienceMarketplaceListItems`:**

| Field | Use for |
|---|---|
| `audience.name` | Search by segment name (use `contains`) |
| `audience.status` | Filter active/inactive |
| `dataProvider.name` | Filter by provider name |

**Example query:**
```graphql
audienceMarketplaceListItems(
  filters: [
    { fieldName: "audience.name", operation: contains, values: ["mobile phone"] },
    { fieldName: "audience.name", operation: contains, values: ["UK"] }
  ]
  pagination: { offset: 0, limit: 20 }
) {
  audiences {
    id
    name
    thirdPartyAudienceId
    dataProvider { name }
    price { cpm }
    composition { uidTotalCount }
  }
  totalCount
}
```

---

## First-Party Data Audiences

Manage and explore your own first-party audience segments built from your website traffic,
customer data, and campaign interactions.

### Your Audience Segments

**Available Information:**
- **Audience Details:** Name, status, and creation date
- **Advertiser Access:** Which advertisers can use each segment
- **Audience Composition:** Geographic distribution and data sources
- **Performance Stats:** Historical campaign performance
- **Configuration:** Rules, TTL settings, and data refresh schedules

**Search Options:**
- **By Advertiser:** Find audiences available to specific accounts
- **By Name:** Search for specific audience segments
- **By Status:** Filter active/inactive audiences

### Audience Categories

Organize your audiences into logical categories for better management:
- **Parent Categories:** Top-level audience groupings
- **Sub-categories:** More specific audience classifications
- **Hierarchical Structure:** Build organized taxonomy

**Common Categories:**
- Demographics (age, gender, income)
- Interests (hobbies, preferences)
- Behavior (purchase history, website activity)
- Geography (location-based segments)
- Custom categories specific to your business

---

## Private Marketplace Deals

Access your private marketplace deals and preferred inventory arrangements with premium publishers
and specialized inventory sources.

### Deal Management

**Deal Information Available:**
- **Deal Details:** Name, type, and pricing structure
- **Inventory Source:** Publisher and exchange information
- **Performance Metrics:** Delivery statistics and health indicators
- **Campaign History:** Recent performance and utilization
- **Advertiser Access:** Which accounts can use each deal

**Performance Monitoring:**
- **Health Status:** Real-time deal performance indicators
- **Delivery Stats:** Impressions, clicks, and engagement metrics
- **Win Rates:** Auction success rates and competition levels
- **Utilization:** How much of the deal capacity is being used

---

## Strategic Applications

**Audience Research Workflow:**
1. **Discovery:** Browse marketplace audiences by category or provider
2. **Evaluation:** Review audience size, composition, and pricing
3. **Comparison:** Compare similar audiences from different providers
4. **Selection:** Choose audiences that align with campaign goals

**First-Party Strategy:**
1. **Audit:** Review existing first-party audience segments
2. **Analysis:** Examine performance and composition data
3. **Optimization:** Refine audience rules and targeting criteria
4. **Expansion:** Build new segments based on successful patterns

**Deal Management:**
1. **Monitoring:** Track deal performance and health status
2. **Optimization:** Adjust bidding strategies based on delivery
3. **Planning:** Forecast inventory availability and costs
4. **Reporting:** Analyze deal effectiveness and ROI

## Best Practices

- **Regular Reviews:** Monitor audience performance and deal health weekly
- **Testing:** Test new audience segments with small budgets first
- **Documentation:** Keep detailed records of audience performance
- **Compliance:** Ensure all audience usage complies with privacy regulations
- **Optimization:** Continuously refine targeting based on performance data
