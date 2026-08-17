"""Download logos for CA grocery retailers.

Uses Google's favicon service as primary source (high-res), falling
back to direct favicon fetch from each brand's website.
"""
import urllib.request
import os
from pathlib import Path

LOGO_DIR = Path(__file__).parent / "logos"

# (banner_group_name, filename, website_url)
RETAILERS = [
    ("Smart & Final", "smart-final.png", "https://www.smartandfinal.com"),
    ("Sprouts Farmers Market", "sprouts.png", "https://www.sprouts.com"),
    ("Costco Wholesale", "costco.png", "https://www.costco.com"),
    ("Trader Joe's", "trader-joes.png", "https://www.traderjoes.com"),
    ("Aldi", "aldi.png", "https://www.aldi.us"),
    ("Food 4 Less", "food-4-less.png", "https://www.food4less.com"),
    ("Stater Bros. Markets", "stater-bros.png", "https://www.staterbros.com"),
    ("Whole Foods Market", "whole-foods.png", "https://www.wholefoodsmarket.com"),
    ("Mother's Nutritional Center", "mothers-nutritional.png", "https://www.mothersmarket.com"),
    ("Superior Grocers", "superior-grocers.png", "https://www.superiorgrocers.com"),
    ("Lucky", "lucky.png", "https://www.luckysupermarkets.com"),
    ("Raley's", "raleys.png", "https://www.raleys.com"),
    ("Ralphs", "ralphs.png", "https://www.ralphs.com"),
    ("Food Maxx", "food-maxx.png", "https://www.foodmaxx.com"),
    ("Ralphs Fresh Fare", "ralphs-fresh-fare.png", "https://www.ralphs.com"),
    ("Primetime Nutrition", "primetime-nutrition.png", "https://www.primetimenutrition.com"),
    ("Walmart Neighborhood Market", "walmart-neighborhood.png", "https://www.walmart.com"),
    ("Save Mart", "save-mart.png", "https://www.savemart.com"),
    ("Sam's Club", "sams-club.png", "https://www.samsclub.com"),
    ("Winco Foods", "winco.png", "https://www.wincofoods.com"),
    ("Bel Air", "bel-air.png", "https://www.belairmarket.com"),
    ("Jacksons Food Stores", "jacksons.png", "https://www.jacksons.com"),
    ("Ralphs Grocery Company", "ralphs-grocery.png", "https://www.ralphs.com"),
    ("Walmart Supercenter", "walmart-supercenter.png", "https://www.walmart.com"),
    ("Redwood Market", "redwood-market.png", "https://www.redwoodmarket.com"),
    ("Foods Co", "foods-co.png", "https://www.foodsco.com"),
    ("Cardenas", "cardenas.png", "https://www.cardenasmarkets.com"),
    ("Target Store", "target.png", "https://www.target.com"),
    ("Nob Hill Foods", "nob-hill.png", "https://www.raleys.com"),
    ("Seafood City Supermarket", "seafood-city.png", "https://www.seafoodcity.com"),
    ("Primetime", "primetime.png", "https://www.primetimenutrition.com"),
    ("Target", "target-2.png", "https://www.target.com"),
    ("Family Market", "family-market.png", "https://www.familymarket.com"),
    ("Prime Time Nutrition", "prime-time-nutrition.png", "https://www.primetimenutrition.com"),
    ("Grocery Outlet", "grocery-outlet.png", "https://www.groceryoutlet.com"),
    ("Island Pacific Supermarket", "island-pacific.png", "https://www.islandpacificmarket.com"),
    ("Village Market", "village-market.png", "https://www.villagemarket.com"),
    ("Bristol Farms", "bristol-farms.png", "https://www.bristolfarms.com"),
]

def download_favicon(website_url: str, filepath: Path) -> bool:
    """Try Google's favicon service first, then direct favicon."""
    domain = website_url.replace("https://www.", "").replace("https://", "").rstrip("/")

    # Google favicon service - returns 32px favicon
    google_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    # Try Google first (higher res with sz=128)
    try:
        req = urllib.request.Request(google_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if len(data) > 100:  # Real image, not empty
                filepath.write_bytes(data)
                return True
    except Exception as e:
        print(f"  Google failed for {domain}: {e}")

    # Try direct favicon.ico
    try:
        fav_url = f"https://www.{domain}/favicon.ico"
        req = urllib.request.Request(fav_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if len(data) > 100:
                filepath.write_bytes(data)
                return True
    except Exception as e:
        print(f"  Direct favicon failed for {domain}: {e}")

    return False


def main():
    LOGO_DIR.mkdir(exist_ok=True)
    success = 0
    failed = []

    for name, filename, website in RETAILERS:
        filepath = LOGO_DIR / filename
        if filepath.exists() and filepath.stat().st_size > 100:
            print(f"  SKIP  {name} (already exists)")
            success += 1
            continue

        print(f"  ...   {name}")
        if download_favicon(website, filepath):
            print(f"  OK    {name} -> {filename} ({filepath.stat().st_size} bytes)")
            success += 1
        else:
            print(f"  FAIL  {name}")
            failed.append(name)

    print(f"\nDone: {success}/{len(RETAILERS)} succeeded")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
