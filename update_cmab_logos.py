#!/usr/bin/env python3
"""Map existing and newly-downloaded retailer logos to banner groups in cmab_map.html."""

import ast
import csv
import json
import os
import re
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse, urljoin

REPO = Path(__file__).parent
HTML = REPO / "cmab_map.html"
MAP = REPO / "data" / "ca_grocer_map_data.json"
CSV = Path("/home/ubuntu/ca_grocery_stores_audited.csv")
LOGO_DIR = REPO / "logos"

DIRECTORY_DOMAINS = {
    "yelp.com", "mapquest.com", "facebook.com", "linkedin.com", "fns.usda.gov",
    "loc8nearme.com", "maps.apple.com", "waze.com", "opendata", "opengovus",
    "showmelocal.com", "merchantcircle.com", "yellowpages.com", "bbb.org",
    "tripadvisor.com", "ubereats.com", "doordash.com", "grubhub.com",
    "allmenus.com", "restaurantji.com", "zomato.com", "foursquare.com",
    "citysearch.com", "chamberofcommerce.com", "manta.com", "superlocalfirm.com",
    "localitybiz.com", "unilocal.com", "unilocal.com.br", "affordablehousing411.com",
    "hey-restaurants.com", "bizprofile.net", "food-us.org", "hub.biz", "res-menu.com",
    "foodnearme247.com", "edan.io", "lacartes.com", "b2byellowpages.com",
    "usarestaurants.info", "find-open-now.com", "storeopeninghours.com", "mylocaldir.com",
    "geodataindia.com", "2findlocal.com", "ezlocal.com",
}

DIRECTORY_SUFFIXES = [
    "yelp.com", "mapquest.com", "facebook.com", "linkedin.com", "fns.usda.gov",
    "loc8nearme.com", "maps.apple.com", "waze.com", "opendataca.com", "opengovus.com",
    "showmelocal.com", "merchantcircle.com", "yellowpages.com", "bbb.org",
    "tripadvisor.com", "ubereats.com", "doordash.com", "grubhub.com",
    "allmenus.com", "restaurantji.com", "zomato.com", "foursquare.com",
    "citysearch.com", "chamberofcommerce.com", "manta.com", "superlocalfirm.com",
    "localitybiz.com", "unilocal.com", "unilocal.com.br", "affordablehousing411.com",
    "hey-restaurants.com", "bizprofile.net", "food-us.org", "hub.biz", "res-menu.com",
    "foodnearme247.com", "edan.io", "lacartes.com", "b2byellowpages.com",
    "usarestaurants.info", "find-open-now.com", "storeopeninghours.com", "mylocaldir.com",
    "geodataindia.com", "2findlocal.com", "ezlocal.com",
]

GENERIC = set(
    "market markets supermarket supermarkets store stores mart marts "
    "mercado mercados supermercado marketplace "
    "inc llc corp corporation company and the of for in us ca com org net gov edu".split()
)

PROCESSOR_LOGOS = {
    "CMAB.svg", "crystal_creamery.png", "hollandia.png", "lucerne.png",
    "maola.png", "sarah_farms.png",
}

MANUAL = {
    "H Mart": ("h-mart.png", "https://www.hmart.com/"),
    "Ray's Food Place": ("rays-food.png", "https://www.gorays.com/"),
    "Chavez Supermarket": ("chavez-supermarket.png", "https://www.chavezsuper.com/"),
}


def canonical(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r"(?<=[a-zA-Z])'S\b", "'s", name)
    name = name.replace("’", "'")
    return name.strip()


def tokenize(s: str):
    if not s:
        return []
    s = s.lower().replace("'", "").replace("’", "").replace("&", "and")
    return [t for t in re.split(r"[^a-z0-9]+", s) if t]


def sig(tokens):
    return [t for t in tokens if t not in GENERIC]


def safe_filename(name: str) -> str:
    name = canonical(name).replace("'s", "s").replace("'", "")
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") + ".png"


def is_directory(url: str) -> bool:
    if not url:
        return True
    try:
        netloc = urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return True
    if not netloc:
        return True
    if netloc in DIRECTORY_DOMAINS:
        return True
    for suf in DIRECTORY_SUFFIXES:
        if netloc == suf or netloc.endswith("." + suf):
            return True
    return False


def domain_from_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        m = re.search(r"https?://(?:www\.)?([^/]+)", url, re.IGNORECASE)
        return m.group(1).lower() if m else ""


def domain_core(url: str):
    dom = domain_from_url(url)
    if not dom:
        return ""
    # strip TLD; keep second-level if present (e.g., 'jonsmarketplace' from 'jonsmarketplace.com')
    parts = dom.split(".")
    return parts[0] if parts else ""


def domain_matches_banner(d_core: str, banner: str) -> bool:
    if not d_core:
        return False
    d_norm = re.sub(r"[^a-z0-9]", "", d_core.lower())
    b_norm = re.sub(r"[^a-z0-9]", "", canonical(banner).lower())
    if not d_norm or not b_norm:
        return False
    if d_norm == b_norm:
        return True
    if d_norm in b_norm or b_norm in d_norm:
        return True
    if d_norm.startswith(b_norm) or d_norm.endswith(b_norm):
        return True
    if b_norm.startswith(d_norm) or b_norm.endswith(d_norm):
        return True
    common = 0
    for a, b in zip(d_norm, b_norm):
        if a == b:
            common += 1
        else:
            break
    min_len = min(len(d_norm), len(b_norm))
    if common >= 6 and common >= min_len * 0.6:
        return True
    # significant token overlap
    d_tokens = set(sig(tokenize(d_core)))
    b_tokens = set(sig(tokenize(banner)))
    if d_tokens and b_tokens and (d_tokens & b_tokens):
        return True
    return False


def parse_known_logos():
    known = {}
    for path in [REPO / "download_logos.py", REPO / "download_logos2.py"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        m = re.search(r"RETAILERS\s*=\s*(\[.*?\n\])", text, re.DOTALL)
        if not m:
            continue
        try:
            lst = ast.literal_eval(m.group(1))
        except Exception as e:
            print(f"  warn: could not parse {path}: {e}")
            continue
        for name, filename, website in lst:
            cname = canonical(name)
            if cname and cname not in known:
                known[cname] = (filename, website)
    known.update({canonical(k): v for k, v in MANUAL.items()})
    return known


def extract_js_object(html: str, name: str):
    pattern = r"  const " + re.escape(name) + r" = \{(.*?)^  \};"
    m = re.search(pattern, html, re.DOTALL | re.MULTILINE)
    if not m:
        return {}
    block = m.group(1)
    entries = {}
    key_value = re.compile(
        r"^\s*(?:"
        r"'([^']+)'|"
        r'"([^"]+)"|'
        r"([A-Za-z0-9_]+)"
        r")\s*:\s*"
        r"(?:'([^']*)'|\"([^\"]*)\")"
        r"\s*,?\s*$"
    )
    for line in block.split("\n"):
        line = line.rstrip(",")
        if not line.strip() or line.strip().startswith("//"):
            continue
        m2 = key_value.match(line)
        if m2:
            k = m2.group(1) or m2.group(2) or m2.group(3)
            v = m2.group(4) if m2.group(4) is not None else m2.group(5)
            entries[canonical(k)] = v.strip()
    return entries


def _fetch_url(req, timeout):
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def download_favicon(website_url: str, filepath: Path) -> bool:
    domain = domain_from_url(website_url)
    if not domain:
        return False
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

    # Google favicon service (high-res)
    google_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    try:
        data = _fetch_url(urllib.request.Request(google_url, headers=headers), 15)
        if len(data) > 100:
            filepath.write_bytes(data)
            return True
    except Exception as e:
        print(f"    google favicon failed for {domain}: {e}")

    # Direct /favicon.ico
    try:
        fav_url = f"https://www.{domain}/favicon.ico"
        data = _fetch_url(urllib.request.Request(fav_url, headers=headers), 15)
        if len(data) > 100:
            filepath.write_bytes(data)
            return True
    except Exception as e:
        print(f"    direct favicon failed for {domain}: {e}")

    # Parse homepage HTML for rel=icon / apple-touch-icon
    try:
        home_url = f"https://www.{domain}/"
        req = urllib.request.Request(home_url, headers=headers)
        html = _fetch_url(req, 15).decode("utf-8", "ignore")
        for rel in ["apple-touch-icon", "icon", "shortcut icon"]:
            pattern = r'<link[^>]*rel=["\'][^"\']*' + re.escape(rel) + r'[^"\']*["\'][^>]*href=["\']([^"\']+)'
            m = re.search(pattern, html, re.IGNORECASE)
            if m:
                icon_url = urljoin(home_url, m.group(1))
                data = _fetch_url(urllib.request.Request(icon_url, headers=headers), 15)
                if len(data) > 100:
                    filepath.write_bytes(data)
                    return True
                break
    except Exception as e:
        print(f"    html favicon failed for {domain}: {e}")

    return False


def find_best_logo_file(banner: str, files: list) -> tuple:
    orig = set(tokenize(banner))
    sig_orig = set(sig(tokenize(banner)))
    best = None
    best_score = 0
    for f in files:
        stem = Path(f).stem
        f_orig = set(tokenize(stem))
        f_sig = set(sig(tokenize(stem)))
        if f_orig == orig:
            score = 100 + len(f_orig)
        elif f_sig and f_sig.issubset(sig_orig):
            score = len(f_sig) * 10 + (1 if f_sig == sig_orig else 0)
        elif f_orig and f_orig.issubset(orig):
            score = len(f_orig) * 5
        else:
            continue
        if score > best_score:
            best_score = score
            best = f
    return best, best_score


def normalize_url(u: str):
    u = u.strip()
    if not u:
        return None
    if not re.match(r"^https?://", u, re.IGNORECASE):
        u = "https://" + u
    try:
        p = urlparse(u)
        if p.scheme not in ("http", "https"):
            return None
        netloc = p.netloc.lower().replace("www.", "")
        if not netloc:
            return None
        return f"{p.scheme}://{netloc}"
    except Exception:
        return None


def main():
    print("Loading map data and CSV...")
    map_data = json.loads(MAP.read_text(encoding="utf-8"))
    stores = map_data.get("stores", [])
    banner_counts = Counter(s.get("banner_group") or s.get("banner") or "Misc." for s in stores)
    banner_counts = Counter({canonical(k): v for k, v in banner_counts.items()})

    # Gather CSV official URLs by canonical banner group (dedupe to domain level)
    csv_rows = []
    if CSV.exists():
        with CSV.open(newline="", encoding="utf-8") as f:
            csv_rows = list(csv.DictReader(f))
    group_urls = defaultdict(list)
    for r in csv_rows:
        bg = canonical(r.get("Normalized_Banner_Group", ""))
        url = r.get("Web_URL", "").strip()
        if bg and url:
            nu = normalize_url(url)
            if nu and not is_directory(nu):
                group_urls[bg].append(nu)

    known = parse_known_logos()
    print(f"  banner groups in map data: {len(banner_counts)}")

    # Start from existing HTML mapping, keeping only files that exist
    html = HTML.read_text(encoding="utf-8")
    existing_logos = extract_js_object(html, "RETAILER_LOGOS")
    existing_borders = extract_js_object(html, "RETAILER_BORDER")
    print(f"  existing RETAILER_LOGOS keys: {len(existing_logos)}")

    logo_files = [f for f in os.listdir(LOGO_DIR) if f not in PROCESSOR_LOGOS]

    retailer_logos = {}
    # 1. Preserve existing RETAILER_LOGOS entries whose file exists
    for k, v in existing_logos.items():
        fn = v.replace("logos/", "")
        if (LOGO_DIR / fn).exists():
            retailer_logos[k] = v

    # 2. Use known logo filenames as a base for chain names that appear in data
    for cname, (filename, url) in known.items():
        if cname in retailer_logos:
            continue
        if (LOGO_DIR / filename).exists() and cname in banner_counts:
            retailer_logos[cname] = f"logos/{filename}"

    # 3. Fuzzy-match any remaining logo files to banner groups
    for banner in list(banner_counts.keys()):
        if banner in retailer_logos:
            continue
        best, score = find_best_logo_file(banner, logo_files)
        if best and score >= 5:
            retailer_logos[banner] = f"logos/{best}"

    # 4. Identify missing logos for chains with official URLs and download them
    def candidates_for(banner: str, count: int):
        """Return an ordered list of (filename, url) candidates to try."""
        out = []
        # Manual overrides first
        if banner in MANUAL:
            out.append(MANUAL[banner])

        # CSV-derived official URL next
        urls = group_urls.get(banner, [])
        if urls:
            top_url, top_count = Counter(urls).most_common(1)[0]
            if top_count >= max(2, count * 0.25) or domain_matches_banner(domain_core(top_url), banner):
                filename = known.get(banner, (None, None))[0] or safe_filename(banner)
                out.append((filename, top_url))

        # Known list from download_logos scripts
        if banner in known:
            out.append(known[banner])

        return out

    def try_candidate(banner: str, filename: str, url: str) -> bool:
        if not filename or not url:
            return False
        if ".." in filename or "/" in filename:
            return False
        if is_directory(url):
            return False
        filepath = LOGO_DIR / filename
        if filepath.exists():
            retailer_logos[banner] = f"logos/{filename}"
            return True
        print(f"  downloading {banner}: {domain_from_url(url)} -> {filename}")
        if download_favicon(url, filepath):
            retailer_logos[banner] = f"logos/{filename}"
            return True
        return False

    downloads_to_run = []
    for banner, count in banner_counts.items():
        if banner in retailer_logos:
            continue
        if count < 3:
            continue
        for filename, url in candidates_for(banner, count):
            if try_candidate(banner, filename, url):
                break
        if banner not in retailer_logos:
            print(f"  no logo for {banner} (count {count})")

    # 5. After downloads, re-run fuzzy matching for any still-unmapped files
    logo_files = [f for f in os.listdir(LOGO_DIR) if f not in PROCESSOR_LOGOS]
    for banner in list(banner_counts.keys()):
        if banner in retailer_logos:
            continue
        best, score = find_best_logo_file(banner, logo_files)
        if best and score >= 5:
            retailer_logos[banner] = f"logos/{best}"

    # 6. Build RETAILER_BORDER colors: keep existing, add generated for new logos
    retailer_borders = dict(existing_borders)
    for k in retailer_logos.keys():
        if k not in retailer_borders:
            h = (hash(k) % 360)
            s = 70
            l = 45
            retailer_borders[k] = f"border:4px solid hsl({h}, {s}%, {l}%)"

    # Ensure Misc. stays last and present (but has no logo)
    if "Misc." not in retailer_borders:
        retailer_borders["Misc."] = "border:4px solid #94a3b8;"
    if "Misc." not in retailer_logos:
        retailer_logos.pop("Misc.", None)

    print(f"  final RETAILER_LOGOS entries: {len(retailer_logos)}")
    print(f"  final RETAILER_BORDER entries: {len(retailer_borders)}")

    # 7. Replace objects in HTML
    def js_key(k):
        if re.match(r"^[A-Za-z0-9_]+$", k):
            return k
        return json.dumps(k)

    def sort_entries(d, misc_last=True):
        keys = sorted(d.keys(), key=lambda x: x.lower())
        if misc_last and "Misc." in keys:
            keys.remove("Misc.")
            keys.append("Misc.")
        return keys

    logos_block = "\n".join(
        f"    {js_key(k)}: '{retailer_logos[k]}'," for k in sort_entries(retailer_logos)
    )
    borders_block = "\n".join(
        f"    {js_key(k)}: '{retailer_borders[k]}'," for k in sort_entries(retailer_borders)
    )

    new_logos_obj = "  const RETAILER_LOGOS = {\n" + logos_block + "\n  };"
    new_borders_obj = "  const RETAILER_BORDER = {\n" + borders_block + "\n  };"

    html_new = re.sub(
        r"  const RETAILER_LOGOS = \{.*?^  \};",
        new_logos_obj,
        html,
        flags=re.DOTALL | re.MULTILINE,
    )
    html_new = re.sub(
        r"  const RETAILER_BORDER = \{.*?^  \};",
        new_borders_obj,
        html_new,
        flags=re.DOTALL | re.MULTILINE,
    )

    if html_new != html:
        HTML.write_text(html_new, encoding="utf-8")
        print("  updated cmab_map.html")
    else:
        print("  no HTML changes needed")

    # Summary
    unmapped = [b for b, c in banner_counts.items() if b not in retailer_logos and c >= 3]
    print(f"  unmapped banner groups with >=3 stores: {len(unmapped)}")
    if unmapped:
        print("    " + ", ".join(sorted(unmapped)[:20]))


if __name__ == "__main__":
    main()
