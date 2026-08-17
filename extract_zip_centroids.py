import json

print("Loading boundary file...")
with open("gopuff_delivery_zip_boundaries_simplified.json") as f:
    gj = json.load(f)

centroids = {}
for feat in gj["features"]:
    props = feat["properties"]
    z = props.get("ZCTA5CE10", "")
    lat = props.get("INTPTLAT10", "")
    lon = props.get("INTPTLON10", "")
    if z and lat and lon:
        centroids[z] = [float(lat), float(lon)]

print(f"Extracted {len(centroids)} zip centroids")
with open("gopuff_zip_centroids.json", "w") as f:
    json.dump(centroids, f)
print("Saved gopuff_zip_centroids.json")
