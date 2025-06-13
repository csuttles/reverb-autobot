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
        # Correctly construct the URL without any markdown formatting.
        url = f"https://api.reverb.com/api/{endpoint}"
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
        raise RuntimeError("Could not find configuration in pyproject.toml.") from e


def read_json(file_path: str) -> List[Dict[str, Any]]:
    """Reads a JSON file and returns a list of dictionaries."""
    try:
        with open(file_path, "r", encoding="utf-8") as jsonfile:
            data = json.load(jsonfile)
            if not isinstance(data, list):
                raise argparse.ArgumentTypeError(
                    f"JSON file must contain a list of products. Found {type(data)}."
                )
            return data
    except FileNotFoundError as e:
        raise argparse.ArgumentTypeError(f"File not found: {file_path}") from e
    except json.JSONDecodeError as e:
        raise argparse.ArgumentTypeError(f"Invalid JSON in file: {file_path}") from e


def export_to_csv(products: List[Dict[str, Any]], output_file_path: str):
    """
    Exports a list of product dictionaries to a CSV file.

    Args:
        products: A list of product data.
        output_file_path: The path to the output CSV file.
    """
    if not products:
        print("No products to export.")
        return

    processed_products = []
    all_headers = set()

    for product in products:
        # Make a copy to avoid modifying the original list
        processed_product = product.copy()

        # Flatten photos into separate columns
        if "photos" in processed_product and isinstance(
            processed_product["photos"], list
        ):
            photos = processed_product.pop("photos")
            for i, photo_url in enumerate(photos, 1):
                processed_product[f"product_image_{i}"] = photo_url

        processed_products.append(processed_product)
        all_headers.update(processed_product.keys())

    try:
        with open(output_file_path, "w", newline="", encoding="utf-8") as csvfile:
            # Sort headers for consistent column order
            fieldnames = sorted(list(all_headers))
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_products)
        print(f"Successfully exported data to {output_file_path}")
    except IOError as e:
        print(f"Error writing to file {output_file_path}: {e}")


def main():
    """The main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="A command-line tool for managing Reverb inventory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List all products in your inventory.")

    create_parser = subparsers.add_parser(
        "create", help="Create new products from a JSON file."
    )
    create_parser.add_argument(
        "-f", "--file", required=True, type=read_json, help="Path to the JSON file."
    )

    update_parser = subparsers.add_parser(
        "update", help="Update existing products from a JSON file."
    )
    update_parser.add_argument(
        "-f", "--file", required=True, type=read_json, help="Path to the JSON file."
    )

    export_parser = subparsers.add_parser(
        "export", help="Export a JSON file to a CSV file."
    )
    export_parser.add_argument(
        "-i",
        "--input-file",
        required=True,
        type=read_json,
        help="Path to the input JSON file.",
    )
    export_parser.add_argument(
        "-o",
        "--output-file",
        required=True,
        help="Path for the output CSV file.",
    )

    args = parser.parse_args()

    try:
        if args.command == "export":
            export_to_csv(args.input_file, args.output_file)
            return

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

