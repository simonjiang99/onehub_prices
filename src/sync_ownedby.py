import argparse
import json
import os
from typing import Dict, List, Tuple

import requests
import yaml


def load_ownedby(json_file_path: str = None, url: str = None) -> List:
    """
    Load data from either a local JSON file or a URL.
    One of `json_file_path` or `url` must be provided.
    """
    if not json_file_path and not url:
        raise ValueError("Either `json_file_path` or `url` must be provided.")

    if json_file_path:
        if not os.path.exists(json_file_path):
            print(f"未找到 {json_file_path} 文件。")
            return []
        with open(json_file_path, "r", encoding="utf-8") as file:
            raw_ownedby = json.load(file)["data"]
    elif url:
        response = requests.get(url)
        response.raise_for_status()
        raw_ownedby = response.json()["data"]

    ownedby_data = {}
    # ownedby_data = {each["name"]: each for each in raw_ownedby.values() if each['name'] != "" else continue}
    for each in raw_ownedby.values():
        if each["name"] == "":
            continue
        ownedby_data[each["name"]] = each

    return ownedby_data


def update_ownedby(
    ownedby_original: Dict[str, Dict[str, str]],
    ownedby_manual: Dict[str, Dict[str, str]],
) -> Dict[str, List]:
    """
    Compare original and manual versions and derive a list of to_delete and to_add
    if an entry is not in original, it's to_add
    if an entry in original is not in manual, it's to_delete
    if an entry is in both, compare the values and if they are different, it's to_delete and to_add
    """

    to_delete = []
    to_add = []

    names_original = set(ownedby_original.keys())
    names_manual = set(ownedby_manual.keys())

    # find all names in original but not in manual
    to_delete.extend(names_original - names_manual)
    # find all names in manual but not in original
    to_add.extend(names_manual - names_original)
    # find all names in both but with different values
    for name in names_original & names_manual:
        # compare by the jsonified dict content
        if json.dumps(ownedby_original[name], sort_keys=True) != json.dumps(
            ownedby_manual[name], sort_keys=True
        ):
            to_delete.append(name)
            to_add.append(name)

    to_delete = [ownedby_original[name] for name in to_delete]
    to_add = [ownedby_manual[name] for name in to_add]

    return {"to_delete": to_delete, "to_add": to_add}


def delete_ownedby(api_url, admin_token, ownedby_id):
    """
    Sends a DELETE request to the ownedby endpoint to delete data.

    :param api_url: Base URL of the API (e.g., 'http://localhost:8080/api/model_ownedby')
    :param admin_token: Admin authentication token
    :param ownedby_id: ID of the ownedby entry to delete
    """
    headers = {
        "Authorization": f"Bearer {admin_token}",
    }
    response = requests.delete(f"{api_url}/{ownedby_id}", headers=headers)

    if response.status_code == 200:
        print("Delete successful:", response.json())
    else:
        print("Delete failed:", response.status_code, response.text)


def add_ownedby(api_url, admin_token, ownedby_data):
    """
    Sends a POST request to the ownedby endpoint to add data.

    :param api_url: Base URL of the API (e.g., 'http://localhost:8080/api/model_ownedby')
    :param admin_token: Admin authentication token
    :param ownedby_data: Dictionary containing ownedby data to add
    """
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }
    response = requests.post(api_url, json=ownedby_data, headers=headers)

    if response.status_code == 200:
        print("Add successful:", response.json())
    else:
        print("Add failed:", response.status_code, response.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge ownedby data.")
    parser.add_argument(
        "--source_json",
        type=str,
        help="Path to the source JSON file (e.g., ownedby.json).",
    )
    parser.add_argument(
        "--source_url",
        type=str,
        help="URL to the source JSON data.",
    )
    parser.add_argument(
        "--manual_json",
        type=str,
        help="Path to the manual JSON file (e.g., ownedby_manual.json).",
    )
    parser.add_argument(
        "--manual_url",
        type=str,
        help="URL to the manual JSON data.",
    )
    args = parser.parse_args()

    # Convert JSON to YAML format
    if not args.source_json and not args.source_url:
        raise ValueError("Either `source_json` or `source_url` must be provided.")
    if not args.manual_json and not args.manual_url:
        raise ValueError("Either `manual_json` or `manual_url` must be provided.")

    ONEHUB_URL = os.getenv("ONEHUB_URL").strip("/")
    API_URL = f"{ONEHUB_URL}/api/model_ownedby"
    ADMIN_TOKEN = os.getenv("ONEHUB_ADMIN_TOKEN")  # Replace with a valid admin token

    assert ONEHUB_URL is not None, "ONEHUB_URL is not set"
    assert ADMIN_TOKEN is not None, "ONEHUB_ADMIN_TOKEN is not set"

    ownedby_original = load_ownedby(
        json_file_path=args.source_json, url=args.source_url
    )
    ownedby_manual = load_ownedby(json_file_path=args.manual_json, url=args.manual_url)

    ownedby_updates = update_ownedby(ownedby_original, ownedby_manual)

    print(json.dumps(ownedby_updates, indent=4, ensure_ascii=False, sort_keys=False))

    for each in ownedby_updates["to_delete"]:
        delete_ownedby(API_URL, ADMIN_TOKEN, each["id"])
    for each in ownedby_updates["to_add"]:
        add_ownedby(API_URL, ADMIN_TOKEN, each)
