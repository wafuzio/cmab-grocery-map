"""Download CA census tract boundaries (TIGER/Line) and merge with
Grocery Gap Atlas metrics to produce a GeoJSON for the map overlay.

Output: data/ca_tract_boundaries.json — GeoJSON FeatureCollection
  Each feature has tract polygon geometry + all GGA metrics as properties.
"""
import json
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

TIGER_URL = "https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_06_tract.zip"
TRACT_CSV = DATA_DIR / "gga_tract_metrics.csv"
OUTPUT = DATA_DIR / "ca_tract_boundaries.json"


def main() -> None:
    # --- Download TIGER shapefile ---
    zip_path = DATA_DIR / "tl_2020_06_tract.zip"
    if zip_path.exists():
        print(f"[cache] {zip_path.name} already downloaded ({zip_path.stat().st_size:,} bytes)")
    else:
        print(f"Downloading {TIGER_URL} ...")
        resp = requests.get(TIGER_URL, timeout=120)
        resp.raise_for_status()
        zip_path.write_bytes(resp.content)
        print(f"  Saved {zip_path.stat().st_size:,} bytes")

    # --- Read shapefile with geopandas ---
    print("Reading shapefile ...")
    try:
        import geopandas as gpd
    except ImportError:
        print("geopandas not installed. Installing ...")
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "geopandas"])
        import geopandas as gpd

    gdf = gpd.read_file(zip_path)
    print(f"  {len(gdf):,} tract polygons")
    print(f"  Columns: {list(gdf.columns)}")
    print(f"  CRS: {gdf.crs}")

    # Convert to WGS84 (EPSG:4326) for Leaflet
    if gdf.crs and str(gdf.crs) != "EPSG:4326":
        print(f"  Reprojecting to WGS84 ...")
        gdf = gdf.to_crs(epsg=4326)

    # Simplify geometries to reduce file size.
    # Project to a planar CRS (CA Albers) for accurate simplification,
    # simplify, then project back to WGS84.
    print("  Simplifying geometries ...")
    gdf_planar = gdf.to_crs(epsg=3310)  # CA Albers
    gdf_planar["geometry"] = gdf_planar.geometry.simplify(tolerance=50)  # 50m tolerance
    gdf_planar["area_km2"] = gdf_planar.geometry.area / 1e6  # sq meters → sq km
    gdf = gdf_planar.to_crs(epsg=4326)
    print(f"  Simplified.")

    # The GEOID column in TIGER is the full 11-digit tract GEOID
    print(f"  Sample GEOID: {gdf['GEOID'].iloc[0]}")

    # --- Load tract metrics ---
    print("Loading tract metrics ...")
    metrics = pd.read_csv(TRACT_CSV, dtype=str)
    print(f"  {len(metrics):,} tracts")

    # Build metrics lookup by GEOID
    metrics_map = {}
    for _, row in metrics.iterrows():
        metrics_map[row["GEOID"]] = row.to_dict()

    # --- Merge: add metrics to each tract polygon ---
    print("Merging metrics with boundaries ...")
    features = []
    matched = 0
    for _, row in gdf.iterrows():
        geoid = row["GEOID"]
        m = metrics_map.get(geoid)
        if m is None:
            continue
        matched += 1

        # Build properties
        def sf(key, cast=float):
            v = m.get(key)
            if v is None or str(v) == "nan":
                return None
            try:
                if cast is int:
                    return int(float(v))
                return cast(v)
            except (ValueError, TypeError):
                return None

        props = {
            "geoid": geoid,
            "name": m.get("NAME", ""),
            "pop": sf("TOTAL_POPULATION", int),
            "sc": 0,  # store count — will be filled from centroids
            "gp": sf("gravity_2023_percentile", int),
            "gps": sf("gravity_2023_state_percentile", int),
            "gv": sf("gravity_2023"),
            "hp": sf("hhi_2023_percentile", int),
            "hps": sf("hhi_2023_state_percentile", int),
            "hv": sf("hhi_2023"),
            "sp": sf("segregation_2023_percentile", int),
            "adi": sf("ADI_NATRANK", int),
            "mi": sf("MEDIAN_HOUSEHOLD_INCOME", int),
            "pov": sf("POVERTY_RATE"),
            "snap": sf("PCT_SNAP_ASSISTANCE"),
            "age": sf("MEDIAN_AGE"),
            "ph": sf("PCT HISPANIC OR LATINO"),
            "pw": sf("PCT NH WHITE"),
            "pb": sf("PCT NH BLACK"),
            "pa": sf("PCT NH ASIAN"),
            "area": round(row["area_km2"], 3) if row["area_km2"] > 0 else None,
        }

        # Compute population density (people per sq km)
        if props["area"] and props["area"] > 0 and props["pop"]:
            props["popd"] = round(props["pop"] / props["area"], 1)
        else:
            props["popd"] = None

        # Get geometry as GeoJSON
        geom = json.loads(json.dumps(row.geometry.__geo_interface__))
        features.append({
            "type": "Feature",
            "properties": props,
            "geometry": geom,
        })

    print(f"  Matched: {matched:,} / {len(gdf):,} tracts")

    # Add store counts from centroids
    centroids = pd.read_csv(DATA_DIR / "gga_tract_centroids.csv", dtype=str)
    sc_map = dict(zip(centroids["geoid"], centroids["store_count"]))
    for f in features:
        f["properties"]["sc"] = int(sc_map.get(f["properties"]["geoid"], 0))

    # --- Write GeoJSON ---
    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    print(f"\nWriting {OUTPUT} ...")
    with OUTPUT.open("w") as f:
        json.dump(geojson, f, separators=(",", ":"))
    size_mb = OUTPUT.stat().st_size / 1024 / 1024
    print(f"  {size_mb:.1f} MB")
    print(f"  {len(features):,} features")
    print("Done.")


if __name__ == "__main__":
    main()
