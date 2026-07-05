from abc import ABC, abstractmethod

from tile_api.application.repositories import ISateliteImageRepository
from tile_api.application.spatial_query_engine import ISpatialQueryEngine
from tile_api.application.tile_stitcher import TileStitcher
from tile_api.application.worker_pool import IWorkerPool

class ITileService(ABC):
    @abstractmethod
    def get_tile(self, z: int, x: int, y: int):
        raise NotImplementedError


class TileService(ITileService):
    def __init__(self, 
            spatial_query_engine: ISpatialQueryEngine, 
            tile_stitcher: TileStitcher, 
            repository: ISateliteImageRepository,
            worker_pool: IWorkerPool,
            max_workers: int = 2,
        ):
        self.spatial_query_engine = spatial_query_engine
        self.repository = repository
        self.stitcher = tile_stitcher
        self.worker_pool = worker_pool
        self.max_workers = max_workers

    def get_tile(self, z: int, x: int, y: int):
        tiles = self.spatial_query_engine.get_tiles(z, x, y)
        if not tiles:
            return None

        max_failures = min(len(tiles), 20)
        images = self.worker_pool.fetch_images_parallel(tiles, self.repository.get_image, self.max_workers, max_failures)

        return self.stitcher.stitch(tiles, images, z, x, y)
