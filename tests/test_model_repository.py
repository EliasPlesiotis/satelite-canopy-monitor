import unittest
from unittest.mock import MagicMock, patch
from tile_api.repositories.model_repository import KerasModelRepository

class TestKerasModelRepository(unittest.TestCase):
    @patch('tile_api.repositories.model_repository.ProcessPoolExecutor')
    @patch('tile_api.repositories.model_repository.threading.Thread')
    def test_init_starts_thread(self, mock_thread, mock_executor):
        repo = KerasModelRepository("dummy_model.h5")
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
        
    @patch('tile_api.repositories.model_repository.ProcessPoolExecutor')
    def test_predict(self, mock_executor_class):
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor
        
        repo = KerasModelRepository("dummy_model.h5")
        repo._ensure_executor()
        
        mock_future = MagicMock()
        mock_future.result.return_value = [b"prediction_bytes"]
        mock_executor.submit.return_value = mock_future
        
        result = repo.predict(b"input_image")
        
        self.assertEqual(result, b"prediction_bytes")
        mock_executor.submit.assert_called_once()

    @patch('tile_api.repositories.model_repository.ProcessPoolExecutor')
    def test_batch_predict(self, mock_executor_class):
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor
        
        repo = KerasModelRepository("dummy_model.h5")
        repo._ensure_executor()
        
        mock_future = MagicMock()
        mock_future.result.return_value = [b"pred1", b"pred2"]
        mock_executor.submit.return_value = mock_future
        
        result = repo.batch_predict([b"img1", b"img2"])
        
        self.assertEqual(result, [b"pred1", b"pred2"])
        mock_executor.submit.assert_called_once()

    @patch('tile_api.repositories.model_repository.ProcessPoolExecutor')
    def test_batch_predict_empty(self, mock_executor_class):
        repo = KerasModelRepository("dummy_model.h5")
        repo._ensure_executor()
        
        result = repo.batch_predict([])
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
