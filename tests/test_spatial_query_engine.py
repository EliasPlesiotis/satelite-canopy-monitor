import unittest

from tile_api.application.spatial_query_engine import SpatialQueryEngine
from tile_api.application.entities.tile import Tile

class TestSpatialQueryEngine(unittest.TestCase):
    def test_get_tiles_same_zoom(self):
        # Arrange
        base_zoom = 10
        engine = SpatialQueryEngine(base_zoom=base_zoom)

        # Act
        tiles = engine.get_tiles(z=10, x=5, y=5)

        # Assert
        self.assertEqual(len(tiles), 1)
        self.assertEqual(tiles[0], Tile(zoom=10, x=5, y=5, diff=0, scale=1))

    def test_get_tiles_lower_zoom(self):
        # Arrange
        base_zoom = 10
        engine = SpatialQueryEngine(base_zoom=base_zoom)

        # Act
        # Requesting z=9, meaning we need 2^1 * 2^1 = 4 base tiles (z=10) to cover the z=9 tile
        # diff = 10 - 9 = 1, scale = 2^1 = 2
        # If z=9, x=5, y=5, base_x_start = 10, base_y_start = 10
        tiles = engine.get_tiles(z=9, x=5, y=5)

        # Assert
        self.assertEqual(len(tiles), 4)
        expected_tiles = [
            Tile(zoom=10, x=10, y=10, diff=1, scale=2),
            Tile(zoom=10, x=10, y=11, diff=1, scale=2),
            Tile(zoom=10, x=11, y=10, diff=1, scale=2),
            Tile(zoom=10, x=11, y=11, diff=1, scale=2),
        ]
        
        for expected_tile in expected_tiles:
            self.assertIn(expected_tile, tiles)

    def test_get_tiles_much_lower_zoom(self):
        # Arrange
        base_zoom = 10
        engine = SpatialQueryEngine(base_zoom=base_zoom)

        # Act
        # z=8, diff=2, scale=4, expected tiles = 16
        tiles = engine.get_tiles(z=8, x=5, y=5)

        # Assert
        self.assertEqual(len(tiles), 16)
        # Check a few bounding box ones
        self.assertIn(Tile(zoom=10, x=20, y=20, diff=2, scale=4), tiles)
        self.assertIn(Tile(zoom=10, x=23, y=23, diff=2, scale=4), tiles)

    def test_get_tiles_lower_zoom_too_small(self):
        # Arrange
        base_zoom = 20
        engine = SpatialQueryEngine(base_zoom=base_zoom)

        # Act
        # If diff > 8, scale > 256. sub_size < 1. Should return []
        tiles = engine.get_tiles(z=11, x=0, y=0)

        # Assert
        self.assertEqual(len(tiles), 0)

    def test_get_tiles_higher_zoom(self):
        # Arrange
        base_zoom = 10
        engine = SpatialQueryEngine(base_zoom=base_zoom)

        # Act
        # Requesting z=11, base_zoom = 10. diff = -1, scale = 2
        # Requested x=11, y=11. base x = 11 // 2 = 5, y = 11 // 2 = 5
        tiles = engine.get_tiles(z=11, x=11, y=11)

        # Assert
        self.assertEqual(len(tiles), 1)
        self.assertEqual(tiles[0], Tile(zoom=10, x=5, y=5, diff=-1, scale=2))

    def test_get_tiles_much_higher_zoom(self):
        # Arrange
        base_zoom = 10
        engine = SpatialQueryEngine(base_zoom=base_zoom)

        # Act
        # z=12, base_zoom = 10, diff = -2, scale = 4
        # requested x=21, y=23. base x = 21 // 4 = 5, y = 23 // 4 = 5
        tiles = engine.get_tiles(z=12, x=21, y=23)

        # Assert
        self.assertEqual(len(tiles), 1)
        self.assertEqual(tiles[0], Tile(zoom=10, x=5, y=5, diff=-2, scale=4))

if __name__ == '__main__':
    unittest.main()
