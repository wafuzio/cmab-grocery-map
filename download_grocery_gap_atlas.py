"""Download Grocery Gap Atlas data for all California census tracts.

Fetches:
  1. Bulk tract metrics CSV (all US tracts) — filter to CA (GEOID starts with '06')
  2. Per-tract store lists from the API (/api/stores/{GEOID})
  3. Parquet files for full tract-level data and concentration metrics

Outputs:
  data/gga_tract_metrics.csv       — one row per CA tract with all metrics
  data/gga_tract_stores.csv        — all stores across all CA tracts
  data/gga_full_tract.parquet      — raw parquet (all US tracts)
  data/gga_concentration.parquet   — raw parquet (concentration metrics)
"""
import io
import json
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

BASE = "https://grocerygapatlas.rafiusa.org"

# --- File URLs (all have CORS: * and are publicly downloadable) ---
CSV_ZIP_URL = f"{BASE}/data/grocery-gap-atlas-data-august-2024.csv.zip"
XLSX_URL = f"{BASE}/data/grocery-gap-atlas-data-august-2024.xlsx"
PARQUET_TRACT_URL = f"{BASE}/data/full_tract.parquet"
PARQUET_CONC_URL = f"{BASE}/data/concentration_metrics_wide.parquet"

# --- API endpoints ---
STORES_API = f"{BASE}/api/stores/{{geoid}}"
CENTROIDS_API = f"{BASE}/api/centroids/{{geoid}}"

# CA tract GEOIDs start with '06'. There are ~8,000 CA census tracts.
CA_PREFIX = "06"

# Be polite to the server — 0.1s between API calls.
API_DELAY = 0.1

# Batch size for progress reporting.
BATCH_SIZE = 500


def download_bulk_csv() -> pd.DataFrame:
    """Download the bulk CSV zip and return all CA tract rows."""
    out = DATA_DIR / "grocery-gap-atlas-data-august-2024.csv.zip"
    if out.exists():
        print(f"  [cache] {out.name} already downloaded ({out.stat().st_size:,} bytes)")
    else:
        print(f"  Downloading {CSV_ZIP_URL} ...")
        resp = requests.get(CSV_ZIP_URL, timeout=120)
        resp.raise_for_status()
        out.write_bytes(resp.content)
        print(f"  Saved {out.stat().st_size:,} bytes")

    # Extract and read
    with zipfile.ZipFile(out) as zf:
        csv_names = [n for n in zf.namelist() if n.endswith(".csv")]
        if not csv_names:
            raise RuntimeError("No CSV found in zip")
        csv_name = csv_names[0]
        print(f"  Reading {csv_name} from zip ...")
        with zf.open(csv_name) as f:
            df = pd.read_csv(f, dtype=str)

    print(f"  Total rows in CSV: {len(df):,}")
    # Filter to CA tracts — GEOID column starts with '06'
    geoid_col = next(c for c in df.columns if c.lower() == "geoid")
    ca_df = df[df[geoid_col].str.startswith(CA_PREFIX)].copy()
    print(f"  CA tracts: {len(ca_df):,}")
    return ca_df


def download_parquets() -> None:
    """Download the parquet files for richer tract-level data."""
    for url, out_name in [
        (PARQUET_TRACT_URL, "gga_full_tract.parquet"),
        (PARQUET_CONC_URL, "gga_concentration.parquet"),
    ]:
        out = DATA_DIR / out_name
        if out.exists():
            print(f"  [cache] {out_name} already downloaded ({out.stat().st_size:,} bytes)")
            continue
        print(f"  Downloading {url} ...")
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        out.write_bytes(resp.content)
        print(f"  Saved {out.stat().st_size:,} bytes")


def fetch_tract_stores(geoid: str) -> list[dict]:
    """Fetch the store list for a single tract from the API."""
    url = STORES_API.format(geoid=geoid)
    resp = requests.get(url, timeout=30)
    if resp.status_code == 404:
        return []
    resp.raise_for_status()
    return resp.json()


def fetch_all_ca_stores(geoids: list[str]) -> pd.DataFrame:
    """Fetch store-level data for every CA tract via the API."""
    all_stores = []
    total = len(geoids)
    print(f"\n  Fetching stores for {total:,} CA tracts via API ...")

    for i, geoid in enumerate(geoids):
        try:
            stores = fetch_tract_stores(geoid)
            all_stores.extend(stores)
        except Exception as e:
            print(f"  [warn] {geoid}: {e}")

        if (i + 1) % BATCH_SIZE == 0 or (i + 1) == total:
            print(f"    Progress: {i + 1:,}/{total:,} tracts — {len(all_stores):,} stores so far")

        time.sleep(API_DELAY)

    if not all_stores:
        return pd.DataFrame()

    df = pd.DataFrame(all_stores)
    # Clean up column names
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    return df


def main() -> None:
    print("=" * 60)
    print("Grocery Gap Atlas — California Data Downloader")
    print("=" * 60)

    # --- Step 1: Download parquet files ---
    print("\n[1/3] Downloading parquet files ...")
    download_parquets()

    # --- Step 2: Download bulk CSV and filter to CA ---
    print("\n[2/3] Downloading bulk tract metrics CSV ...")
    ca_metrics = download_bulk_csv()

    metrics_out = DATA_DIR / "gga_tract_metrics.csv"
    ca_metrics.to_csv(metrics_out, index=False)
    print(f"  Written {len(ca_metrics):,} CA tract metrics to {metrics_out}")

    # Show what columns we have
    print(f"  Columns ({len(ca_metrics.columns)}):")
    for c in ca_metrics.columns:
        print(f"    - {c}")

    # --- Step 3: Fetch per-tract store data via API ---
    print("\n[3/3] Fetching per-tract store data ...")
    geoid_col = next(c for c in ca_metrics.columns if c.lower() == "geoid")
    ca_geoids = ca_metrics[geoid_col].tolist()

    stores_df = fetch_all_ca_stores(ca_geoids)

    stores_out = DATA_DIR / "gga_tract_stores.csv"
    if not stores_df.empty:
        stores_df.to_csv(stores_out, index=False)
        print(f"\n  Written {len(stores_df):,} store records to {stores_out}")
        print(f"  Unique tracts with stores: {stores_df['geoid'].nunique():,}")
        print(f"  Unique companies: {stores_df['company'].nunique():,}")
        print(f"\n  Top 15 parent companies by store count:")
        print(stores_df["parent_company"].value_counts().head(15).to_string())
    else:
        print("  No store data retrieved.")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  CA tract metrics:   {len(ca_metrics):,} tracts → {metrics_out}")
    print(f"  CA tract stores:    {len(stores_df):,} stores  → {stores_out}")
    print(f"  Parquet (all US):   {DATA_DIR / 'gga_full_tract.parquet'}")
    print(f"  Parquet (conc):     {DATA_DIR / 'gga_concentration.parquet'}")
    print("\nDone.")


if __name__ == "__main__":
    main()
