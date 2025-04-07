from scrapers.sneakers.nike import scrape_nike_air_max_1

def main():
    print("Finding Nike Air Max 1 deals...\n")

    deals = scrape_nike_air_max_1()

    print("\nFinal Nike Air Max 1 Deals:\n")
    if not deals:
        print("No deals found.")
        return

    for deal in deals:
        print(f"{deal['title']} ({deal['style_id']})")
        print(f"  Price: {deal['price']}")
        print(f"  URL: {deal['url']}\n")

    print("Summary:")
    print(f"  Total unique products: {len(deals)}")
    print(f"  Variants on sale: {sum(1 for d in deals if 'Sale' in d['price'])}")

if __name__ == "__main__":
    main()
