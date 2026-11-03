# Adform Agentic Skills

Read-only skills that help programmatic traders and campaign managers work with the **Adform FLOW DSP** in Claude. Ask about pacing, delivery problems, performance, forecasts, deals, audiences, or account governance, and the skills guide Claude to the right data and how to present it.

## What's included

- **Campaign setup:** find advertisers, campaigns, orders, and line items, and inspect their configuration, targeting, and tracking.
- **Delivery and performance:** check pacing, budget risk, delivery blockers, and deal health, and report on metrics such as CTR, viewability, and eCPM.
- **Planning:** review media plans, forecast reach and available inventory, and explore bid landscapes, past traffic, deals, and audiences.
- **Governance:** audit naming, labels, frequency caps, viewability settings, segments, stale entities, and direct versus RTB overlap.

## Requirements

You need an Adform account and a connection to the Adform GraphQL MCP server. This plugin doesn't include that connection, so set it up first by following the [Adform MCP guides](https://solutions.adform.com/tools/mcp-guides).

## What the plugin runs and sends

The plugin contains only skill instructions: Markdown files and no scripts, hooks, or MCP server configuration.

- **Credentials:** the plugin doesn't read or store credentials. Sign-in belongs to the Adform MCP connection you set up.
- **Data:** the skills ask Claude to query the Adform MCP server you connected. The plugin sends data to no other service.
- **Changes:** the skills only read data and don't change anything in your Adform account.

## License

MIT
