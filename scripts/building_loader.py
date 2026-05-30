"""Helpers to load building footprints from a local OSM PBF (pyrosm) or fall back to Overpass (osmnx).

Usage:
  - Prefer: provide a Geofabrik borough PBF and call `get_borough_buildings(borough_query, pbf_path=...)`
  - Fallback: if `pyrosm` or `pbf_path` is unavailable, this will try `osmnx.features_from_place` (Overpass)

The loader caches per-borough files under `cache/buildings/` as GPKG files.
"""
from pathlib import Path
import logging

import geopandas as gpd
import osmnx as ox

logger = logging.getLogger(__name__)


def _slug(text: str) -> str:
    # simple slug for filenames
    return "".join(c if c.isalnum() else "_" for c in text).strip("_")


def _cache_path(cache_dir: Path, borough_query: str) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    name = _slug(borough_query)
    return cache_dir / f"buildings_{name}.gpkg"


def load_buildings_from_pbf(pbf_path: str, bbox: tuple = None) -> gpd.GeoDataFrame:
    """Load buildings from a local OSM PBF using pyrosm.

    pbf_path: path to a .osm.pbf file (e.g. Geofabrik extract)
    bbox: optional (minx, miny, maxx, maxy) in lon/lat to restrict the extract
    Returns GeoDataFrame in EPSG:27700.
    """
    try:
        from pyrosm import OSM
    except Exception as e:
        raise RuntimeError("pyrosm is not available; install pyrosm to load local PBFs") from e

    osm = OSM(pbf_path)
    if bbox is not None:
        buildings = osm.get_buildings(bbox=bbox)
    else:
        buildings = osm.get_buildings()

    if buildings is None or buildings.shape[0] == 0:
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")

    # ensure a GeoDataFrame and project to EPSG:27700
    if not isinstance(buildings, gpd.GeoDataFrame):
        buildings = gpd.GeoDataFrame(buildings, geometry="geometry")
    if buildings.crs is None:
        buildings.set_crs(epsg=4326, inplace=True)
    return buildings.to_crs("EPSG:27700")


def get_borough_buildings(borough_query: str, pbf_path: str = None, cache_dir: str = "cache/buildings") -> gpd.GeoDataFrame:
    """Return buildings GeoDataFrame for a borough query.

    If a cached file exists it will be loaded. If `pbf_path` is provided, attempt to extract
    buildings from that PBF using pyrosm. Otherwise fall back to Overpass via osmnx.features_from_place.
    The returned GeoDataFrame is in EPSG:27700.
    """
    cache_dir = Path(cache_dir)
    cache_file = _cache_path(cache_dir, borough_query)

    if cache_file.exists():
        try:
            gdf = gpd.read_file(cache_file)
            if gdf.crs is None:
                gdf.set_crs(epsg=27700, inplace=True)
            return gdf.to_crs("EPSG:27700")
        except Exception:
            logger.warning("Failed to read cached buildings file, will re-fetch: %s", cache_file)

    # get borough geometry in lat/lon to use as bbox when reading PBF
    try:
        place_gdf = ox.geocode_to_gdf(borough_query)
    except Exception as e:
        raise RuntimeError(f"Could not geocode borough query '{borough_query}': {e}") from e

    place_gdf = place_gdf.to_crs(epsg=4326)
    geom = place_gdf.geometry.unary_union
    minx, miny, maxx, maxy = geom.bounds

    buildings = None
    if pbf_path is not None:
        try:
            buildings = load_buildings_from_pbf(pbf_path, bbox=(minx, miny, maxx, maxy))
        except Exception as e:
            logger.warning("Failed to load from PBF (%s): %s", pbf_path, e)

    if buildings is None or buildings.shape[0] == 0:
        # fallback to Overpass via osmnx
        try:
            tags = {"building": True}
            # features_from_place returns in EPSG:4326 by default
            feats = ox.features_from_place(borough_query, tags)
            if feats is None or feats.empty:
                buildings = gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")
            else:
                buildings = feats.to_crs(epsg=27700)
        except Exception as e:
            logger.warning("Could not fetch building footprints from Overpass: %s", e)
            buildings = gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:27700")

    # ensure correct crs and save cache
    if buildings.crs is None:
        buildings.set_crs(epsg=27700, inplace=True)
    else:
        buildings = buildings.to_crs(epsg=27700)

    # write cache safely
    try:
        buildings.to_file(cache_file, driver="GPKG")
    except Exception:
        logger.warning("Failed to cache buildings to %s", cache_file)

    return buildings
