import argparse
import json
import os

import requests


def sync_ownedby(api_url, admin_token, ownedby_data):
    """
    Sends a PUT request to the ownedby endpoint to update data.

    :param api_url: Base URL of the API (e.g., 'http://localhost:8080/api/model_ownedby')
    :param admin_token: Admin authentication token
    :param ownedby_data: Dictionary containing ownedby data to update
    """
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }
    response = requests.put(api_url, json=ownedby_data, headers=headers)

    if response.status_code == 200:
        print("Update successful:", response.json())
    else:
        print("Update failed:", response.status_code, response.text)


# Example usage
def main():
    ONEHUB_URL = os.getenv("ONEHUB_URL").strip("/")
    API_URL = f"{ONEHUB_URL}/api/model_ownedby"
    ADMIN_TOKEN = os.getenv("ONEHUB_ADMIN_TOKEN")  # Replace with a valid admin token

    assert ONEHUB_URL is not None, "ONEHUB_URL is not set"
    assert ADMIN_TOKEN is not None, "ONEHUB_ADMIN_TOKEN is not set"

    parser = argparse.ArgumentParser(description="Update ownedby data.")
    parser.add_argument(
        "--json_file",
        "--json",
        "-j",
        type=str,
        default="./ownedby.json",
        help="Path to the JSON file containing ownedby data (default: ./ownedby.json)",
    )
    parser.add_argument(
        "--json_url",
        "-u",
        type=str,
        help="URL to the JSON data containing ownedby information",
    )
    args = parser.parse_args()

    ownedby_json = None
    if args.json_url:
        response = requests.get(args.json_url)
        response.raise_for_status()
        ownedby_json = response.json()
    else:
        with open(args.json_file, "r") as f:
            ownedby_json = json.load(f)

    if isinstance(ownedby_json, dict):
        ownedby_data = ownedby_json.get("data", {})
    else:
        ownedby_data = {}

    sync_ownedby(API_URL, ADMIN_TOKEN, ownedby_data)


if __name__ == "__main__":
    main()
