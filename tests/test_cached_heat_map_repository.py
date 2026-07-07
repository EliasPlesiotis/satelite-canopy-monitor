import unittest
from unittest.mock import MagicMock, patch
import hashlib
from tile_api.repositories.cached_heat_map_repository import CachedHeatMapRepository

class TestCachedHeatMapRepository(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()

    @patch('tile_api.repositories.cached_heat_map_repository.Path')
    def test_init_creates_dir(self, mock_path_class):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        
        CachedHeatMapRepository(self.mock_repo, "dummy/dir")
        
        mock_path_class.assert_called_with("dummy/dir")
        mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('tile_api.repositories.cached_heat_map_repository.Path')
    def test_get_heat_map_cache_hit(self, mock_path_class):
        mock_cache_dir = MagicMock()
        mock_path_class.return_value = mock_cache_dir
        
        mock_file_path = MagicMock()
        mock_cache_dir.__truediv__.return_value = mock_file_path
        
        mock_file_path.exists.return_value = True
        mock_file_path.read_bytes.return_value = b"cached_heatmap_data"
        
        repo = CachedHeatMapRepository(self.mock_repo, "dummy/dir")
        
        result = repo.get_heat_map("London", "2023-01-01T12:00:00Z")
        
        self.assertEqual(result, b"cached_heatmap_data")
        
        cache_key = hashlib.md5(b"London_2023-01-01T12:00:00Z").hexdigest()
        mock_cache_dir.__truediv__.assert_called_with(f"heatmap_{cache_key}.img")
        self.mock_repo.get_heat_map.assert_not_called()

    @patch('tile_api.repositories.cached_heat_map_repository.Path')
    def test_get_heat_map_cache_miss(self, mock_path_class):
        mock_cache_dir = MagicMock()
        mock_path_class.return_value = mock_cache_dir
        
        mock_file_path = MagicMock()
        mock_cache_dir.__truediv__.return_value = mock_file_path
        
        mock_file_path.exists.return_value = False
        
        self.mock_repo.get_heat_map.return_value = b"new_heatmap_data"
        
        repo = CachedHeatMapRepository(self.mock_repo, "dummy/dir")
        
        result = repo.get_heat_map("London", "2023-01-01T12:00:00Z")
        
        self.assertEqual(result, b"new_heatmap_data")
        
        cache_key = hashlib.md5(b"London_2023-01-01T12:00:00Z").hexdigest()
        mock_cache_dir.__truediv__.assert_called_with(f"heatmap_{cache_key}.img")
        self.mock_repo.get_heat_map.assert_called_once_with("London", "2023-01-01T12:00:00Z")
        mock_file_path.write_bytes.assert_called_once_with(b"new_heatmap_data")

    @patch('tile_api.repositories.cached_heat_map_repository.Path')
    def test_get_heat_map_cache_miss_none(self, mock_path_class):
        mock_cache_dir = MagicMock()
        mock_path_class.return_value = mock_cache_dir
        
        mock_file_path = MagicMock()
        mock_cache_dir.__truediv__.return_value = mock_file_path
        
        mock_file_path.exists.return_value = False
        
        self.mock_repo.get_heat_map.return_value = None
        
        repo = CachedHeatMapRepository(self.mock_repo, "dummy/dir")
        
        result = repo.get_heat_map("London", "2023-01-01T12:00:00Z")
        
        self.assertIsNone(result)
        mock_file_path.write_bytes.assert_not_called()

if __name__ == '__main__':
    unittest.main()
