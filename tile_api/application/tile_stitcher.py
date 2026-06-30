import io
from typing import Optional
from PIL import Image
from abc import ABC, abstractmethod

from satelite_temperature_prediction.tile_api.application.entities.tile import Tile

try:
    Resampling = Image.Resampling
except AttributeError:
    Resampling = Image

class ITileSticher(ABC):
    @abstractmethod
    def stitch(self, tiles: list[Tile], images: list[bytes], request_z: int, request_x: int, request_y: int) -> Optional[bytes]:
        raise NotImplementedError

class TileStitcher:
    def __init__(self, target_size: int = 256):
        self.target_size = target_size

    def stitch(self, tiles: list[Tile], images: list[bytes], request_z: int, request_x: int, request_y: int) -> Optional[bytes]:
        if not tiles or len(images) != len(tiles):
            return None

        first_tile = tiles[0]
        if first_tile.diff == 0:
            return images[0]

        if first_tile.diff is None:
            return None

        scale = first_tile.scale or 1
        sub_size = self.target_size // scale
        if sub_size < 1:
            return None

        if first_tile.diff > 0:
            return self._stitch_lower_zoom(tiles, images, scale, sub_size, request_x, request_y)

        return self._stitch_higher_zoom(first_tile, images[0], scale, sub_size, request_x, request_y)

    def _stitch_lower_zoom(
        self,
        tiles: list[Tile],
        images: list[bytes],
        scale: int,
        sub_size: int,
        request_x: int,
        request_y: int,
    ) -> Optional[bytes]:
        result_image = Image.new("RGBA", (self.target_size, self.target_size), (0, 0, 0, 0))
        base_x_start = request_x * scale
        base_y_start = request_y * scale
        found_any = False

        for tile, image_bytes in zip(tiles, images):
            if image_bytes is None:
                continue

            found_any = True
            with Image.open(io.BytesIO(image_bytes)) as tile_image:
                tile_image = tile_image.convert("RGBA")
                tile_image = tile_image.resize(
                    (sub_size, sub_size),
                    getattr(Resampling, "LANCZOS", getattr(Image, "ANTIALIAS", 1)),
                )
                paste_x = (tile.x - base_x_start) * sub_size
                paste_y = (tile.y - base_y_start) * sub_size
                result_image.paste(tile_image, (paste_x, paste_y))

        if not found_any:
            return None

        output = io.BytesIO()
        result_image.save(output, format="PNG")
        return output.getvalue()

    def _stitch_higher_zoom(
        self,
        tile: Tile,
        image_bytes: bytes,
        scale: int,
        sub_size: int,
        request_x: int,
        request_y: int,
    ) -> Optional[bytes]:
        if image_bytes is None:
            return None

        with Image.open(io.BytesIO(image_bytes)) as tile_image:
            tile_image = tile_image.convert("RGBA")
            offset_x = (request_x % scale) * sub_size
            offset_y = (request_y % scale) * sub_size
            cropped = tile_image.crop((offset_x, offset_y, offset_x + sub_size, offset_y + sub_size))
            result_image = cropped.resize(
                (self.target_size, self.target_size),
                getattr(Resampling, "LANCZOS", getattr(Image, "ANTIALIAS", 1)),
            )

            output = io.BytesIO()
            result_image.save(output, format="PNG")
            return output.getvalue()
