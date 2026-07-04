import hashlib
from pathlib import Path
from tile_api.application.repositories import IHeatMapRepository

class CachedHeatMapRepository(IHeatMapRepository):
    def __init__(self, repository: IHeatMapRepository, cache_dir: Path):
        self.repository = repository
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_heat_map(self, city: str, time: str) -> bytes | None:
        cache_key = hashlib.md5(f"{city}_{time}".encode('utf-8')).hexdigest()
        cache_path = self.cache_dir / f"heatmap_{cache_key}.img"

        if cache_path.exists():
            return cache_path.read_bytes()

        image_data = self.repository.get_heat_map(city, time)
        if image_data:
            cache_path.write_bytes(image_data)
        
        return image_data
