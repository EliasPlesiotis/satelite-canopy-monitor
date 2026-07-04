from fastapi import HTTPException
from fastapi.responses import JSONResponse

from tile_api.application.weather_station_service import IWeatherStationService


class WeatherStationHandler:
    def __init__(self, weather_station_service: IWeatherStationService):
        self.weather_station_service = weather_station_service

    async def get_weather_stations(self):
        try:
            stations = self.weather_station_service.get_weather_stations()
        except Exception as exc:
            print(exc)
            raise HTTPException(status_code=500, detail=f"Unable to load weather stations: {exc}") from exc

        return JSONResponse(content=stations, headers={"Cache-Control": "public, max-age=600"})
