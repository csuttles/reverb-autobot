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
Create a ProductTo create a new product, you'll need to provide the path to a CSV file with the product information:poetry run python reverb_inventory_tool.py create --file /path/to/your/products.csv
Update a ProductTo update existing products, you'll also use a CSV file. The file should contain the sku of the products you want to update, along with the fields that need to be changed.poetry run python reverb_inventory_tool.py update --file /path/to/your/products.csv
Updating ImagesYou can also update product images using the update command. To do this, add columns to your CSV file with the headers product_image_1, product_image_2, and so on. The value in each of these columns should be a publicly accessible URL to the image.Example CSV for updating images:sku,product_image_1,product_image_2
REV-123,[https://your-image-host.com/image1.jpg,https://your-image-host.com/image2.jpg](https://your-image-host.com/image1.jpg,https://your-image-host.com/image2.jpg)

