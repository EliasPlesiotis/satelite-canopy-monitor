import unittest
from unittest.mock import MagicMock, patch
import hashlib
from tile_api.repositories.cached_model_repository import CachedModelRepository

class TestCachedModelRepository(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()

    @patch('tile_api.repositories.cached_model_repository.Path')
    def test_init_creates_dir(self, mock_path_class):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        
        CachedModelRepository(self.mock_repo, "dummy/dir")
        
        mock_path_class.assert_called_with("dummy/dir")
        mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('tile_api.repositories.cached_model_repository.Path')
    def test_predict(self, mock_path_class):
        mock_cache_dir = MagicMock()
        mock_path_class.return_value = mock_cache_dir
        
        repo = CachedModelRepository(self.mock_repo, "dummy/dir")
        
        # Mock batch_predict for predict
        repo.batch_predict = MagicMock(return_value=[b"prediction"])
        
        result = repo.predict(b"input_data")
        
        self.assertEqual(result, b"prediction")
        repo.batch_predict.assert_called_once_with([b"input_data"])

    @patch('tile_api.repositories.cached_model_repository.Path')
    def test_batch_predict_cache_hit(self, mock_path_class):
        mock_cache_dir = MagicMock()
        mock_path_class.return_value = mock_cache_dir
        
        mock_file_path = MagicMock()
        mock_cache_dir.__truediv__.return_value = mock_file_path
        
        mock_file_path.exists.return_value = True
        mock_file_path.read_bytes.return_value = b"cached_prediction"
        
        repo = CachedModelRepository(self.mock_repo, "dummy/dir")
        
        result = repo.batch_predict([b"input_data"])
        
        self.assertEqual(result, [b"cached_prediction"])
        
        cache_key = hashlib.sha256(b"input_data").hexdigest()
        mock_cache_dir.__truediv__.assert_called_with(f"{cache_key}.png")
        self.mock_repo.batch_predict.assert_not_called()

    @patch('tile_api.repositories.cached_model_repository.Path')
    def test_batch_predict_cache_miss(self, mock_path_class):
        mock_cache_dir = MagicMock()
        mock_path_class.return_value = mock_cache_dir
        
        mock_file_path = MagicMock()
        mock_cache_dir.__truediv__.return_value = mock_file_path
        mock_file_path.exists.return_value = False
        
        self.mock_repo.batch_predict.return_value = [b"new_prediction"]
        
        repo = CachedModelRepository(self.mock_repo, "dummy/dir")
        
        result = repo.batch_predict([b"input_data"])
        
        self.assertEqual(result, [b"new_prediction"])
        
        cache_key = hashlib.sha256(b"input_data").hexdigest()
        mock_cache_dir.__truediv__.assert_called_with(f"{cache_key}.png")
        self.mock_repo.batch_predict.assert_called_once_with([b"input_data"])
        mock_file_path.write_bytes.assert_called_once_with(b"new_prediction")

    @patch('tile_api.repositories.cached_model_repository.Path')
    def test_batch_predict_mixed(self, mock_path_class):
        mock_cache_dir = MagicMock()
        mock_path_class.return_value = mock_cache_dir
        
        repo = CachedModelRepository(self.mock_repo, "dummy/dir")
        
        hit_path = MagicMock()
        hit_path.exists.return_value = True
        hit_path.read_bytes.return_value = b"hit_prediction"
        
        miss_path = MagicMock()
        miss_path.exists.return_value = False
        
        key_hit = hashlib.sha256(b"hit_input").hexdigest()
        key_miss = hashlib.sha256(b"miss_input").hexdigest()
        
        def truediv_impl(name):
            if name == f"{key_hit}.png":
                return hit_path
            elif name == f"{key_miss}.png":
                return miss_path
            return MagicMock()

        mock_cache_dir.__truediv__.side_effect = truediv_impl
        
        self.mock_repo.batch_predict.return_value = [b"new_prediction"]
        
        result = repo.batch_predict([b"hit_input", None, b"miss_input"])
        
        self.assertEqual(result, [b"hit_prediction", None, b"new_prediction"])
        
        self.mock_repo.batch_predict.assert_called_once_with([b"miss_input"])
        miss_path.write_bytes.assert_called_once_with(b"new_prediction")
        hit_path.write_bytes.assert_not_called()

if __name__ == '__main__':
    unittest.main()
