# scrape_deals.py

from scrapers.sneakers.nike import scrape_nike_air_max_1

def main():
    print("Finding Nike Air Max 1 deals...\n")
    products = scrape_nike_air_max_1()

    if not products:
        print("No deals found.")
        return

    # You can extend this later to filter deals, tweet, or save to a file.
    # For now, it just prints everything inside nike.py

if __name__ == "__main__":
    main()
