from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from ..constants.index import CACHE, GTFS_PATH, TMP_DIR

router = APIRouter()

@router.get("/upload")
async def upload_gtfs(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        with open(GTFS_PATH, "wb") as f:
            f.write(content)
        CACHE.clear()
        os.makedirs(TMP_DIR, exist_ok=True)
        return {"status": "ok", "message": "GTFS uploaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error: {str(e)}")





