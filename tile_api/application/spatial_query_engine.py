from abc import ABC, abstractmethod

from satelite_temperature_prediction.tile_api.application.entities.tile import Tile

class ISpatialQueryEngine(ABC):
    @abstractmethod
    def get_tiles(self, z: int, x: int, y: int) -> list[Tile]:
        raise NotImplementedError
    
class SpatialQueryEngine(ISpatialQueryEngine):
    def __init__(self, base_zoom):
        self.base_zoom = base_zoom

    def get_tiles(self, z: int, x: int, y: int) -> list[Tile]:
        if z == self.base_zoom:
            return [Tile(self.base_zoom, x, y, diff=0, scale=1)]
        elif z < self.base_zoom:
            return self._generate_lower_zoom_tile(z, x, y)
        else:
            return self._generate_higher_zoom_tile(z, x, y)

    def _generate_lower_zoom_tile(self, z: int, x: int, y: int):
        tiles = []
        diff = self.base_zoom - z
        scale = 2 ** diff
        target_size = 256
        sub_size = target_size // scale

        if sub_size < 1:
            return []

        base_x_start = x * scale
        base_y_start = y * scale

        for i in range(scale):
            for j in range(scale):
                bx = base_x_start + i
                by = base_y_start + j
                tiles.append(Tile(self.base_zoom, bx, by, diff=diff, scale=scale))
        
        return tiles

    def _generate_higher_zoom_tile(self, z: int, x: int, y: int):
        diff = self.base_zoom - z
        scale = 2 ** abs(diff)
        bx = x // scale
        by = y // scale

        return [Tile(self.base_zoom, bx, by, diff=diff, scale=scale)]
    