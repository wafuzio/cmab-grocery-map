#!/usr/bin/env python3
"""Apply official URLs and verified-chain status to known banner groups."""
import csv
from pathlib import Path

REPO = Path(__file__).parent
CSV_PATH = REPO / "data" / "ca_grocery_stores_audited.csv"

# Banner group -> official homepage.
# These are real chains whose official domain was confirmed via web search.
CHAIN_URLS = {
    "Primetime Nutrition": "https://www.nfiptn.com/",
    "Quickeroo": "https://www.nfiptn.com/",
    "Bel Air": "https://www.raleys.com/",
    "Foods Co": "https://www.foodsco.net/",
    "Pavilions": "https://www.pavilions.com/",
    "Ray's Food Place": "https://www.gorays.com/",
    "Chavez Supermarket": "https://www.chavezsuper.com/",
    "Bonfare Market": "https://www.bonfaremarkets.com/",
    "Redwood Market": "https://redwoodoil.com/",
    "Holiday Market": "https://shopholidaymarket.com/",
    "Sav Mor Foods": "https://www.shopsavmor.com/",
    "Andronico's": "https://www.andronicos.com/",
    "Beyond Food Mart": "https://beyondfoodmart.com/",
    "La Perla Tapatia": "https://www.lptmarkets.com/",
    "Sf Supermarket": "https://shunfatsupermarket.com/",
    "Rancho San Miguel Market": "https://ranchosanmiguelmarkets.com/",
    "Tower Market": "https://www.towermarket.com/",
}


def main() -> None:
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys()) if rows else []

    updated = 0
    for r in rows:
        group = (r.get("Normalized_Banner_Group") or "").strip()
        url = CHAIN_URLS.get(group)
        if not url:
            continue
        # Only overwrite empty or directory-looking URLs.
        current = (r.get("Web_URL") or "").strip()
        if current and not current.lower().startswith("http"):
            current = ""
        if current and current != url:
            continue
        r["Web_URL"] = url
        if r.get("Verified_Status") != "verified - active chain":
            r["Verified_Status"] = "verified - active chain"
            notes = (r.get("Verification_Notes") or "").strip()
            r["Verification_Notes"] = (
                (notes + "; verified via official chain website").strip("; ")
                if notes
                else "verified via official chain website"
            )
        updated += 1

    with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {updated} rows with official chain URLs.")


if __name__ == "__main__":
    main()
