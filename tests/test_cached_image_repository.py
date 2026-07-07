import unittest
from unittest.mock import MagicMock, patch
from tile_api.repositories.cached_image_repository import CachedImageRepository

class TestCachedImageRepository(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()

    @patch('tile_api.repositories.cached_image_repository.Path')
    def test_init_creates_dir(self, mock_path_class):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        
        CachedImageRepository(self.mock_repo, "dummy/dir", 18)
        
        mock_path_class.assert_called_with("dummy/dir")
        mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('tile_api.repositories.cached_image_repository.Path')
    def test_get_image_wrong_zoom(self, mock_path_class):
        repo = CachedImageRepository(self.mock_repo, "dummy/dir", 18)
        with self.assertRaises(Exception):
            repo.get_image(10, 10, 10)

    @patch('tile_api.repositories.cached_image_repository.Path')
    def test_get_image_cache_hit(self, mock_path_class):
        mock_cache_dir = MagicMock()
        mock_path_class.return_value = mock_cache_dir
        
        mock_file_path = MagicMock()
        mock_cache_dir.__truediv__.return_value = mock_file_path
        
        mock_file_path.exists.return_value = True
        mock_file_path.read_bytes.return_value = b"cached_image_data"
        
        repo = CachedImageRepository(self.mock_repo, "dummy/dir", 18)
        
        result = repo.get_image(10, 20, 18)
        
        self.assertEqual(result, b"cached_image_data")
        mock_cache_dir.__truediv__.assert_called_with("18_10_20.png")
        self.mock_repo.get_image.assert_not_called()

    @patch('tile_api.repositories.cached_image_repository.Path')
    def test_get_image_cache_miss(self, mock_path_class):
        mock_cache_dir = MagicMock()
        mock_path_class.return_value = mock_cache_dir
        
        mock_file_path = MagicMock()
        mock_cache_dir.__truediv__.return_value = mock_file_path
        
        mock_file_path.exists.return_value = False
        
        self.mock_repo.get_image.return_value = b"new_image_data"
        
        repo = CachedImageRepository(self.mock_repo, "dummy/dir", 18)
        
        result = repo.get_image(10, 20, 18)
        
        self.assertEqual(result, b"new_image_data")
        mock_file_path.write_bytes.assert_called_once_with(b"new_image_data")
        self.mock_repo.get_image.assert_called_once_with(10, 20, 18)

    @patch('tile_api.repositories.cached_image_repository.Path')
    def test_get_image_cache_miss_none(self, mock_path_class):
        mock_cache_dir = MagicMock()
        mock_path_class.return_value = mock_cache_dir
        
        mock_file_path = MagicMock()
        mock_cache_dir.__truediv__.return_value = mock_file_path
        
        mock_file_path.exists.return_value = False
        
        self.mock_repo.get_image.return_value = None
        
        repo = CachedImageRepository(self.mock_repo, "dummy/dir", 18)
        
        result = repo.get_image(10, 20, 18)
        
        self.assertIsNone(result)
        mock_file_path.write_bytes.assert_not_called()

if __name__ == '__main__':
    unittest.main()
