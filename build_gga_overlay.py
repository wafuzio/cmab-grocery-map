"""Build a compact JSON of CA tract data for the map overlay.

Merges tract metrics with computed centroids (from store locations).
Output: data/gga_tract_overlay.json — lightweight, one entry per tract.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

TRACT_CSV = DATA_DIR / "gga_tract_metrics.csv"
CENTROIDS_CSV = DATA_DIR / "gga_tract_centroids.csv"
OUTPUT = DATA_DIR / "gga_tract_overlay.json"


def safe_float(v):
    if v is None or str(v) == "nan":
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def safe_int(v):
    f = safe_float(v)
    return int(f) if f is not None else None


def main() -> None:
    print("Loading tract metrics ...")
    tracts_df = pd.read_csv(TRACT_CSV, dtype=str)
    print(f"  {len(tracts_df):,} tracts")

    print("Loading centroids ...")
    centroids_df = pd.read_csv(CENTROIDS_CSV, dtype=str)
    centroids_df["lat"] = pd.to_numeric(centroids_df["lat"], errors="coerce")
    centroids_df["lon"] = pd.to_numeric(centroids_df["lon"], errors="coerce")
    centroids_df["store_count"] = pd.to_numeric(centroids_df["store_count"], errors="coerce").astype(int)
    centroid_map = centroids_df.set_index("geoid").to_dict("index")
    print(f"  {len(centroids_df):,} centroids")

    tracts = []
    for _, row in tracts_df.iterrows():
        geoid = row["GEOID"]
        c = centroid_map.get(geoid)
        if c is None or pd.isna(c["lat"]) or pd.isna(c["lon"]):
            continue
        tracts.append({
            "geoid": geoid,
            "lat": round(c["lat"], 5),
            "lon": round(c["lon"], 5),
            "sc": int(c["store_count"]),
            "name": row.get("NAME", ""),
            "pop": safe_int(row.get("TOTAL_POPULATION")),
            "gp": safe_int(row.get("gravity_2023_percentile")),        # gravity percentile (food access)
            "gps": safe_int(row.get("gravity_2023_state_percentile")),  # state percentile
            "gv": safe_float(row.get("gravity_2023")),                  # raw gravity score
            "hp": safe_int(row.get("hhi_2023_percentile")),            # HHI percentile (concentration)
            "hps": safe_int(row.get("hhi_2023_state_percentile")),
            "hv": safe_float(row.get("hhi_2023")),                     # raw HHI
            "sp": safe_int(row.get("segregation_2023_percentile")),    # segregation percentile
            "adi": safe_int(row.get("ADI_NATRANK")),                   # socioeconomic disadvantage
            "mi": safe_int(row.get("MEDIAN_HOUSEHOLD_INCOME")),        # median household income
            "pov": safe_float(row.get("POVERTY_RATE")),                # poverty rate
            "snap": safe_float(row.get("PCT_SNAP_ASSISTANCE")),        # SNAP %
            "age": safe_float(row.get("MEDIAN_AGE")),
            "ph": safe_float(row.get("PCT HISPANIC OR LATINO")),
            "pw": safe_float(row.get("PCT NH WHITE")),
            "pb": safe_float(row.get("PCT NH BLACK")),
            "pa": safe_float(row.get("PCT NH ASIAN")),
        })

    print(f"  {len(tracts):,} tracts with coordinates")
    output = {"tracts": tracts}
    print(f"Writing {OUTPUT} ...")
    with OUTPUT.open("w") as f:
        json.dump(output, f, separators=(",", ":"))
    size_mb = OUTPUT.stat().st_size / 1024 / 1024
    print(f"  {size_mb:.1f} MB")
    print("Done.")


if __name__ == "__main__":
    main()
