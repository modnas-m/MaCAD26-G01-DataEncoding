"""Helpers to load Barcelona street segments from a local Cataluña OSM PBF.

The loader uses pyogrio directly against the OSM layers exposed by the PBF.
This avoids runtime dependencies on pyrosm and keeps the extraction fully local.
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path

import geopandas as gpd
import pandas as pd
from pyogrio import read_dataframe

logger = logging.getLogger(__name__)

DEFAULT_PROJECTED_CRS = "EPSG:25831"
DEFAULT_BOROUGH_LABEL = "Barcelona, Catalonia, Spain"
DEFAULT_BOUNDARY_NAME = "Barcelona"
DEFAULT_NETWORK_TYPE = "all"


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()


def _parse_other_tags(other_tags):
    if other_tags is None or (isinstance(other_tags, float) and pd.isna(other_tags)):
        return {}

    text = str(other_tags)
    matches = re.findall(r'"([^"]+)"=>"([^"]*)"', text)
    return {key: value for key, value in matches}


def _as_text(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text if text and text.lower() != "none" else None


def _normalise_tag_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = df.copy()
    for column in columns:
        if column not in result.columns:
            result[column] = None
        result[column] = result[column].apply(_as_text)
    return result


def load_barcelona_boundary(
    pbf_path: str | Path,
    boundary_name: str = DEFAULT_BOUNDARY_NAME,
    admin_level: str = "8",
) -> gpd.GeoDataFrame:
    """Load the Barcelona municipality boundary from the local PBF."""

    pbf_path = Path(pbf_path)
    if not pbf_path.exists():
        raise FileNotFoundError(f"PBF file not found: {pbf_path}")

    boundaries = read_dataframe(
        pbf_path,
        layer="multipolygons",
        columns=["name", "admin_level", "boundary", "type", "other_tags"],
    )

    if boundaries is None or boundaries.empty:
        raise RuntimeError(f"Could not read boundary layer from {pbf_path}")

    boundaries = boundaries.copy()
    name_mask = boundaries["name"].astype(str).str.contains(boundary_name, case=False, na=False)
    boundary_mask = boundaries["boundary"].astype(str).eq("administrative")
    admin_mask = boundaries["admin_level"].astype(str).eq(str(admin_level))

    selected = boundaries[name_mask & boundary_mask & admin_mask].copy()
    if selected.empty:
        selected = boundaries[name_mask & boundary_mask].copy()
    if selected.empty:
        selected = boundaries[name_mask].copy()
    if selected.empty:
        raise RuntimeError(f"Could not find a boundary named {boundary_name!r} in the PBF")

    selected = selected.to_crs(DEFAULT_PROJECTED_CRS)
    selected["_area"] = selected.geometry.area
    selected = selected.sort_values("_area", ascending=False).head(1).drop(columns="_area")
    return selected.reset_index(drop=True)


def _filter_highway_type(series: pd.Series, network_type: str) -> pd.Series:
    if network_type == "all":
        return series.notna()

    allowed = {
        "driving": {
            "motorway",
            "motorway_link",
            "trunk",
            "trunk_link",
            "primary",
            "primary_link",
            "secondary",
            "secondary_link",
            "tertiary",
            "tertiary_link",
            "unclassified",
            "residential",
            "service",
        },
        "driving+service": {
            "motorway",
            "motorway_link",
            "trunk",
            "trunk_link",
            "primary",
            "primary_link",
            "secondary",
            "secondary_link",
            "tertiary",
            "tertiary_link",
            "unclassified",
            "residential",
            "service",
        },
        "walking": {
            "footway",
            "path",
            "pedestrian",
            "living_street",
            "track",
            "residential",
            "service",
            "steps",
            "cycleway",
            "unclassified",
            "primary",
            "secondary",
            "tertiary",
        },
        "cycling": {
            "cycleway",
            "path",
            "living_street",
            "residential",
            "service",
            "unclassified",
            "primary",
            "secondary",
            "tertiary",
            "track",
        },
    }
    allowed_values = allowed.get(network_type, None)
    if allowed_values is None:
        return series.notna()
    return series.astype(str).str.lower().isin(allowed_values)


def load_street_edges_from_pbf(
    pbf_path: str | Path,
    *,
    boundary: gpd.GeoDataFrame | None = None,
    network_type: str = DEFAULT_NETWORK_TYPE,
    clip_to_boundary: bool = True,
) -> gpd.GeoDataFrame:
    """Load street-network edges from a local PBF."""

    pbf_path = Path(pbf_path)
    if not pbf_path.exists():
        raise FileNotFoundError(f"PBF file not found: {pbf_path}")

    bbox = None
    if boundary is not None and not boundary.empty:
        bbox = tuple(boundary.to_crs("EPSG:4326").total_bounds)

    edges = read_dataframe(
        pbf_path,
        layer="lines",
        bbox=bbox,
        columns=["osm_id", "name", "highway", "waterway", "aerialway", "barrier", "man_made", "railway", "z_order", "other_tags"],
    )

    if edges is None or edges.empty:
        raise RuntimeError(f"No street edges could be read from {pbf_path}")

    edges = edges.copy()
    edges = edges[edges.geometry.notna() & ~edges.geometry.is_empty].copy()
    edges = edges[edges.geometry.geom_type.isin(["LineString", "MultiLineString"])].copy()

    edges = _normalise_tag_columns(edges, ["highway", "name"])
    edges["highway"] = edges["highway"].apply(_as_text)
    edges = edges[edges["highway"].notna()].copy()
    edges = edges[_filter_highway_type(edges["highway"], network_type)].copy()

    extracted = edges["other_tags"].apply(_parse_other_tags)
    tag_columns = [
        "lanes",
        "maxspeed",
        "oneway",
        "sidewalk",
        "cycleway",
        "width",
        "service",
        "access",
        "surface",
        "smoothness",
        "lit",
        "bridge",
        "tunnel",
        "layer",
        "ref",
        "junction",
        "oneway:cycleway",
        "cycleway:both",
        "cycleway:left",
        "cycleway:right",
        "foot",
        "motor_vehicle",
        "bicycle",
        "footway",
    ]
    for column in tag_columns:
        if column not in edges.columns:
            edges[column] = extracted.apply(lambda d: d.get(column) if isinstance(d, dict) else None)
        else:
            edges[column] = edges[column].fillna(extracted.apply(lambda d: d.get(column) if isinstance(d, dict) else None))

    edges = _normalise_tag_columns(edges, tag_columns)

    if clip_to_boundary and boundary is not None and not boundary.empty:
        boundary_proj = boundary.to_crs(edges.crs)
        try:
            edges = gpd.clip(edges, boundary_proj)
        except Exception as exc:
            logger.warning("Clipping street edges to Barcelona boundary failed, keeping bbox-filtered edges: %s", exc)

    edges = edges.reset_index(drop=True)
    return edges


def build_segment_table(
    pbf_path: str | Path,
    *,
    boundary: gpd.GeoDataFrame | None = None,
    boundary_name: str = DEFAULT_BOUNDARY_NAME,
    borough_label: str = DEFAULT_BOROUGH_LABEL,
    network_type: str = DEFAULT_NETWORK_TYPE,
    projected_crs: str = DEFAULT_PROJECTED_CRS,
) -> gpd.GeoDataFrame:
    """Build a Barcelona street-segment table from the local Cataluña PBF."""

    if boundary is None or boundary.empty:
        boundary = load_barcelona_boundary(pbf_path, boundary_name=boundary_name)
    edges = load_street_edges_from_pbf(
        pbf_path,
        boundary=boundary,
        network_type=network_type,
        clip_to_boundary=True,
    )

    if edges.crs is None:
        edges = edges.set_crs(epsg=4326)
    edges = edges.to_crs(projected_crs)

    sort_cols = [c for c in ["osm_id", "highway", "name"] if c in edges.columns]
    if sort_cols:
        edges = edges.sort_values(sort_cols).reset_index(drop=True)

    segments_wgs84 = edges.to_crs("EPSG:4326")
    midpoints = segments_wgs84.geometry.apply(
        lambda geom: geom.interpolate(0.5, normalized=True) if geom.geom_type in ("LineString", "MultiLineString") else geom.centroid
    )

    result = edges.copy()
    result["borough"] = borough_label
    result["longitude"] = [round(float(pt.x), 7) for pt in midpoints]
    result["latitude"] = [round(float(pt.y), 7) for pt in midpoints]
    borough_slug = _slug(borough_label)
    result["location_id"] = [f"{borough_slug}_{idx:06d}" for idx in range(len(result))]

    # Keep downstream schema-friendly placeholders so later notebooks can fill them.
    for column in ["lighting", "connectivity", "enclosure"]:
        if column not in result.columns:
            result[column] = pd.NA

    return result.reset_index(drop=True)


def export_segment_table(
    pbf_path: str | Path,
    output_path: str | Path,
    *,
    boundary: gpd.GeoDataFrame | None = None,
    boundary_name: str = DEFAULT_BOUNDARY_NAME,
    borough_label: str = DEFAULT_BOROUGH_LABEL,
    network_type: str = DEFAULT_NETWORK_TYPE,
    projected_crs: str = DEFAULT_PROJECTED_CRS,
) -> Path:
    """Build and write the Barcelona segment table as CSV."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    segments = build_segment_table(
        pbf_path,
        boundary=boundary,
        boundary_name=boundary_name,
        borough_label=borough_label,
        network_type=network_type,
        projected_crs=projected_crs,
    )

    csv_frame = segments.copy()
    csv_frame["geometry"] = csv_frame.geometry.to_wkt()
    csv_frame = csv_frame.drop(columns="geometry")
    csv_frame.to_csv(output_path, index=False)
    return output_path


def _main() -> int:
    parser = argparse.ArgumentParser(description="Extract Barcelona street segments from a local Cataluña OSM PBF.")
    parser.add_argument(
        "--pbf",
        dest="pbf_path",
        default=str(Path("geofabrik") / "cataluna-260611.osm.pbf"),
        help="Path to the Cataluña .osm.pbf file.",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        default=str(Path("csv") / "barcelona_segments_from_cataluna_pbf.csv"),
        help="Output CSV path for the extracted Barcelona segment table.",
    )
    parser.add_argument(
        "--boundary-name",
        default=DEFAULT_BOUNDARY_NAME,
        help="Boundary name to extract from the PBF.",
    )
    parser.add_argument(
        "--borough-label",
        default=DEFAULT_BOROUGH_LABEL,
        help="Text label to write into the borough column.",
    )
    parser.add_argument(
        "--network-type",
        default=DEFAULT_NETWORK_TYPE,
        choices=["walking", "cycling", "driving", "driving+service", "all"],
        help="Street-network profile to extract.",
    )
    parser.add_argument(
        "--projected-crs",
        default=DEFAULT_PROJECTED_CRS,
        help="Projected CRS used for geometry and derived coordinates.",
    )
    args = parser.parse_args()

    output_path = export_segment_table(
        args.pbf_path,
        args.output_path,
        boundary_name=args.boundary_name,
        borough_label=args.borough_label,
        network_type=args.network_type,
        projected_crs=args.projected_crs,
    )
    print(f"Saved Barcelona street segments to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())