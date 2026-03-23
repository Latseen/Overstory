import httpx

FOOTPRINT_URL = "https://data.cityofnewyork.us/resource/5zhs-2jue.json"


async def get_footprint(bbl: str) -> dict | None:
    """
    Fetch building footprint data from the NYC Building Footprints dataset.

    Returns:
      - height_ft:      LiDAR-derived roof height above ground in feet
      - footprint_area: Actual building polygon area in sq ft
      - the_geom:       GeoJSON polygon of the building footprint (WGS84)

    Returns None on any failure so callers can fall back gracefully.
    """
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                FOOTPRINT_URL,
                params={"base_bbl": bbl, "$limit": 1},
            )
            response.raise_for_status()
            data = response.json()

        if not data:
            return None

        b = data[0]
        height = _float(b.get("height_roof"))   # Socrata field name has underscore
        area = _float(b.get("shape_area"))
        geom = b.get("the_geom")  # GeoJSON polygon, WGS84
        bin_num = b.get("bin")    # Building Identification Number (NYC 3D Model key)
        doitt_id = b.get("doitt_id")  # Links building to NYC 3D Building Model dataset

        if height is not None and (height < 5 or height > 2000):
            height = None
        if area is not None and area < 100:
            area = None

        if height is None and area is None and geom is None:
            return None

        return {
            "height_ft": height,
            "footprint_area": area,
            "the_geom": geom,
            "bin": bin_num,
            "doitt_id": doitt_id,
        }

    except Exception:
        return None


def _float(val) -> float | None:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
