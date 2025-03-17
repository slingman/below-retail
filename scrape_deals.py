from scrapers.sneakers.nike import scrape_nike
from scrapers.sneakers.footlocker import scrape_footlocker
from utils.file_manager import save_deals

def main():
    print("\n🔍 Searching for Nike Air Max 1 at Nike and Foot Locker...\n")

    nike_deals = scrape_nike("air max 1")
    footlocker_deals = scrape_footlocker("air max 1")

    # Ensure both scrapers return lists of deals
    nike_deals = list(nike_deals.values()) if isinstance(nike_deals, dict) else nike_deals
    footlocker_deals = list(footlocker_deals.values()) if isinstance(footlocker_deals, dict) else footlocker_deals

    all_deals = nike_deals + footlocker_deals

    if not all_deals:
        print("❌ No deals found!")
        return

    save_deals(all_deals)
    print(f"\n✅ Scraped {len(all_deals)} deals for Nike Air Max 1!\n")

if __name__ == "__main__":
    main()
