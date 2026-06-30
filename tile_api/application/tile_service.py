from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed

from satelite_temperature_prediction.tile_api.application.entities.tile import Tile
from satelite_temperature_prediction.tile_api.application.repositories import ISateliteImageRepository
from satelite_temperature_prediction.tile_api.application.spatial_query_engine import ISpatialQueryEngine
from satelite_temperature_prediction.tile_api.application.tile_stitcher import TileStitcher

class ITileService(ABC):
    @abstractmethod
    def get_tile(self, z: int, x: int, y: int):
        raise NotImplementedError


class TileService(ITileService):
    def __init__(self, 
            spatial_query_engine: ISpatialQueryEngine, 
            tile_stitcher: TileStitcher, 
            repository: ISateliteImageRepository,
            max_workers: int = 2,
        ):
        self.spatial_query_engine = spatial_query_engine
        self.repository = repository
        self.stitcher = tile_stitcher
        self.max_workers = max_workers

    def get_tile(self, z: int, x: int, y: int):
        tiles = self.spatial_query_engine.get_tiles(z, x, y)
        if not tiles:
            return None

        images = [None] * len(tiles)
        max_failures = min(len(tiles), 20)
        failures = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.repository.get_image, tile.x, tile.y, tile.zoom): index
                for index, tile in enumerate(tiles)
            }
            for future in as_completed(futures):
                index = futures[future]
                try:
                    images[index] = future.result()
                except Exception:
                    failures += 1
                    if failures >= max_failures:
                        for pending_future in futures:
                            if not pending_future.done():
                                pending_future.cancel()
                        break

        return self.stitcher.stitch(tiles, images, z, x, y)
