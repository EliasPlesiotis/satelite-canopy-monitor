import unittest
from unittest.mock import MagicMock
from tile_api.application.worker_pool import WorkerPool

class TestWorkerPool(unittest.TestCase):
    def setUp(self):
        self.worker_pool = WorkerPool()
        self.mock_tile1 = MagicMock(x=1, y=2, zoom=10)
        self.mock_tile2 = MagicMock(x=3, y=4, zoom=10)
        self.tiles = [self.mock_tile1, self.mock_tile2]

    def test_fetch_images_parallel_success(self):
        def mock_fetch_func(x, y, zoom):
            return f"image_{x}_{y}_{zoom}"

        results = self.worker_pool.fetch_images_parallel(
            tiles=self.tiles,
            fetch_func=mock_fetch_func,
            max_workers=2,
            max_failures=2
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], "image_1_2_10")
        self.assertEqual(results[1], "image_3_4_10")

    def test_fetch_images_parallel_with_failures_below_max(self):
        def mock_fetch_func(x, y, zoom):
            if x == 1:
                raise Exception("Network error")
            return f"image_{x}_{y}_{zoom}"

        results = self.worker_pool.fetch_images_parallel(
            tiles=self.tiles,
            fetch_func=mock_fetch_func,
            max_workers=2,
            max_failures=2
        )

        self.assertEqual(len(results), 2)
        self.assertIsNone(results[0])
        self.assertEqual(results[1], "image_3_4_10")

    def test_fetch_images_parallel_with_failures_exceeding_max(self):
        def mock_fetch_func(x, y, zoom):
            raise Exception("Network error")

        results = self.worker_pool.fetch_images_parallel(
            tiles=self.tiles,
            fetch_func=mock_fetch_func,
            max_workers=2,
            max_failures=1
        )

        self.assertEqual(len(results), 2)
        self.assertIsNone(results[0])
        self.assertIsNone(results[1])

if __name__ == '__main__':
    unittest.main()
