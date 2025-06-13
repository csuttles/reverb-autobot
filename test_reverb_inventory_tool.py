"""
Unit tests for the Reverb inventory management tool.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import HTTPError

# Import functions and classes from the main script
import reverb_inventory_tool as rit


@pytest.fixture
def mock_api(mocker):
    """Fixture to mock the ReverbAPI class."""
    mock = mocker.patch("reverb_inventory_tool.ReverbAPI", autospec=True)
    # To mock the instance created by ReverbAPI(token)
    instance = mock.return_value
    instance.list_products.return_value = [{"title": "Test Product"}]
    instance.create_product.return_value = {"title": "New Product"}
    instance.update_product.return_value = {"title": "Updated Product"}
    return instance


@pytest.fixture
def api_instance():
    """Returns a real ReverbAPI instance for testing _make_request."""
    return rit.ReverbAPI(api_token="test_token")


def test_make_request_success(mocker, api_instance):
    """Test a successful API request."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status.return_value = None
    mocker.patch("requests.request", return_value=mock_response)

    endpoint = "my/listings"
    result = api_instance._make_request("GET", endpoint)

    # Check that requests.request was called correctly
    requests.request.assert_called_once_with(
        "GET",
        f"https://api.reverb.com/api/{endpoint}",
        headers=api_instance.headers,
        params=None,
        json=None,
        timeout=30,
    )
    assert result == {"status": "ok"}


def test_make_request_http_error(mocker, api_instance):
    """Test that an HTTPError is correctly handled."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
    mocker.patch("requests.request", return_value=mock_response)

    with pytest.raises(ValueError, match="HTTP error occurred"):
        api_instance._make_request("GET", "bad/endpoint")


def test_read_json_success(tmp_path):
    """Test reading a valid JSON file."""
    content = [{"id": 1, "name": "Test"}]
    p = tmp_path / "test.json"
    p.write_text(json.dumps(content))
    data = rit.read_json(str(p))
    assert data == content


def test_read_json_not_found():
    """Test reading a non-existent JSON file."""
    with pytest.raises(pytest.raises(argparse.ArgumentTypeError, match="File not found")):
        rit.read_json("non_existent_file.json")


def test_read_json_invalid_format(tmp_path):
    """Test reading an invalid JSON file."""
    p = tmp_path / "invalid.json"
    p.write_text("this is not json")
    with pytest.raises(pytest.raises(argparse.ArgumentTypeError, match="Invalid JSON")):
        rit.read_json(str(p))


def test_export_to_csv(tmp_path):
    """Test exporting data to a CSV file."""
    products = [
        {"sku": "123", "price": "100", "photos": ["url1", "url2"]},
        {"sku": "456", "price": "200", "title": "Another Item"},
    ]
    output_file = tmp_path / "output.csv"
    rit.export_to_csv(products, str(output_file))

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        # Headers are sorted alphabetically
        assert header == ["price", "product_image_1", "product_image_2", "sku", "title"]
        row1 = next(reader)
        assert row1 == ["100", "url1", "url2", "123", ""]
        row2 = next(reader)
        assert row2 == ["200", "", "", "456", "Another Item"]

# --- CLI Command Tests ---

def test_main_list_command(mocker, mock_api):
    """Test the 'list' command."""
    mocker.patch("sys.argv", ["reverb_inventory_tool.py", "list"])
    mocker.patch("reverb_inventory_tool.load_config", return_value={"api_token": "fake_token"})

    rit.main()

    # Verify the correct API method was called
    mock_api.list_products.assert_called_once()


def test_main_update_command(mocker, tmp_path, mock_api):
    """Test the 'update' command."""
    json_content = [{"sku": "abc", "price": "99.99"}]
    p = tmp_path / "update.json"
    p.write_text(json.dumps(json_content))

    mocker.patch("sys.argv", ["reverb_inventory_tool.py", "update", "--file", str(p)])
    mocker.patch("reverb_inventory_tool.load_config", return_value={"api_token": "fake_token"})

    rit.main()

    # Verify the update method was called with the correct data
    mock_api.update_product.assert_called_once_with("abc", {"price": "99.99"})


def test_main_export_command(mocker, tmp_path):
    """Test the 'export' command."""
    json_content = [{"sku": "xyz", "title": "Export Me"}]
    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps(json_content))
    output_file = tmp_path / "output.csv"

    mocker.patch("sys.argv", ["reverb_inventory_tool.py", "export", "--input-file", str(input_file), "--output-file", str(output_file)])

    # Mock the export function to check if it's called
    mock_export_func = mocker.patch("reverb_inventory_tool.export_to_csv")

    rit.main()

    mock_export_func.assert_called_once_with(json_content, str(output_file))


