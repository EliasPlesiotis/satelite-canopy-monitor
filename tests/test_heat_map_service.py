import unittest
from unittest.mock import MagicMock
from tile_api.application.heat_map_service import HeatMapService
from tile_api.application.repositories import IHeatMapRepository

class TestHeatMapService(unittest.TestCase):
    def test_get_heat_map_returns_bytes(self):
        mock_repo = MagicMock(spec=IHeatMapRepository)
        mock_repo.get_heat_map.return_value = b"mocked_heat_map_data"
        service = HeatMapService(heat_map_repository=mock_repo)

        result = service.get_heat_map("TestCity", "2023-01-01T00:00:00Z")

        self.assertEqual(result, b"mocked_heat_map_data")
        mock_repo.get_heat_map.assert_called_once_with("TestCity", "2023-01-01T00:00:00Z")

    def test_get_heat_map_returns_none(self):
        mock_repo = MagicMock(spec=IHeatMapRepository)
        mock_repo.get_heat_map.return_value = None
        service = HeatMapService(heat_map_repository=mock_repo)

        result = service.get_heat_map("TestCity", "2023-01-01T00:00:00Z")

        self.assertIsNone(result)
        mock_repo.get_heat_map.assert_called_once_with("TestCity", "2023-01-01T00:00:00Z")

if __name__ == '__main__':
    unittest.main()
