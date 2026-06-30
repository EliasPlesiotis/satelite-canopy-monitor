from abc import ABC, abstractmethod

from satelite_temperature_prediction.tile_api.application.repositories import INeighborhoodRepository


class INeighborhoodService(ABC):
    @abstractmethod
    def get_neighborhoods_geojson(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_neighborhood_list(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_neighborhoods_geojson_by_fids(self, fids: list[int]) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_neighborhood_temperatures_by_fids(self, fids: list[int]) -> dict:
        raise NotImplementedError


class NeighborhoodService(INeighborhoodService):
    def __init__(self, repository: INeighborhoodRepository):
        self.repository = repository

    def get_neighborhoods_geojson(self) -> dict:
        return self.repository.get_neighborhoods_geojson()

    def get_neighborhood_list(self) -> list[dict]:
        return self.repository.get_neighborhood_list()

    def get_neighborhoods_geojson_by_fids(self, fids: list[int]) -> dict:
        return self.repository.get_neighborhoods_geojson_by_fids(fids)

    def get_neighborhood_temperatures_by_fids(self, fids: list[int]) -> dict:
        return self.repository.get_neighborhood_temperatures_by_fids(fids)
