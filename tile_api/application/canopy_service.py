from abc import ABC, abstractmethod

from tile_api.application.repositories import ISateliteImageRepository
from tile_api.application.repositories import IModelRepository
from tile_api.application.spatial_query_engine import ISpatialQueryEngine
from tile_api.application.tile_stitcher import ITileSticher
from tile_api.application.worker_pool import IWorkerPool


class ICanopyTileService(ABC):
    @abstractmethod
    def get_tile(self, z: int, x: int, y: int):
        raise NotImplementedError

class CanopyTileService(ICanopyTileService):
    def __init__(
            self, 
            spatial_query_engine: ISpatialQueryEngine, 
            tile_stitcher: ITileSticher, 
            image_repository: ISateliteImageRepository, 
            model_repository: IModelRepository,
            worker_pool: IWorkerPool,
            max_workers: int = 4
        ):
        self.spatial_query_engine = spatial_query_engine
        self.tile_stitcher = tile_stitcher
        self.image_repository = image_repository
        self.model_repository = model_repository
        self.worker_pool = worker_pool
        self.max_workers = max_workers

    def get_tile(self, z: int, x: int, y: int):
        tiles = self.spatial_query_engine.get_tiles(z, x, y)
        if not tiles:
            return None

        max_failures = min(len(tiles), 20)
        images = self.worker_pool.fetch_images_parallel(tiles, self.image_repository.get_image, self.max_workers, max_failures)

        predictions = self.model_repository.batch_predict(images)

        return self.tile_stitcher.stitch(tiles, predictions, z, x, y)
