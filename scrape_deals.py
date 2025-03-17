from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

def scrape_deals():
    all_deals = []

    # Fetch Nike deals
    print("\nFetching Nike deals...\n")
    try:
        nike_deals = get_nike_deals()
        for deal in nike_deals:
            print(deal)
        all_deals.extend(nike_deals)
    except Exception as e:
        print(f"Error fetching Nike deals: {e}")

    # Fetch Foot Locker deals
    print("\nFetching Foot Locker deals...\n")
    try:
        footlocker_deals = get_footlocker_deals()
        for deal in footlocker_deals:
            print(deal)
        all_deals.extend(footlocker_deals)
    except Exception as e:
        print(f"Error fetching Foot Locker deals: {e}")

    return all_deals

if __name__ == "__main__":
    deals = scrape_deals()
    print(f"\nTotal deals scraped: {len(deals)}")
