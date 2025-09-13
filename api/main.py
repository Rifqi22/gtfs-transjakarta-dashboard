# File: api/index.py
"""
FastAPI app to parse GTFS static zip and expose GeoJSON endpoints
Designed to be deployed on Vercel (Serverless Function):
- Upload a GTFS zip via POST /upload (multipart/form-data)
- Or provide a remote GTFS zip URL via query param ?url=
- Endpoints: /stops.geojson, /shapes.geojson, /routes.geojson (basic)

Notes:
- Keeps everything in memory (/tmp/gtfs.zip for the serverless invocation).
- Lightweight CSV parsing without heavy geospatial deps.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import routes, shapes, stops, upload


app = FastAPI()

# Allow CORS from anywhere for development; tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router, prefix="/api")
app.include_router(shapes.router, prefix="/api")
app.include_router(stops.router, prefix="/api")
app.include_router(upload.router, prefix="/api")


@app.get("/")
def test():
    return {"FASTAPI": "WORKING"}


@app.get("/health")
def health():
    return {"status": "ok"}
