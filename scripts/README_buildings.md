Downloading and using local OSM PBFs for building footprints

1) Download a borough-level PBF from Geofabrik:

- Visit https://download.geofabrik.de/ and navigate to the appropriate extract (e.g. `europe/great-britain/england/greater-london.html`).
- Download the `.osm.pbf` file for the region you need (may be large).

2) Place the `.osm.pbf` file somewhere accessible, e.g. `data/greater-london-latest.osm.pbf`.

3) Use the loader in `scripts/building_loader.py` from Python or from the notebook:

```py
from scripts.building_loader import get_borough_buildings

bld = get_borough_buildings("City of London, UK", pbf_path="data/greater-london-latest.osm.pbf")
print(bld.shape)
```

4) The loader caches per-borough files to `cache/buildings/` as GPKG files for fast reuse.

Notes:
- Installing `pyrosm` is required to read `.osm.pbf` files locally: `pip install pyrosm`.
- If `pyrosm` is not available or the PBF is not provided, the loader will attempt an Overpass fetch (rate-limited).
