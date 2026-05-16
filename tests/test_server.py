import os
from unittest.mock import AsyncMock, patch

import pytest

# Ensure env vars are set before importing server
os.environ.setdefault("EBIRD_API_KEY", "test-key")
os.environ.setdefault("EBIRD_DEFAULT_REGION", "US-MA")

from bird_outing_mcp.server import (
    _date_path,
    _default_region,
    _region,
    get_checklist,
    get_historic_observations,
    get_hotspot_info,
    get_hotspots,
    get_nearby_hotspots,
    get_nearby_notable,
    get_nearby_observations,
    get_nearby_species,
    get_nearest_species,
    get_notable_observations,
    get_observations,
    get_region_info,
    get_regions,
    get_adjacent_regions,
    get_species_list,
    get_species_observations,
    get_taxonomy,
    get_taxonomy_forms,
    get_taxonomy_groups,
    get_taxonomy_locales,
    get_taxonomy_versions,
    get_top_100,
    get_totals,
    get_visits,
)


def test_date_path():
    assert _date_path("2024-05-01") == "2024/05/01"


def test_region_uses_default():
    assert _region(None) == "US-MA"


def test_region_explicit_overrides_default():
    assert _region("US-NY") == "US-NY"


def test_region_raises_when_no_default(monkeypatch):
    monkeypatch.delenv("EBIRD_DEFAULT_REGION", raising=False)
    with pytest.raises(ValueError, match="region is required"):
        _region(None)


@pytest.fixture
def mock_get():
    with patch("bird_outing_mcp.server._get", new_callable=AsyncMock) as m:
        m.return_value = []
        yield m


async def test_get_observations_default_region(mock_get):
    await get_observations()
    mock_get.assert_called_once()
    path = mock_get.call_args[0][0]
    assert "/data/obs/US-MA/recent" in path


async def test_get_observations_explicit_region(mock_get):
    await get_observations(region="US-NY")
    path = mock_get.call_args[0][0]
    assert "/data/obs/US-NY/recent" in path


async def test_get_notable_observations(mock_get):
    await get_notable_observations()
    path = mock_get.call_args[0][0]
    assert "/data/obs/US-MA/recent/notable" in path


async def test_get_species_observations(mock_get):
    await get_species_observations("norcar")
    path = mock_get.call_args[0][0]
    assert "/data/obs/US-MA/recent/norcar" in path


async def test_get_nearby_observations(mock_get):
    await get_nearby_observations(42.36, -71.06)
    path = mock_get.call_args[0][0]
    assert "/data/obs/geo/recent" in path


async def test_get_nearby_species(mock_get):
    await get_nearby_species("norcar", 42.36, -71.06)
    path = mock_get.call_args[0][0]
    assert "/data/obs/geo/recent/norcar" in path


async def test_get_nearby_notable(mock_get):
    await get_nearby_notable(42.36, -71.06)
    path = mock_get.call_args[0][0]
    assert "/data/obs/geo/recent/notable" in path


async def test_get_nearest_species(mock_get):
    await get_nearest_species("norcar", 42.36, -71.06)
    path = mock_get.call_args[0][0]
    assert "/data/nearest/geo/recent/norcar" in path


async def test_get_historic_observations(mock_get):
    await get_historic_observations("2024-05-01")
    path = mock_get.call_args[0][0]
    assert "/data/obs/US-MA/historic/2024/05/01" in path


async def test_get_visits_recent(mock_get):
    await get_visits()
    path = mock_get.call_args[0][0]
    assert "/product/lists/US-MA" in path
    assert "historic" not in path


async def test_get_visits_by_date(mock_get):
    await get_visits(date="2024-05-01")
    path = mock_get.call_args[0][0]
    assert "/product/lists/US-MA/2024/05/01" in path


async def test_get_checklist(mock_get):
    mock_get.return_value = {}
    await get_checklist("S12345678")
    path = mock_get.call_args[0][0]
    assert "/product/checklist/view/S12345678" in path


async def test_get_hotspots(mock_get):
    await get_hotspots()
    path = mock_get.call_args[0][0]
    assert "/ref/hotspot/US-MA" in path


async def test_get_nearby_hotspots(mock_get):
    await get_nearby_hotspots(42.36, -71.06)
    path = mock_get.call_args[0][0]
    assert "/ref/hotspot/geo" in path


async def test_get_hotspot_info(mock_get):
    mock_get.return_value = {}
    await get_hotspot_info("L374326")
    path = mock_get.call_args[0][0]
    assert "/ref/hotspot/info/L374326" in path


async def test_get_regions(mock_get):
    await get_regions("subnational1")
    path = mock_get.call_args[0][0]
    assert "/ref/region/list/subnational1/US-MA" in path


async def test_get_adjacent_regions(mock_get):
    await get_adjacent_regions()
    path = mock_get.call_args[0][0]
    assert "/ref/adjacent/US-MA" in path


async def test_get_region_info(mock_get):
    mock_get.return_value = {}
    await get_region_info()
    path = mock_get.call_args[0][0]
    assert "/ref/region/info/US-MA" in path


async def test_get_species_list(mock_get):
    await get_species_list()
    path = mock_get.call_args[0][0]
    assert "/product/spplist/US-MA" in path


async def test_get_taxonomy(mock_get):
    await get_taxonomy()
    path = mock_get.call_args[0][0]
    assert "/ref/taxonomy/ebird" in path


async def test_get_taxonomy_forms(mock_get):
    await get_taxonomy_forms("horlar")
    path = mock_get.call_args[0][0]
    assert "/ref/taxon/forms/horlar" in path


async def test_get_taxonomy_groups(mock_get):
    await get_taxonomy_groups()
    path = mock_get.call_args[0][0]
    assert "/ref/sppgroup/ebird" in path


async def test_get_taxonomy_versions(mock_get):
    await get_taxonomy_versions()
    path = mock_get.call_args[0][0]
    assert "/ref/taxonomy/versions" in path


async def test_get_taxonomy_locales(mock_get):
    await get_taxonomy_locales()
    path = mock_get.call_args[0][0]
    assert "/ref/taxa-locales/ebird" in path


async def test_get_top_100(mock_get):
    await get_top_100("2024-05-01")
    path = mock_get.call_args[0][0]
    assert "/product/top100/US-MA/2024/05/01" in path


async def test_get_totals(mock_get):
    mock_get.return_value = {}
    await get_totals("2024-05-01")
    path = mock_get.call_args[0][0]
    assert "/product/stats/US-MA/2024/05/01" in path
