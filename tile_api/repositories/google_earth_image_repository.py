import urllib.request

from satelite_temperature_prediction.tile_api.application.repositories import ISateliteImageRepository


class GoogleEarthImageRepository(ISateliteImageRepository):
    def __init__(self, timeout: int = 10):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        self.timeout = timeout

    def get_image(self, x, y, z) -> bytes:
        url = f"https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
        headers = {"User-Agent": self.user_agent}
        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return response.read()
        except Exception as exc:
            print(f"Error downloading tile {z}/{x}/{y}: {exc}")
            raise RuntimeError(f"Error downloading tile {z}/{x}/{y}: {exc}")
