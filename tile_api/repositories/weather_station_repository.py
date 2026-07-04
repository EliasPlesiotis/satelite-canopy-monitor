import json
from pathlib import Path
from typing import Any

from satelite_temperature_prediction.tile_api.application.repositories import IWeatherStationRepository


class JsonWeatherStationRepository(IWeatherStationRepository):
    def __init__(self, data_path: str | Path | None = None):
        self.data_path = Path(data_path or Path(__file__).resolve().parents[3] / "data" / "weather_stations_joined.json")

    def get_weather_stations(self) -> list[dict[str, Any]]:
        with self.data_path.open("r", encoding="utf-8") as handle:
            stations = json.load(handle)

        temperature_stations = []
        for key, station in stations.items():
            try:
                station_values = list(station['values'].values())
                if len(station_values) == 0 and station_values[0]['temp_out']:
                    continue

                temperature = station_values[0]['temp_out']

                temperature_stations.append({
                    'temperature': temperature,
                    'latitude': station.get('loc_point_lat'),
                    'longitude': station.get('loc_point_lng'),
                    'name': station.get('loc_reg_name_gr'),
                })
            except Exception as e:
                print('Error while retrieving weather station:', e)
                continue

        return temperature_stations
