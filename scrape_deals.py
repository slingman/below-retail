from scrapers.sneakers.nike import scrape_nike
from scrapers.sneakers.footlocker import scrape_footlocker
from utils.file_manager import save_deals

def main():
    keyword = "Nike Air Max 1"
    print(f"\n🔍 Searching for {keyword} at Nike and Foot Locker...\n")

    # Scrape Nike
    nike_deals = scrape_nike(keyword)
    
    # Scrape Foot Locker
    footlocker_deals = scrape_footlocker(keyword)

    # Combine and compare prices based on style ID
    all_deals = {}
    
    for deal in nike_deals + footlocker_deals:
        style_id = deal.get("style_id")
        if style_id:
            if style_id not in all_deals:
                all_deals[style_id] = {"name": deal["name"], "image": deal["image"], "prices": []}
            all_deals[style_id]["prices"].append({"store": deal["store"], "price": deal["price"], "link": deal["link"]})

    # Save deals to JSON
    save_deals(all_deals)
    
    print(f"\n✅ Scraped {len(all_deals)} sneaker deals comparing Nike vs. Foot Locker!")

if __name__ == "__main__":
    main()
