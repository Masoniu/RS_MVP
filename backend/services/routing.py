import httpx
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models


async def fetch_osm_data(lat: float, lon: float, radius_km: float, db: Session):
    cache_key = f"osm_{lat}_{lon}_{radius_km}"
    cached = db.query(models.OSMCache).filter(models.OSMCache.cache_key == cache_key).first()

    if cached and cached.expires_at > datetime.utcnow():
        return cached.response

    radius_m = radius_km * 1000
    query = f"""
    [out:json];
    (
      node["leisure"="park"](around:{radius_m},{lat},{lon});
      node["tourism"="museum"](around:{radius_m},{lat},{lon});
      node["amenity"~"cafe|restaurant"](around:{radius_m},{lat},{lon});
    );
    out center;
    """

    url = "https://overpass-api.de/api/interpreter"

    headers = {
        "User-Agent": "RouteSplitter_MVP/1.0 (Student Project)"
    }

    async with httpx.AsyncClient(headers=headers) as client:
        for attempt in range(2):
            try:
                response = await client.post(url, data={"data": query}, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                break
            except Exception:
                if attempt == 1:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Помилка з'єднання з Overpass API після двох спроб"
                    )

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

async def generate_route(budget: float, radius_km: float, lat: float, lon: float, db: Session):
    osm_data = await fetch_osm_data(lat, lon, radius_km, db)
    elements = osm_data.get("elements", [])

    parks = [el for el in elements if el.get("tags", {}).get("leisure") == "park"]
    museums = [el for el in elements if el.get("tags", {}).get("tourism") == "museum"]
    cafes = [el for el in elements if "amenity" in el.get("tags", {})]

    if not parks or not museums or not cafes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Недостатньо локацій різних категорій у цьому радіусі"
        )
    prices_db = {p.osm_id: p.entry_price for p in db.query(models.LocationPrice).all()}

    default_prices = {"park": 0.0, "museum": 100.0, "cafe": 250.0}

    def get_price(osm_node, category):
        osm_id = f"{osm_node.get('type', 'node')}/{osm_node['id']}"
        return prices_db.get(osm_id, default_prices[category])

    random.shuffle(parks)
    random.shuffle(museums)
    random.shuffle(cafes)

    for park in parks:
        p_price = get_price(park, "park")
        for museum in museums:
            m_price = get_price(museum, "museum")
            for cafe in cafes:
                c_price = get_price(cafe, "cafe")

                if (p_price + m_price + c_price) <= budget:
                    return [
                        {
                            "name": park.get("tags", {}).get("name", "Парк (без назви)"),
                            "lat": park.get("lat") or park.get("center", {}).get("lat"),
                            "lon": park.get("lon") or park.get("center", {}).get("lon"),
                            "price": p_price,
                            "category": "park"
                        },
                        {
                            "name": museum.get("tags", {}).get("name", "Музей (без назви)"),
                            "lat": museum.get("lat") or museum.get("center", {}).get("lat"),
                            "lon": museum.get("lon") or museum.get("center", {}).get("lon"),
                            "price": m_price,
                            "category": "museum"
                        },
                        {
                            "name": cafe.get("tags", {}).get("name", "Кафе (без назви)"),
                            "lat": cafe.get("lat") or cafe.get("center", {}).get("lat"),
                            "lon": cafe.get("lon") or cafe.get("center", {}).get("lon"),
                            "price": c_price,
                            "category": "cafe"
                        }
                    ]

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Неможливо згенерувати маршрут: не вистачає бюджету для знайдених локацій"
    )