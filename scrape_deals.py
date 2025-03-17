import json
from scrapers.sneakers.nike import scrape_nike
from scrapers.sneakers.footlocker import scrape_footlocker
from utils.file_manager import save_deals

def convert_list_to_dict(deals_list, source):
    """ Converts a list of deals into a dictionary indexed by style_id """
    deals_dict = {}

    for product in deals_list:
        if not isinstance(product, dict):  # Debugging: Print if data is incorrect
            print(f"❌ Error: Invalid product format from {source}: {product}")
            continue

        style_id = product.get("style_id")
        if style_id:  # Only store if style_id exists
            deals_dict[style_id] = product
        else:
            print(f"⚠️ Warning: Missing style_id for {product.get('name', 'UNKNOWN')} from {source}, skipping.")

    return deals_dict

def main():
    print("\n🔍 Searching for Nike Air Max 1 at Nike and Foot Locker...\n")

    # Scrape Nike and Foot Locker
    nike_deals_list = scrape_nike("air max 1")
    footlocker_deals_list = scrape_footlocker("air max 1")

    # Convert lists to dictionaries (Handle incorrect data gracefully)
    nike_deals = convert_list_to_dict(nike_deals_list, "Nike")
    footlocker_deals = convert_list_to_dict(footlocker_deals_list, "Foot Locker")

    # Compare deals by style ID
    matched_deals = {}

    for style_id, nike_product in nike_deals.items():
        if style_id in footlocker_deals:
            footlocker_product = footlocker_deals[style_id]

            # Merge the price data
            combined_prices = nike_product["prices"] + footlocker_product["prices"]

            matched_deals[style_id] = {
                "name": nike_product["name"],
                "image": nike_product["image"],
                "prices": combined_prices,
            }

    # Save results
    save_deals(matched_deals)

    print(f"\n✅ Scraped {len(matched_deals)} deals for Nike Air Max 1!\n")


if __name__ == "__main__":
    main()
