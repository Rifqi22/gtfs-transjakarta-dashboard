from fastapi import HTTPException, Query, APIRouter
from fastapi.responses import JSONResponse

from ..services.utils import ensure_gtfs_loaded, shapes_to_geojson
from ..constants.index import CACHE

router = APIRouter()

@router.get("/shapes.geojson")
async def get_shapes(url: str = Query(None), refresh: bool = Query(False)):
    try:
        await ensure_gtfs_loaded(url, refresh)
        if not refresh and "shapes.geojson" in CACHE:
            return JSONResponse(content=CACHE["shapes.geojson"])
        geo = shapes_to_geojson(CACHE["shapes"])
        CACHE["shapes.geojson"] = geo
        return JSONResponse(content=geo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error: {str(e)}")
