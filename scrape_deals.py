# scrape_deals.py

from scrapers.sneakers.nike import scrape_nike_air_max_1

def main():
    print("Finding Nike Air Max 1 deals...\n")
    deals = scrape_nike_air_max_1()

    print("\nFinal Nike Air Max 1 Deals:\n")
    for deal in deals:
        print(f"{deal['title']} ({deal['style']})")
        print(f"  Current Price: {deal['price']}")
        print(f"  Original Price: {deal['original_price']}")
        if deal['discount']:
            print(f"  Discount: {deal['discount']}")
        print(f"  URL: {deal['url']}\n")

    print("Summary:")
    print(f"  Total unique products: {len(deals)}")
    sale_count = sum(1 for d in deals if d['discount'])
    print(f"  Variants on sale: {sale_count}")

if __name__ == "__main__":
    main()
