"""
A command-line tool for managing inventory on Reverb.com using their API.
"""

import argparse
import csv
import json
from functools import lru_cache
from typing import Any, Dict, List

import requests
import toml


class ReverbAPI:
    """A wrapper for the Reverb API."""

    BASE_URL = "[https://api.reverb.com/api](https://api.reverb.com/api)"

    def __init__(self, api_token: str):
        """
        Initializes the ReverbAPI client.

        Args:
            api_token: Your Reverb Personal Access Token.
        """
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/hal+json",
            "Accept": "application/hal+json",
            "Accept-Version": "3.0",
        }

    @lru_cache(maxsize=128)
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Makes a request to the Reverb API.

        Args:
            method: The HTTP method to use (e.g., 'GET', 'POST', 'PUT').
            endpoint: The API endpoint to call.
            params: A dictionary of query parameters.
            data: A dictionary of data to send in the request body.

        Returns:
            The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: For network-related errors.
            ValueError: If the API returns an error.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            raise ValueError(f"HTTP error occurred: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            raise ValueError(f"Request error occurred: {req_err}") from req_err

    def list_products(self) -> List[Dict[str, Any]]:
        """
        Retrieves a list of all products.

        Returns:
            A list of dictionaries, where each dictionary represents a product.
        """
        return self._make_request("GET", "my/listings")

    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new product.

        Args:
            product_data: A dictionary of product data.

        Returns:
            The newly created product.
        """
        return self._make_request("POST", "listings", data=product_data)

    def update_product(self, sku: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing product.

        Args:
            sku: The SKU of the product to update.
            product_data: A dictionary of product data to update.

        Returns:
            The updated product.
        """
        endpoint = f"listings/{sku}"
        return self._make_request("PUT", endpoint, data=product_data)


def load_config() -> Dict[str, Any]:
    """Loads the configuration from pyproject.toml."""
    try:
        return toml.load("pyproject.toml")["tool"]["reverb_inventory_tool"]
    except (FileNotFoundError, KeyError) as e:
        raise RuntimeError(
            "Could not find configuration in pyproject.toml."
        ) from e


def read_csv(file_path: str) -> List[Dict[str, Any]]:
    """Reads a CSV file and returns a list of dictionaries."""
    try:
        with open(file_path, "r", encoding="utf-8") as csvfile:
            return list(csv.DictReader(csvfile))
    except FileNotFoundError as e:
        raise argparse.ArgumentTypeError(f"File not found: {file_path}") from e


def main():
    """The main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="A command-line tool for managing Reverb inventory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # List command
    subparsers.add_parser("list", help="List all products in your inventory.")

    # Create command
    create_parser = subparsers.add_parser(
        "create", help="Create new products from a CSV file."
    )
    create_parser.add_argument(
        "-f",
        "--file",
        required=True,
        type=read_csv,
        help="Path to the CSV file with new products.",
    )

    # Update command
    update_parser = subparsers.add_parser(
        "update", help="Update existing products from a CSV file."
    )
    update_parser.add_argument(
        "-f",
        "--file",
        required=True,
        type=read_csv,
        help="Path to the CSV file with product updates.",
    )

    args = parser.parse_args()

    try:
        config = load_config()
        api = ReverbAPI(config["api_token"])

        if args.command == "list":
            products = api.list_products()
            print(json.dumps(products, indent=2))

        elif args.command == "create":
            for product in args.file:
                created_product = api.create_product(product)
                print(f"Created product: {created_product.get('title')}")

        elif args.command == "update":
            for product in args.file:
                sku = product.pop("sku", None)
                if not sku:
                    print("SKU is required for updating a product.")
                    continue
                updated_product = api.update_product(sku, product)
                print(f"Updated product: {updated_product.get('title')}")

    except (RuntimeError, ValueError, argparse.ArgumentTypeError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
