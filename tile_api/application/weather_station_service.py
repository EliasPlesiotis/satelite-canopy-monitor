from abc import ABC, abstractmethod

from satelite_temperature_prediction.tile_api.application.repositories import IWeatherStationRepository


class IWeatherStationService(ABC):
    @abstractmethod
    def get_weather_stations(self) -> list[dict]:
        raise NotImplementedError


class WeatherStationService(IWeatherStationService):
    def __init__(self, repository: IWeatherStationRepository):
        self.repository = repository

    def get_weather_stations(self) -> list[dict]:
        return self.repository.get_weather_stations()
