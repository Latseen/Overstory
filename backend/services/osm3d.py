"""Fetch 3D building-part geometry from OpenStreetMap via the Overpass API.

OSM mappers encode tall buildings with `building:part` ways, each carrying
its own footprint polygon plus `height` / `min_height` / `building:levels`
tags.  Querying these gives us real, community-sourced setback geometry for
any building that OSM has modelled in 3D — no hardcoding required.

Returns an empty list when OSM has no part data (e.g. the Flatiron), which
signals the frontend to fall back to a plain extrusion of the main footprint.
"""

import httpx

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
_M_TO_FT = 3.28084
_LEVELS_TO_M = 3.0  # rough metres-per-floor when height tag is absent


def _parse_height(value: str | None) -> float | None:
    """Parse an OSM height tag like '443', '443 m', '1454 ft' → float metres."""
    if not value:
        return None
    v = value.strip()
    if v.endswith("ft"):
        try:
            return float(v[:-2].strip()) / _M_TO_FT
        except ValueError:
            return None
    # strip trailing 'm' or nothing
    try:
        return float(v.replace("m", "").strip())
    except ValueError:
        return None


def _way_to_part(element: dict) -> dict | None:
    """Convert an Overpass way element to a building-part dict, or None if unusable."""
    nodes = element.get("geometry", [])
    if len(nodes) < 3:
        return None

    tags = element.get("tags", {})

    # Build closed GeoJSON ring [[lng, lat], ...]
    coords = [[n["lon"], n["lat"]] for n in nodes]
    if coords[0] != coords[-1]:
        coords.append(coords[0])

    # Resolve height (top of section, metres)
    height_m = _parse_height(tags.get("height"))
    if height_m is None:
        levels = tags.get("building:levels") or tags.get("levels")
        try:
            height_m = float(levels) * _LEVELS_TO_M if levels else None
        except ValueError:
            height_m = None

    # Resolve min_height (bottom of section, metres)
    min_height_m = _parse_height(tags.get("min_height")) or 0.0

    return {
        "geometry": {"type": "Polygon", "coordinates": [coords]},
        "height_ft": round(height_m * _M_TO_FT, 1) if height_m is not None else None,
        "min_height_ft": round(min_height_m * _M_TO_FT, 1),
    }


async def fetch_building_parts(lat: float, lng: float) -> list[dict]:
    """Return OSM building:part sections within ~60 m of (lat, lng).

    Gracefully returns [] on any network or parse error so the frontend can
    fall back to a plain extrusion without crashing the request.
    """
    query = (
        f"[out:json][timeout:10];\n"
        f'(way["building:part"](around:60,{lat},{lng}););\n'
        f"out body geom;"
    )
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(OVERPASS_URL, content=query)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return []

    parts = []
    for element in data.get("elements", []):
        if element.get("type") != "way":
            continue
        part = _way_to_part(element)
        if part:
            parts.append(part)

    return parts
