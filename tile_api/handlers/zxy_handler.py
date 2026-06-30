from fastapi import HTTPException, Response
from satelite_temperature_prediction.tile_api.application.tile_service import ITileService
from satelite_temperature_prediction.tile_api.application.canopy_service import ICanopyTileService

class ZxyHandler:
    def __init__(self, canopy_service: ICanopyTileService, satelite_service: ITileService):
        self.canopy_service = canopy_service
        self.satelite_service = satelite_service

    async def get_canopy_tile(self, z: int, x: int, y: int):
        tile_data = self.canopy_service.get_tile(z, x, y)
        if tile_data:
            return Response(content=tile_data, media_type="image/png")
        raise HTTPException(status_code=404, detail="Tile not found")

    async def get_satelite_tile(self, z: int, x: int, y: int):
        tile_data = self.satelite_service.get_tile(z, x, y)
        if tile_data:
            return Response(content=tile_data, media_type="image/png")
        raise HTTPException(status_code=404, detail="Tile not found")
