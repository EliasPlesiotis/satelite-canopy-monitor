from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from pathlib import Path

from satelite_temperature_prediction.tile_api.repositories.cached_image_repository import CachedImageRepository
from satelite_temperature_prediction.tile_api.repositories.cached_model_repository import CachedModelRepository
from satelite_temperature_prediction.tile_api.repositories.google_earth_image_repository import GoogleEarthImageRepository
from satelite_temperature_prediction.tile_api.repositories.model_repository import KerasModelRepository
from satelite_temperature_prediction.tile_api.repositories.weather_station_repository import JsonWeatherStationRepository
from satelite_temperature_prediction.tile_api.repositories.meteoblue_heat_map_repository import MeteoblueHeatMapRepository
from satelite_temperature_prediction.tile_api.repositories.cached_heat_map_repository import CachedHeatMapRepository

from satelite_temperature_prediction.tile_api.application.tile_service import TileService
from satelite_temperature_prediction.tile_api.application.canopy_service import CanopyTileService
from satelite_temperature_prediction.tile_api.application.tile_service import TileService
from satelite_temperature_prediction.tile_api.application.spatial_query_engine import SpatialQueryEngine
from satelite_temperature_prediction.tile_api.application.tile_stitcher import TileStitcher
from satelite_temperature_prediction.tile_api.application.weather_station_service import WeatherStationService
from satelite_temperature_prediction.tile_api.application.heat_map_service import HeatMapService

from satelite_temperature_prediction.tile_api.handlers.zxy_handler import ZxyHandler
from satelite_temperature_prediction.tile_api.handlers.weather_station_handler import WeatherStationHandler
from satelite_temperature_prediction.tile_api.handlers.heat_map_handler import HeatMapHandler


app = FastAPI(title="Tile Server API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root directory of the workspace
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"

CANOPY_CACHE_DIR = Path("./.canopy_cache")
TILE_CACHE_DIR = Path("./.tile_cache")
HEATMAP_CACHE_DIR = Path("./.heatmap_cache")
MODEL_PATH = Path("./models/tree_mask_autoencoder_model.keras")


google_earth_repository = GoogleEarthImageRepository()
canopy_model_repository = KerasModelRepository(str(MODEL_PATH))
weather_station_repository = JsonWeatherStationRepository(DATA_DIR / "weather_stations_joined.json")
heat_map_repository = MeteoblueHeatMapRepository()

cached_google_earth_repository = CachedImageRepository(google_earth_repository, TILE_CACHE_DIR)
cached_canopy_model_repository = CachedModelRepository(canopy_model_repository, CANOPY_CACHE_DIR)
cached_heat_map_repository = CachedHeatMapRepository(heat_map_repository, HEATMAP_CACHE_DIR)

tile_sticher = TileStitcher(target_size=256)
spatial_tile_engine = SpatialQueryEngine(base_zoom=18)

canopy_service = CanopyTileService(spatial_tile_engine, tile_sticher, cached_google_earth_repository, cached_canopy_model_repository)
satelite_service = TileService(spatial_tile_engine, tile_sticher, cached_google_earth_repository)
weather_station_service = WeatherStationService(weather_station_repository)
heat_map_service = HeatMapService(cached_heat_map_repository)

zxy_handler = ZxyHandler(canopy_service, satelite_service)
zxy_router = APIRouter()
zxy_router.add_api_route("/v1/canopy/{z}/{x}/{y}.png", zxy_handler.get_canopy_tile, methods=["GET"])
zxy_router.add_api_route("/v1/satelite/{z}/{x}/{y}.png", zxy_handler.get_satelite_tile, methods=["GET"])
app.include_router(zxy_router)

weather_station_handler = WeatherStationHandler(weather_station_service)
weather_station_router = APIRouter()
weather_station_router.add_api_route("/v1/weather-stations", weather_station_handler.get_weather_stations, methods=["GET"])
app.include_router(weather_station_router)

heat_map_handler = HeatMapHandler(heat_map_service)
heat_map_router = APIRouter()
heat_map_router.add_api_route("/v1/heat-map/{city}/{time}.webp", heat_map_handler.get_heat_map, methods=["GET"])
app.include_router(heat_map_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
