import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

BASE_URL = "https://api.ebird.org/v2"

mcp = FastMCP("bird-outing-mcp")


def _api_key() -> str:
    key = os.environ.get("EBIRD_API_KEY", "")
    if not key or key == "your_api_key_here":
        raise RuntimeError("EBIRD_API_KEY is not set in .env")
    return key


def _default_region() -> Optional[str]:
    return os.environ.get("EBIRD_DEFAULT_REGION") or None


def _region(region: Optional[str]) -> str:
    value = region or _default_region()
    if not value:
        raise ValueError("region is required (or set EBIRD_DEFAULT_REGION in .env)")
    return value


def _date_path(date: str) -> str:
    """Convert YYYY-MM-DD to YYYY/MM/DD for URL paths."""
    return date.replace("-", "/")


async def _get(path: str, params: dict) -> list | dict:
    clean = {k: v for k, v in params.items() if v is not None}
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_URL}{path}",
            params=clean,
            headers={"X-eBirdApiToken": _api_key()},
        )
        r.raise_for_status()
        return r.json()


# ---------------------------------------------------------------------------
# Observations
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_observations(
    region: Optional[str] = None,
    back: int = 14,
    max_results: Optional[int] = None,
    locale: str = "en",
    provisional: bool = False,
    hotspot: bool = False,
    detail: str = "simple",
    category: Optional[str] = None,
) -> list:
    """Recent observations (up to 30 days) for a region or location.

    Args:
        region: eBird region/location code (e.g. US-MA, L374326). Falls back to EBIRD_DEFAULT_REGION.
        back: Days back to search (1–30, default 14).
        max_results: Maximum observations to return (1–10000).
        locale: Language code for common names (default "en").
        provisional: Include unreviewed records.
        hotspot: Restrict to hotspots only.
        detail: "simple" or "full".
        category: Species category filter, e.g. "species", "hybrid".
    """
    area = _region(region)
    params = {
        "back": back,
        "maxObservations": max_results,
        "sppLocale": locale,
        "includeProvisional": provisional,
        "hotspot": hotspot,
        "detail": detail,
    }
    if category:
        params["cat"] = category
    return await _get(f"/data/obs/{area}/recent", params)


@mcp.tool()
async def get_notable_observations(
    region: Optional[str] = None,
    back: int = 14,
    max_results: Optional[int] = None,
    locale: str = "en",
    hotspot: bool = False,
    detail: str = "simple",
) -> list:
    """Recent notable (rare) observations for a region or location.

    Args:
        region: eBird region/location code. Falls back to EBIRD_DEFAULT_REGION.
        back: Days back to search (1–30, default 14).
        max_results: Maximum observations to return (1–10000).
        locale: Language code for common names.
        hotspot: Restrict to hotspots only.
        detail: "simple" or "full".
    """
    area = _region(region)
    params = {
        "back": back,
        "maxObservations": max_results,
        "sppLocale": locale,
        "hotspot": hotspot,
        "detail": detail,
    }
    return await _get(f"/data/obs/{area}/recent/notable", params)


@mcp.tool()
async def get_species_observations(
    species_code: str,
    region: Optional[str] = None,
    back: int = 14,
    max_results: Optional[int] = None,
    locale: str = "en",
    provisional: bool = False,
    hotspot: bool = False,
    detail: str = "simple",
) -> list:
    """Recent observations of a specific species in a region.

    Args:
        species_code: 6-letter eBird species code (e.g. "norcar" for Northern Cardinal).
        region: eBird region/location code. Falls back to EBIRD_DEFAULT_REGION.
        back: Days back to search (1–30, default 14).
        max_results: Maximum observations to return (1–10000).
        locale: Language code for common names.
        provisional: Include unreviewed records.
        hotspot: Restrict to hotspots only.
        detail: "simple" or "full".
    """
    area = _region(region)
    params = {
        "back": back,
        "maxObservations": max_results,
        "sppLocale": locale,
        "includeProvisional": provisional,
        "hotspot": hotspot,
        "detail": detail,
    }
    return await _get(f"/data/obs/{area}/recent/{species_code}", params)


@mcp.tool()
async def get_nearby_observations(
    lat: float,
    lng: float,
    dist: int = 25,
    back: int = 14,
    max_results: Optional[int] = None,
    locale: str = "en",
    provisional: bool = False,
    hotspot: bool = False,
    category: Optional[str] = None,
    sort: str = "date",
) -> list:
    """Most recent observation of each species near a latitude/longitude.

    Args:
        lat: Latitude (rounded to 2 decimal places).
        lng: Longitude (rounded to 2 decimal places).
        dist: Radius in km (0–50, default 25).
        back: Days back to search (1–30, default 14).
        max_results: Maximum observations to return (1–10000).
        locale: Language code for common names.
        provisional: Include unreviewed records.
        hotspot: Restrict to hotspots only.
        category: Species category filter.
        sort: Sort by "date" or "species".
    """
    params = {
        "lat": lat,
        "lng": lng,
        "dist": dist,
        "back": back,
        "maxObservations": max_results,
        "sppLocale": locale,
        "includeProvisional": provisional,
        "hotspot": hotspot,
        "sort": sort,
    }
    if category:
        params["cat"] = category
    return await _get("/data/obs/geo/recent", params)


@mcp.tool()
async def get_nearby_species(
    species_code: str,
    lat: float,
    lng: float,
    dist: int = 25,
    back: int = 14,
    max_results: Optional[int] = None,
    locale: str = "en",
    provisional: bool = False,
    hotspot: bool = False,
) -> list:
    """Most recent observation of a specific species near a latitude/longitude.

    Args:
        species_code: 6-letter eBird species code.
        lat: Latitude.
        lng: Longitude.
        dist: Radius in km (0–50, default 25).
        back: Days back to search (1–30, default 14).
        max_results: Maximum observations to return.
        locale: Language code for common names.
        provisional: Include unreviewed records.
        hotspot: Restrict to hotspots only.
    """
    params = {
        "lat": lat,
        "lng": lng,
        "dist": dist,
        "back": back,
        "maxObservations": max_results,
        "sppLocale": locale,
        "includeProvisional": provisional,
        "hotspot": hotspot,
    }
    return await _get(f"/data/obs/geo/recent/{species_code}", params)


@mcp.tool()
async def get_nearby_notable(
    lat: float,
    lng: float,
    dist: int = 25,
    back: int = 14,
    max_results: Optional[int] = None,
    locale: str = "en",
    hotspot: bool = False,
    detail: str = "simple",
) -> list:
    """Recent notable (rare) observations near a latitude/longitude.

    Args:
        lat: Latitude.
        lng: Longitude.
        dist: Radius in km (0–50, default 25).
        back: Days back to search (1–30, default 14).
        max_results: Maximum observations to return.
        locale: Language code for common names.
        hotspot: Restrict to hotspots only.
        detail: "simple" or "full".
    """
    params = {
        "lat": lat,
        "lng": lng,
        "dist": dist,
        "back": back,
        "maxObservations": max_results,
        "sppLocale": locale,
        "hotspot": hotspot,
        "detail": detail,
    }
    return await _get("/data/obs/geo/recent/notable", params)


@mcp.tool()
async def get_nearest_species(
    species_code: str,
    lat: float,
    lng: float,
    dist: int = 25,
    back: int = 14,
    max_results: Optional[int] = None,
    locale: str = "en",
    provisional: bool = False,
    hotspot: bool = False,
) -> list:
    """Nearest recent observations of a species to a latitude/longitude.

    Args:
        species_code: 6-letter eBird species code.
        lat: Latitude.
        lng: Longitude.
        dist: Radius in km (0–50, default 25).
        back: Days back to search (1–30, default 14).
        max_results: Maximum observations to return (1–1000).
        locale: Language code for common names.
        provisional: Include unreviewed records.
        hotspot: Restrict to hotspots only.
    """
    params = {
        "lat": lat,
        "lng": lng,
        "dist": dist,
        "back": back,
        "maxObservations": max_results,
        "sppLocale": locale,
        "includeProvisional": provisional,
        "hotspot": hotspot,
    }
    return await _get(f"/data/nearest/geo/recent/{species_code}", params)


@mcp.tool()
async def get_historic_observations(
    date: str,
    region: Optional[str] = None,
    max_results: Optional[int] = None,
    locale: str = "en",
    provisional: bool = False,
    hotspot: bool = False,
    detail: str = "simple",
    category: Optional[str] = None,
) -> list:
    """Observations recorded on a specific date for a region.

    Args:
        date: Date in YYYY-MM-DD format.
        region: eBird region/location code. Falls back to EBIRD_DEFAULT_REGION.
        max_results: Maximum observations to return (1–10000).
        locale: Language code for common names.
        provisional: Include unreviewed records.
        hotspot: Restrict to hotspots only.
        detail: "simple" or "full".
        category: Species category filter.
    """
    area = _region(region)
    params = {
        "rank": "mrec",
        "detail": detail,
        "sppLocale": locale,
        "includeProvisional": provisional,
        "hotspot": hotspot,
        "maxObservations": max_results,
    }
    if category:
        params["cat"] = category
    return await _get(f"/data/obs/{area}/historic/{_date_path(date)}", params)


# ---------------------------------------------------------------------------
# Checklists
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_visits(
    region: Optional[str] = None,
    date: Optional[str] = None,
    max_results: int = 10,
) -> list:
    """Recent checklists submitted for a region, optionally filtered to a date.

    Args:
        region: eBird region/location code. Falls back to EBIRD_DEFAULT_REGION.
        date: Optional date in YYYY-MM-DD format to filter by.
        max_results: Maximum checklists to return (1–200, default 10).
    """
    area = _region(region)
    params = {"maxVisits": max_results, "sortKey": "obs_dt"}
    if date:
        return await _get(f"/product/lists/{area}/{_date_path(date)}", params)
    return await _get(f"/product/lists/{area}", params)


@mcp.tool()
async def get_checklist(sub_id: str) -> dict:
    """Full details of a single checklist by its submission ID.

    Args:
        sub_id: eBird checklist submission ID (e.g. "S22893621").
    """
    return await _get(f"/product/checklist/view/{sub_id}", {})


# ---------------------------------------------------------------------------
# Hotspots
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_hotspots(
    region: Optional[str] = None,
    back: Optional[int] = None,
) -> list:
    """All hotspots within a region, optionally filtered to recently visited ones.

    Args:
        region: eBird region code (country, subnational1, or subnational2). Falls back to EBIRD_DEFAULT_REGION.
        back: If provided, only return hotspots visited in this many days (1–30).
    """
    area = _region(region)
    params: dict = {"fmt": "json"}
    if back is not None:
        params["back"] = back
    return await _get(f"/ref/hotspot/{area}", params)


@mcp.tool()
async def get_nearby_hotspots(
    lat: float,
    lng: float,
    dist: int = 25,
    back: Optional[int] = None,
) -> list:
    """Hotspots within a radius of a latitude/longitude.

    Args:
        lat: Latitude.
        lng: Longitude.
        dist: Radius in km (0–50, default 25).
        back: If provided, only return hotspots visited in this many days (1–30).
    """
    params: dict = {"lat": lat, "lng": lng, "dist": dist, "fmt": "json"}
    if back is not None:
        params["back"] = back
    return await _get("/ref/hotspot/geo", params)


@mcp.tool()
async def get_hotspot_info(loc_id: str) -> dict:
    """Geographic details for a hotspot (name, coordinates, region).

    Args:
        loc_id: eBird location code for a hotspot (e.g. "L374326").
    """
    return await _get(f"/ref/hotspot/info/{loc_id}", {})


# ---------------------------------------------------------------------------
# Regions
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_regions(region_type: str, region: Optional[str] = None) -> list:
    """Sub-regions of a given region.

    Args:
        region_type: One of "country", "subnational1", or "subnational2".
        region: Parent region code (e.g. "world", "US", "US-MA"). Falls back to EBIRD_DEFAULT_REGION.
    """
    area = _region(region)
    return await _get(f"/ref/region/list/{region_type}/{area}", {})


@mcp.tool()
async def get_adjacent_regions(region: Optional[str] = None) -> list:
    """Regions adjacent (bordering) to a given region.

    Args:
        region: eBird region code. Falls back to EBIRD_DEFAULT_REGION.
    """
    area = _region(region)
    return await _get(f"/ref/adjacent/{area}", {})


@mcp.tool()
async def get_region_info(region: Optional[str] = None) -> dict:
    """Geographic details for a region (name, bounds, type).

    Args:
        region: eBird region code. Falls back to EBIRD_DEFAULT_REGION.
    """
    area = _region(region)
    return await _get(f"/ref/region/info/{area}", {})


# ---------------------------------------------------------------------------
# Species
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_species_list(region: Optional[str] = None) -> list:
    """All species ever recorded in a region or location.

    Returns a list of 6-letter eBird species codes.

    Args:
        region: eBird region/location code. Falls back to EBIRD_DEFAULT_REGION.
    """
    area = _region(region)
    return await _get(f"/product/spplist/{area}", {})


# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_taxonomy(
    category: Optional[str] = None,
    locale: str = "en",
    version: Optional[str] = None,
    species: Optional[str] = None,
) -> list:
    """eBird/Clements taxonomy, optionally filtered by category or species.

    Args:
        category: Filter by category: "species", "hybrid", "issf", "spuh", "slash", "domestic", "form", "intergrade".
        locale: Language code for common names (default "en").
        version: Taxonomy version number (default is latest).
        species: Comma-separated species codes to filter by.
    """
    params: dict = {"locale": locale, "fmt": "json"}
    if category:
        params["cat"] = category
    if version:
        params["version"] = version
    if species:
        params["species"] = species
    return await _get("/ref/taxonomy/ebird", params)


@mcp.tool()
async def get_taxonomy_forms(species_code: str) -> list:
    """All sub-specific forms (subspecies/intergrades) for a species.

    Args:
        species_code: 6-letter eBird species code (e.g. "horlar" for Horned Lark).
    """
    return await _get(f"/ref/taxon/forms/{species_code}", {})


@mcp.tool()
async def get_taxonomy_groups(ordering: str = "ebird", locale: str = "en") -> list:
    """Species groups used in the eBird taxonomy.

    Args:
        ordering: Group ordering — "ebird" (taxonomic) or "merlin" (by likeness).
        locale: Language code for group names.
    """
    params = {"groupNameLocale": locale}
    return await _get(f"/ref/sppgroup/{ordering}", params)


@mcp.tool()
async def get_taxonomy_versions() -> list:
    """All available eBird taxonomy versions."""
    return await _get("/ref/taxonomy/versions", {})


@mcp.tool()
async def get_taxonomy_locales() -> list:
    """All locales (languages) supported for species common names."""
    return await _get("/ref/taxa-locales/ebird", {})


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_top_100(
    date: str,
    region: Optional[str] = None,
    rank: str = "spp",
    max_results: int = 100,
) -> list:
    """Top 100 observers by species seen or checklists submitted on a date.

    Args:
        date: Date in YYYY-MM-DD format.
        region: eBird region code. Falls back to EBIRD_DEFAULT_REGION.
        rank: Rank by "spp" (species seen) or "cl" (checklists submitted).
        max_results: Maximum observers to return (1–100, default 100).
    """
    area = _region(region)
    params = {"maxObservers": max_results, "rankedBy": rank}
    return await _get(f"/product/top100/{area}/{_date_path(date)}", params)


@mcp.tool()
async def get_totals(date: str, region: Optional[str] = None) -> dict:
    """Number of contributors, checklists, and species seen on a date.

    Args:
        date: Date in YYYY-MM-DD format.
        region: eBird region/location code. Falls back to EBIRD_DEFAULT_REGION.
    """
    area = _region(region)
    return await _get(f"/product/stats/{area}/{_date_path(date)}", {})


def main() -> None:
    mcp.run()
