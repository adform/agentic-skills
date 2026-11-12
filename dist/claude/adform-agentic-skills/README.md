# Adform Agentic Skills

Read-only skills that help programmatic traders and campaign managers work with the **Adform FLOW DSP** in Claude. Ask about pacing, delivery problems, performance, forecasts, deals, audiences, or account governance, and the skills guide Claude to the right data and how to present it.

## What's included

The plugin includes 33 skills, grouped by what they help you do. Claude picks the right one from your question, so you don't need to name a skill.

### Find and look up

| Skill | What it does |
|---|---|
| `adform-buyer-entity-resolver` | Resolve a person's name to their user IDs, and entity names to IDs |
| `adform-entity-browsing` | Find and list advertisers, campaigns, orders, and line items by name or ID |
| `adform-classifier-lookup` | Look up IDs for geo, device, network, content, and mobile targeting values |
| `adform-geo-reference` | Search geo targeting IDs, currency rates, and the label taxonomy |

### Campaign setup

| Skill | What it does |
|---|---|
| `adform-campaign-structure` | Walk the advertiser, campaign, order, and line item hierarchy |
| `adform-campaign-management` | Inspect campaign and order settings, labels, brand safety, and delivery plans |
| `adform-line-items` | Inspect line item configuration, targeting, deals, and creatives |
| `adform-tracking-tags` | Inspect tracking points, tracking filters, tags, and creatives |
| `adform-targeting-segments` | Inspect targeting lists, segments, DMP taxonomy, and brand safety and contextual data |

### Pacing and delivery

| Skill | What it does |
|---|---|
| `adform-pacing-check` | Check whether a campaign, order, or line item is pacing to its budget |
| `adform-delivery-health` | Find what is blocking a line item from delivering |
| `adform-budget-risk-monitor` | Flag orders in a campaign that are likely to under-deliver or overspend |
| `adform-underdelivery-triage` | Rank and diagnose every underpacing line item across the account |
| `adform-deal-health-check` | Find deals in a campaign with little or no delivery |

### Performance and reporting

| Skill | What it does |
|---|---|
| `adform-campaign-performance` | Portfolio view of campaign spend, pacing, and key metrics |
| `adform-reporting` | Monitor spend, pacing, and budget flights, with headline performance metrics |
| `adform-stats-performance` | Break performance down by date, campaign, domain, deal, and more |

### Forecasting and planning

| Skill | What it does |
|---|---|
| `adform-pipeline-forecast` | Forecast next week's daily spend and explain the change from last week |
| `adform-reach-forecast` | Forecast impressions, reach, spend, and bid pricing for a media plan |
| `adform-bid-landscape` | Show the CPM-versus-win-rate curve for an RTB line item |
| `adform-past-traffic` | Show recent traffic for domains, apps, or deals |
| `adform-inventory-availability-forecast` | Size future inventory supply before launch |
| `adform-media-plans` | Inspect media plans, their forecasts, and recommendations |
| `adform-media-plan-review` | Review a pre-launch media plan and the campaign tree it would generate |

### Inventory and audiences

| Skill | What it does |
|---|---|
| `adform-inventory-deals` | Explore inventory sources, deals, and deal groups |
| `adform-audience-discovery` | Find and evaluate audience segments for targeting |

### Governance audits

| Skill | What it does |
|---|---|
| `adform-stale-entity-audit` | Find ended campaigns and orphaned line items still marked active |
| `adform-taxonomy-governance` | Audit names against a naming convention and check required labels |
| `adform-frequency-cap-audit` | Check line item frequency caps against the brief |
| `adform-viewability-audit` | Check viewability settings are consistent across campaigns |
| `adform-channel-conflict-audit` | Find direct and RTB line items targeting the same inventory |
| `adform-creative-discrepancy-audit` | Check that the ads serving match the creative setup |
| `adform-segment-governance` | Find stale or unused first-party segments |

## Requirements

You need an Adform account and a connection to the Adform GraphQL MCP server. This plugin doesn't include that connection, so set it up first.

## What the plugin runs and sends

The plugin contains only skill instructions: Markdown files and no scripts, hooks, or MCP server configuration.

- **Credentials:** the plugin doesn't read or store credentials. Sign-in belongs to the Adform MCP connection you set up.
- **Data:** the skills ask Claude to query the Adform MCP server you connected. The plugin sends data to no other service.
- **Changes:** the skills only read data and don't change anything in your Adform account.

## License

MIT
