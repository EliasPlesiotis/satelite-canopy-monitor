import unittest
from unittest.mock import MagicMock, patch
from tile_api.repositories.meteoblue_heat_map_repository import MeteoblueHeatMapRepository

class TestMeteoblueHeatMapRepository(unittest.TestCase):
    @patch('tile_api.repositories.meteoblue_heat_map_repository.urllib.request.urlopen')
    @patch('tile_api.repositories.meteoblue_heat_map_repository.urllib.request.Request')
    def test_get_heat_map_success(self, mock_request_class, mock_urlopen):
        mock_request = MagicMock()
        mock_request_class.return_value = mock_request
        
        mock_response = MagicMock()
        mock_response.read.return_value = b"heatmap_data"
        
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_context_manager
        
        repo = MeteoblueHeatMapRepository(timeout=5)
        result = repo.get_heat_map("London", "2023-01-01")
        
        self.assertEqual(result, b"heatmap_data")
        
        # Depending on urlencode, the order of parameters might be deterministic or not.
        # But 'city=London&time=2023-01-01' is expected for python 3.7+
        expected_url = "https://cityclimateapi.meteoblue.com/v2/heat-maps/?city=London&time=2023-01-01"
        mock_request_class.assert_called_once_with(expected_url, headers={"User-Agent": repo.user_agent})
        mock_urlopen.assert_called_once_with(mock_request, timeout=5)

    @patch('tile_api.repositories.meteoblue_heat_map_repository.urllib.request.urlopen')
    def test_get_heat_map_error(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Network Error")
        
        repo = MeteoblueHeatMapRepository(timeout=5)
        result = repo.get_heat_map("London", "2023-01-01")
        
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
