from dataclasses import dataclass
from typing import Optional


@dataclass
class Tile:
    zoom: int
    x: int
    y: int
    diff: Optional[int] = None
    scale: Optional[int] = None
    target_size: int = 256
