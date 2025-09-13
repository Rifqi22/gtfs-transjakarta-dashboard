from fastapi import HTTPException, Query, APIRouter
from fastapi.responses import JSONResponse

from ..services.utils import ensure_gtfs_loaded, routes_basic_geojson
from ..constants.index import CACHE

router = APIRouter()

@router.get("/routes.json")
async def get_routes(url: str = Query(None), refresh: bool = Query(False)):

    try:
        await ensure_gtfs_loaded(url, refresh)
        if not refresh and "routes.json" in CACHE:
            return JSONResponse(content=CACHE["routes.json"])
        geo = routes_basic_geojson(CACHE["trips"], CACHE["routes"])
        CACHE["routes.json"] = geo
        return JSONResponse(content=geo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error: {str(e)}")