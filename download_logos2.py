"""Download logos for newly discovered CA grocery chains."""
import urllib.request
from pathlib import Path

LOGO_DIR = Path(__file__).parent / "logos"

RETAILERS = [
    ("El Super", "el-super.png", "https://www.elsupermarkets.com"),
    ("Vallarta Supermarket", "vallarta.png", "https://www.vallartasupermarkets.com"),
    ("Northgate Market", "northgate.png", "https://www.northgatemarket.com"),
    ("Gelson's Market", "gelsons.png", "https://www.gelsons.com"),
    ("Bonfare Market", "bonfare.png", "https://www.bonfaremarkets.com"),
    ("Holiday Market", "holiday-market.png", "https://www.holidaymarket.com"),
    ("Chavez Supermarket", "chavez.png", "https://www.chavezsupermarket.com"),
    ("Nugget Market", "nugget.png", "https://www.nuggetmarket.com"),
    ("Ray's Food Place", "rays-food.png", "https://www.raysfoodplace.com"),
    ("Verdugo Market", "verdugo.png", "https://www.verdugomarket.com"),
    ("99 Ranch Market", "ranch-99.png", "https://www.99ranch.com"),
    ("SF Supermarket", "sf-supermarket.png", "https://www.sfsupermarket.com"),
    ("Pavilions", "pavilions.png", "https://www.pavilions.com"),
    ("Jons Market", "jons-market.png", "https://www.jonsmarket.com"),
    ("Super King Market", "super-king.png", "https://www.superkingmarkets.com"),
    ("Mother's Market", "mothers-market.png", "https://www.mothersmarket.com"),
    ("Mother Earth Nutrition", "mother-earth.png", "https://www.motherearthnutrition.com"),
    ("Sav Mor Foods", "sav-mor.png", "https://www.savmorfoods.com"),
    ("Big Saver Foods", "big-saver.png", "https://www.bigsaverfoods.com"),
    ("Barons Market", "barons.png", "https://www.baronsmarket.com"),
    ("New Leaf Community Market", "new-leaf.png", "https://www.newleaf.com"),
    ("168 Market", "168-market.png", "https://www.168market.com"),
    ("Lunardi's Market", "lunardis.png", "https://www.lunardismarkets.com"),
    ("Mollie Stone's Market", "mollie-stones.png", "https://www.molliestones.com"),
    ("Andronico's", "andronicos.png", "https://www.andronicos.com"),
    ("Pak 'N Save", "pak-n-save.png", "https://www.paknsave.com"),
    ("Rancho San Miguel Market", "rancho-san-miguel.png", "https://www.ranchosanmiguel.com"),
    ("Quickeroo", "quickeroo.png", "https://www.quickeroo.com"),
    ("Baby Nutrition", "baby-nutrition.png", "https://www.babynutrition.com"),
    ("Basic Nutrition", "basic-nutrition.png", "https://www.basicnutrition.com"),
    ("First Step Nutrition", "first-step.png", "https://www.firststepnutrition.com"),
    ("Kids Nutricare", "kids-nutricare.png", "https://www.kidsnutricare.com"),
]

def download_favicon(website_url, filepath):
    domain = website_url.replace("https://www.", "").replace("https://", "").rstrip("/")
    google_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    try:
        req = urllib.request.Request(google_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if len(data) > 100:
                filepath.write_bytes(data)
                return True
    except Exception as e:
        print(f"  Google failed for {domain}: {e}")
    try:
        fav_url = f"https://www.{domain}/favicon.ico"
        req = urllib.request.Request(fav_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if len(data) > 100:
                filepath.write_bytes(data)
                return True
    except Exception as e:
        print(f"  Direct failed for {domain}: {e}")
    return False

def main():
    LOGO_DIR.mkdir(exist_ok=True)
    success, failed = 0, []
    for name, filename, website in RETAILERS:
        filepath = LOGO_DIR / filename
        if filepath.exists() and filepath.stat().st_size > 100:
            print(f"  SKIP  {name}")
            success += 1
            continue
        print(f"  ...   {name}")
        if download_favicon(website, filepath):
            print(f"  OK    {name} ({filepath.stat().st_size} bytes)")
            success += 1
        else:
            print(f"  FAIL  {name}")
            failed.append(name)
    print(f"\nDone: {success}/{len(RETAILERS)}")
    if failed:
        print(f"Failed: {', '.join(failed)}")

if __name__ == "__main__":
    main()
