from abc import ABC, abstractmethod

class ISateliteImageRepository(ABC):
    @abstractmethod
    def get_image(self, x, y, z):
        raise NotImplementedError


class IModelRepository(ABC):
    @abstractmethod
    def predict(self, input_data):
        pass

    @abstractmethod
    def batch_predict(self, input_images):
        pass


class INeighborhoodRepository(ABC):
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


class IWeatherStationRepository(ABC):
    @abstractmethod
    def get_weather_stations(self) -> list[dict]:
        raise NotImplementedError
