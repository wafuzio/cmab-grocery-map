"""Build a JSON file of Grocery Gap Atlas data for the CA map.

Produces:
  data/gga_tract_data.json — {
    tracts: { GEOID -> { metrics... } },
    stores: [ { company, addr, city, lat, lon, geoid, parent_company, pct_tract_sales } ],
    parent_companies: [ { name, store_count } ]
  }
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

TRACT_CSV = DATA_DIR / "gga_tract_metrics.csv"
STORES_CSV = DATA_DIR / "gga_tract_stores.csv"
OUTPUT = DATA_DIR / "gga_tract_data.json"


def main() -> None:
    # --- Load tract metrics ---
    print("Loading tract metrics ...")
    tracts_df = pd.read_csv(TRACT_CSV, dtype=str)
    print(f"  {len(tracts_df):,} tracts")

    # Build tract dict keyed by GEOID
    tracts = {}
    for _, row in tracts_df.iterrows():
        geoid = row["GEOID"]
        tracts[geoid] = {
            "name": row.get("NAME", ""),
            "population": int(float(row["TOTAL_POPULATION"])) if row.get("TOTAL_POPULATION") and str(row["TOTAL_POPULATION"]) != "nan" else 0,
            "gravity_2023": float(row["gravity_2023"]) if row.get("gravity_2023") and str(row["gravity_2023"]) != "nan" else None,
            "gravity_pct": int(float(row["gravity_2023_percentile"])) if row.get("gravity_2023_percentile") and str(row["gravity_2023_percentile"]) != "nan" else None,
            "gravity_pct_state": int(float(row["gravity_2023_state_percentile"])) if row.get("gravity_2023_state_percentile") and str(row["gravity_2023_state_percentile"]) != "nan" else None,
            "hhi_2023": float(row["hhi_2023"]) if row.get("hhi_2023") and str(row["hhi_2023"]) != "nan" else None,
            "hhi_pct": int(float(row["hhi_2023_percentile"])) if row.get("hhi_2023_percentile") and str(row["hhi_2023_percentile"]) != "nan" else None,
            "hhi_pct_state": int(float(row["hhi_2023_state_percentile"])) if row.get("hhi_2023_state_percentile") and str(row["hhi_2023_state_percentile"]) != "nan" else None,
            "segregation_pct": int(float(row["segregation_2023_percentile"])) if row.get("segregation_2023_percentile") and str(row["segregation_2023_percentile"]) != "nan" else None,
            "adi_natrank": int(float(row["ADI_NATRANK"])) if row.get("ADI_NATRANK") and str(row["ADI_NATRANK"]) != "nan" else None,
            "adi_staternk": int(float(row["ADI_STATERNK"])) if row.get("ADI_STATERNK") and str(row["ADI_STATERNK"]) != "nan" else None,
            "median_income": int(float(row["MEDIAN_HOUSEHOLD_INCOME"])) if row.get("MEDIAN_HOUSEHOLD_INCOME") and str(row["MEDIAN_HOUSEHOLD_INCOME"]) != "nan" else None,
            "poverty_rate": float(row["POVERTY_RATE"]) if row.get("POVERTY_RATE") and str(row["POVERTY_RATE"]) != "nan" else None,
            "pct_snap": float(row["PCT_SNAP_ASSISTANCE"]) if row.get("PCT_SNAP_ASSISTANCE") and str(row["PCT_SNAP_ASSISTANCE"]) != "nan" else None,
            "pct_no_healthcare": float(row["PCT_NO_HEALTHCARE"]) if row.get("PCT_NO_HEALTHCARE") and str(row["PCT_NO_HEALTHCARE"]) != "nan" else None,
            "pct_with_disability": float(row["PCT_WITH_A_DISABILITY"]) if row.get("PCT_WITH_A_DISABILITY") and str(row["PCT_WITH_A_DISABILITY"]) != "nan" else None,
            "median_age": float(row["MEDIAN_AGE"]) if row.get("MEDIAN_AGE") and str(row["MEDIAN_AGE"]) != "nan" else None,
            # Race/ethnicity percentages
            "pct_white": float(row["PCT NH WHITE"]) if row.get("PCT NH WHITE") and str(row["PCT NH WHITE"]) != "nan" else None,
            "pct_black": float(row["PCT NH BLACK"]) if row.get("PCT NH BLACK") and str(row["PCT NH BLACK"]) != "nan" else None,
            "pct_asian": float(row["PCT NH ASIAN"]) if row.get("PCT NH ASIAN") and str(row["PCT NH ASIAN"]) != "nan" else None,
            "pct_hispanic": float(row["PCT HISPANIC OR LATINO"]) if row.get("PCT HISPANIC OR LATINO") and str(row["PCT HISPANIC OR LATINO"]) != "nan" else None,
            # Parent company market shares (for the tract)
            "market_shares": {
                "Albertsons": float(row["ALBERTSONS CO INC"]) if row.get("ALBERTSONS CO INC") and str(row["ALBERTSONS CO INC"]) != "nan" else None,
                "Costco": float(row["COSTCO WHOLESALE CORP"]) if row.get("COSTCO WHOLESALE CORP") and str(row["COSTCO WHOLESALE CORP"]) != "nan" else None,
                "Dollar General": float(row["DOLLAR GENERAL CORP"]) if row.get("DOLLAR GENERAL CORP") and str(row["DOLLAR GENERAL CORP"]) != "nan" else None,
                "Dollar Tree": float(row["DOLLAR TREE INC"]) if row.get("DOLLAR TREE INC") and str(row["DOLLAR TREE INC"]) != "nan" else None,
                "Kroger": float(row["KROGER CO"]) if row.get("KROGER CO") and str(row["KROGER CO"]) != "nan" else None,
                "Target": float(row["TARGET CORP"]) if row.get("TARGET CORP") and str(row["TARGET CORP"]) != "nan" else None,
                "Trader Joes": float(row["TRADER JOE'S"]) if row.get("TRADER JOE'S") and str(row["TRADER JOE'S"]) != "nan" else None,
                "Walmart": float(row["WALMART INC"]) if row.get("WALMART INC") and str(row["WALMART INC"]) != "nan" else None,
            },
        }
    print(f"  Built {len(tracts):,} tract records")

    # --- Load store data ---
    print("Loading store data ...")
    stores_df = pd.read_csv(STORES_CSV, dtype=str)
    print(f"  {len(stores_df):,} store records")

    stores = []
    for _, row in stores_df.iterrows():
        lat = float(row["store_lat"]) if row.get("store_lat") and row["store_lat"] != "nan" else None
        lon = float(row["store_lon"]) if row.get("store_lon") and row["store_lon"] != "nan" else None
        if lat is None or lon is None:
            continue
        stores.append({
            "geoid": row["geoid"],
            "company": row.get("company", ""),
            "addr": row.get("address_line_1", ""),
            "city": row.get("city", ""),
            "state": row.get("state", "CA"),
            "zip": str(row.get("zipcode", "")).replace(".0", ""),
            "parent_company": row.get("parent_company", ""),
            "pct_tract_sales": float(row["pct_of_tract_sales"]) if row.get("pct_of_tract_sales") and row["pct_of_tract_sales"] != "nan" else None,
            "lat": lat,
            "lon": lon,
            "county": row.get("county", ""),
        })
    print(f"  {len(stores):,} stores with valid coordinates")

    # Parent company summary
    pc_counts = stores_df["parent_company"].value_counts()
    parent_companies = [
        {"name": name, "store_count": int(count)}
        for name, count in pc_counts.head(30).items()
    ]

    # --- Write output ---
    output = {
        "meta": {
            "source": "Grocery Gap Atlas (rafiusa.org)",
            "date": "August 2024 data",
            "ca_tracts": len(tracts),
            "ca_stores": len(stores),
        },
        "tracts": tracts,
        "stores": stores,
        "parent_companies": parent_companies,
    }

    print(f"\nWriting {OUTPUT} ...")
    with OUTPUT.open("w") as f:
        json.dump(output, f)
    print(f"  {OUTPUT.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"\nDone. {len(tracts):,} tracts, {len(stores):,} stores.")


if __name__ == "__main__":
    main()
