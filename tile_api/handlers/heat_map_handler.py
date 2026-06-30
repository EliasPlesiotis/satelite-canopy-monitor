from fastapi import HTTPException, Response
from satelite_temperature_prediction.tile_api.application.heat_map_service import HeatMapService

class HeatMapHandler:
    def __init__(self, heat_map_service: HeatMapService):
        self.heat_map_service = heat_map_service

    async def get_heat_map(self, city: str, time: str):
        image_data = self.heat_map_service.get_heat_map(city, time)
        if image_data:
            return Response(content=image_data, media_type="image/jpeg")
        raise HTTPException(status_code=404, detail="Heat map not found")
