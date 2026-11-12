# Adform Agentic Skills

Read-only skills for the **Adform FLOW DSP** via the Adform GraphQL MCP server. Each skill is a `.md` file that defines the skill's purpose, illustrative GraphQL queries, usage constraints, and presentation guidance. The skills are ready to use with agentic AI systems and can be used individually or as a packaged plugin if available.

---

## Repository Structure

```
adform-agentic-skills/
├── .claude-plugin/
│   └── marketplace.json                # Claude Code marketplace manifest (points to dist/claude)
├── dist/
│   ├── claude/
│   │   └── adform-agentic-skills/       # Unpacked Claude plugin (installed via the marketplace)
│   │       ├── .claude-plugin/plugin.json
│   │       └── skills/
│   └── generic/
│       ├── adform-audience-discovery/
│       ├── ... # other skills
```

All publishable artifacts live under `dist/`. They are organized by target model/platform:

| Path             | Description                                                              |
|------------------|--------------------------------------------------------------------------|
| `dist/claude/`   | Packaged skill plugin for Claude (Anthropic)                             |
| `dist/generic/`  | Platform-agnostic skills following the https://agentskills.io standard   |

---

## How to Use

1. Connect your agentic AI system to the Adform GraphQL MCP server.
2. Add and install the skills for your platform:
   - **Claude Code (recommended)** — add this repo as a plugin marketplace and install the plugin:
     ```
     claude plugin marketplace add adform/agentic-skills
     /plugin install adform-agentic-skills@adform-agentic-skills
     ```
   - **Other platforms** — use the platform-agnostic skills under `dist/generic/`.
3. Use the skills to query and analyze Adform FLOW DSP data.

---

## Skills

The 33 skills, grouped by what they help you do. The same skills ship in `dist/generic/` and in the Claude plugin.

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

---

## License

[MIT License](./LICENSE.md) — Copyright (c) 2026 Adform
