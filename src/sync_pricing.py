import argparse
import json
import os
import sys

import requests

_current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.extend([_current_dir])

from utils import get_channel_id_mapping


def sync_pricing(
    api_url: str, admin_token: str, prices: list, overwrite: bool = False
) -> None:
    """
    Sends a POST request to the syncPricing endpoint to update pricing data.

    Args:
        api_url (str): Base URL of the API (e.g., 'http://localhost:8080/api/prices/sync').
        admin_token (str): Admin authentication token.
        prices (list): List of price objects to sync.
        overwrite (bool, optional): Whether to overwrite existing prices (default: False).

    Returns:
        None
    """
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }
    params = {"overwrite": str(overwrite).lower()}
    response = requests.post(api_url, json=prices, headers=headers, params=params)

    if response.status_code == 200:
        print("Sync successful:", response.json())
    else:
        print("Sync failed:", response.status_code, response.text)


# Example usage
def main() -> None:
    parser = argparse.ArgumentParser(description="Sync pricing data.")
    parser.add_argument(
        "--json_file",
        "--json",
        "-j",
        type=str,
        default="./oneapi_prices.json",
        help="Path to the JSON file containing pricing data (default: ./oneapi_prices.json)",
    )
    parser.add_argument(
        "--json_url",
        "-u",
        type=str,
        help="URL to the JSON data containing pricing information",
    )
    args = parser.parse_args()

    ONEHUB_URL = os.getenv("ONEHUB_URL").strip("/")
    API_URL = f"{ONEHUB_URL}/api/prices/sync"
    ADMIN_TOKEN = os.getenv("ONEHUB_ADMIN_TOKEN")  # Replace with a valid admin token
    OVERWRITE = os.getenv("SYNC_PRICE_OVERWRITE", True)

    assert ONEHUB_URL is not None, "ONEHUB_URL is not set"
    assert ADMIN_TOKEN is not None, "ONEHUB_ADMIN_TOKEN is not set"

    price_json = None
    if args.json_url:
        response = requests.get(args.json_url)
        response.raise_for_status()
        price_json = response.json()
    else:
        with open(args.json_file, "r") as f:
            price_json = json.load(f)
    prices = []
    if isinstance(price_json, list):
        prices = price_json
    elif isinstance(price_json, dict):
        prices = price_json["data"]
    else:
        prices = []
    print(prices)

    sync_pricing(API_URL, ADMIN_TOKEN, prices, OVERWRITE)

    # download the latest ownedby.json to local for git purpose
    get_channel_id_mapping(save_to_file=True)

if __name__ == "__main__":
    main()
