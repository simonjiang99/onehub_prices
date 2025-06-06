import json
import os
import urllib
import urllib.request

import dotenv


def fetch_and_sort_models(url, endpoint, headers):
    """
    Fetches models from the given URL and sorts them by modelName.

    Parameters:
    url (str): The base URL for the HTTPS connection.
    endpoint (str): The endpoint to send the GET request to.
    headers (dict): Dictionary containing any necessary headers.

    Returns:
    list: A sorted list of models based on modelName.
    """
    req = urllib.request.Request(f"{url}{endpoint}", headers=headers, method="GET")
    with urllib.request.urlopen(req) as response:
        body = response.read().decode("utf-8")
        model_json = json.loads(body)["data"]["models"]

    sorted_models = sorted(model_json, key=lambda x: x["modelName"])
    return sorted_models


def extract_specific_price(model_pricing, specification):
    """
    Retrieves and converts the price for a specific specification from the pricing data.

    Parameters:
    model_pricing (list): List of pricing details as dictionaries.
    specification (str): The specification to filter by (e.g., "completion" or "prompt").

    Returns:
    float: The price as a float, or None if the specification is not found.
    """
    return float(
        next(
            (
                item["price"]
                for item in model_pricing
                if item["specification"] == specification
            ),
            None,
        )
    )


if __name__ == "__main__":
    dotenv.load_dotenv()  # Load environment variables from .env file

    api_key: str = os.getenv("SILICONFLOW_API_KEY")
    assert api_key is not None, "SILICONFLOW_API_KEY is not set"

    url = "https://busy-bear.siliconflow.cn"  # Note: Removed 'https://' as http.client needs the host part
    endpoint = "/api/v1/playground/comprehensive/all"
    headers = {"Authorization": f"Bearer {api_key}"}

    siliconflow_channel_type: int = 45  # reference https://your-oneapi-url/api/ownedby

    model_json = fetch_and_sort_models(url, endpoint, headers)
    scale_factor = 0.014

    processed_prices = []
    for model in model_json:
        model_name = model["modelName"]
        model_pricing = model["pricing"]
        model_price_unit = model["priceUnit"]

        if model_price_unit == "/ M Tokens" and len(model_pricing) == 2:
            completion_price = extract_specific_price(model_pricing, "completion")
            prompt_price = extract_specific_price(model_pricing, "prompt")
            print(
                f"Model Name: {model_name}, Completion Price: {completion_price} {model_price_unit}, , Prompt Price: {prompt_price} {model_price_unit}",
                flush=True,
            )
            price_data = {
                "model": model_name,
                "type": "tokens",
                "channel_type": siliconflow_channel_type,
                "input": prompt_price / 1000 / scale_factor,
                "output": completion_price / 1000 / scale_factor,
            }

        else:
            model_price = float(model["price"])

            if model_price_unit in ["/ M Tokens", "/ M UTF-8 bytes", "/ M px / Steps"]:
                price_data = {
                    "model": model_name,
                    "type": "tokens",
                    "channel_type": siliconflow_channel_type,
                    "input": model_price / 1000 / scale_factor,
                    "output": model_price / 1000 / scale_factor,
                }
            elif model_price_unit in ["/ Video", "/ Image", ""]:
                price_data = {
                    "model": model_name,
                    "type": "times",
                    "channel_type": siliconflow_channel_type,
                    "input": model_price,
                    "output": model_price,
                }
            else:
                raise ValueError(f"Unknown price unit: {model_price_unit}")
            print(
                f"Model Name: {model_name}, Pricing Unit: {model_price_unit}, Pricing: {model_price}"
            )

        processed_prices.append(price_data)
        print("-" * 40)

    siliconflow_prices = {"data": processed_prices}
    # 保存集成后的价格数据
    with open("siliconflow_prices.json", "w", encoding="utf-8") as f:
        json.dump(siliconflow_prices, f, ensure_ascii=False, indent=2)
