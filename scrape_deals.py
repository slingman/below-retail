import json
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals
from utils.promo_codes import apply_promo_code

def match_deals(nike_deals, footlocker_deals):
    """Match Nike's results with Foot Locker's based on exact style ID and apply promo codes."""
    
    matched_deals = []

    for nike_deal in nike_deals:
        nike_link = nike_deal["link"]
        nike_price = nike_deal["price"]
        
        # Extract style ID from Nike's link (last segment after the last '/')
        nike_style_id = nike_link.split("/")[-1]

        for footlocker_deal in footlocker_deals:
            footlocker_link = footlocker_deal["link"]
            
            # Extract style ID from Foot Locker's link (last segment before ".html")
            footlocker_style_id = footlocker_link.split("/")[-1].split(".")[0]

            if nike_style_id == footlocker_style_id:
                # Apply promo codes
                nike_final_price, nike_promo = apply_promo_code("Nike", nike_price)
                footlocker_final_price, footlocker_promo = apply_promo_code("Foot Locker", footlocker_deal["price"])

                # Determine best price
                if nike_final_price and footlocker_final_price:
                    best_store = "Nike" if nike_final_price < footlocker_final_price else "Foot Locker"
                    best_price = min(nike_final_price, footlocker_final_price)
                elif nike_final_price:
                    best_store = "Nike"
                    best_price = nike_final_price
                elif footlocker_final_price:
                    best_store = "Foot Locker"
                    best_price = footlocker_final_price
                else:
                    best_store = None
                    best_price = None

                matched_deals.append({
                    "style_id": nike_style_id,
                    "product_name": nike_deal["name"],
                    "best_store": best_store,
                    "best_price": best_price,
                    "nike": {
                        "price": nike_price,
                        "final_price": nike_final_price,
                        "promo_code": nike_promo,
                        "link": nike_link
                    },
                    "footlocker": {
                        "price": footlocker_deal["price"],
                        "final_price": footlocker_final_price,
                        "promo_code": footlocker_promo,
                        "link": footlocker_link
                    }
                })

    return matched_deals

def main():
    print("\n🔍 Searching for Nike Air Max 1 at Nike and Foot Locker...\n")

    nike_deals = get_nike_deals()
    footlocker_deals = get_footlocker_deals()

    matched_deals = match_deals(nike_deals, footlocker_deals)

    results = {
        "nike": nike_deals,
        "footlocker": footlocker_deals,
        "matches": matched_deals
    }

    with open("deals.json", "w") as f:
        json.dump(results, f, indent=4)

    print("\n✅ Deals successfully saved to deals.json")
    print(f"\n✅ Scraped {len(nike_deals) + len(footlocker_deals)} total deals!")
    print(f"✅ Matched {len(matched_deals)} deals by style ID!")

if __name__ == "__main__":
    main()
