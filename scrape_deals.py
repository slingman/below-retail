from scrapers.sneakers.nike import scrape_nike_air_max_1

def main():
    print("Finding Nike Air Max 1 deals...\n")
    deals = scrape_nike_air_max_1()

    print("\nFinal Nike Air Max 1 Deals:\n")
    for deal in deals:
        print(f"{deal['title']} ({deal['style']})")
        print(f"  Price: {deal['price']}")
        print(f"  URL: {deal['url']}\n")

    print("Summary:")
    print(f"  Total unique products: {len(deals)}")
    on_sale = [d for d in deals if "%" in d['price']]
    print(f"  Variants on sale: {len(on_sale)}")

if __name__ == "__main__":
    main()
