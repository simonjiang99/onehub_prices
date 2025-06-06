import http.client
import json

from utils import SCALE_FACTOR_USD, integrate_prices, yaml_to_json


def round_to_three(num: float) -> float:
    return round(num * 1000) / 1000

if __name__ == "__main__":
    url = "openrouter.ai"
    endpoint = "/api/v1/models"
    headers = {"Content-Type": "application/json"}

    openrouter_channel_type = 20  # Matches OpenRouter in ownedby.json

    conn = http.client.HTTPSConnection(url)
    conn.request("GET", endpoint, headers=headers)

    response = conn.getresponse()
    print(response.status)

    body = response.read().decode("utf-8")
    models = json.loads(body)["data"]

    openrouter_price_json = []
    for model in models:
        try:
            model_name = model["id"]
            input_price = float(model["pricing"]["prompt"]) * 1000 / SCALE_FACTOR_USD
            output_price = (
                float(model["pricing"]["completion"]) * 1000 / SCALE_FACTOR_USD
            )

            input_price = round_to_three(input_price)
            output_price = round_to_three(output_price)

            if input_price >= 0 and output_price >= 0:
                price_data = {
                    "model": model_name,
                    "type": "tokens",
                    "channel_type": openrouter_channel_type,
                    "input": input_price,
                    "output": output_price,
                }
                openrouter_price_json.append(price_data)
                print(
                    f"Model: {model_name}, Input: {input_price}, Output: {output_price}"
                )
                print("-" * 40)
        except KeyError:
            continue

    # Load and convert manual_prices/OpenRouter.yaml
    manual_prices = yaml_to_json("manual_prices", "OpenRouter.yaml")

    # Integrate manual prices and openrouter_prices
    integrated_prices = integrate_prices(manual_prices, {"data": openrouter_price_json})

    # Save integrated price data
    with open("openrouter_prices.json", "w", encoding="utf-8") as f:
        json.dump(integrated_prices, f, ensure_ascii=False, indent=2)
