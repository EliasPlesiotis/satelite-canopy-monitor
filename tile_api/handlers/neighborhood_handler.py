from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from satelite_temperature_prediction.tile_api.application.neighborhood_service import INeighborhoodService

class NeighborhoodIdsRequest(BaseModel):
    fids: list[int]

class NeighborhoodHandler:
    def __init__(self, neighborhood_service: INeighborhoodService):
        self.neighborhood_service = neighborhood_service

    async def get_neighborhood_list(self):
        try:
            neighborhood_list = self.neighborhood_service.get_neighborhood_list()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Unable to load neighborhood list: {exc}")

        return JSONResponse(content=neighborhood_list)

    async def post_neighborhoods_by_fids(self, request: NeighborhoodIdsRequest):
        try:
            geojson = self.neighborhood_service.get_neighborhoods_geojson_by_fids(request.fids)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Unable to load selected neighborhoods: {exc}")

        return JSONResponse(content=geojson)

    async def get_neighborhoods_geojson(self):
        try:
            geojson = self.neighborhood_service.get_neighborhoods_geojson()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Unable to load neighborhoods: {exc}")

        return JSONResponse(content=geojson)

    async def post_neighborhood_temperatures(self, request: NeighborhoodIdsRequest):
        try:
            timeseries = self.neighborhood_service.get_neighborhood_temperatures_by_fids(request.fids)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Unable to load neighborhood temperatures: {exc}")

        return JSONResponse(content=timeseries)
