from fastapi import HTTPException, Query, APIRouter
from fastapi.responses import JSONResponse

from ..services.utils import ensure_gtfs_loaded, stops_to_geojson
from ..constants.index import CACHE

router = APIRouter()

@router.get("/stops.geojson")
async def get_stops(url: str = Query(None), refresh: bool = Query(False)):
    try:
            await ensure_gtfs_loaded(url, refresh)
            if not refresh and "stops.geojson" in CACHE:
                return JSONResponse(content=CACHE["stops.geojson"])
            geo = stops_to_geojson(CACHE["stops"])
            CACHE["stops.geojson"] = geo
            return JSONResponse(content=geo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error: {str(e)}")