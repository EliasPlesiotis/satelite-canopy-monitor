from pathlib import Path

from PIL import Image

from tile_api.application.repositories import ISateliteImageRepository

try:
    Resampling = Image.Resampling
except AttributeError:
    Resampling = Image


class CachedImageRepository(ISateliteImageRepository):
    def __init__(self, repository: ISateliteImageRepository, cache_dir: Path, base_zoom: int = 18):
        self.repository = repository
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.base_zoom = base_zoom

    def get_image(self, x: int, y: int, z: int):
        if z == self.base_zoom:
            return self._fetch_and_cache_base_tile(x, y)
        else:
            raise Exception("Only accepting z = " + self.base_zoom)


    def _fetch_and_cache_base_tile(self, x: int, y: int):
        base_tile_path = self.cache_dir / f"{self.base_zoom}_{x}_{y}.png"
        if base_tile_path.exists():
            return base_tile_path.read_bytes()

        tile_data = self.repository.get_image(x, y, self.base_zoom)
        if tile_data is None:
            return None

        base_tile_path.write_bytes(tile_data)
        return tile_data
