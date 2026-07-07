import unittest
from unittest.mock import MagicMock, patch
from tile_api.repositories.google_earth_image_repository import GoogleEarthImageRepository

class TestGoogleEarthImageRepository(unittest.TestCase):
    @patch('tile_api.repositories.google_earth_image_repository.urllib.request.urlopen')
    @patch('tile_api.repositories.google_earth_image_repository.urllib.request.Request')
    def test_get_image_success(self, mock_request_class, mock_urlopen):
        mock_request = MagicMock()
        mock_request_class.return_value = mock_request
        
        mock_response = MagicMock()
        mock_response.read.return_value = b"image_data"
        
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_context_manager
        
        repo = GoogleEarthImageRepository(timeout=5)
        result = repo.get_image(10, 20, 15)
        
        self.assertEqual(result, b"image_data")
        
        expected_url = "https://mt1.google.com/vt/lyrs=s&x=10&y=20&z=15"
        mock_request_class.assert_called_once_with(expected_url, headers={"User-Agent": repo.user_agent})
        mock_urlopen.assert_called_once_with(mock_request, timeout=5)

    @patch('tile_api.repositories.google_earth_image_repository.urllib.request.urlopen')
    def test_get_image_error(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Network Error")
        
        repo = GoogleEarthImageRepository(timeout=5)
        with self.assertRaisesRegex(RuntimeError, "Error downloading tile 15/10/20: Network Error"):
            repo.get_image(10, 20, 15)

if __name__ == '__main__':
    unittest.main()
