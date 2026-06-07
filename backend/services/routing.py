import httpx
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models
import asyncio


async def fetch_osm_data(lat: float, lon: float, radius_km: float, db: Session):
    cache_key = f"osm_{lat}_{lon}_{radius_km}"
    cached = db.query(models.OSMCache).filter(models.OSMCache.cache_key == cache_key).first()

    if cached and cached.expires_at > datetime.utcnow():
        return cached.response

    radius_m = radius_km * 1000

    query = f"""
    [out:json];
    (
      nwr["leisure"="park"](around:{radius_m},{lat},{lon});
      nwr["tourism"="museum"](around:{radius_m},{lat},{lon});
      nwr["amenity"~"cafe|restaurant"](around:{radius_m},{lat},{lon});
    );
    out center tags;
    """

    url = "https://overpass-api.de/api/interpreter"
    headers = {
        "User-Agent": "RouteSplitter_MVP/1.0 (Student Project)"
    }

    async with httpx.AsyncClient(headers=headers) as client:
        for attempt in range(3):
            try:
                response = await client.post(url, data={"data": query}, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                break
            except Exception:
                if attempt == 2:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Помилка з'єднання з Overpass API після двох спроб"
                    )
                await asyncio.sleep(2 ** attempt)

    new_cache = models.OSMCache(
        cache_key=cache_key,
        response=data,
        lat=lat,
        lng=lon,
        radius_km=radius_km,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(new_cache)
    db.commit()

    return data

async def get_route_candidates(radius_km: float, lat: float, lon: float, db: Session):
    osm_data = await fetch_osm_data(lat, lon, radius_km, db)
    elements = osm_data.get("elements", [])

    prices_db = {p.osm_id: p.entry_price for p in db.query(models.LocationPrice).all()}
    default_prices = {"park": 0.0, "museum": 100.0, "cafe": 250.0}

    def get_price(osm_node, category):
        osm_id = f"{osm_node.get('type', 'node')}/{osm_node['id']}"
        return prices_db.get(osm_id, default_prices[category])

    parks = []
    museums = []
    cafes = []

    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name", tags.get("official_name", "Без назви"))

        obj_lat = el.get("lat") or el.get("center", {}).get("lat")
        obj_lon = el.get("lon") or el.get("center", {}).get("lon")
        osm_id = f"{el.get('type', 'node')}/{el.get('id')}"

        if not obj_lat or not obj_lon:
            continue

        item = {
            "osm_id": osm_id,
            "name": name,
            "lat": obj_lat,
            "lon": obj_lon
        }

        if tags.get("leisure") == "park":
            item["category"] = "park"
            item["price"] = get_price(el, "park")
            parks.append(item)

        elif tags.get("tourism") == "museum":
            item["category"] = "museum"
            item["price"] = get_price(el, "museum")
            museums.append(item)

        elif "amenity" in tags:
            item["category"] = "cafe"
            item["price"] = get_price(el, "cafe")
            cafes.append(item)

    random.shuffle(parks)
    random.shuffle(museums)
    random.shuffle(cafes)

    return {
        "parks": parks[:20],
        "museums": museums[:20],
        "cafes": cafes[:20]
    }