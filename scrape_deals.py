from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

if __name__ == "__main__":
    print("\nFetching Nike deals...")
    nike_deals = get_nike_deals()
    print(f"\nFetched {len(nike_deals)} Nike deals.")

    print("\nFetching Foot Locker deals...")
    footlocker_deals = get_footlocker_deals()
    print(f"\nFetched {len(footlocker_deals)} Foot Locker deals.")
