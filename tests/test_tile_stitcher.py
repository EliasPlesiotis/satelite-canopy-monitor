import unittest
from unittest.mock import MagicMock
import io
from PIL import Image

from tile_api.application.tile_stitcher import TileStitcher
from tile_api.application.entities.tile import Tile

def create_dummy_png(color, size=(256, 256)):
    img = Image.new("RGBA", size, color)
    output = io.BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()

class TestTileStitcher(unittest.TestCase):
    def setUp(self):
        self.stitcher = TileStitcher(target_size=256)

    def test_stitch_no_tiles(self):
        result = self.stitcher.stitch([], [], 10, 0, 0)
        self.assertIsNone(result)

    def test_stitch_mismatched_lengths(self):
        tiles = [Tile(zoom=10, x=0, y=0, diff=0, scale=1)]
        result = self.stitcher.stitch(tiles, [], 10, 0, 0)
        self.assertIsNone(result)

    def test_stitch_diff_zero(self):
        tiles = [Tile(zoom=10, x=0, y=0, diff=0, scale=1)]
        image_bytes = b"dummy_image_data"
        result = self.stitcher.stitch(tiles, [image_bytes], 10, 0, 0)
        self.assertEqual(result, image_bytes)

    def test_stitch_diff_none(self):
        tiles = [Tile(zoom=10, x=0, y=0, diff=None, scale=1)]
        image_bytes = b"dummy_image_data"
        result = self.stitcher.stitch(tiles, [image_bytes], 10, 0, 0)
        self.assertIsNone(result)

    def test_stitch_sub_size_less_than_one(self):
        tile = Tile(zoom=10, x=0, y=0, diff=9, scale=512)
        result = self.stitcher.stitch([tile], [b"data"], 1, 0, 0)
        self.assertIsNone(result)

    def test_stitch_lower_zoom(self):
        tiles = [
            Tile(zoom=10, x=2, y=2, diff=1, scale=2),
            Tile(zoom=10, x=3, y=3, diff=1, scale=2)
        ]
        images = [
            create_dummy_png((255, 0, 0, 255)), 
            create_dummy_png((0, 0, 255, 255))
        ]
        
        result = self.stitcher.stitch(tiles, images, 9, 1, 1)
        
        self.assertIsNotNone(result)
        result_img = Image.open(io.BytesIO(result))
        self.assertEqual(result_img.size, (256, 256))
        
        pixels = result_img.load()
        self.assertEqual(pixels[0, 0], (255, 0, 0, 255))
        self.assertEqual(pixels[255, 255], (0, 0, 255, 255))
        self.assertEqual(pixels[255, 0], (0, 0, 0, 0))

    def test_stitch_lower_zoom_all_none(self):
        tiles = [Tile(zoom=10, x=2, y=2, diff=1, scale=2)]
        images = [None]
        result = self.stitcher.stitch(tiles, images, 9, 1, 1)
        self.assertIsNone(result)

    def test_stitch_higher_zoom(self):
        tile = Tile(zoom=10, x=1, y=1, diff=-1, scale=2)
        image_bytes = create_dummy_png((0, 255, 0, 255))
        
        result = self.stitcher.stitch([tile], [image_bytes], 11, 2, 2)
        
        self.assertIsNotNone(result)
        result_img = Image.open(io.BytesIO(result))
        self.assertEqual(result_img.size, (256, 256))
        
        pixels = result_img.load()
        self.assertEqual(pixels[128, 128], (0, 255, 0, 255))

    def test_stitch_higher_zoom_none_image(self):
        tile = Tile(zoom=10, x=1, y=1, diff=-1, scale=2)
        result = self.stitcher.stitch([tile], [None], 11, 2, 2)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
