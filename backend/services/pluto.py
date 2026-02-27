import httpx

PLUTO_URL = "https://data.cityofnewyork.us/resource/64uk-42ks.json"


async def get_building(bbl: str) -> dict:
    """
    Fetch building data from NYC PLUTO via the Socrata Open Data API.
    Raises ValueError if building not found.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(PLUTO_URL, params={"bbl": bbl})
        response.raise_for_status()
        data = response.json()

    if not data:
        raise ValueError(f"No PLUTO record found for BBL: {bbl}")

    b = data[0]
    return {
        "bbl": bbl,
        "address": b.get("address", ""),
        "borough": b.get("borough", ""),
        "zip_code": b.get("zipcode", ""),
        "year_built": _int(b.get("yearbuilt")),
        "num_floors": _float(b.get("numfloors")),
        "building_class": b.get("bldgclass", ""),
        "lot_area": _float(b.get("lotarea")),
        "bld_area": _float(b.get("bldgarea")),
        "zoning_district": b.get("zonedist1", ""),
        "land_use": b.get("landuse", ""),
        "owner_name": b.get("ownername", ""),
        "condo_flag": b.get("condono", "") != "",
    }


def _int(val) -> int | None:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _float(val) -> float | None:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
