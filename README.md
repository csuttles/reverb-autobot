# Reverb Inventory Management Tool

This is a command-line tool for managing your inventory on Reverb.com. It allows you to list, create, and update products using the Reverb API.

## Setup

1.  **Install Poetry:** If you don't have Poetry installed, follow the instructions on the [official website](https://python-poetry.org/docs/).

2.  **Install Dependencies:** Navigate to the project directory and run:

    ```bash
    poetry install
    ```

3.  **Configure API Token:** Open the `pyproject.toml` file and add your Reverb Personal Access Token to the `[tool.reverb_inventory_tool]` section:

    ```toml
    [tool.reverb_inventory_tool]
    api_token = "YOUR_REVERB_API_TOKEN"
    ```

## Usage

The tool is used from the command line. You can get a list of all available commands and their options by running:

```bash
poetry run python reverb_inventory_tool.py --help
List ProductsTo list all of your current products on Reverb:poetry run python reverb_inventory_tool.py list
Create ProductsTo create new products, you'll need to provide the path to a JSON file containing an array of product objects.poetry run python reverb_inventory_tool.py create --file /path/to/your/products.json
Update ProductsTo update existing products, you'll also use a JSON file. The file should contain an array of product objects. Each object must have a sku key, along with any other fields that need to be updated.poetry run python reverb_inventory_tool.py update --file /path/to/your/products.json
Export to CSVTo convert a JSON product file back to a CSV format, use the export command.poetry run python reverb_inventory_tool.py export --input-file /path/to/products.json --output-file /path/to/output.csv
TestingThis project uses pytest for unit testing. To run the tests, first ensure you have installed the development dependencies:poetry install
Then, run the test suite from your terminal:poetry run pytest
Example JSON for Creating/Updating ProductsYour JSON file should contain a list of products. For updates, ensure the sku is present. For image updates, use the photos key with an array of image URLs.[
  {
    "sku": "REV-123-UPDATE",
    "title": "Updated Vintage Pedal",
    "price": "199.99",
    "photos": [
      "[https://your-image-host.com/image1-updated.jpg](https://your-image-host.com/image1-updated.jpg)",
      "[https://your-image-host.com/image2-updated.jpg](https://your-image-host.com/image2-updated.jpg)"
    ]
  },
  {
    "new_listing": "true",
    "title": "Brand New Guitar",
    "make": "AwesomeGuitars",
    "model": "ShredMaster 5000",
    "price": "1299.00",
    "condition": "Brand New",
    "photos": [
      "[https://your-image-host.com/shredmaster1.jpg](https://your-image-host.com/shredmaster1.jpg)"
    ]
  }
]

