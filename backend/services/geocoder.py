import httpx

GEOSEARCH_URL = "https://geosearch.planninglabs.nyc/v2/search"


async def geocode_address(address: str) -> dict:
    """
    Geocode an NYC address using NYC Planning Labs GeoSearch.
    Returns lat, lng, BBL, and normalized address.
    Raises ValueError if address cannot be found.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(GEOSEARCH_URL, params={"text": address, "size": 1})
        response.raise_for_status()
        data = response.json()

    features = data.get("features", [])
    if not features:
        raise ValueError(f"Address not found: {address}")

    feature = features[0]
    props = feature["properties"]
    coords = feature["geometry"]["coordinates"]  # [lng, lat]

    bbl = props.get("addendum", {}).get("pad", {}).get("bbl")
    if not bbl:
        raise ValueError(f"No BBL found for address: {address}")

    return {
        "address": props.get("label", address),
        "lng": coords[0],
        "lat": coords[1],
        "bbl": bbl,
        "borough": props.get("borough", ""),
    }
