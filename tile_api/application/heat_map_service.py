from tile_api.application.repositories import IHeatMapRepository

class HeatMapService:
    def __init__(self, heat_map_repository: IHeatMapRepository):
        self.heat_map_repository = heat_map_repository

    def get_heat_map(self, city: str, time: str) -> bytes | None:
        return self.heat_map_repository.get_heat_map(city, time)
