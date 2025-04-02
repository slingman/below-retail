from scrapers.sneakers.nike import scrape_nike_air_max_1

if __name__ == "__main__":
    print("Finding Nike Air Max 1 deals...\n")
    results = scrape_nike_air_max_1()

    if not results:
        print("No deals found.")
