# bird-outing-mcp

An MCP (Model Context Protocol) server that wraps the [eBird API 2.0](https://documenter.getpostman.com/view/664302/S1ENwy59), giving Claude and other MCP clients access to real-time bird observation data, hotspots, checklists, taxonomy, and more.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- An [eBird API key](https://ebird.org/api/keygen)

## Setup

1. **Clone and install dependencies:**

   ```bash
   git clone <repo-url>
   cd bird_outing_mcp
   uv sync
   ```

2. **Configure your API key:**

   Copy `.env.example` to `.env` and fill in your values:

   ```bash
   cp .env.example .env
   ```

   ```ini
   EBIRD_API_KEY=your_api_key_here
   EBIRD_DEFAULT_REGION=US-CO-067
   ```

   `EBIRD_DEFAULT_REGION` is optional but recommended — it is used as the default for any tool that accepts a `region` parameter. eBird region codes follow a hierarchical format:

   | Level | Format | Example |
   |---|---|---|
   | Country | ISO 2-letter code | `US` |
   | State / Province | `{country}-{state}` | `US-CO` |
   | County | `{country}-{state}-{county}` | `US-CO-067` |
   | Hotspot / Location | Starts with `L` | `L374326` |

## Running the server

```bash
uv run bird-outing-mcp
```

The server runs over stdio, which is the standard transport for MCP clients (Claude Desktop, Claude Code, etc.).

### Activating the virtual environment manually

```bash
source .venv/bin/activate
```

## Connecting to Claude Desktop

Add the server to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "bird-outing-mcp": {
      "command": "uv",
      "args": ["--directory", "/path/to/bird_outing_mcp", "run", "bird-outing-mcp"]
    }
  }
}
```

## Available tools

### Observations
| Tool | Description |
|---|---|
| `get_observations` | Recent observations for a region or location |
| `get_notable_observations` | Recent rare/notable observations for a region |
| `get_species_observations` | Recent observations of a specific species in a region |
| `get_nearby_observations` | Most recent observation of each species near a lat/lng |
| `get_nearby_species` | Most recent observation of a specific species near a lat/lng |
| `get_nearby_notable` | Recent notable observations near a lat/lng |
| `get_nearest_species` | Nearest recent observations of a species to a lat/lng |
| `get_historic_observations` | Observations recorded on a specific date |

### Checklists
| Tool | Description |
|---|---|
| `get_visits` | Recent checklists for a region, optionally filtered by date |
| `get_checklist` | Full details of a single checklist by submission ID |

### Hotspots
| Tool | Description |
|---|---|
| `get_hotspots` | All hotspots in a region |
| `get_nearby_hotspots` | Hotspots within a radius of a lat/lng |
| `get_hotspot_info` | Geographic details for a specific hotspot |

### Regions
| Tool | Description |
|---|---|
| `get_regions` | Sub-regions of a given region |
| `get_adjacent_regions` | Regions bordering a given region |
| `get_region_info` | Geographic details for a region |

### Species
| Tool | Description |
|---|---|
| `get_species_list` | All species ever recorded in a region |

### Taxonomy
| Tool | Description |
|---|---|
| `get_taxonomy` | eBird/Clements taxonomy, optionally filtered |
| `get_taxonomy_forms` | Sub-specific forms for a species |
| `get_taxonomy_groups` | Species groups used in the taxonomy |
| `get_taxonomy_versions` | Available taxonomy versions |
| `get_taxonomy_locales` | Languages supported for common names |

### Statistics
| Tool | Description |
|---|---|
| `get_top_100` | Top 100 observers for a date |
| `get_totals` | Contributor, checklist, and species counts for a date |

## Development

Run the test suite:

```bash
uv run pytest
```

Add a dependency:

```bash
uv add <package>
```
