import unittest
from unittest.mock import MagicMock

from tile_api.application.tile_service import TileService

class TestTileService(unittest.TestCase):
    def setUp(self):
        self.mock_spatial_query_engine = MagicMock()
        self.mock_tile_stitcher = MagicMock()
        self.mock_repository = MagicMock()
        self.mock_worker_pool = MagicMock()
        
        self.tile_service = TileService(
            spatial_query_engine=self.mock_spatial_query_engine,
            tile_stitcher=self.mock_tile_stitcher,
            repository=self.mock_repository,
            worker_pool=self.mock_worker_pool,
            max_workers=2
        )

    def test_get_tile_success(self):
        z, x, y = 10, 100, 200
        mock_tiles = [
            {'z': 18, 'x': 25000, 'y': 50000},
            {'z': 18, 'x': 25001, 'y': 50000}
        ]
        mock_images = ["image1", "image2"]
        mock_stitched_image = "stitched_image"
        
        self.mock_spatial_query_engine.get_tiles.return_value = mock_tiles
        self.mock_worker_pool.fetch_images_parallel.return_value = mock_images
        self.mock_tile_stitcher.stitch.return_value = mock_stitched_image

        result = self.tile_service.get_tile(z, x, y)

        self.assertEqual(result, mock_stitched_image)
        
        self.mock_spatial_query_engine.get_tiles.assert_called_once_with(z, x, y)
        self.mock_worker_pool.fetch_images_parallel.assert_called_once_with(
            mock_tiles, 
            self.mock_repository.get_image, 
            2,
            2
        )
        self.mock_tile_stitcher.stitch.assert_called_once_with(
            mock_tiles, 
            mock_images, 
            z, x, y
        )

    def test_get_tile_no_tiles(self):
        z, x, y = 10, 100, 200
        self.mock_spatial_query_engine.get_tiles.return_value = []

        result = self.tile_service.get_tile(z, x, y)

        self.assertIsNone(result)
        self.mock_spatial_query_engine.get_tiles.assert_called_once_with(z, x, y)
        self.mock_worker_pool.fetch_images_parallel.assert_not_called()
        self.mock_tile_stitcher.stitch.assert_not_called()

if __name__ == '__main__':
    unittest.main()
