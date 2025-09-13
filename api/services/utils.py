from fastapi import HTTPException
import zipfile 
import io 
import csv 
from typing import Dict, List, Any 
import os 
import httpx

from ..constants.index import CACHE, GTFS_PATH

async def fetch_remote_zip(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.content


def read_csv_from_zip(z: zipfile.ZipFile, name: str) -> List[Dict[str, str]]:
    """Return list of rows (dict) for a csv file in the zip. Case-insensitive match."""
    target = None
    names = {n.lower(): n for n in z.namelist()}
    if name.lower() in names:
        target = names[name.lower()]
    else:
        for k, v in names.items():
            if k.endswith(name.lower()):
                target = v
                break
    if not target:
        return []
    with z.open(target) as fh:
        text = io.TextIOWrapper(fh, encoding="utf-8-sig")
        reader = csv.DictReader(text)
        return [row for row in reader]


def stops_to_geojson(rows: List[Dict[str, str]]) -> Dict:
    features = []
    for r in rows:
        try:
            lat = float(r.get("stop_lat") or 0)
            lon = float(r.get("stop_lon") or 0)
        except Exception:
            continue
        props = {k: v for k, v in r.items() if k not in ("stop_lat", "stop_lon")}
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": props,
        })
    return {"type": "FeatureCollection", "features": features}


def shapes_to_geojson(rows: List[Dict[str, str]]) -> Dict:
    shapes: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        sid = r.get("shape_id")
        if not sid:
            continue
        try:
            lat = float(r.get("shape_pt_lat"))
            lon = float(r.get("shape_pt_lon"))
        except Exception:
            continue
        seq = r.get("shape_pt_sequence") or "0"
        try:
            seqn = int(float(seq))
        except Exception:
            seqn = 0
        shapes.setdefault(sid, []).append({"seq": seqn, "coord": [lon, lat]})
    features = []
    for sid, pts in shapes.items():
        pts_sorted = sorted(pts, key=lambda x: x["seq"]) if pts else []
        coords = [p["coord"] for p in pts_sorted]
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {"shape_id": sid},
        })
    return {"type": "FeatureCollection", "features": features}


def routes_basic_geojson(trips: List[Dict[str, str]], routes: List[Dict[str, str]]) -> Dict:
    route_map: Dict[str, Dict[str, Any]] = {}
    for r in routes:
        rid = r.get("route_id")
        if not rid:
            continue
        route_map[rid] = {"route_id": rid, "props": r, "trips": []}
    for t in trips:
        rid = t.get("route_id")
        if not rid:
            continue
        if rid not in route_map:
            route_map[rid] = {"route_id": rid, "props": {}, "trips": []}
        route_map[rid]["trips"].append(t.get("trip_id"))
    features = []
    for rid, info in route_map.items():
        features.append({
            "type": "Feature",
            "geometry": None,
            "properties": {"route_id": rid, "trip_count": len(info["trips"]), **(info["props"] or {})},
        })
    return {"type": "FeatureCollection", "features": features}


async def ensure_gtfs_loaded(url: str = None, refresh: bool = False) -> None:
    """Make sure GTFS is downloaded + parsed once. Re-download if refresh=True."""
    if refresh:
        CACHE.clear()

    if "parsed" in CACHE and not refresh:
        return

    if url:
        content = await fetch_remote_zip(url)
        CACHE["zip_bytes"] = content
    elif not CACHE.get("zip_bytes") and os.path.exists(GTFS_PATH):
        with open(GTFS_PATH, "rb") as f:
            CACHE["zip_bytes"] = f.read()
    elif not CACHE.get("zip_bytes"):
        raise HTTPException(status_code=404, detail="No GTFS available. Upload or provide ?url=")

    with zipfile.ZipFile(io.BytesIO(CACHE["zip_bytes"]), "r") as z:
        CACHE["stops"] = read_csv_from_zip(z, "stops.txt")
        CACHE["shapes"] = read_csv_from_zip(z, "shapes.txt")
        CACHE["trips"] = read_csv_from_zip(z, "trips.txt")
        CACHE["routes"] = read_csv_from_zip(z, "routes.txt")
    CACHE["parsed"] = True

