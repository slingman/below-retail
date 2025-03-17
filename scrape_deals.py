import json
import os
from sneakers.nike import get_nike_deals
from sneakers.footlocker import get_footlocker_deals

def compare_prices(nike_deals, footlocker_deals):
    """Compare Nike and Foot Locker deals based on matching style IDs."""
    nike_style_map = {deal["style_id"]: deal for deal in nike_deals if deal.get("style_id")}
    footlocker_style_map = {deal["style_id"]: deal for deal in footlocker_deals if deal.get("style_id")}

    matches = []

    for style_id, nike_deal in nike_style_map.items():
        if style_id in footlocker_style_map:
            footlocker_deal = footlocker_style_map[style_id]

            nike_price = float(nike_deal["price"]) if nike_deal["price"] else float("inf")
            footlocker_price = float(footlocker_deal["price"]) if footlocker_deal["price"] else float("inf")

            cheaper_store = "Nike" if nike_price < footlocker_price else "Foot Locker"
            final_price = min(nike_price, footlocker_price)

            matches.append({
                "style_id": style_id,
                "product_name": nike_deal["name"],
                "cheapest_store": cheaper_store,
                "nike_price": nike_price if nike_price != float("inf") else None,
                "footlocker_price": footlocker_price if footlocker_price != float("inf") else None,
                "final_price": final_price,
                "nike_link": nike_deal["link"],
                "footlocker_link": footlocker_deal["link"],
            })

    return matches

def save_results(nike_deals, footlocker_deals, matches):
    """Save the deals and matches to a JSON file."""
    results = {
        "nike": nike_deals,
        "footlocker": footlocker_deals,
        "matches": matches,
    }

    with open("deals.json", "w") as f:
        json.dump(results, f, indent=4)

def main():
    print("\nFetching Nike deals...\n")
    nike_deals = get_nike_deals()

    print("\nFetching Foot Locker deals...\n")
    footlocker_deals = get_footlocker_deals()

    print("\nComparing matching products by style ID...\n")
    matches = compare_prices(nike_deals, footlocker_deals)

    save_results(nike_deals, footlocker_deals, matches)
    print("\n✅ Done fetching and comparing sneaker deals!\n")

if __name__ == "__main__":
    main()
