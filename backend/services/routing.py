import httpx
import random
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models
import asyncio

logger = logging.getLogger(__name__)


async def fetch_osm_data(lat: float, lon: float, radius_km: float, db: Session):
    """
    Fetch OSM data from Overpass API with caching and retry logic
    """
    # Validate coordinates
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невірні координати широти/довготи"
        )
    
    cache_key = f"osm_{lat}_{lon}_{radius_km}"
    cached = db.query(models.OSMCache).filter(models.OSMCache.cache_key == cache_key).first()

    if cached and cached.expires_at > datetime.utcnow():
        logger.info(f"Cache hit for {cache_key}")
        return cached.response

    radius_m = radius_km * 1000

    query = f"""
    [out:json][timeout:25];
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

    data = None
    last_error = None
    
    for attempt in range(3):
        try:
            logger.info(f"Attempt {attempt + 1}/3: Fetching OSM data for lat={lat}, lon={lon}, radius={radius_km}km")
            
            async with httpx.AsyncClient(headers=headers, timeout=35.0) as client:
                response = await client.post(url, data={"data": query})
                if response.status_code == 429:
                    wait_time = 2 ** (attempt + 2)
                    logger.warning(f"Rate limited by Overpass API. Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                data = response.json()

                if "elements" in data:
                    logger.info(f"Successfully fetched {len(data['elements'])} elements from Overpass API")
                    break
                else:
                    logger.warning("Overpass API returned empty elements array")
                    data = {"elements": []}
                    break
                    
        except asyncio.TimeoutError:
            last_error = "Request timeout (>35s)"
            logger.warning(f"Timeout on attempt {attempt + 1}: {last_error}")
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
        except httpx.HTTPStatusError as e:
            last_error = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            logger.warning(f"HTTP error on attempt {attempt + 1}: {last_error}")
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Error on attempt {attempt + 1}: {last_error}")
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
    
    if data is None:
        logger.error(f"Failed to fetch from Overpass API after 3 attempts. Last error: {last_error}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Сервіс Overpass API недоступний. Спробуйте ще раз пізніше. ({last_error[:50]})"
        )

    try:
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
        logger.info(f"Cached OSM data for key: {cache_key}")
    except Exception as e:
        logger.error(f"Failed to cache OSM data: {e}")
        db.rollback()

    return data

async def get_route_candidates(radius_km: float, lat: float, lon: float, db: Session):
    """
    Get location candidates for route planning
    """
    try:
        osm_data = await fetch_osm_data(lat, lon, radius_km, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_route_candidates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка при отриманні кандидатів маршруту"
        )
    
    elements = osm_data.get("elements", [])
    
    if not elements:
        logger.warning(f"No elements found for lat={lat}, lon={lon}, radius={radius_km}km")
        return {
            "parks": [],
            "museums": [],
            "cafes": []
        }

    prices_db = {p.osm_id: p.entry_price for p in db.query(models.LocationPrice).all()}
    default_prices = {"park": 0.0, "museum": 100.0, "cafe": 250.0}

    def get_price(osm_node, category):
        osm_id = f"{osm_node.get('type', 'node')}/{osm_node['id']}"
        return prices_db.get(osm_id, default_prices.get(category, 0.0))

    parks = []
    museums = []
    cafes = []

    for el in elements:
        try:
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
        except Exception as e:
            logger.warning(f"Error processing element {el.get('id')}: {e}")
            continue

    random.shuffle(parks)
    random.shuffle(museums)
    random.shuffle(cafes)

    return {
        "parks": parks[:20],
        "museums": museums[:20],
        "cafes": cafes[:20]
    }