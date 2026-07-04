import urllib.request
import urllib.parse
from tile_api.application.repositories import IHeatMapRepository

class MeteoblueHeatMapRepository(IHeatMapRepository):
    def __init__(self, timeout: int = 20):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        self.timeout = timeout
        self.base_url = "https://cityclimateapi.meteoblue.com/v2/heat-maps/"

    def get_heat_map(self, city: str, time: str) -> bytes | None:
        params = urllib.parse.urlencode({
            'city': city,
            'time': time
        })
        url = f"{self.base_url}?{params}"
        
        headers = {"User-Agent": self.user_agent}
        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return response.read()
        except Exception as exc:
            print(f"Error downloading heat map for {city} at {time}: {exc}")
            return None
