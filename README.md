# Adform Agentic Skills

Read-only skills for the **Adform FLOW DSP** via the Adform GraphQL MCP server. Each skill is a `.md` file that defines the skill's purpose, illustrative GraphQL queries, usage constraints, and presentation guidance. The skills are ready to use with agentic AI systems and can be used individually or as a packaged plugin if available.

---

## Repository Structure

```
adform-agentic-skills/
├── dist/
│   ├── claude/
│   │   └── adform-agentic-skills.zip   # Packaged plugin for Claude
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

1. Connect your agentic AI system to the Adform GraphQL MCP server as outlined here: https://solutions.adform.com/tools/mcp-guides.
2. Download the skills or plugins from the `dist/` directory.
3. Import the skills into your agentic AI system.
4. Use the skills to query and analyze Adform FLOW DSP data.

---

## License

[MIT License](./LICENSE.md) — Copyright (c) 2026 Adform
