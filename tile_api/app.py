from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from pathlib import Path

from satelite_temperature_prediction.tile_api.repositories.cached_image_repository import CachedImageRepository
from satelite_temperature_prediction.tile_api.repositories.cached_model_repository import CachedModelRepository
from satelite_temperature_prediction.tile_api.repositories.google_earth_image_repository import GoogleEarthImageRepository
from satelite_temperature_prediction.tile_api.repositories.model_repository import KerasModelRepository
from satelite_temperature_prediction.tile_api.repositories.neighborhood_repository import SqliteNeighborhoodRepository
from satelite_temperature_prediction.tile_api.repositories.weather_station_repository import JsonWeatherStationRepository

from satelite_temperature_prediction.tile_api.application.tile_service import TileService
from satelite_temperature_prediction.tile_api.application.canopy_service import CanopyTileService
from satelite_temperature_prediction.tile_api.application.neighborhood_service import NeighborhoodService
from satelite_temperature_prediction.tile_api.application.tile_service import TileService
from satelite_temperature_prediction.tile_api.application.spatial_query_engine import SpatialQueryEngine
from satelite_temperature_prediction.tile_api.application.tile_stitcher import TileStitcher
from satelite_temperature_prediction.tile_api.application.weather_station_service import WeatherStationService

from satelite_temperature_prediction.tile_api.handlers.zxy_handler import ZxyHandler
from satelite_temperature_prediction.tile_api.handlers.neighborhood_handler import NeighborhoodHandler
from satelite_temperature_prediction.tile_api.handlers.weather_station_handler import WeatherStationHandler


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
NEIGHBORHOODS_SQLITE = DATA_DIR / "neighborhood_athens.sqlite"

CANOPY_CACHE_DIR = Path("./.canopy_cache")
TILE_CACHE_DIR = Path("./.tile_cache")
MODEL_PATH = Path("./models/tree_mask_autoencoder_model.keras")

google_earth_repository = GoogleEarthImageRepository()
canopy_model_repository = KerasModelRepository(str(MODEL_PATH))
neighborhood_repository = SqliteNeighborhoodRepository(NEIGHBORHOODS_SQLITE)
weather_station_repository = JsonWeatherStationRepository(DATA_DIR / "weather_stations_joined.json")

cached_google_earth_repository = CachedImageRepository(google_earth_repository, TILE_CACHE_DIR)
cached_canopy_model_repository = CachedModelRepository(canopy_model_repository, CANOPY_CACHE_DIR)

tile_sticher = TileStitcher(target_size=256)
spatial_tile_engine = SpatialQueryEngine(base_zoom=18)

canopy_service = CanopyTileService(spatial_tile_engine, tile_sticher, cached_google_earth_repository, cached_canopy_model_repository)
satelite_service = TileService(spatial_tile_engine, tile_sticher, cached_google_earth_repository)
neighborhood_service = NeighborhoodService(neighborhood_repository)
weather_station_service = WeatherStationService(weather_station_repository)

zxy_handler = ZxyHandler(canopy_service, satelite_service)
zxy_router = APIRouter()
zxy_router.add_api_route("/v1/canopy/{z}/{x}/{y}.png", zxy_handler.get_canopy_tile, methods=["GET"])
zxy_router.add_api_route("/v1/satelite/{z}/{x}/{y}.png", zxy_handler.get_satelite_tile, methods=["GET"])
app.include_router(zxy_router)

neighborhood_handler = NeighborhoodHandler(neighborhood_service)
neighborhood_router = APIRouter()
neighborhood_router.add_api_route("/v1/neighborhood-list", neighborhood_handler.get_neighborhood_list, methods=["GET"])
neighborhood_router.add_api_route("/v1/neighborhoods", neighborhood_handler.post_neighborhoods_by_fids, methods=["POST"])
neighborhood_router.add_api_route("/v1/neighborhoods", neighborhood_handler.get_neighborhoods_geojson, methods=["GET"])
neighborhood_router.add_api_route("/v1/neighborhoods/timeseries", neighborhood_handler.post_neighborhood_temperatures, methods=["POST"])
app.include_router(neighborhood_router)

weather_station_handler = WeatherStationHandler(weather_station_service)
weather_station_router = APIRouter()
weather_station_router.add_api_route("/v1/weather-stations", weather_station_handler.get_weather_stations, methods=["GET"])
app.include_router(weather_station_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
