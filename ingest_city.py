#!/usr/bin/env python3
"""Global City Spawner for Restaurant Radar ($199/mo City License).

Queries OpenStreetMap Overpass API for restaurants, cafes, bars, food trucks,
and fuel stops within any city bounding box worldwide, normalizes records with
source attribution and published opening_hours, and emits a white-label city
pack (JSON + bilingual EN/ES config).
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def build_overpass_query(south: float, west: float, north: float, east: float) -> str:
    bbox = f"{south},{west},{north},{east}"
    return f"""
[out:json][timeout:45];
(
  node["amenity"~"^(restaurant|cafe|bar|fast_food|fuel)$"]({bbox});
  way["amenity"~"^(restaurant|cafe|bar|fast_food|fuel)$"]({bbox});
);
out center tags;
""".strip()


def normalize_elements(elements: list[dict], city_name: str, country_code: str = "US") -> dict:
    venues = []
    fuel_stops = []
    with_hours = 0
    for el in elements:
        tags = el.get("tags") or {}
        name = tags.get("name")
        if not name:
            continue
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        amenity = tags.get("amenity", "restaurant")
        hours = tags.get("opening_hours")
        if hours:
            with_hours += 1
        rec = {
            "osm_id": f"{el.get('type', 'node')}/{el.get('id')}",
            "name": name,
            "category": "fuel" if amenity == "fuel" else amenity,
            "city": city_name,
            "country": country_code,
            "lat": round(float(lat), 6),
            "lon": round(float(lon), 6),
            "phone": tags.get("phone") or tags.get("contact:phone") or "",
            "website": tags.get("website") or tags.get("contact:website") or "",
            "opening_hours": hours or "",
            "hours_verified": bool(hours),
            "source": "OpenStreetMap contributors (ODbL)",
        }
        if amenity == "fuel":
            fuel_stops.append(rec)
        else:
            venues.append(rec)
    return {
        "schema_version": "radar-city-pack-1.0",
        "city": city_name,
        "country": country_code,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "bilingual_labels": {
            "en": {
                "headline": f"{city_name} Live Venue & Fuel Radar",
                "subhead": f"{len(venues)} dining venues and {len(fuel_stops)} fuel stops on one map.",
                "cta": "Open Live Map",
            },
            "es": {
                "headline": f"Radar en Vivo de Restaurantes y Gasolineras en {city_name}",
                "subhead": f"{len(venues)} restaurantes/cafes y {len(fuel_stops)} gasolineras en un solo mapa.",
                "cta": "Abrir Mapa en Vivo",
            },
        },
        "counts": {
            "venues": len(venues),
            "fuel_stops": len(fuel_stops),
            "with_published_hours": with_hours,
        },
        "venues": venues,
        "fuel_stops": fuel_stops,
    }


def run_selftest() -> int:
    sample_elements = [
        {
            "type": "node",
            "id": 1001,
            "lat": 38.2544,
            "lon": -104.6091,
            "tags": {
                "name": "El Pueblo Taqueria",
                "amenity": "restaurant",
                "opening_hours": "Mo-Su 08:00-21:00",
                "phone": "+1-719-555-0101",
            },
        },
        {
            "type": "node",
            "id": 1002,
            "lat": 38.2610,
            "lon": -104.6150,
            "tags": {
                "name": "I-25 Travel Plaza",
                "amenity": "fuel",
            },
        },
    ]
    pack = normalize_elements(sample_elements, "Pueblo, CO", "US")
    assert pack["counts"]["venues"] == 1
    assert pack["counts"]["fuel_stops"] == 1
    assert pack["counts"]["with_published_hours"] == 1
    assert "es" in pack["bilingual_labels"] and "en" in pack["bilingual_labels"]
    assert pack["venues"][0]["hours_verified"] is True
    assert pack["fuel_stops"][0]["hours_verified"] is False
    print("INGEST_CITY_SELFTEST: PASS (venues=1, fuel=1, bilingual=en+es, source=OSM)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Global City Spawner for Restaurant Radar")
    ap.add_argument("--city", default="Pueblo, CO", help="City display name")
    ap.add_argument("--country", default="US", help="ISO country code")
    ap.add_argument("--bbox", help="south,west,north,east bounding box")
    ap.add_argument("--out", help="Output JSON path")
    ap.add_argument("--selftest", action="store_true", help="Run deterministic offline self-test")
    args = ap.parse_args()

    if args.selftest:
        return run_selftest()

    if not args.bbox:
        ap.error("--bbox south,west,north,east is required unless --selftest is used")

    parts = [float(x.strip()) for x in args.bbox.split(",")]
    if len(parts) != 4:
        ap.error("--bbox must have 4 comma-separated floats: south,west,north,east")

    q = build_overpass_query(*parts)
    data = urllib.parse.urlencode({"data": q}).encode("utf-8")
    req = urllib.request.Request(OVERPASS_URL, data=data, headers={"User-Agent": "RestaurantRadarCitySpawner/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    pack = normalize_elements(raw.get("elements", []), args.city, args.country)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(pack, f, indent=2, ensure_ascii=False)
        print(f"Wrote {args.out}: {pack['counts']}")
    else:
        print(json.dumps(pack["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
